#!/usr/bin/env python3
"""
cross_agent_connector.py — Holistic cross-agent compound finding synthesis.

Reads ALL specialist agent findings simultaneously and makes a single LLM call
that sees the complete picture, identifying exploit paths that emerge only when
multiple findings are combined — paths invisible to pairwise pattern matching.

Output behavior (user-confirmed):
  - If a combination escalates severity → write new CC_CA-NNN finding to
    output/findings_cross_agent.json
  - If no severity escalation → annotate existing finding JSON files with
    compound_with + cross_agent_note fields

This runs as Step 2.5 between specialist agents (Step 2) and compound synthesis
(Step 3). findings_cross_agent.json is automatically included in the Step 3
synthesize_compound_findings.py glob pass.

Usage:
    python scripts/cross_agent_connector.py
    python scripts/cross_agent_connector.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Load .env
if Path(".env").exists():
    for _line in Path(".env").read_text().splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import optional_llm  # graceful no-key skip (this is an optional enhancer stage)

ROOT = Path(__file__).resolve().parent.parent
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192

OUTPUT_DIR = audit_path("output")
OUT_FILE = OUTPUT_DIR / "findings_cross_agent.json"

SEVERITY_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Informational": 0}

# ─────────────────────────────────────────────────────────────────────────────
# Tool-use setup (retriever access for compound evidence)
# ─────────────────────────────────────────────────────────────────────────────

RETRIEVER_TOOLS = [
    {
        "name": "search_kb",
        "description": (
            "Search the Solodit/Code4rena/Sherlock knowledge base for audit findings "
            "similar to a compound vulnerability pattern."
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
            "a compound vulnerability pattern."
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


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    tools_dir = ROOT / "tools"
    if tool_name == "search_kb":
        cmd = [
            sys.executable,
            str(tools_dir / "retriever.py"),
            tool_input.get("vuln_type", "other"),
            tool_input.get("query", ""),
        ]
    else:  # search_immunefi
        cmd = [
            sys.executable,
            str(tools_dir / "immunefi_retriever.py"),
            tool_input.get("vuln_type", "other"),
            tool_input.get("query", ""),
        ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else "[]"
    except Exception as e:
        return f"[]  # tool error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def _load_all_findings() -> list[dict]:
    findings: list[dict] = []
    seen_ids: set[str] = set()
    for path in sorted(OUTPUT_DIR.glob("findings_*.json")):
        if path.name in ("findings_cross_agent.json", "findings_confirmed.json"):
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"  [warn] Cannot parse {path.name}: {e}")
            continue
        agent = data.get("agent", "unknown")
        if agent == "protocol_context":
            continue
        for f in data.get("findings", []):
            fid = f.get("id", "")
            if fid and fid in seen_ids:
                continue
            findings.append(f)
            if fid:
                seen_ids.add(fid)
    return findings


def _load_promising_threads() -> list[dict]:
    threads_path = audit_path("data/threads") / "promising_threads.jsonl"
    if not threads_path.exists():
        return []
    threads = []
    for line in threads_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            t = json.loads(line)
            if t.get("verdict") != "DEAD_END":
                threads.append(t)
        except json.JSONDecodeError:
            continue
    return threads


def _load_attack_surface() -> list[dict]:
    path = OUTPUT_DIR / "attack_surface.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        fns = data.get("functions", [])
        # Return top-5 by attack_surface_score
        return sorted(fns, key=lambda x: x.get("attack_surface_score", 0), reverse=True)[:5]
    except Exception:
        return []


def _slim_finding(f: dict) -> dict:
    return {
        "id": f.get("id", ""),
        "title": f.get("title", ""),
        "severity": f.get("severity", ""),
        "vuln_type": f.get("vuln_type", ""),
        "agent": f.get("agent", ""),
        "description": (f.get("description", "") or "")[:400],
        "location": f.get("location", {}),
        "impact": (f.get("impact", "") or "")[:200],
        "cross_agent_refs": f.get("cross_agent_refs", []),
    }


# ─────────────────────────────────────────────────────────────────────────────
# LLM call with tool-use loop
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior smart contract security researcher performing holistic
cross-agent compound vulnerability analysis.

You have been given ALL findings from parallel specialist agents, promising deep-trace
threads, and the top attack-surface functions for a smart contract audit.

Your task: identify 2-5 finding combinations that together create an exploit path not
captured by any single finding. Focus on:

(a) Findings touching the same function from different vuln_type angles — one enables
    the precondition for another (e.g., missing access control makes a reentrant callback
    reachable by an attacker who otherwise couldn't call the function).

(b) Findings in contracts that call each other via a shared interface — a vulnerability
    in contract A exposes state that contract B's vulnerability can then exploit.

(c) Findings where a behavioral divergence (BSA agent) or invariant violation exposes
    a state path that a separate reentrancy or arithmetic finding can then exploit.

For each compound you identify:
1. List the component finding IDs
2. Describe the combined exploit path step by step
3. Assess whether the combined severity EXCEEDS max(component severities)
4. If yes, name the new severity and provide a one-sentence title
5. Use search_kb and search_immunefi to find precedents before finalizing

Return a JSON object (no markdown wrapper) with this exact structure:
{
  "compounds": [
    {
      "component_ids": ["RE-001", "AC-003"],
      "combined_path": "Step 1: attacker calls X...\nStep 2: ...",
      "severity_escalates": true,
      "new_severity": "Critical",
      "title": "Permissionless Reentrancy via Ownable Fallback",
      "description": "...",
      "rationale": "..."
    }
  ]
}

If no meaningful compound exists, return {"compounds": []}.
Do NOT invent compounds where components do not actually interact.
Only escalate severity if you can articulate the concrete combined exploit path."""


def _call_claude_holistic(
    findings: list[dict],
    threads: list[dict],
    hotspots: list[dict],
    client,
) -> list[dict]:
    payload = {
        "findings": [_slim_finding(f) for f in findings],
        "threads": [
            {
                "id": t.get("thread_id", t.get("id", "")),
                "category": t.get("category", ""),
                "summary": (t.get("summary", "") or "")[:300],
                "verdict": t.get("verdict", ""),
                "chain_id": t.get("chain_id", ""),
            }
            for t in threads[:10]
        ],
        "hotspots": hotspots,
    }

    user_msg = (
        "Analyze the following audit data for compound exploit paths.\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```\n\n"
        "Before finalizing each compound, use search_kb and search_immunefi to verify "
        "precedents exist for the combined pattern. Return only valid JSON."
    )

    messages: list[dict] = [{"role": "user", "content": user_msg}]

    for round_num in range(6):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=RETRIEVER_TOOLS,
            messages=messages,
        )

        if resp.stop_reason == "end_turn":
            text = ""
            for block in resp.content:
                if hasattr(block, "text"):
                    text = block.text
                    break
            # Extract JSON from response
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group())
                    return result.get("compounds", [])
                except json.JSONDecodeError:
                    pass
            return []

        if resp.stop_reason == "tool_use":
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    kb_result = _execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": kb_result,
                    })
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": tool_results})
            continue

        # Unexpected stop reason
        break

    return []


# ─────────────────────────────────────────────────────────────────────────────
# Output handling
# ─────────────────────────────────────────────────────────────────────────────

def _next_cc_ca_id(existing: list[dict]) -> str:
    used = set()
    for f in existing:
        fid = f.get("id", "")
        m = re.match(r"CC_CA-(\d+)", fid)
        if m:
            used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"CC_CA-{n:03d}"


def _max_severity(component_ids: list[str], findings_by_id: dict) -> str:
    max_rank = 0
    max_sev = "Low"
    for fid in component_ids:
        sev = findings_by_id.get(fid, {}).get("severity", "Low")
        if SEVERITY_RANK.get(sev, 0) > max_rank:
            max_rank = SEVERITY_RANK[sev]
            max_sev = sev
    return max_sev


def _build_new_finding(compound: dict, component_ids: list[str], next_id: str) -> dict:
    return {
        "id": next_id,
        "agent": "cross_agent",
        "title": compound.get("title", "Cross-Agent Compound Finding"),
        "severity": compound.get("new_severity", "High"),
        "vuln_type": "logic-error",
        "description": compound.get("description", compound.get("combined_path", "")),
        "impact": (
            f"Combined exploit path escalates severity to {compound.get('new_severity', 'High')}. "
            f"Component findings: {', '.join(component_ids)}."
        ),
        "proof_of_concept": compound.get("combined_path", ""),
        "recommendation": (
            "Address all component findings to eliminate the compound exploit path. "
            "See individual findings for specific remediations."
        ),
        "location": {"file": "", "function": ""},
        "confidence": "Medium",
        "cross_agent_refs": component_ids,
        "compound_with": component_ids,
        "cross_agent_note": compound.get("rationale", ""),
        "metadata": {
            "compound_pattern": "CC_CA",
            "component_ids": component_ids,
            "severity_escalated_from": compound.get("_max_component_severity", ""),
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def _annotate_existing(compound: dict, component_ids: list[str], findings_by_id: dict, dry_run: bool):
    """Add compound_with annotation to the source finding files."""
    for fid in component_ids:
        f = findings_by_id.get(fid)
        if not f:
            continue
        agent = f.get("agent", "")
        if not agent:
            continue
        findings_file = OUTPUT_DIR / f"findings_{agent}.json"
        if not findings_file.exists():
            continue
        try:
            data = json.loads(findings_file.read_text())
        except json.JSONDecodeError:
            continue

        others = [x for x in component_ids if x != fid]
        modified = False
        for entry in data.get("findings", []):
            if entry.get("id") == fid:
                existing = entry.get("compound_with", [])
                new_ids = [x for x in others if x not in existing]
                if new_ids:
                    entry["compound_with"] = existing + new_ids
                    entry["cross_agent_note"] = compound.get("rationale", "")
                    modified = True
                break

        if modified and not dry_run:
            findings_file.write_text(json.dumps(data, indent=2))
            print(f"  Annotated {findings_file.name} → {fid}.compound_with += {others}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Cross-agent holistic compound synthesis")
    parser.add_argument("--dry-run", action="store_true", help="Print results but do not write files")
    args = parser.parse_args()

    print("Cross-Agent Connector — holistic compound synthesis")
    print("=" * 60)

    # Enforce thread-finding join before loading findings so annotations are present
    print("  [pre-step] Thread-Finding Join …")
    _ann_script = ROOT / "scripts" / "annotate_findings_with_threads.py"
    if _ann_script.exists():
        _ann_flags = ["--dry-run"] if args.dry_run else []
        subprocess.run(
            [sys.executable, str(_ann_script)] + _ann_flags,
            cwd=ROOT, check=False,
        )
    else:
        print("  [warn] annotate_findings_with_threads.py not found — skipping join")

    findings = _load_all_findings()
    if not findings:
        print("No findings found — nothing to synthesize.")
        return

    threads = _load_promising_threads()
    hotspots = _load_attack_surface()

    print(f"  Loaded {len(findings)} findings, {len(threads)} threads, {len(hotspots)} hotspots")

    findings_by_id = {f.get("id", ""): f for f in findings if f.get("id")}

    client = optional_llm("cross_agent_connector")
    if client is None:
        # No API key: skip the holistic LLM pass and continue. Pairwise compound synthesis
        # (synthesize_compound_findings) and the deterministic merge still carry the run.
        compounds = []
        print("  Skipped holistic compound analysis (no API key) — continuing.")
    else:
        print("  Calling Claude for holistic compound analysis...")
        compounds = _call_claude_holistic(findings, threads, hotspots, client)
        print(f"  Claude returned {len(compounds)} compound(s)")

    # Load existing CC_CA findings (avoid ID collisions across runs)
    existing_ca: list[dict] = []
    if OUT_FILE.exists():
        try:
            existing_ca = json.loads(OUT_FILE.read_text()).get("findings", [])
        except json.JSONDecodeError:
            existing_ca = []

    new_findings: list[dict] = []

    for compound in compounds:
        component_ids = compound.get("component_ids", [])
        if len(component_ids) < 2:
            continue

        # Verify component IDs actually exist
        valid_ids = [fid for fid in component_ids if fid in findings_by_id]
        if len(valid_ids) < 2:
            print(f"  [skip] Compound references unknown IDs: {component_ids}")
            continue

        max_sev = _max_severity(valid_ids, findings_by_id)
        compound["_max_component_severity"] = max_sev
        new_sev = compound.get("new_severity", max_sev)

        escalates = (
            compound.get("severity_escalates", False)
            and SEVERITY_RANK.get(new_sev, 0) > SEVERITY_RANK.get(max_sev, 0)
        )

        if escalates:
            next_id = _next_cc_ca_id(existing_ca + new_findings)
            new_f = _build_new_finding(compound, valid_ids, next_id)
            new_findings.append(new_f)
            print(
                f"  [NEW] {next_id} — {new_f['title']} "
                f"({max_sev} → {new_sev}) "
                f"[{', '.join(valid_ids)}]"
            )
        else:
            print(
                f"  [ANN] No escalation — annotating components {valid_ids} "
                f"with cross_agent_note"
            )
            _annotate_existing(compound, valid_ids, findings_by_id, args.dry_run)

    new_findings_count = len(new_findings)
    annotation_count   = sum(1 for c in compounds if not (
        c.get("severity_escalates") and
        SEVERITY_RANK.get(c.get("new_severity", ""), 0) >
        SEVERITY_RANK.get(c.get("_max_component_severity", ""), 0)
    ))

    if new_findings:
        output = {
            "agent": "cross_agent",
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
            "findings": existing_ca + new_findings,
        }
        if args.dry_run:
            print("\n[dry-run] Would write to findings_cross_agent.json:")
            print(json.dumps(output, indent=2)[:2000])
        else:
            OUT_FILE.write_text(json.dumps(output, indent=2))
            print(f"\n  Written {len(new_findings)} new CC_CA finding(s) → {OUT_FILE.name}")
            try:
                from viz.event_emitter import emit as _viz_emit
                for _nf in new_findings:
                    _nf_id = _nf.get("id", "")
                    _viz_emit("HYPOTHESIS_BORN", source_agent="cross_agent_connector",
                              target_node_id=_nf_id, payload={
                                  "hypothesis_text": _nf.get("title", ""),
                                  "severity_ceiling": _nf.get("severity", ""),
                                  "exploit_class": "compound",
                                  "confidence": 0.7,
                                  "linked_contracts": _nf.get("compound_with", []),
                              })
                    for _comp_id in _nf.get("compound_with", []):
                        _viz_emit("EVIDENCE_ATTACHED", source_agent="cross_agent_connector",
                                  target_node_id=None, payload={
                                      "attached_to": _nf_id,
                                      "evidence_type": "component_finding",
                                      "content": f"Component finding {_comp_id}",
                                      "confidence_delta": 0.1,
                                  })
            except Exception:
                pass
    elif not args.dry_run and OUT_FILE.exists():
        print(f"\n  No new compound findings (existing file unchanged)")
    else:
        print("\n  No new compound findings.")

    # ── Post-run observability brief ──────────────────────────────────────────
    print("\n" + "─" * 60)
    print("Cross-Agent Connector — Run Summary")
    print("─" * 60)
    print(f"  Findings analysed:      {len(findings)}")
    print(f"  Compounds evaluated:    {len(compounds)}")
    print(f"  New CC_CA findings:     {new_findings_count}  (severity escalation confirmed)")
    print(f"  Annotation-only:        {annotation_count}  (compound noted, no escalation)")
    if new_findings_count == 0 and len(compounds) == 0:
        print("\n  NOTE: Claude returned 0 compound candidates.")
        print("  This may mean findings are independent, or the model needs more context.")
        print("  Check: are specialist agent outputs in output/findings_*.json?")
        print("  Check: does output/attack_surface.json exist?")

    # Write run log for dashboard visibility
    try:
        from audit_context import audit_path
        log_path = audit_path("output") / "cross_agent_run_log.json"
        log_entry = {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "findings_analysed": len(findings),
            "compounds_evaluated": len(compounds),
            "new_cc_ca_findings": new_findings_count,
            "annotation_only": annotation_count,
            "dry_run": args.dry_run,
        }
        log_path.write_text(json.dumps(log_entry, indent=2))
    except Exception:
        pass  # non-fatal

    print("Done.")


if __name__ == "__main__":
    main()
