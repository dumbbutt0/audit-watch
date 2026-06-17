#!/usr/bin/env python3
"""
triage_findings.py — Triages specialist agent findings for contest submission.

Reads output/findings_*.json, runs local hard-reject pre-checks, then calls
Claude claude-sonnet-4-20250514 (via Anthropic SDK) for nuanced triage decisions.

Outputs per-bucket JSONL files in data/triage/:
  submit.jsonl       — score >= 28, no PoC needed
  poc_required.jsonl — score >= 22, needs proof
  downgraded.jsonl   — score 16-21
  merged.jsonl       — duplicate of another finding
  rejected.jsonl     — score < 16 or hard reject

Usage:
    python scripts/triage_findings.py
"""

import json
import os
import re
import sys
from pathlib import Path

# Load .env into os.environ so anthropic picks up ANTHROPIC_API_KEY
if Path(".env").exists():
    for _line in Path(".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

import anthropic

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 2

OUTPUT_DIR  = audit_path("output")
TRIAGE_DIR  = audit_path("data/triage")
FP_DIR      = audit_path("data/fp_autopsies")
EXPLOIT_DIR = audit_path("data/exploitability")
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

SPECULATIVE_WORDS = [
    "future", "refactor", "consider", "might", "could potentially",
    "may in the future", "possible future", "would be good to",
]
ADMIN_KEYWORDS = ["admin", "emission_manager", "emergency_admin"]

# ─────────────────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────────────────

def load_all_findings() -> list[dict]:
    # Prefer merged_findings.json (already deduplicated by report_generator)
    merged_path = OUTPUT_DIR / "merged_findings.json"
    if merged_path.exists():
        try:
            data = json.loads(merged_path.read_text())
            findings = data.get("findings", [])
            for f in findings:
                if "_source_agent" not in f:
                    f["_source_agent"] = f.get("agent", "unknown")
            return findings
        except json.JSONDecodeError as e:
            print(f"  [warn] merged_findings.json parse error: {e} — falling back to per-agent files")

    # Fallback: per-agent files with set-based dedup by ID
    findings = []
    seen_ids: set[str] = set()
    for path in sorted(OUTPUT_DIR.glob("findings_*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"  [warn] Could not parse {path.name}: {e}")
            continue
        agent = data.get("agent", "")
        if agent == "protocol_context":
            continue
        for f in data.get("findings", []):
            fid = f.get("id", "")
            if fid and fid in seen_ids:
                continue
            f["_source_agent"] = agent
            findings.append(f)
            if fid:
                seen_ids.add(fid)
    return findings


def load_compound_risk_notes() -> list[str]:
    merged_path = OUTPUT_DIR / "merged_findings.json"
    if not merged_path.exists():
        return []
    try:
        data = json.loads(merged_path.read_text())
        notes = data.get("compound_risk_notes", [])
        if isinstance(notes, list):
            return notes
        return [str(notes)]
    except (json.JSONDecodeError, KeyError):
        return []


def load_system_prompt() -> str:
    try:
        from audit_context import get_audit_meta
        meta = get_audit_meta()
        platform = meta.get("platform", "immunefi")
    except Exception:
        platform = "immunefi"

    prompt_name = "triager_code4rena.md" if platform == "code4rena" else "triager.md"
    p = PROMPTS_DIR / prompt_name
    if not p.exists():
        p = PROMPTS_DIR / "triager.md"  # fallback
    if not p.exists():
        sys.exit(f"[error] {p} not found — cannot run triage")
    print(f"  Using triager prompt: {p.name}  (platform={platform})")
    return p.read_text()


# ─────────────────────────────────────────────────────────────────────────────
# Local pre-checks (no API call)
# ─────────────────────────────────────────────────────────────────────────────

def pre_check_speculative(finding: dict) -> tuple[bool, str]:
    desc = (finding.get("description", "") + " " + finding.get("impact", "")).lower()
    poc = finding.get("proof_of_concept", "") or ""
    found = [w for w in SPECULATIVE_WORDS if w in desc]
    if found and not poc.strip():
        return True, f"speculative language without PoC: {found}"
    return False, ""


def pre_check_admin_attacker(finding: dict) -> tuple[bool, str]:
    desc = (finding.get("description", "") + " " + finding.get("impact", "")).lower()
    poc = (finding.get("proof_of_concept", "") or "").lower()
    is_admin = any(kw in desc for kw in ADMIN_KEYWORDS)
    if not is_admin:
        return False, ""
    # Check if the finding explicitly argues admin is untrusted
    untrusted_markers = ["untrusted admin", "admin is untrusted", "admin can be compromised",
                         "compromised admin", "malicious admin"]
    for marker in untrusted_markers:
        if marker in desc or marker in poc:
            return False, ""
    return True, "admin-only attacker without explicit untrusted-admin argument"


def pre_check_confidence(finding: dict) -> tuple[bool, str]:
    if finding.get("confidence") == "Low" and not (finding.get("proof_of_concept") or "").strip():
        return True, "Low confidence with no proof_of_concept"
    return False, ""


def allowance_check_note(finding: dict) -> str | None:
    poc = (finding.get("proof_of_concept", "") or "").lower()
    if "allowance" in poc or "approve" in poc:
        return "Requires victim allowance — verify permissionless trigger path exists"
    return None


def cpu_dos_needs_poc(finding: dict) -> bool:
    if finding.get("_source_agent") != "dos":
        return False
    if finding.get("severity", "").lower() not in ("high", "critical"):
        return False
    poc = (finding.get("proof_of_concept", "") or "").lower()
    operation_indicators = ["operations", "iterations", "loop count", "gas estimate",
                            "o(n)", "complexity", "count:"]
    return not any(ind in poc for ind in operation_indicators)


def _make_hard_reject(
    finding: dict,
    invalidation_tags: list[str],
    blocking_issues: list[str],
    reason_prefix: str = "",
) -> dict:
    """Build a triage record for a hard-rejected finding (no API call needed)."""
    reason = f"{reason_prefix} {'; '.join(blocking_issues)}".strip()
    return {
        "finding_id": finding.get("id", "unknown"),
        "title": finding.get("title", ""),
        "triage_status": "reject",
        "recommended_severity": finding.get("severity", "medium").lower(),
        "score": {
            "attacker_control": 0, "sensitive_sink": 0, "missing_check_clarity": 0,
            "impact_realism": 0, "poc_feasibility": 0, "scope_safety": 0,
            "duplicate_risk": 0, "total": 0,
        },
        "confidence": 1,
        "attacker_model": {
            "attacker_type": "unknown",
            "required_permissions": [],
            "required_preconditions": [],
            "realistic": False,
        },
        "exploitability": {
            "can_trigger": False, "profit_or_damage": "none",
            "blocked_by_auth": True, "blocked_by_atomicity": False,
            "blocked_by_scope": False, "needs_poc": False,
        },
        "impact": {
            "asset_at_risk": "none", "victim": "none",
            "loss_type": "none", "severity_reason": reason,
        },
        "quality_gate": {
            "has_exact_location": False, "has_root_cause": False,
            "has_exploit_steps": False, "has_patch": False,
            "likely_duplicate": False, "speculative_language": [],
        },
        "invalidation_tags": invalidation_tags,
        "decision_reason": reason,
        "required_next_steps": [f"Hard-rejected by pre-screening: {reason}"],
        "_hard_reject": True,
    }


def pre_check_defense_coverage(finding: dict, defense_map: dict) -> tuple[bool, str]:
    """Hard reject if the vulnerable function has full defense coverage and no evasion path."""
    fid = finding.get("id", "")
    mapping = defense_map.get(fid, {})
    if not mapping:
        return False, ""
    if mapping.get("coverage") == "full" and not mapping.get("evasion_path", ""):
        names = [d.get("modifier") for d in mapping.get("applicable_defenses", [])]
        inherited = mapping.get("inherited_from", "")
        note = f"inherited from {inherited}" if inherited else "applied directly"
        return True, f"full defense coverage via {names} ({note}) — no evasion path"
    return False, ""


def pre_check_economics(finding: dict, exploit_models: dict) -> tuple[bool, str]:
    """Hard reject if attack cost clearly exceeds profit or no economic impact exists."""
    fid = finding.get("id", "")
    model = exploit_models.get(fid, {})

    pod = model.get("profit_or_damage", {})
    if isinstance(pod, dict) and pod.get("type") == "none" and pod.get("bounded"):
        return True, "exploitability model: no profit or damage possible (type=none, bounded=True)"

    desc = finding.get("description", "") + " " + (finding.get("proof_of_concept", "") or "")
    cost_matches = re.findall(r'cost[s]?\s+(?:of\s+)?(\d+\.?\d*)\s*ETH', desc, re.IGNORECASE)
    gain_matches = re.findall(r'(?:gain|profit|steal|extract|drain)\s+(\d+\.?\d*)\s*ETH', desc, re.IGNORECASE)
    if cost_matches and gain_matches:
        max_cost = max(float(x) for x in cost_matches)
        max_gain = max(float(x) for x in gain_matches)
        if max_cost > max_gain * 1.5:
            return True, f"attack cost ({max_cost} ETH) > estimated profit ({max_gain} ETH)"
    return False, ""


def pre_check_ice_hold(finding: dict, ice_findings: dict) -> tuple[bool, str]:
    """Route findings held by impact chain escalation to poc_required/manual_review.
    Returns (should_route_to_poc_required, reason). Never permanently rejects on hold alone."""
    fid = finding.get("id", "")
    ice = ice_findings.get(fid, {}).get("ice", {})
    if not ice:
        return False, ""
    if ice.get("hold") and not ice.get("manual_override", {}).get("enabled"):
        return True, "ice.hold=true: no consumer found for corrupted state. Route to poc_required."
    if ice.get("severity_ceiling"):
        claimed = finding.get("severity", "")
        ceiling = ice.get("severity_ceiling", "")
        severity_rank = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Informational": 0}
        if severity_rank.get(claimed, 0) > severity_rank.get(ceiling, 4):
            finding["severity"] = ceiling  # cap severity in-place, don't reject
    return False, ""


def _load_ice_findings() -> dict:
    """Load findings_ice.json as a dict keyed by finding_id."""
    path = OUTPUT_DIR / "findings_ice.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return {f.get("id", ""): f for f in data.get("findings", []) if f.get("id")}
    except json.JSONDecodeError:
        return {}


def _load_defense_map() -> dict:
    path = OUTPUT_DIR / "defense_map.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text()).get("defense_mappings", {})
    except json.JSONDecodeError:
        return {}


def _load_defense_rejected() -> set[str]:
    """Load finding IDs hard-tagged already_guarded by defense_mapper at Step 1.5."""
    path = OUTPUT_DIR / "defense_rejected.jsonl"
    if not path.exists():
        return set()
    ids: set[str] = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                ids.add(json.loads(line).get("finding_id", ""))
            except json.JSONDecodeError:
                pass
    return ids


def _load_exploit_models() -> dict:
    path = EXPLOIT_DIR / "models.jsonl"
    if not path.exists():
        return {}
    models: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            models[rec["finding_id"]] = rec
        except (json.JSONDecodeError, KeyError):
            continue
    return models


def _load_gate_results() -> dict:
    path = TRIAGE_DIR / "gate_results.jsonl"
    if not path.exists():
        return {}
    gate_map: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            gate_map[rec["finding_id"]] = rec
        except (json.JSONDecodeError, KeyError):
            continue
    return gate_map


def _load_fp_pattern_results() -> dict:
    path = FP_DIR / "pattern_check_results.jsonl"
    if not path.exists():
        return {}
    fp_map: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            fp_map[rec["finding_id"]] = rec
        except (json.JSONDecodeError, KeyError):
            continue
    return fp_map


def apply_admin_pre_score(finding: dict, triage_obj: dict) -> None:
    flagged, _ = pre_check_admin_attacker(finding)
    if not flagged:
        return
    score = triage_obj.get("score")
    if not isinstance(score, dict):
        return
    score["attacker_control"] = min(score.get("attacker_control", 5), 1)
    score["scope_safety"] = min(score.get("scope_safety", 5), 2)
    dims = ["attacker_control", "sensitive_sink", "missing_check_clarity",
            "impact_realism", "poc_feasibility", "scope_safety", "duplicate_risk"]
    score["total"] = sum(score.get(d, 0) for d in dims)


# ─────────────────────────────────────────────────────────────────────────────
# Compound bonus
# ─────────────────────────────────────────────────────────────────────────────

def apply_compound_bonus(triage_results: list[dict], compound_notes: list[str]) -> None:
    if not compound_notes:
        return
    submit_ids = {t["finding_id"] for t in triage_results
                  if t.get("triage_status") in ("submit", "poc_required")}
    id_pattern = re.compile(r'\b([A-Z]{2,3}-\d{3})\b')
    for note in compound_notes:
        ids_in_note = id_pattern.findall(note)
        if len(ids_in_note) >= 2 and all(fid in submit_ids for fid in ids_in_note):
            for t in triage_results:
                if t["finding_id"] in ids_in_note:
                    t["score"]["total"] += 3
                    t["_compound_bonus"] = True


# ─────────────────────────────────────────────────────────────────────────────
# Tool-use setup (retriever access during triage)
# ─────────────────────────────────────────────────────────────────────────────

RETRIEVER_TOOLS = [
    {
        "name": "search_kb",
        "description": (
            "Search the Solodit/Code4rena/Sherlock knowledge base for audit findings "
            "similar to the vulnerability being triaged."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vuln_type": {
                    "type": "string",
                    "enum": [
                        "reentrancy", "access-control", "arithmetic",
                        "oracle-manipulation", "flash-loan", "logic-error",
                        "dos", "other",
                    ],
                },
                "query": {"type": "string"},
            },
            "required": ["vuln_type", "query"],
        },
    },
    {
        "name": "search_immunefi",
        "description": (
            "Search the Immunefi bug-bounty report database for precedents matching "
            "the vulnerability pattern being triaged."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vuln_type": {"type": "string"},
                "query": {"type": "string"},
            },
            "required": ["vuln_type", "query"],
        },
    },
]

_TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"


def _execute_triage_tool(tool_name: str, tool_input: dict) -> str:
    import subprocess
    if tool_name == "search_kb":
        cmd = [
            sys.executable,
            str(_TOOLS_DIR / "retriever.py"),
            tool_input.get("vuln_type", "other"),
            tool_input.get("query", ""),
        ]
    else:  # search_immunefi
        cmd = [
            sys.executable,
            str(_TOOLS_DIR / "immunefi_retriever.py"),
            tool_input.get("vuln_type", "other"),
            tool_input.get("query", ""),
        ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else "[]"
    except Exception as e:
        return f"[]  # tool error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Claude API call
# ─────────────────────────────────────────────────────────────────────────────

def build_user_message(batch: list[dict], compound_notes: list[str]) -> str:
    parts = ["Triage the following findings. Return a JSON array — one object per finding.\n"]
    for finding in batch:
        parts.append(f"--- FINDING {finding.get('id', '?')} ---")
        parts.append(json.dumps(finding, indent=2))
    if compound_notes:
        parts.append("\n--- COMPOUND RISK NOTES ---")
        for note in compound_notes:
            parts.append(f"• {note}")
    return "\n".join(parts)


# Maps Claude's natural decision language → canonical triage_status values
_DECISION_MAP = {
    "submit":           "submit",
    "submit now":       "submit",
    "ready to submit":  "submit",
    "poc required":     "poc_required",
    "poc_required":     "poc_required",
    "needs poc":        "poc_required",
    "proof of concept": "poc_required",
    "downgrade":        "downgrade",
    "downgraded":       "downgrade",
    "merge":            "merge",
    "duplicate":        "merge",
    "reject":           "reject",
    "rejected":         "reject",
    "invalid":          "reject",
    "qa":               "reject",
}

_SEVERITY_MAP = {
    "critical": "critical", "high": "high", "medium": "medium",
    "low": "low", "qa": "qa", "invalid": "invalid",
    "informational": "low", "info": "low",
}


def normalize_claude_item(raw_item: dict, finding_id: str) -> dict:
    """
    Map Claude's natural-language JSON output to our canonical triage schema.

    Claude reliably returns reasoning and scores but uses different field names
    each run (id vs finding_id, decision vs triage_status, scores vs score, etc.).
    This normaliser makes the pipeline robust to those variations.
    """
    # ── finding_id ────────────────────────────────────────────────────────────
    fid = (raw_item.get("finding_id") or raw_item.get("id") or finding_id)

    # ── triage_status ─────────────────────────────────────────────────────────
    raw_decision = (raw_item.get("triage_status") or raw_item.get("decision") or "").lower().strip()
    status = _DECISION_MAP.get(raw_decision, "poc_required")

    # ── recommended_severity ──────────────────────────────────────────────────
    raw_sev = (raw_item.get("recommended_severity") or raw_item.get("severity")
               or raw_item.get("final_severity") or "low").lower().strip()
    severity = _SEVERITY_MAP.get(raw_sev, "low")

    # ── score block ───────────────────────────────────────────────────────────
    dims = ["attacker_control", "sensitive_sink", "missing_check_clarity",
            "impact_realism", "poc_feasibility", "scope_safety", "duplicate_risk"]

    raw_scores = raw_item.get("score") or raw_item.get("scores") or {}
    if not isinstance(raw_scores, dict):
        raw_scores = {}
    score_dict = {d: int(raw_scores.get(d, 3)) for d in dims}
    # Accept total from Claude or recompute
    raw_total = raw_item.get("total_score") or (raw_scores.get("total") if isinstance(raw_scores, dict) else None)
    score_dict["total"] = int(raw_total) if raw_total is not None else sum(score_dict[d] for d in dims)

    # ── confidence ────────────────────────────────────────────────────────────
    confidence = int(raw_item.get("confidence", 3))

    # ── attacker_model ────────────────────────────────────────────────────────
    am_raw = raw_item.get("attacker_model") or {}
    attacker_model = {
        "attacker_type": am_raw.get("attacker_type", "unknown"),
        "required_permissions":   am_raw.get("required_permissions", []),
        "required_preconditions": am_raw.get("required_preconditions", []),
        "realistic": bool(am_raw.get("realistic", False)),
    }

    # ── exploitability ────────────────────────────────────────────────────────
    ex_raw = raw_item.get("exploitability") or {}
    hard_reject = raw_item.get("hard_rejection_triggered", False)
    exploitability = {
        "can_trigger":          bool(ex_raw.get("can_trigger", not hard_reject)),
        "profit_or_damage":     ex_raw.get("profit_or_damage", ""),
        "blocked_by_auth":      bool(ex_raw.get("blocked_by_auth", hard_reject)),
        "blocked_by_atomicity": bool(ex_raw.get("blocked_by_atomicity", False)),
        "blocked_by_scope":     bool(ex_raw.get("blocked_by_scope", False)),
        "needs_poc":            bool(ex_raw.get("needs_poc", status == "poc_required")),
    }

    # ── impact ────────────────────────────────────────────────────────────────
    imp_raw = raw_item.get("impact") or {}
    impact = {
        "asset_at_risk":   imp_raw.get("asset_at_risk", "unknown"),
        "victim":          imp_raw.get("victim", "unknown"),
        "loss_type":       imp_raw.get("loss_type", "none"),
        "severity_reason": (imp_raw.get("severity_reason")
                            or str(raw_item.get("rationale") or "")[:300]),
    }

    # ── quality_gate ──────────────────────────────────────────────────────────
    qg_raw = raw_item.get("quality_gate") or {}
    quality_gate = {
        "has_exact_location": bool(qg_raw.get("has_exact_location", False)),
        "has_root_cause":     bool(qg_raw.get("has_root_cause", False)),
        "has_exploit_steps":  bool(qg_raw.get("has_exploit_steps", False)),
        "has_patch":          bool(qg_raw.get("has_patch", False)),
        "likely_duplicate":   bool(qg_raw.get("likely_duplicate", False)),
        "speculative_language": qg_raw.get("speculative_language", []),
    }

    # ── decision_reason ───────────────────────────────────────────────────────
    decision_reason = (raw_item.get("decision_reason")
                       or raw_item.get("rationale")
                       or raw_item.get("reason", ""))

    return {
        "finding_id":          fid,
        "title":               raw_item.get("title", ""),
        "triage_status":       status,
        "recommended_severity": severity,
        "score":               score_dict,
        "confidence":          confidence,
        "attacker_model":      attacker_model,
        "exploitability":      exploitability,
        "impact":              impact,
        "quality_gate":        quality_gate,
        "decision_reason":     decision_reason,
        "required_next_steps": raw_item.get("required_next_steps", []),
    }


def call_triager(client: anthropic.Anthropic, system_prompt: str,
                 batch: list[dict], compound_notes: list[str]) -> list[dict]:
    user_msg = build_user_message(batch, compound_notes)
    messages: list[dict] = [{"role": "user", "content": user_msg}]
    import time as _time
    raw = ""
    for _ in range(5):  # max 5 tool-use rounds
        for _retry in range(4):  # retry up to 4× on rate limit
            try:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=8192,
                    system=system_prompt,
                    tools=RETRIEVER_TOOLS,
                    messages=messages,
                )
                break
            except anthropic.RateLimitError:
                wait = 60 * (_retry + 1)
                print(f"  [rate-limit] waiting {wait}s before retry...")
                _time.sleep(wait)
        else:
            raise RuntimeError("Rate limit retry exhausted")
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    raw = block.text.strip()
                    break
            break
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    kb_result = _execute_triage_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": kb_result,
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            continue
        # Unexpected stop reason — take whatever text we have
        for block in response.content:
            if hasattr(block, "text"):
                raw = block.text.strip()
                break
        break

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            # Unwrap common envelope keys Claude uses when returning arrays
            for key in ("results", "findings", "triaged_findings", "triage",
                        "output", "triage_results", "items"):
                if key in parsed and isinstance(parsed[key], list):
                    parsed = parsed[key]
                    break
            else:
                parsed = [parsed]

        # Build a lookup from batch IDs so we can match Claude's results
        # even if it returns them in a different order or with different ID fields
        batch_id_map = {f.get("id"): f for f in batch}

        normalised = []
        for item in parsed:
            raw_id = item.get("finding_id") or item.get("id") or ""
            # Exact match first; fall back to case-insensitive
            matched_id = (raw_id if raw_id in batch_id_map
                          else next((k for k in batch_id_map if k.upper() == raw_id.upper()), raw_id))
            normalised.append(normalize_claude_item(item, matched_id))
        return normalised

    except json.JSONDecodeError as e:
        # Safe default: move all findings in batch to poc_required
        print(f"  [warn] JSON parse error from Claude: {e}")
        safe = []
        for finding in batch:
            fid = finding.get("id", "unknown")
            print(f"  [warn] Moving {fid} to poc_required (parse error safe default)")
            safe.append(_fallback_triage(finding))
        return safe


def _fallback_triage(finding: dict) -> dict:
    return {
        "finding_id": finding.get("id", "unknown"),
        "title": finding.get("title", ""),
        "triage_status": "poc_required",
        "recommended_severity": finding.get("severity", "medium").lower(),
        "score": {
            "attacker_control": 3, "sensitive_sink": 3,
            "missing_check_clarity": 3, "impact_realism": 3,
            "poc_feasibility": 3, "scope_safety": 3, "duplicate_risk": 3,
            "total": 21,
        },
        "confidence": 2,
        "attacker_model": {
            "attacker_type": "unknown",
            "required_permissions": [],
            "required_preconditions": [],
            "realistic": False,
        },
        "exploitability": {
            "can_trigger": False, "profit_or_damage": "unknown",
            "blocked_by_auth": False, "blocked_by_atomicity": False,
            "blocked_by_scope": False, "needs_poc": True,
        },
        "impact": {
            "asset_at_risk": "unknown", "victim": "unknown",
            "loss_type": "none", "severity_reason": "parse error — manual review required",
        },
        "quality_gate": {
            "has_exact_location": False, "has_root_cause": False,
            "has_exploit_steps": False, "has_patch": False,
            "likely_duplicate": False, "speculative_language": [],
        },
        "decision_reason": "Claude returned malformed JSON; moved to poc_required for manual review",
        "required_next_steps": ["Manual review required — automatic triage failed"],
        "_parse_error": True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Routing
# ─────────────────────────────────────────────────────────────────────────────

def route(triage: dict) -> str:
    status = triage.get("triage_status", "reject")
    # Normalise merge → merged for filename consistency
    if status == "merge":
        return "merged"
    return status


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def _write_per_finding_mds(buckets: dict, triage_dir: Path) -> None:
    """Write data/triage/<finding_id>.md for each finding (CONFIRMED or downgraded).

    This is formatting-only work — no re-analysis. Fields are populated from the
    existing triage payload already computed by this pipeline.
    """
    VERDICT_MAP = {
        "submit":       "CONFIRMED — all claims verified end-to-end",
        "poc_required": "CONFIRMED (PoC required to finalize severity)",
        "downgraded":   "DOWNGRADED — prior score too high",
        "merged":       "MERGED — duplicate of another finding",
        "rejected":     "INVALID — claim does not hold",
    }

    for bucket, items in buckets.items():
        verdict = VERDICT_MAP.get(bucket, bucket.upper())
        for item in items:
            fid    = item.get("finding_id") or item.get("id", "UNKNOWN")
            title  = item.get("title", fid)
            sev    = item.get("recommended_severity") or item.get("severity", "?")
            conf   = item.get("recommended_confidence") or item.get("confidence", "?")
            expl   = item.get("recommended_exploitability") or item.get("exploitability", "?")
            prior_sev  = item.get("claimed_severity") or item.get("severity", "?")
            prior_conf = item.get("confidence", "?")
            prior_expl = item.get("exploitability", "?")

            root_cause   = item.get("root_cause")    or item.get("description", "")
            entry_point  = item.get("entry_point")   or item.get("function", "")
            attack_steps = item.get("attack_vector") or item.get("attack_steps") or []
            guards_raw   = item.get("guards_evaluated") or []
            notes        = item.get("decision_reason") or item.get("triage_notes", "")
            before_state = item.get("state_before", "")
            after_state  = item.get("state_after", "")

            # Normalise attack_steps to list of strings
            if isinstance(attack_steps, str):
                import re as _re
                attack_steps = _re.split(r"\n\d+\.\s+|\n- ", attack_steps.strip())

            # Guards table rows
            guard_rows: list[str] = []
            for g in guards_raw:
                if isinstance(g, dict):
                    guard_rows.append(
                        f"| {g.get('name','?')} | {g.get('location','?')} | {g.get('why_fails','?')} |"
                    )
                elif isinstance(g, str):
                    guard_rows.append(f"| {g} | — | — |")

            attack_seq = "\n".join(
                f"{i+1}. {step}" for i, step in enumerate(attack_steps) if step
            )

            reason_change = ""
            if sev != prior_sev or conf != prior_conf:
                reason_change = "score changed during triage validation"

            lines = [
                f"# {fid} — {title}",
                "",
                "## Re-Derived Root Cause",
                root_cause or "*(not available — check merged_findings.json)*",
                "",
                "## External Entry Point",
                f"`{entry_point}`" if entry_point else "INVALID — NO EXTERNAL ENTRY",
                "",
                "## Attack Sequence",
                attack_seq or "*(not available)*",
                "",
                "## Defenses Evaluated",
                "| Guard | Location | Why It Fails |",
                "|---|---|---|",
            ]
            lines += guard_rows or ["| *(none documented)* | — | — |"]
            lines += [
                "",
                "## State Before / After Attack",
                f"**Before:** {before_state}" if before_state else "**Before:** *(not documented)*",
                f"**After:** {after_state}"  if after_state  else "**After:** *(not documented)*",
                "",
                "## ICE Re-Score",
                "| Axis | Prior | Validated | Reason for Change |",
                "|---|---|---|---|",
                f"| I | {prior_sev} | {sev} | {reason_change or '—'} |",
                f"| C | {prior_conf} | {conf} | — |",
                f"| E | {prior_expl} | {expl} | — |",
                "",
                "## Validation Verdict",
                f"[x] {verdict}",
                "",
                "## Triage Notes",
                notes or "*(none)*",
            ]

            md_path = triage_dir / f"{fid}.md"
            md_path.write_text("\n".join(lines))


def main():
    TRIAGE_DIR.mkdir(parents=True, exist_ok=True)

    from audit_context import get_audit_meta
    meta = get_audit_meta()
    _audit_id = meta.get("audit_id", "")
    print(f"Active audit: {meta.get('name','?')} ({_audit_id})")
    print("Smart Contract Auditor — Triage Agent\n")

    # ── Hermes routing consult ────────────────────────────────────────────────
    try:
        from scripts.hermes_bridge import get_routing_recommendation
        _hrec = get_routing_recommendation("pre_triage", {
            "audit_id": _audit_id,
            "budget_mode": meta.get("budget_mode", "normal"),
        })
        if _hrec["confidence"] > 0.5:
            print(f"[HERMES] Routing: {_hrec['recommendation']}")
            if _hrec.get("escalate_to_human"):
                print(f"[HERMES] ⚠ Human escalation: {_hrec['escalation_reason']}")
    except Exception:
        pass

    # Load inputs
    findings = load_all_findings()
    print(f"  Loaded {len(findings)} findings from output/findings_*.json")

    compound_notes = load_compound_risk_notes()
    if compound_notes:
        print(f"  Loaded {len(compound_notes)} compound risk notes")

    system_prompt = load_system_prompt()

    # Load pipeline artifacts for pre-checks (non-fatal on missing files)
    defense_map      = _load_defense_map()
    defense_rejected = _load_defense_rejected()
    exploit_models   = _load_exploit_models()
    gate_map         = _load_gate_results()
    fp_map           = _load_fp_pattern_results()
    ice_findings     = _load_ice_findings()

    if defense_map:
        print(f"  Defense map loaded: {len(defense_map)} entries")
    if defense_rejected:
        print(f"  Defense-rejected (Step 1.5): {len(defense_rejected)} already_guarded")
    if gate_map:
        print(f"  Gate results loaded: {len(gate_map)} entries")
    if fp_map:
        print(f"  FP pattern results loaded: {len(fp_map)} entries")
    if ice_findings:
        print(f"  ICE findings loaded: {len(ice_findings)} entries")

    # ── Local pre-screening ──────────────────────────────────────────────────
    to_api: list[dict] = []
    hard_rejects: list[dict] = []
    poc_holds: list[dict] = []    # ice.hold=true → poc_required (not rejected)
    pre_flags: dict[str, list[str]] = {}  # finding id → list of flag notes

    for finding in findings:
        fid = finding.get("id", "?")
        flags = []

        # ── Defense mapper Step 1.5 hard reject (already_guarded, no evasion) ──
        if fid in defense_rejected:
            print(f"  [defense-step1.5] {fid}: already_guarded (tagged by defense_mapper)")
            hard_reject_rec = _make_hard_reject(
                finding, ["already_guarded"],
                ["full defense coverage, no evasion path — tagged at Step 1.5"],
                reason_prefix="[defense-coverage]",
            )
            hard_rejects.append(hard_reject_rec)
            continue

        # ── Gate-based hard reject (Step 3.7 output) ──────────────────────
        gate = gate_map.get(fid, {})
        if gate.get("overall_verdict") == "REJECT":
            tags = gate.get("invalidation_tags", [])
            issues = gate.get("blocking_issues", [])
            print(f"  [gate-reject] {fid}: tags={tags}")
            hard_reject_rec = _make_hard_reject(finding, tags, issues, reason_prefix="[pre-submission-gate]")
            hard_rejects.append(hard_reject_rec)
            continue
        elif gate.get("overall_verdict") == "HUMAN_REVIEW":
            finding["_human_review_forced"] = True
            for issue in gate.get("blocking_issues", [])[:2]:
                flags.append(f"[gate-warn] {issue}")

        # ── FP pattern hard reject ─────────────────────────────────────────
        fp_result = fp_map.get(fid, {})
        if fp_result.get("recommended_action") == "reject":
            top_rule = (fp_result.get("matching_rules") or [{}])[0]
            reason = top_rule.get("rejection_reason", "matches known FP pattern")[:80]
            print(f"  [fp-pattern-reject] {fid}: {reason}")
            hard_reject_rec = _make_hard_reject(
                finding, ["duplicate_pattern"], [reason], reason_prefix="[fp-pattern]"
            )
            hard_rejects.append(hard_reject_rec)
            continue

        # ── Defense coverage hard reject ───────────────────────────────────
        def_flag, def_reason = pre_check_defense_coverage(finding, defense_map)
        if def_flag:
            print(f"  [defense-reject] {fid}: {def_reason}")
            hard_reject_rec = _make_hard_reject(
                finding, ["already_guarded"], [def_reason], reason_prefix="[defense-coverage]"
            )
            hard_rejects.append(hard_reject_rec)
            continue

        # ── Economics hard reject ──────────────────────────────────────────
        econ_flag, econ_reason = pre_check_economics(finding, exploit_models)
        if econ_flag:
            print(f"  [economics-reject] {fid}: {econ_reason}")
            hard_reject_rec = _make_hard_reject(
                finding, ["no_profitability"], [econ_reason], reason_prefix="[economics]"
            )
            hard_rejects.append(hard_reject_rec)
            continue

        # ── ice_chain.consumer_found=false → poc_required ─────────────────
        # If an agent explicitly answered the ICE question and found no consumer,
        # route to poc_required before the API call. Agents that don't set ice_chain
        # are not penalised — this only fires when the field is present and false.
        ice_chain = finding.get("ice_chain") or {}
        if ice_chain and ice_chain.get("consumer_found") is False:
            corrupted = ice_chain.get("corrupted_state", "unknown state")
            print(f"  [ice-chain] {fid}: no consumer found for '{corrupted}' → poc_required")
            poc_hold_rec = _fallback_triage(finding)
            poc_hold_rec["triage_status"] = "poc_required"
            poc_hold_rec["decision_reason"] = (
                f"ice_chain.consumer_found=false: no trusted consumer identified "
                f"for corrupted state '{corrupted}'. Trace consumer chain before triage."
            )
            poc_hold_rec["required_next_steps"] = [
                f"Identify which protocol function reads '{corrupted}'",
                "Spawn agents/impact_chain_escalation.md to trace the consumer chain",
                "Set ice_chain.consumer_found=true with consumer_function before re-triaging",
            ]
            poc_holds.append(poc_hold_rec)
            continue

        # ── ICE hold → poc_required (NOT rejected) ────────────────────────
        ice_hold, ice_reason = pre_check_ice_hold(finding, ice_findings)
        if ice_hold:
            print(f"  [ice-hold] {fid}: {ice_reason}")
            poc_hold_rec = _fallback_triage(finding)
            poc_hold_rec["triage_status"] = "poc_required"
            poc_hold_rec["decision_reason"] = ice_reason
            poc_hold_rec["required_next_steps"] = [
                ice_reason,
                "Spawn agents/impact_chain_escalation.md to trace consumer chain",
                "Set ice.manual_override.enabled=true after manual confirmation",
            ]
            poc_holds.append(poc_hold_rec)
            continue

        spec_flag, spec_reason = pre_check_speculative(finding)
        if spec_flag:
            flags.append(spec_reason)

        conf_flag, conf_reason = pre_check_confidence(finding)
        if conf_flag:
            flags.append(conf_reason)

        allowance_note = allowance_check_note(finding)
        if allowance_note:
            flags.append(f"[human-review] {allowance_note}")

        if cpu_dos_needs_poc(finding):
            flags.append("[dos-check] High DoS claim missing operation count estimate")
            finding["_needs_poc_forced"] = True

        admin_flag, admin_reason = pre_check_admin_attacker(finding)
        if admin_flag:
            flags.append(admin_reason)
            finding["_admin_pre_score"] = True

        if flags:
            pre_flags[fid] = flags
            print(f"  [pre-flag] {fid}: {'; '.join(flags)}")

        to_api.append(finding)

    if hard_rejects:
        print(f"  Hard-rejected {len(hard_rejects)} findings (gates/defense/economics/FP-pattern) — skipping API")
    if poc_holds:
        print(f"  ICE-held {len(poc_holds)} findings (no consumer found, high-risk vuln) → poc_required")

    print(f"\n  Sending {len(to_api)} findings to Claude in batches of {BATCH_SIZE}...")

    # ── API calls ────────────────────────────────────────────────────────────
    # Graceful no-key failure → points to the /triage skill (credit-free path).
    from llm_runtime import require_llm
    client = require_llm(skill="triage", bundle_hint="data/triage/_bundles/")
    all_triage: list[dict] = []

    for i in range(0, len(to_api), BATCH_SIZE):
        if i > 0:
            import time; time.sleep(35)  # rate-limit guard: 30K tokens/min tier
        batch = to_api[i : i + BATCH_SIZE]
        ids = [f.get("id", "?") for f in batch]
        print(f"  Batch {i // BATCH_SIZE + 1}: {ids}")
        results = call_triager(client, system_prompt, batch, compound_notes)
        # Ensure we got one result per finding in batch
        result_ids = {r.get("finding_id") for r in results}
        for finding in batch:
            fid = finding.get("id")
            if fid not in result_ids:
                print(f"  [warn] No triage result for {fid} — using fallback")
                results.append(_fallback_triage(finding))
        all_triage.extend(results)

    # Merge ICE-held findings into all_triage (already set to poc_required)
    all_triage.extend(poc_holds)

    # ── Post-processing ──────────────────────────────────────────────────────
    # Apply admin pre-score adjustments
    for triage in all_triage:
        fid = triage.get("finding_id")
        source_finding = next((f for f in findings if f.get("id") == fid), None)
        if source_finding and source_finding.get("_admin_pre_score"):
            apply_admin_pre_score(source_finding, triage)

    # Apply needs_poc from dos pre-check
    for triage in all_triage:
        fid = triage.get("finding_id")
        source_finding = next((f for f in findings if f.get("id") == fid), None)
        if source_finding and source_finding.get("_needs_poc_forced"):
            triage["exploitability"]["needs_poc"] = True

    # Attach pre-flag notes to required_next_steps
    for triage in all_triage:
        fid = triage.get("finding_id")
        if fid in pre_flags:
            existing = triage.get("required_next_steps", [])
            triage["required_next_steps"] = existing + pre_flags[fid]

    # Apply compound bonus
    apply_compound_bonus(all_triage, compound_notes)

    # Re-route after score adjustments (apply thresholds again)
    for triage in all_triage:
        score = triage.get("score", {}).get("total", 0)
        needs_poc = triage.get("exploitability", {}).get("needs_poc", False)
        status = triage.get("triage_status", "reject")

        # Only override if pre-scores changed the outcome
        if status not in ("merge",):
            if score < 16:
                triage["triage_status"] = "reject"
            elif 16 <= score <= 21:
                if status not in ("reject",):
                    triage["triage_status"] = "downgrade"
            elif score >= 22:
                if needs_poc and status not in ("reject", "downgrade"):
                    triage["triage_status"] = "poc_required"
                elif not needs_poc and score >= 28 and status not in ("reject", "downgrade", "poc_required"):
                    triage["triage_status"] = "submit"

    # ── Write output files ───────────────────────────────────────────────────
    buckets: dict[str, list[dict]] = {
        "submit": [], "poc_required": [], "downgraded": [], "merged": [], "rejected": []
    }

    # Hard-rejected findings go directly to rejected bucket (no score adjustment needed)
    for hr in hard_rejects:
        buckets["rejected"].append(hr)

    for triage in all_triage:
        bucket = route(triage)
        if bucket not in buckets:
            bucket = "rejected"
        buckets[bucket].append(triage)

    for bucket, items in buckets.items():
        out_path = TRIAGE_DIR / f"{bucket}.jsonl"
        with out_path.open("w") as fh:
            for item in items:
                fh.write(json.dumps(item) + "\n")

    # ── per-finding markdown (human-readable companion to JSONL) ─────────────
    _write_per_finding_mds(buckets, TRIAGE_DIR)

    # ── viz: emit triage decisions ───────────────────────────────────────────
    try:
        from viz.event_emitter import emit as _viz_emit
        for _item in buckets.get("submit", []) + buckets.get("poc_required", []):
            _fid = _item.get("finding_id", "")
            _score = _item.get("score", {})
            _total = _score.get("total", _score) if isinstance(_score, dict) else _score
            _viz_emit("TRIAGER_DECISION", source_agent="triage", target_node_id=_fid, payload={
                "decision": _item.get("triage_status", "submit"),
                "recommended_severity": _item.get("recommended_severity", ""),
                "score": _total,
            })
        for _item in buckets.get("rejected", []):
            _fid = _item.get("finding_id", "")
            _reason = _item.get("required_next_steps", [""])[0] if _item.get("required_next_steps") else _item.get("triage_status", "rejected")
            _score = _item.get("score", {})
            _total = _score.get("total", _score) if isinstance(_score, dict) else _score
            _viz_emit("BRANCH_INVALIDATED", source_agent="triage", target_node_id=_fid, payload={
                "reason": _reason, "score": _total,
            })
    except Exception:
        pass

    # ── Hermes: emit triage decisions ────────────────────────────────────────
    try:
        from scripts.emit_hermes_event import emit_hermes as _h_emit
        for _bucket in ("submit", "poc_required", "downgraded", "rejected"):
            for _item in buckets.get(_bucket, []):
                _fid = _item.get("finding_id", "")
                _score = _item.get("score", {})
                _total = _score.get("total", _score) if isinstance(_score, dict) else _score
                _h_emit("triage_decision", {
                    "finding_id": _fid,
                    "decision": _bucket,
                    "score": _total,
                    "recommended_severity": _item.get("recommended_severity", ""),
                    "rejection_reason": _item.get("decision_reason", ""),
                    "invalidation_tags": _item.get("invalidation_tags", []),
                    "audit_id": _audit_id,
                })
    except Exception:
        pass

    # ── Summary table ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"{'Bucket':<20} {'Count':>5}")
    print("-" * 60)
    total = 0
    for bucket in ["submit", "poc_required", "downgraded", "merged", "rejected"]:
        n = len(buckets[bucket])
        total += n
        print(f"  {bucket:<18} {n:>5}")
    print(f"  {'TOTAL':<18} {total:>5}")
    print("=" * 60)

    top5 = sorted(buckets["submit"], key=lambda t: t.get("score", {}).get("total", 0), reverse=True)[:5]
    if top5:
        print("\nTop 5 submit findings by score:")
        for t in top5:
            print(f"  {t.get('finding_id','?'):10}  score={t['score']['total']:2}  "
                  f"sev={t.get('recommended_severity','?'):8}  {t.get('title','')[:55]}")

    print(f"\nOutputs written to {TRIAGE_DIR}/")
    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
