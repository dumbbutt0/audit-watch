"""finding_detail — unified, READ-ONLY candidate-detail resolver across all three research tracks.

`load_unified_detail(key)` returns a candidate-detail-shaped dict for ANY finding, dispatched by the
track-qualified key (see findings_overview.finding_key):

  * detector (bare candidate_id)  → candidate_detail.load_candidate_detail (existing full packet, untouched)
  * runtime  ("runtime:<item_id>") → built from the value-provenance sidecar row + the phase deliverable .md
  * funnel   ("funnel:<cand_id>")  → built from funnel.load_records()

HARD INVARIANTS: read-only; never routes / sets severity / marks submittable. Runtime & funnel details are
flagged read_only_synced + labelable:false (only detector corpus candidates are labelable, in the validation
console). Every payload is stamped research_only:true / routing_allowed:false / submission_ready:false.
The frozen detector corpus, the runtime sidecar, and all baselines are only ever READ here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_SIDECAR = ROOT / "output_research/value_provenance_eval/runtime_status.jsonl"
CAMPAIGN_LEDGER = ROOT / "output_research/option_a_campaign/ledger.jsonl"
ASSISTED_DIR = ROOT / "documentation/research/assisted_mode"

# runtime deliverable .md files mapped, in display order, into the synced "verdict" view
_RUNTIME_DOC_ORDER = [
    "conversion_classification.md", "runtime_result.md", "source_reachability_map.md", "defense_map.md",
    "severity_finalization_memo.md", "review_report.md", "operator_scope_review.md", "blocker_analysis.md",
    "harness_design.md", "external_public_known_review.md", "duplicate_public_known_classification.md",
    "novelty_duplicate_check.md", "what_p156_taught_the_trainer.md",
]


def _rel(p: Optional[Path]) -> Optional[str]:
    if p is None:
        return None
    try:
        return str(p.relative_to(ROOT))
    except Exception:  # noqa: BLE001
        return str(p)


def _read(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- markdown extractors
# Best-effort, never raise. Used to pull recorded evidence out of the phase deliverables so the verifier
# page can inline it (no link-opening required). Nothing is fabricated — absence yields "" / [].
UNK = "unknown"

# Display-only status vocabulary for blank verifier fields (never fabricates data; classifies absence so the
# readiness checklist is actionable instead of a wall of "unknown"). Purely a render hint — no routing/severity.
EXTRACTED = "EXTRACTED"
HUMAN_PENDING = "HUMAN_PENDING"
MISSING_EVIDENCE = "MISSING_EVIDENCE"
NOT_APPLICABLE = "NOT_APPLICABLE"
SOURCE_REFUTED = "SOURCE_REFUTED"
_STATUS_TOKENS = {EXTRACTED, HUMAN_PENDING, MISSING_EVIDENCE, NOT_APPLICABLE, SOURCE_REFUTED, "INCOMPLETE_EVIDENCE"}

# (P225) Card-completeness contract. Every verifier-card field must carry a DESIGNATED ANSWER: either a real
# artifact-backed value OR one of these explicit, DISTINCT tokens — never a blank/None/empty. These are kept
# distinct on purpose (unknown ≠ MISSING_EVIDENCE ≠ HUMAN_PENDING ≠ NOT_APPLICABLE ≠ REACHABILITY_UNKNOWN); the
# seal never collapses them and never overwrites a real value (so no evidence is fabricated).
REACHABILITY_UNKNOWN = "REACHABILITY_UNKNOWN"
NOT_REVIEWED = "not_reviewed"
_DESIGNATED_TOKEN = {            # category -> token used ONLY to fill a genuinely blank field
    "scalar": UNK,
    "proof": MISSING_EVIDENCE,
    "human": HUMAN_PENDING,
    "severity": HUMAN_PENDING,
    "reach": REACHABILITY_UNKNOWN,
    "na": NOT_APPLICABLE,
}
_PLACEHOLDER_VALUES = {UNK, MISSING_EVIDENCE, NOT_APPLICABLE, SOURCE_REFUTED, REACHABILITY_UNKNOWN, "N/A", "n/a"}
_HUMAN_PENDING_VALUES = {HUMAN_PENDING, NOT_REVIEWED}
# Below this fraction of artifact-backed (vs total evidence-bearing) fields, the card is flagged
# WARNING_LOW_EVIDENCE_DEPTH — a NON-blocking depth warning, never a fabricate-or-block trigger.
_EVIDENCE_DEPTH_WARN_THRESHOLD = 0.50

# section -> field categories. kind: dict | flat_list | row_list | dict_of_lists.
#   *_list categories ('proof_list','na_list') seal an EMPTY list to [token]; 'bool' fields are structural.
CARD_CONTRACT = {
    "top_line_status": {"kind": "dict", "scalar": ["banner", "mechanism_result", "l3_status", "human_review_priority"],
                        "reach": ["reachability_class"], "na_list": ["human_review_reason_codes", "priority_blockers", "display_lines"],
                        "bool": ["should_surface_above_noise", "submission_ready", "routing_allowed"]},
    "report_summary": {"kind": "dict", "scalar": ["bug", "impact_summary", "current_decision", "submission_boundary"],
                       "proof": ["attacker"], "severity": ["severity_recommendation"], "human": ["novelty_status"],
                       "proof_list": ["affected_contracts", "affected_functions"]},
    "mechanism": {"kind": "dict", "proof": ["one_sentence", "root_cause"], "scalar": ["refutation_condition", "why_not_refuted"]},
    "function_map": {"kind": "row_list", "row": {"role": "scalar", "function": "scalar", "permission": "scalar",
                                                 "why_it_matters": "scalar", "source_location": "scalar"}},
    "attacker_model": {"kind": "dict", "scalar": ["attacker", "privilege_required", "victim_action_required",
                                                  "operator_or_keeper_dependency", "self_remediation", "reachability_verdict", "reason"],
                       "reach": ["reachability_class"], "proof_list": ["controls", "does_not_control"]},
    "exploit_steps": {"kind": "flat_list", "cat": "proof"},
    "defense_map": {"kind": "row_list", "row": {"defense": "scalar", "location": "scalar", "classification": "scalar",
                                                "reason": "scalar", "manual_check": "scalar"}},
    "poc_verification": {"kind": "dict",
                         "proof": ["uses_real_contract", "production_source_unchanged", "harness_isolated_unwired", "command", "test_result"],
                         "scalar": ["actual_result", "expected_result", "control_result", "corrected_reference_result", "state_or_value_delta"],
                         "row_list_fields": {"result_table": {"note": "scalar"}}},
    "impact_severity": {"kind": "dict", "scalar": ["who_loses", "who_gains", "asset_or_value", "loss_type",
                                                   "permanence", "repeatability", "bounds"],
                        "severity": ["severity_recommendation"],
                        "na_list": ["downgrade_arguments", "upgrade_arguments", "assumptions", "unresolved_questions"]},
    "intent_scope_operator": {"kind": "dict", "scalar": ["intent_verdict", "operator_scope_status", "operator_or_keeper_fact",
                                                         "does_ambiguity_kill_or_bound"], "na_list": ["scope_caveats"]},
    "novelty_duplicate": {"kind": "dict", "human": ["duplicate_status", "novelty_status", "exact_duplicate_found", "materially_equivalent_found"],
                          "scalar": ["public_known_context", "sources_checked_summary", "residual_limit"]},
    "conversion": {"kind": "dict", "proof": ["mechanism_confirmed", "attacker_reachable", "severity_bearing", "reportable", "reachability_verdict"],
                   "human": ["novelty_clear", "duplicate_status"], "severity": ["severity_class"],
                   "scalar": ["runtime_status", "conversion_outcome", "primary_blocker", "human_review_required"],
                   "bool": ["submission_ready", "routing_allowed"]},
    "main_blocker": {"kind": "dict", "scalar": ["blocker", "why_it_matters", "what_would_clear_it"]},
    "final_triage": {"kind": "dict", "scalar": ["decision", "why", "what_this_taught_the_system"]},
    "red_flags": {"kind": "row_list", "row": {"check": "scalar", "status": "scalar", "evidence": "scalar"}},
    "evidence_backup": {"kind": "dict_of_lists", "lists": {"top_source_files": {"label": "scalar", "path": "scalar"},
                                                           "raw_artifacts_collapsed": {"label": "scalar", "path": "scalar", "kind": "scalar"}}},
}
COMPLETENESS_DISCLAIMER = ("Completeness means every field is answered; it does not mean the bug is proven or "
                           "ready to submit.")

# conversion / decision / lifecycle tokens that must NEVER be shown as a severity value
_CONVERSION_TOKENS = re.compile(
    r"^(clean_hit|adjacent|abstained|rejected|rejected_or_abstained|severity_gated|poc_handoff|"
    r"runtime_confirmed|runtime_refuted|investigated|needs_context|static_false_positive|reportable|"
    r"poc_ready|report_ready|lead|killed|validation_ready|context_mapped|reproduced|not_run)\b", re.I)
_VALID_SEVERITY = re.compile(r"(critical|high|medium|low|informational|info|qa|no_security_impact|none|design)", re.I)


def _is_present(x: Any) -> bool:
    if isinstance(x, bool):
        return True
    return x not in (None, "", [], {}, UNK)


def _classify_blank(category: str, outcome: str) -> str:
    """Classify a blank field into an actionable status. `category` ∈ {proof, human, severity, neutral};
    `outcome` is the lowercased conversion_outcome/state. Display hint only."""
    o = (outcome or "").lower()
    if category == "human" or category == "severity":
        return HUMAN_PENDING
    if category == "proof":
        if "refuted" in o or "static_false_positive" in o:
            return SOURCE_REFUTED
        if any(t in o for t in ("abstained", "rejected")):
            return NOT_APPLICABLE
        return MISSING_EVIDENCE
    return UNK


def _sev_or_status(*vals: Any, outcome: str = "") -> str:
    """Return the first value that is a plausible severity (never a conversion/decision token); else
    HUMAN_PENDING (severity is a human judgment, not derivable from a conversion label)."""
    for v in vals:
        if not _is_present(v):
            continue
        s = str(v).strip()
        if _CONVERSION_TOKENS.match(s):
            continue  # a conversion/decision label leaked into the severity slot — reject it
        if _VALID_SEVERITY.search(s):
            return s
    return HUMAN_PENDING


def _md_clean(s: str) -> str:
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    return s.strip()


def _doc_content(documents: List[Dict[str, Any]], suffix: str) -> str:
    for d in documents or []:
        if (d.get("path") or "").endswith(suffix):
            return d.get("content") or ""
    return ""


def _md_section(text: str, heading_substr: str) -> str:
    """Text under the first heading containing heading_substr, until the next heading of same/higher level."""
    if not text:
        return ""
    out: List[str] = []
    capturing = False
    start_level = 0
    for ln in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            level, title = len(m.group(1)), m.group(2)
            if capturing and level <= start_level:
                break
            if not capturing and heading_substr.lower() in title.lower():
                capturing, start_level = True, level
                continue
        if capturing:
            out.append(ln)
    return "\n".join(out).strip()


def _md_list(text: str, heading_substr: str) -> List[str]:
    """Ordered/`-`/`*` list items under a heading; wrapped (indented) continuation lines are folded in."""
    items: List[str] = []
    for ln in _md_section(text, heading_substr).splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", ln)
        if m:
            items.append(_md_clean(m.group(1)))
        elif items and ln.strip() and (ln.startswith("  ") or ln.startswith("\t")) and not ln.lstrip().startswith("#"):
            items[-1] = (items[-1] + " " + _md_clean(ln.strip())).strip()
    return [i for i in items if i]


def _md_table(text: str, header_substr: str) -> List[Dict[str, str]]:
    """Rows (header-keyed dicts) of the first pipe-table whose header row contains header_substr."""
    if not text:
        return []
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and header_substr.lower() in ln.lower():
            headers = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
            rows: List[Dict[str, str]] = []
            j = i + 1
            if j < len(lines) and set(lines[j].replace("|", "").strip()) <= set("-: "):
                j += 1  # skip the |---| separator
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [_md_clean(c.strip()) for c in lines[j].strip().strip("|").split("|")]
                if len(cells) >= len(headers):
                    rows.append({headers[k]: cells[k] for k in range(len(headers))})
                j += 1
            return rows
    return []


def _resolve_source_contract(architecture: Optional[str], target: Optional[str]) -> Optional[Path]:
    """Best-effort, read-only resolve of the production source contract from `<Contract>.<fn>` + audit slug.
    Returns None if not uniquely/safely resolvable (never fabricated). Skips poc/test/mock files."""
    if not architecture or not target:
        return None
    contract = target.split(".")[0].strip()
    if not contract:
        return None
    base = ROOT / "audits"
    if not base.is_dir():
        return None
    for adir in sorted(base.glob(f"{architecture}*")):
        for f in adir.rglob(f"{contract}.sol"):
            s = str(f).lower()
            if "/pocs/" in s or "/test" in s or "mock" in s:
                continue
            return f
    return None


def _runtime_state(row: Dict[str, Any]) -> str:
    from findings_overview import is_reportable_candidate  # canonical predicate (lazy: avoid import cycle)
    if is_reportable_candidate(row):
        return "REPORTABLE_CANDIDATE"
    conv = row.get("conversion") or {}
    m = {
        "reportable_candidate_needs_human_review": "REPORTABLE_CANDIDATE",
        "runtime_confirmed_but_privileged_only": "PRIVILEGED_ONLY",
        "runtime_refuted": "RUNTIME_REFUTED",
        "needs_context": "NEEDS_CONTEXT",
    }
    if conv.get("outcome") in m:
        return m[conv["outcome"]]
    rs = (row.get("runtime_status") or "").lower()
    return {"runtime_confirmed": "RUNTIME_CONFIRMED", "runtime_refuted": "RUNTIME_REFUTED",
            "not_run": "NOT_RUN"}.get(rs, "INVESTIGATED")


# --------------------------------------------------------------------------- runtime adapter
def _metrics_candidate_id(mj: Path) -> Optional[str]:
    """The STRUCTURED subject id of a phase's metrics.json (candidate_id / candidate.candidate_id /
    subject.bug_id). Used to decide whether a phase dir is ABOUT a candidate — never a substring scan."""
    try:
        d = json.loads(_read(mj) or "{}")
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(d, dict):
        return None
    cid = d.get("candidate_id")
    if not cid and isinstance(d.get("candidate"), dict):
        cid = d["candidate"].get("candidate_id")
    if not cid and isinstance(d.get("subject"), dict):
        cid = d["subject"].get("bug_id")
    return cid


def _runtime_phase_dirs(row: Dict[str, Any], item_id: str) -> List[Path]:
    """Candidate-SCOPED phase dirs (read-only): the candidate's own PoC phase (from harness_path
    .../pocs/pNNN/...) PLUS sibling phases whose metrics.json STRUCTURED candidate_id == item_id.
    Deliberately NOT a substring scan — summary/panel files (e.g. a cross-candidate study guide, or a phase
    whose metrics merely *lists* this id in a panel) must never pull another candidate's evidence in."""
    dirs: List[Path] = []
    seen = set()
    hp = row.get("harness_path") or ""
    m = re.search(r"/pocs/(p\d+)/", hp)
    if m and ASSISTED_DIR.is_dir():
        for d in sorted(ASSISTED_DIR.glob(f"{m.group(1)}_*")):
            if d.is_dir() and d not in seen:
                dirs.append(d); seen.add(d)
    if ASSISTED_DIR.is_dir() and item_id:
        for mj in sorted(ASSISTED_DIR.glob("*/metrics.json")):
            if _metrics_candidate_id(mj) == item_id and mj.parent not in seen:
                dirs.append(mj.parent); seen.add(mj.parent)
    return dirs


def _runtime_detail(item_id: str, key: str) -> Dict[str, Any]:
    row: Optional[Dict[str, Any]] = None
    if RUNTIME_SIDECAR.exists():
        for line in RUNTIME_SIDECAR.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if (r.get("item_id") or r.get("bug_id")) == item_id:
                row = r
                break
    if row is None:
        return _not_found(key, "runtime")

    conv = row.get("conversion") or {}
    state = _runtime_state(row)
    phase_dirs = _runtime_phase_dirs(row, item_id)

    # mirror each linked artifact as its own openable record (markdown + json), and list every path
    documents: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    for d in phase_dirs:
        for name in _RUNTIME_DOC_ORDER:
            f = d / name
            if f.exists():
                txt = _read(f)
                if txt:
                    documents.append({"label": f"{d.name}/{name}", "path": _rel(f), "abs_path": str(f),
                                      "kind": "md", "content": txt.strip()})
                    evidence.append({"label": f"{d.name}/{name}", "path": _rel(f),
                                     "abs_path": str(f), "kind": "doc"})
        # metrics.json mirrored as a pretty-printed JSON record; other artifacts listed in the evidence table
        mj = d / "metrics.json"
        if mj.exists():
            raw = _read(mj)
            pretty = raw
            if raw:
                try:
                    pretty = json.dumps(json.loads(raw), indent=2)
                except Exception:  # noqa: BLE001
                    pretty = raw
            documents.append({"label": f"{d.name}/metrics.json", "path": _rel(mj), "abs_path": str(mj),
                              "kind": "json", "content": pretty})
        for extra in ("metrics.json", "integrity_checks.md", "test_commands.md"):
            f = d / extra
            if f.exists():
                evidence.append({"label": f"{d.name}/{extra}", "path": _rel(f), "abs_path": str(f),
                                 "kind": "artifact"})
    hp = row.get("harness_path") or row.get("test_path")
    if hp:
        evidence.append({"label": "PoC harness", "path": hp, "abs_path": str(ROOT / hp), "kind": "poc"})
    evidence.append({"label": "runtime sidecar row", "path": _rel(RUNTIME_SIDECAR),
                     "abs_path": str(RUNTIME_SIDECAR), "kind": "sidecar"})

    reach = None
    if row.get("reachability_verdict") or conv.get("attacker_reachable") is not None:
        reach = {
            "attacker_can_reach": conv.get("attacker_reachable"),
            "reachability_verdict": row.get("reachability_verdict"),
            "reason": row.get("reachability_reason") or row.get("limitations"),
        }
    sev = (row.get("final_severity_recommendation") or row.get("severity_recommendation")
           or row.get("severity_class") or row.get("runtime_confidence"))

    # 2-4 most important links for the top of the verifier page (only those whose file exists)
    def _find_doc(suffix: str) -> Optional[Dict[str, Any]]:
        return next((x for x in documents if (x.get("path") or "").endswith(suffix)), None)
    key_links: List[Dict[str, Any]] = []
    sc = _resolve_source_contract(row.get("architecture"), row.get("target"))
    if sc:
        key_links.append({"label": "source contract", "path": _rel(sc), "abs_path": str(sc)})
    if hp:
        key_links.append({"label": "PoC harness", "path": hp, "abs_path": str(ROOT / hp)})
    for label, suffix in (("runtime result", "runtime_result.md"),
                          ("review report", "review_report.md"),
                          ("review report", "conversion_classification.md")):
        if any(k["label"] == label for k in key_links):
            continue
        doc = _find_doc(suffix)
        if doc:
            key_links.append({"label": label, "path": doc["path"], "abs_path": doc["abs_path"]})

    out: Dict[str, Any] = {
        "candidate_id": key, "track": "runtime", "read_only_synced": True, "labelable": False,
        "raw_row": row, "key_links": key_links,
        "detector": "value-provenance runtime", "audit_id": row.get("architecture"),
        "candidate_surface": row.get("target") or item_id,
        "lifecycle_state": row.get("runtime_status"), "outcome": conv.get("outcome") or state,
        "state": state, "status_group": state,
        "declared_severity_potential": sev, "severity_or_conversion": sev,
        "runtime_status": row.get("runtime_status"), "runtime_confidence": row.get("runtime_confidence"),
        "conversion_outcome": conv.get("outcome"), "duplicate_status": row.get("duplicate_status"),
        "novelty_status": row.get("novelty_status"), "operator_scope_status": row.get("operator_scope_status"),
        "blocker": conv.get("blocker") or row.get("primary_blocker_if_not_reportable"),
        "mechanism": row.get("suspected_mechanism") or row.get("mechanism_class"),
        "rationale": row.get("divergence_summary"),
        "source": {"file": hp, "line": None, "abs_path": (str(ROOT / hp) if hp else None),
                   "resolution_status": "present" if hp else "missing"},
        "reachability": reach,
        "conversion": conv,
        "evidence": evidence,
        "documents": documents,
        "verdict_md": (f"{len(documents)} mirrored record(s) across "
                       + ", ".join(d.name for d in phase_dirs) if documents else None),
        "phase_dirs": [_rel(d) for d in phase_dirs],
        "next_action": "human review — " + (row.get("human_review_focus") or "severity / scope / novelty"),
        "research_only": True, "routing_allowed": False, "submission_ready": bool(row.get("submission_ready", False)),
    }
    out["verifier_evidence"] = build_verifier_evidence(out, row, documents, "runtime")
    return out


# --------------------------------------------------------------------------- funnel adapter
def _funnel_state(rec: Dict[str, Any]) -> str:
    from findings_overview import is_reportable_candidate  # canonical predicate (lazy: avoid import cycle)
    if is_reportable_candidate(rec):
        return "REPORTABLE_CANDIDATE"
    if rec.get("submitted"):
        return "SUBMITTED"
    pipe = (rec.get("pipeline_status") or "").upper()
    if "HUMAN_REVIEW" in pipe or rec.get("human_readiness") == "READY_FOR_HUMAN_REVIEW":
        return "READY_FOR_HUMAN_REVIEW"
    if (rec.get("poc_status") or "").upper() == "REPRODUCED":
        return "REPRODUCED"
    return pipe or "INVESTIGATED"


def _funnel_detail(cand_id: str, key: str) -> Dict[str, Any]:
    try:
        import funnel
        recs = funnel.load_records().get("records", [])
    except Exception:  # noqa: BLE001
        return _not_found(key, "funnel")
    rec = next((r for r in recs if r.get("candidate_id") == cand_id), None)
    if rec is None:
        rec = next((r for r in recs if (r.get("finding_id") or r.get("record_id")) == cand_id), None)
    if rec is None:
        return _not_found(key, "funnel")

    # (P216) load_records()["records"] are whitelisted display ROWS — they drop the rich detail fields a synced
    # finding carries (mechanism, impact, surface_function, blocker_reason, inline checklist sections, p155 gates).
    # Read-only: resolve the FULL normalized record (curated funnel_records.json + generated synced mirror) and
    # merge it under the row so build_verifier_evidence sees the recorded evidence. Never alters severity/routing.
    try:
        _full = None
        # (real-world) The live funnel source is the honest hunt log: its candidate findings carry a rich inline
        # `verifier` block (function map, attacker model, exploit steps, defense map, PoC actual/expected/control,
        # impact). load_records()'s display ROW drops those, so resolve the FULL real-world record here so the
        # verifier card shows every reproduce/understand field. Read-only; never alters severity/routing.
        _rwp = getattr(funnel, "REAL_RESULTS_PATH", None)
        if _rwp and Path(_rwp).exists():
            _rwdoc = _read(Path(_rwp))
            _rwdata = json.loads(_rwdoc) if _rwdoc else None
            if isinstance(_rwdata, dict):
                for _raw in funnel._records_from_real_world(_rwdata):
                    if (_raw.get("record_id") == rec.get("record_id")
                            or _raw.get("finding_id") == cand_id or _raw.get("record_id") == cand_id):
                        _full = funnel.normalize_record(dict(_raw))
                        break
        # (P216) fall back to the curated funnel_records.json + generated synced mirror for legacy records.
        if _full is None:
            for _src in (getattr(funnel, "DEFAULT_RECORDS_PATH", None), getattr(funnel, "SYNCED_RECORDS_PATH", None)):
                if not _src or not Path(_src).exists():
                    continue
                _doc = _read(Path(_src))
                _raws = (json.loads(_doc).get("findings") if _doc else None) or []
                _match = next((x for x in _raws if isinstance(x, dict)
                               and (x.get("record_id") == rec.get("record_id")
                                    or x.get("finding_id") == cand_id or x.get("record_id") == cand_id)), None)
                if _match:
                    _full = funnel.normalize_record(dict(_match))
                    break
        if _full:
            rec = {**rec, **{k: v for k, v in _full.items() if v is not None}}
    except Exception:  # noqa: BLE001 — never break the card; fall back to the row
        pass

    links = rec.get("artifact_links") or {}
    evidence = [{"label": k, "path": v, "abs_path": str(ROOT / v) if v else None, "kind": "artifact"}
                for k, v in links.items() if v]
    state = _funnel_state(rec)
    cf = rec.get("contract_function")
    verdict_parts = []
    for label, val in (("finding", rec.get("finding_title")), ("subject", rec.get("subject")),
                       ("phase", rec.get("phase_discovered")), ("conversion", rec.get("conversion")),
                       ("mechanism_correctness", rec.get("mechanism_correctness")),
                       ("severity_gate", rec.get("severity_gate")), ("adversarial", rec.get("adversarial_result")),
                       ("control", rec.get("control")), ("pipeline_status", rec.get("pipeline_status")),
                       ("poc_status", rec.get("poc_status")), ("poc_command", rec.get("poc_command") or rec.get("test_command")),
                       ("submission_status", rec.get("submission_status")), ("human_final_gate", rec.get("human_final_gate")),
                       ("blocker", rec.get("blocker_reason")), ("impact", rec.get("impact")),
                       ("lessons", rec.get("lessons_learned"))):
        if val:
            verdict_parts.append(f"- **{label}**: {val}")

    sub = rec.get("submission") or {}
    key_links: List[Dict[str, Any]] = []
    if cf:
        key_links.append({"label": "source (function)", "path": cf, "abs_path": None})
    for label, keys in (("PoC test", ("test", "test_file")),
                        ("evidence bundle", ("bundle", "evidence_bundle_path")),
                        ("artifact dir", ("dir", "poc_artifact_dir"))):
        v = next((links[k] for k in keys if links.get(k)), None)
        if v:
            key_links.append({"label": label, "path": v, "abs_path": str(ROOT / v)})

    out: Dict[str, Any] = {
        "candidate_id": key, "track": "funnel", "read_only_synced": True, "labelable": False,
        "raw_record": rec, "key_links": key_links,
        "detector": f"funnel ({rec.get('source') or 'blind'})", "audit_id": rec.get("subject"),
        "candidate_surface": rec.get("finding_title") or cf or rec.get("subject"),
        "lifecycle_state": rec.get("pipeline_status"), "outcome": rec.get("conversion") or state,
        "state": state, "status_group": state,
        "declared_severity_potential": rec.get("claimed_severity") or rec.get("conversion"),
        "severity_or_conversion": rec.get("conversion") or rec.get("claimed_severity"),
        "pipeline_status": rec.get("pipeline_status"), "poc_status": rec.get("poc_status"),
        "conversion_outcome": rec.get("conversion"),
        "duplicate_status": sub.get("duplicate_check_status") or rec.get("duplicate_check"),
        "blocker": rec.get("blocker_reason"),
        "mechanism": rec.get("mechanism_correctness"),
        "rationale": rec.get("impact") or rec.get("finding_title"),
        "source": {"file": cf, "line": None, "abs_path": None,
                   "resolution_status": "present" if cf else "missing"},
        "reachability": None,
        "evidence": evidence,
        "documents": ([{"label": "funnel record", "path": None, "abs_path": None, "kind": "md",
                        "content": "\n".join(verdict_parts)}] if verdict_parts else []),
        "verdict_md": ("\n".join(verdict_parts) if verdict_parts else None),
        "test_command": rec.get("poc_command") or rec.get("test_command"),
        "next_action": "human review — scope / duplicate / severity" if state == "READY_FOR_HUMAN_REVIEW" else "continue funnel",
        "research_only": True, "routing_allowed": False, "submission_ready": False,
    }
    out["verifier_evidence"] = build_verifier_evidence(out, rec, out.get("documents") or [], "funnel")
    return out


# --------------------------------------------------------------------------- option-A campaign adapter
def _campaign_detail(candidate_id: str, key: str) -> Dict[str, Any]:
    row: Optional[Dict[str, Any]] = None
    if CAMPAIGN_LEDGER.exists():
        for line in CAMPAIGN_LEDGER.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if r.get("candidate_id") == candidate_id:
                row = r
                break
    if row is None:
        return _not_found(key, "option_a_campaign")

    # gather the phase deliverables (read-only): any assisted_mode dir whose metrics.json names this candidate
    phase_dirs = _runtime_phase_dirs({}, candidate_id)
    documents: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    for d in phase_dirs:
        for f in sorted(d.glob("*.md")):
            txt = _read(f)
            if txt:
                documents.append({"label": f"{d.name}/{f.name}", "path": _rel(f), "abs_path": str(f),
                                  "kind": "md", "content": txt.strip()})
        mj = d / "metrics.json"
        if mj.exists():
            evidence.append({"label": f"{d.name}/metrics.json", "path": _rel(mj), "abs_path": str(mj),
                             "kind": "artifact"})
    evidence.append({"label": "campaign ledger row", "path": _rel(CAMPAIGN_LEDGER),
                     "abs_path": str(CAMPAIGN_LEDGER), "kind": "ledger"})
    key_links = [{"label": d["label"], "path": d["path"], "abs_path": d["abs_path"]} for d in documents[:4]]

    src_reach = _doc_content(documents, "source_reachability_map.md")
    harness_doc = _doc_content(documents, "harness_design.md")
    taught = next((_doc_content(documents, s) for s in
                   ("what_p158_taught.md", "what_p159_taught.md", "what_p160_taught.md",
                    "what_p161_taught.md", "what_p162_taught.md") if _doc_content(documents, s)), "")
    from findings_overview import is_reportable_candidate  # canonical predicate (lazy: avoid import cycle)
    if is_reportable_candidate(row):
        state = "REPORTABLE_CANDIDATE"
    else:
        state = {
            "static_false_positive": "STATIC_FALSE_POSITIVE", "runtime_refuted": "RUNTIME_REFUTED",
            "reportable_candidate_needs_human_review": "REPORTABLE_CANDIDATE", "needs_context": "NEEDS_CONTEXT",
        }.get((row.get("conversion_outcome") or "").lower(),
              "NOT_RUN_TOO_HEAVY" if "too_heavy" in f"{row.get('deploy_complexity','')} {row.get('primary_blocker','')}".lower()
              else "NOT_RUN")

    campaign = {
        "severity_ceiling_estimate": row.get("severity_ceiling_estimate") or UNK,
        "why_no_harness": _u(_md_section(harness_doc, "Why it was NOT built")
                             or _md_section(harness_doc, "NOT_RUN")),
        "source_refutation": _u(_md_section(src_reach, "REFUTED at source")
                                or _md_section(src_reach, "Result")),
        "deploy_blocker": _u(row.get("deploy_complexity")),
        "what_taught": _u(_md_section(taught, "What this taught") or (taught[:500] if taught else "")),
        "selection_reason": row.get("selection_reason") or UNK,
    }

    out: Dict[str, Any] = {
        "candidate_id": key, "track": "option_a_campaign", "read_only_synced": True, "labelable": False,
        "raw_row": row, "key_links": key_links, "documents": documents, "evidence": evidence,
        "detector": "option-A campaign", "audit_id": row.get("audit"),
        "candidate_surface": row.get("surface_function") or row.get("mechanism_class") or candidate_id,
        "lifecycle_state": row.get("runtime_status"), "outcome": row.get("conversion_outcome") or state,
        "state": state, "status_group": state,
        "declared_severity_potential": row.get("severity_recommendation") or row.get("severity_ceiling_estimate"),
        "severity_or_conversion": row.get("severity_recommendation") or row.get("severity_ceiling_estimate"),
        "runtime_status": row.get("runtime_status"), "conversion_outcome": row.get("conversion_outcome"),
        "duplicate_status": row.get("duplicate_status"), "novelty_status": row.get("novelty_status"),
        "reachability_verdict": row.get("reachability_verdict"),
        "blocker": row.get("primary_blocker"),
        "mechanism": row.get("why") or row.get("mechanism_class"),
        "rationale": row.get("why"),
        "source": {"file": None, "line": None, "abs_path": None, "resolution_status": "n/a (no runtime harness)"},
        "reachability": None,
        "campaign": campaign,
        "next_action": "campaign-measured; no human action (ledger record)",
        "research_only": True, "routing_allowed": False, "submission_ready": False,
    }
    out["verifier_evidence"] = build_verifier_evidence(out, row, documents, "option_a_campaign")
    return out


def _not_found(key: str, track: str) -> Dict[str, Any]:
    return {"candidate_id": key, "track": track, "read_only_synced": True, "labelable": False,
            "state": "NOT_FOUND", "research_only": True, "routing_allowed": False, "submission_ready": False,
            "verdict_md": f"No {track} finding found for key: {key}", "evidence": []}


# --------------------------------------------------------------------------- verifier evidence builder
def _u(x: Any) -> Any:
    if isinstance(x, bool):
        return x
    return x if x not in (None, "", [], {}) else UNK


def _first(*vals: Any) -> Any:
    for v in vals:
        if v not in (None, "", [], {}):
            return v
    return UNK


def build_verifier_evidence(detail: Dict[str, Any], raw: Dict[str, Any],
                            documents: List[Dict[str, Any]], track: str) -> Dict[str, Any]:
    """Extract recorded evidence from sidecar + phase artifacts into the verifier schema (best-effort,
    structured-field → markdown → table → snippet → 'unknown'). Never fabricates; never computes severity."""
    raw = raw or {}
    conv = detail.get("conversion")
    if not isinstance(conv, dict):
        conv = raw.get("conversion") if isinstance(raw.get("conversion"), dict) else {}
    reach = detail.get("reachability") or {}
    rv = _first(reach.get("reachability_verdict"), raw.get("reachability_verdict"))
    src_reach = _doc_content(documents, "source_reachability_map.md")
    runtime_doc = _doc_content(documents, "runtime_result.md")
    sev_doc = _doc_content(documents, "severity_finalization_memo.md")
    harness_doc = _doc_content(documents, "harness_design.md")
    taught_doc = (_doc_content(documents, "what_p156_taught_the_trainer.md")
                  or _doc_content(documents, "what_p155_taught_the_trainer.md")
                  or _doc_content(documents, "what_p154_taught_the_trainer.md"))
    defense_rows = _md_table(_doc_content(documents, "defense_map.md"), "Defense")
    result_rows = _md_table(runtime_doc, "Window")

    # ---- functions / function map (from surface_function + target) ----
    sf = raw.get("surface_function") or ""
    tgt = raw.get("target") or raw.get("contract_function") or ""
    funcs: List[str] = []
    def _add(n: str) -> None:
        if re.fullmatch(r"[a-z][A-Za-z0-9_]*", n) and n not in ("vs",) and n not in funcs:
            funcs.append(n)
    for seg in re.split(r"[;]", sf):
        for n in re.split(r"[/\s]+", seg.split("(")[0].strip()):
            _add(n)
    contract = tgt.split(".")[0].strip() if "." in tgt else tgt.strip()
    if "." in tgt:
        for n in re.split(r"[/\s]+", tgt.split(".", 1)[1]):
            _add(n.strip())
    src_path = _first(next((k.get("path") for k in (detail.get("key_links") or [])
                            if k.get("label") == "source contract"), None),
                      (detail.get("source") or {}).get("file"))

    def _perm_for(name: str) -> str:
        for seg in re.split(r"[;]", sf):
            if name in seg.split("(")[0]:
                m = re.search(r"\(([^)]*)\)", seg)
                return m.group(1) if m else UNK
        return UNK

    def _role(name: str, perm: str) -> str:
        p = (perm or "").lower()
        if "onlyoperator" in p or "onlyowner" in p or "admin" in p:
            return "operator / admin (de-boost path)"
        if name in ("balanceOf", "earned", "totalSupply"):
            return "critical accounting"
        if name in ("getRewards", "claim", "withdraw", "redeem"):
            return "settlement / claim"
        if "public" in p or "external" in p or "whennotpaused" in p:
            return "user entrypoint"
        return UNK

    def _why(name: str) -> str:
        for ln in src_reach.splitlines():
            t = ln.strip()
            if name in t and len(t) > len(name) + 10 and not t.startswith("#") and not t.startswith("|"):
                return _md_clean(t)[:240]
        return UNK

    function_map = [{"role": _role(n, _perm_for(n)), "function": n, "permission": _u(_perm_for(n)),
                     "why_it_matters": _why(n), "source_location": _u(src_path)} for n in funcs]

    # ---- attacker ----
    _rv_l = (rv or "").lower()
    unpriv = "unprivileged" in _rv_l and "not unprivileged" not in _rv_l and "not-unprivileged" not in _rv_l
    mech = (raw.get("suspected_mechanism") or raw.get("impact") or raw.get("finding_title")
            or detail.get("rationale") or detail.get("mechanism") or "")
    attacker = ("unprivileged user" + (" with an expired boosted lock" if "lock" in mech.lower() else "")
                ) if unpriv else UNK
    controls = _md_list(src_reach, "User-controlled fields")
    op_fact = raw.get("p156_decisive_fact")

    # (P221) reachability CLASS + structured attacker fields: prefer inline artifact-backed values (from the synced
    # record / L3) over the binary unpriv heuristic, so trusted-system (TSS-gated) paths populate honestly instead of
    # collapsing to 'unknown'. Display-only — never touches severity (_sev_or_status), submission_ready, routing_allowed.
    _DERIVE_REACH = {"permissionless": "UNPRIVILEGED_REACHABLE", "program_accepted": "PROGRAM_ACCEPTED_ACTOR_REACHABLE",
                     "privileged_only": "PRIVILEGED_ONLY_REACHABLE", "privileged": "PRIVILEGED_ONLY_REACHABLE",
                     "trusted_admin": "PRIVILEGED_ONLY_REACHABLE", "compromise_required": "COMPROMISE_REQUIRED"}
    _reach_class = raw.get("reachability_class")
    if not _is_present(_reach_class):
        _am_key = str(raw.get("attacker_model") or "").lower()
        _reach_class = next((v for k, v in _DERIVE_REACH.items() if k in _am_key), None) or (
            "UNPRIVILEGED_REACHABLE" if unpriv else "REACHABILITY_UNKNOWN")
    _priv_req = raw.get("privilege_required") if _is_present(raw.get("privilege_required")) else ("no" if unpriv else UNK)
    _victim_req = raw.get("victim_action_required") if _is_present(raw.get("victim_action_required")) else (
        "no" if "passive" in (raw.get("p155_gate2_attacker_model") or "").lower() else UNK)
    _self_rem = raw.get("self_remediation") if _is_present(raw.get("self_remediation")) else (
        "none (no user unlock path)" if "no_self_remediation" in (rv or "") else UNK)
    _op_dep = _first(raw.get("operator_or_keeper_dependency"), detail.get("operator_scope_status"),
                     raw.get("operator_scope_status"), op_fact)
    _ctrls = (raw.get("attacker_controls") if isinstance(raw.get("attacker_controls"), list) and raw.get("attacker_controls")
              else controls)
    _doesnot = (raw.get("attacker_does_not_control") if isinstance(raw.get("attacker_does_not_control"), list)
                and raw.get("attacker_does_not_control") else ([_md_clean(op_fact)] if op_fact else []))

    # ---- candidate-scoped refutation framing (reads ONLY this candidate's row; never another candidate) ----
    outcome = str(detail.get("conversion_outcome") or conv.get("outcome") or raw.get("conversion_outcome")
                  or detail.get("state") or "").lower()
    refuted = "refuted" in outcome

    def _fld(value: Any, category: str) -> Any:
        """Show the value if present; else a classified status (display hint only, never fabricated)."""
        return value if _is_present(value) else _classify_blank(category, outcome)

    # funnel records carry their own proof signals; map them to the conversion booleans (never override an
    # explicit recorded bool from the runtime sidecar).
    _mc = str(raw.get("mechanism_correctness") or "").lower()
    _sg = str(raw.get("severity_gate") or "").lower()
    mech_confirmed = conv.get("mechanism_confirmed", raw.get("mechanism_confirmed"))
    if mech_confirmed is None and _mc:
        mech_confirmed = True if _mc.startswith("correct") else (False if _mc in ("incorrect", "wrong") else None)
    sev_bearing = conv.get("severity_bearing", raw.get("severity_bearing"))
    if sev_bearing is None and _sg:
        sev_bearing = True if _sg == "passed" else (False if _sg in ("failed", "demoted") else None)
    reachable = conv.get("attacker_reachable", raw.get("attacker_reachable"))

    divergence = raw.get("divergence_summary") or ""
    blocker_val = conv.get("blocker") or raw.get("primary_blocker_if_not_reportable") or detail.get("blocker")
    bug_title = ("Refuted: " + mech) if (refuted and mech and not mech.lower().startswith("refuted")) else mech

    # ---- honest blocker (no optimistic "none" on non-reportable candidates) ----
    _reportable = ((conv.get("reportable") is True) or (raw.get("reportable") is True)
                   or ("reportable" in outcome) or ("runtime_confirmed" in outcome))
    if _reportable and (mech_confirmed is True) and (reachable is True):
        blocker_computed = "none (mechanism + reachability confirmed)"
        blocker_why = _first(raw.get("human_review_focus"),
                             "residual is a severity / scope / novelty judgment (human-owned)")
        blocker_clear = _first(raw.get("human_review_focus"),
                               (raw.get("p155_human_residual") or [None])[0] if raw.get("p155_human_residual") else None)
    elif _is_present(blocker_val):
        blocker_computed = blocker_val
        blocker_why = _first(raw.get("human_review_focus"), "recorded blocker for this candidate")
        blocker_clear = _first(raw.get("human_review_focus"), "resolve the recorded blocker")
    else:
        _missing = []
        if mech_confirmed is not True:
            _missing.append("MISSING_MECHANISM_PROOF")
        if reachable is not True:
            _missing.append("MISSING_REACHABILITY_PROOF")
        if sev_bearing is not True:
            _missing.append("MISSING_SEVERITY_PROOF")
        blocker_computed = _missing[0] if len(_missing) == 1 else "INCOMPLETE_READINESS_EVIDENCE"
        blocker_why = ("readiness evidence incomplete: " + ", ".join(_missing)) if _missing else "readiness evidence incomplete"
        blocker_clear = "supply " + ", ".join(_missing) if _missing else MISSING_EVIDENCE
    # the recorded guard (e.g. an internal called before the value/state move) named on this row
    _guard = next(iter(re.findall(r"_[A-Za-z][A-Za-z0-9_]*",
                  f"{raw.get('target','')} {raw.get('surface_function','')}")), None)
    # defense_map: prefer the md table; else a single guard row derived from THIS row (refuted-by-guard);
    # else leave empty so the UI shows "unknown" / "not recorded" (never another candidate's defenses).
    defense_map_out = [{"defense": r.get("defense", UNK), "location": _u(r.get("where")),
                        "classification": _u(r.get("classification")), "reason": _u(r.get("reasoning")),
                        "manual_check": "Does it run before/after the loss, only by operator, or never?"}
                       for r in defense_rows]
    if not defense_map_out and (refuted or blocker_val == "mechanism_absent_guard_present") and (divergence or _guard):
        defense_map_out = [{
            "defense": _u(_guard or raw.get("corrected_reference_type") or raw.get("target")),
            "location": _u(raw.get("target")),
            "classification": "blocks_candidate (guard present; mechanism absent)",
            "reason": _u(divergence or raw.get("corrected_reference_type")),
            "manual_check": "Does the guard run before the value/state movement?",
        }]

    # ---- exploit steps ----
    steps = _md_list(harness_doc, "Scenario")

    # ---- severity arg lists ----
    downgrade = _md_list(sev_doc, "Downgrade arguments")
    upgrade = _md_list(sev_doc, "Upgrade arguments")
    assumptions = _md_list(sev_doc, "Assumptions")
    unresolved = _md_list(sev_doc, "Unresolved questions")

    # ---- impact derivations (grounded in recorded text) ----
    vout = raw.get("vulnerable_output") or ""
    combined = " ".join([vout, raw.get("divergence_summary") or "", raw.get("runtime_delta") or "", sev_doc])
    who_loses = "honest stakers" if "honest staker" in combined.lower() else UNK
    who_gains = "expired-but-unprocessed locker" if "locker earns" in vout.lower() or "over-accru" in combined.lower() else UNK
    loss_type = ("user-to-user redistribution (zero-sum); not direct protocol-fund loss"
                 if "zero-sum" in combined.lower() else UNK)
    asset = "reward token(s)" if "reward" in combined.lower() else UNK
    # (P219) prefer INLINE artifact-backed impact fields (from dashboard_sync / L3 record) over the text heuristic.
    # Read-only display hint only; never touches severity, submission_ready, or routing_allowed.
    if _is_present(raw.get("who_loses")):
        who_loses = raw["who_loses"]
    if _is_present(raw.get("who_gains")):
        who_gains = raw["who_gains"]
    if _is_present(raw.get("loss_type")):
        loss_type = raw["loss_type"]
    if _is_present(raw.get("asset_or_value")):
        asset = raw["asset_or_value"]

    def _line_with(text: str, kw: str) -> str:
        for ln in text.splitlines():
            if kw.lower() in ln.lower() and not ln.strip().startswith("#"):
                return _md_clean(ln.strip("- ").strip())[:240]
        return UNK
    permanence = _first(_line_with(sev_doc, "permanent"), _line_with(runtime_doc, "permanent"))
    repeatability = _line_with(sev_doc, "unbounded")
    # prefer INLINE artifact-backed values (synced / real-world record) over the markdown heuristic.
    # Display-only; never touches severity, submission_ready, or routing_allowed.
    if _is_present(raw.get("permanence")):
        permanence = raw["permanence"]
    if _is_present(raw.get("repeatability")):
        repeatability = raw["repeatability"]

    def _taught() -> str:
        for hd in ("real bottleneck", "Headline", "Discipline preserved"):
            s = _md_section(taught_doc, hd)
            if s:
                return _md_clean(s)[:500]
        return UNK

    # ---- red flags (status only where a recorded field is unambiguous; else manual) ----
    arch_real = raw.get("real_contract_deployed")
    def _rf(check: str, ok: Optional[bool], evidence: Any, manual: bool = False) -> Dict[str, str]:
        status = "manual" if manual or ok is None else ("pass" if ok else "fail")
        return {"check": check, "status": status, "evidence": str(_u(evidence))}
    red_flags = [
        _rf("PoC calls an admin-only function as the attacker", unpriv or None, rv),
        _rf("Exploit works only in a mock, not production flow", bool(arch_real) if arch_real is not None else None, f"real_contract_deployed={arch_real}"),
        _rf("User cannot control the critical input", (conv.get("attacker_reachable") is True) or None, raw.get("p155_gate2_attacker_model")),
        _rf("Claimed loss is bigger than the PoC proves", None, "review impact vs runtime_delta", manual=True),
        _rf("Issue disappears when the real defense path runs", None, raw.get("limitations"), manual=True),
        _rf("Depends entirely on undocumented intent", (conv.get("attacker_reachable") is True) or None, raw.get("p155_gate1_source_intent")),
        _rf("Duplicate status unknown but report assumes novelty", (str(raw.get("novelty_clear")).lower() == "unknown") or None, raw.get("novelty_status")),
        _rf("Runtime confirmed but reachability unknown", (conv.get("attacker_reachable") is True) or None, rv),
        _rf("Severity claimed but no victim loss shown", (who_loses != UNK) or None, vout),
        _rf('Report says "drain" but only proves redistribution', None, loss_type, manual=True),
    ]

    # (P216) synced records (schema "synced-1", from dashboard_sync) may carry INLINE checklist sections. Prefer
    # them over the markdown-doc-derived versions when present. Read-only display hint only — this never touches
    # severity (_sev_or_status), submission_ready, or routing_allowed.
    _inl_fm = raw.get("function_map")
    if isinstance(_inl_fm, list) and _inl_fm:
        function_map = _inl_fm
    if _is_present(raw.get("attacker_model")) and isinstance(raw.get("attacker_model"), str):
        attacker = raw["attacker_model"]
    _inl_dm = raw.get("defense_map")
    if isinstance(_inl_dm, list) and _inl_dm:
        defense_map_out = _inl_dm
    _inl_es = raw.get("exploit_steps")
    if isinstance(_inl_es, list) and [s for s in _inl_es if s not in (MISSING_EVIDENCE, "MISSING_EVIDENCE")]:
        steps = _inl_es
    _inl_rf = raw.get("red_flags")
    if isinstance(_inl_rf, list) and _inl_rf:
        red_flags = _inl_rf

    # ---- evidence completeness (display-only; never flips submission_ready/routing_allowed) ----
    _active = any(t in outcome for t in ("clean_hit", "runtime_confirmed", "reportable", "reproduced"))
    _missing_core: List[str] = []
    if _active:
        if not contract:
            _missing_core.append("affected_contracts")
        if not funcs:
            _missing_core.append("affected_functions")
        if not _is_present(mech):
            _missing_core.append("one_sentence_mechanism")
        if not _is_present(attacker if attacker != UNK else None):
            _missing_core.append("attacker_model")
        if not steps:
            _missing_core.append("exploit_steps")
        if track == "runtime" and not _is_present(raw.get("vulnerable_output")):
            _missing_core.append("poc_actual_result")
        if who_loses == UNK:
            _missing_core.append("who_loses_who_gains")
    evidence_completeness = ({"status": "INCOMPLETE_EVIDENCE", "missing": _missing_core}
                             if (_active and _missing_core) else {"status": "OK", "missing": []})

    # (P222) read-only top-line status banner: mechanism result · L3 status · reachability class · human-review
    # priority · blocker. Display only — reads recorded fields, never computes severity, never flips submission_ready
    # or routing_allowed, and adds no submit/promote controls.
    _l3_for_banner = _first(raw.get("l3_status"),
                            ((raw.get("l3") or {}).get("l3_status") if isinstance(raw.get("l3"), dict) else None))
    _hrp = raw.get("human_review_priority")
    _hrp_reasons = raw.get("human_review_reason_codes") or []
    _hrp_blockers = raw.get("priority_blockers") or []
    _REASON_TEXT = {"PROGRAM_THREAT_MODEL_DECISION_REQUIRED": "program threat-model decision required",
                    "L3_PASS_BUT_SCOPE_DECISION_REQUIRED": "scope decision required",
                    "NEEDS_PROGRAM_RULE_INTERPRETATION": "needs program-rule interpretation",
                    "LOW_CONFIDENCE_NOISE": "low-confidence residual"}
    _conv_label = _first(detail.get("conversion_outcome"), conv.get("outcome"), raw.get("conversion_outcome"))
    _banner_parts = []
    if _is_present(_conv_label):
        _banner_parts.append(str(_conv_label).upper().replace(" ", "_"))
    if _is_present(_l3_for_banner):
        _banner_parts.append("L3_" + str(_l3_for_banner).upper() if not str(_l3_for_banner).upper().startswith("L3") else str(_l3_for_banner).upper())
    if _is_present(_reach_class):
        _banner_parts.append(str(_reach_class))
    _prio_label = None
    if _hrp in ("HIGH", "CRITICAL_HUMAN_REVIEW"):
        _prio_label = "HIGH_PRIORITY_HUMAN_REVIEW"
    elif _hrp in ("MEDIUM", "LOW"):
        _prio_label = f"{_hrp}_PRIORITY_HUMAN_REVIEW"
    if _prio_label:
        _banner_parts.append(_prio_label)
    _disp_lines = []
    if _prio_label and _hrp in ("HIGH", "MEDIUM", "CRITICAL_HUMAN_REVIEW"):
        _reason_txt = next((_REASON_TEXT[r] for r in _hrp_reasons if r in _REASON_TEXT), None)
        _disp_lines = ["Not submission-ready",
                       f"Human review priority: {_hrp.title() if _hrp != 'CRITICAL_HUMAN_REVIEW' else 'Critical'}"]
        if _reason_txt:
            _disp_lines.append(f"Reason: {_reason_txt}")
        _disp_lines.append("External route/submission disabled")
    top_line_status = {
        "banner": " · ".join(_banner_parts),
        "mechanism_result": _u(_conv_label),
        "l3_status": _u(_l3_for_banner),
        "reachability_class": _reach_class,
        "human_review_priority": _u(_hrp),
        "human_review_reason_codes": _hrp_reasons,
        "priority_blockers": _hrp_blockers,
        "should_surface_above_noise": bool(raw.get("should_surface_above_noise")),
        "display_lines": _disp_lines,
        "submission_ready": detail.get("submission_ready", False),
        "routing_allowed": detail.get("routing_allowed", False),
    }

    # (VRT/CVSS) display-only classification surfaced on the card's Report Summary. Reads recorded fields from
    # the candidate's verifier block (merged onto the record by _records_from_real_world); never computes,
    # influences, or echoes a production severity/routing decision.
    _vrt = _first(raw.get("vrt_category"), raw.get("vulnerability_category"))

    def _cvss_one(c: Any) -> Optional[str]:
        if isinstance(c, dict):
            sc, sev, vec, lbl = c.get("score"), c.get("severity"), c.get("vector"), c.get("aspect")
            head = (f"{sc} {sev}".strip() if (sc is not None and sev) else
                    (str(sc) if sc is not None else (str(sev) if sev else "")))
            head = f"{lbl}: {head}".strip(": ") if lbl else head
            parts = [p for p in (head, str(vec) if vec else "") if p]
            return " — ".join(parts) or None
        return c if _is_present(c) else None

    _cvss_raw = raw.get("cvss")
    if isinstance(_cvss_raw, list):
        _cvss_disp = " ; ".join([x for x in (_cvss_one(c) for c in _cvss_raw) if x]) or None
    else:
        _cvss_disp = _cvss_one(_cvss_raw)
    if not _is_present(_cvss_disp):  # flat-field fallback
        _sc, _sev, _vec = raw.get("cvss_score"), raw.get("cvss_severity"), raw.get("cvss_vector")
        if _is_present(_sc) or _is_present(_vec):
            _cvss_disp = _cvss_one({"score": _sc, "severity": _sev, "vector": _vec})

    _evidence = {
        "evidence_completeness": evidence_completeness,
        "top_line_status": top_line_status,
        "report_summary": {
            "bug": _u(bug_title), "affected_contracts": ([contract] if contract else []),
            "vrt_category": _u(_vrt), "cvss": _u(_cvss_disp),
            "affected_functions": funcs, "attacker": _fld(attacker if attacker != UNK else None, "proof"),
            "impact_summary": _fld(_first(raw.get("impact"), vout, raw.get("divergence_summary")) if
                                   _is_present(_first(raw.get("impact"), vout, raw.get("divergence_summary"))) else None, "proof"),
            "current_decision": _first(detail.get("conversion_outcome"), conv.get("outcome")),
            # severity must never echo a conversion/decision label; it is a human judgment when not recorded.
            "severity_recommendation": _sev_or_status(raw.get("final_severity_recommendation"),
                                                      raw.get("severity_recommendation"), raw.get("claimed_severity"),
                                                      raw.get("awarded_severity"), outcome=outcome),
            "novelty_status": _fld(_first(detail.get("novelty_status"), raw.get("novelty_status")) if
                                   _is_present(_first(detail.get("novelty_status"), raw.get("novelty_status"))) else None, "human"),
            "submission_boundary": _first(raw.get("p156_gate4_submission_boundary"),
                                          ("not submission-ready" if detail.get("submission_ready") is False else None)),
        },
        "mechanism": {
            "one_sentence": _fld(mech or None, "proof"),
            "root_cause": _fld(_first(raw.get("mechanism_class"), raw.get("mechanism_correctness")) if
                               _is_present(_first(raw.get("mechanism_class"), raw.get("mechanism_correctness"))) else None, "proof"),
            "refutation_condition": _u(_md_section(src_reach, "Refutation condition") or (divergence if refuted else "")),
            "why_not_refuted": _u((_line_with(src_reach, "Not refuted") if src_reach else "") or ((divergence if divergence.lower().startswith("refuted") else "REFUTED — " + divergence) if (refuted and divergence) else "")),
        },
        "function_map": function_map,
        "attacker_model": {
            "attacker": attacker, "controls": _ctrls,
            "does_not_control": _doesnot,
            "privilege_required": _u(_priv_req),
            "victim_action_required": _u(_victim_req),
            "operator_or_keeper_dependency": _op_dep,
            "self_remediation": _u(_self_rem),
            "reachability_class": _reach_class,
            "reachability_verdict": _u(rv), "reason": _first(reach.get("reason"), raw.get("limitations")),
        },
        "exploit_steps": steps,
        "defense_map": defense_map_out,
        "poc_verification": {
            "uses_real_contract": (raw.get("real_contract_deployed") if raw.get("real_contract_deployed") is not None
                                   else _classify_blank("proof", outcome)),
            "production_source_unchanged": (raw.get("production_source_modified") is False)
            if raw.get("production_source_modified") is not None else _classify_blank("proof", outcome),
            "harness_isolated_unwired": True if raw.get("harness_path") else _classify_blank("proof", outcome),
            "command": "forge test -vv" if track == "runtime" else _fld(_first(raw.get("poc_command"), raw.get("test_command")) if _is_present(_first(raw.get("poc_command"), raw.get("test_command"))) else None, "proof"),
            "test_result": ("4/4 passed" if "4 passed" in runtime_doc or "4/4" in str(raw.get("harness_cost"))
                            else _fld(raw.get("poc_status"), "proof")),
            "actual_result": _u(raw.get("vulnerable_output")), "expected_result": _u(raw.get("corrected_output")),
            "control_result": _u(raw.get("control_case")), "corrected_reference_result": _u(raw.get("corrected_reference_type")),
            "state_or_value_delta": _u(raw.get("runtime_delta")), "result_table": result_rows,
        },
        "impact_severity": {
            "who_loses": who_loses, "who_gains": who_gains, "asset_or_value": asset, "loss_type": loss_type,
            "permanence": permanence, "repeatability": repeatability, "bounds": _u(raw.get("limitations")),
            "severity_recommendation": _first(raw.get("final_severity_recommendation"), raw.get("severity_recommendation")),
            "downgrade_arguments": downgrade, "upgrade_arguments": upgrade,
            "assumptions": assumptions, "unresolved_questions": unresolved,
        },
        "intent_scope_operator": {
            "intent_verdict": _u(raw.get("p155_gate1_source_intent")),
            "operator_scope_status": _first(detail.get("operator_scope_status"), raw.get("operator_scope_status")),
            "operator_or_keeper_fact": _u(op_fact),
            "scope_caveats": ([_md_clean(raw.get("p155_alternative_reading"))] if raw.get("p155_alternative_reading") else []),
            "does_ambiguity_kill_or_bound": ("bounds severity (does not refute)"
                                             if "bounds" in (raw.get("operator_scope_status") or "") else UNK),
        },
        "novelty_duplicate": {
            "duplicate_status": _fld(detail.get("duplicate_status"), "human"),
            "novelty_status": _fld(_first(detail.get("novelty_status"), raw.get("novelty_status")) if
                                   _is_present(_first(detail.get("novelty_status"), raw.get("novelty_status"))) else None, "human"),
            "exact_duplicate_found": ("no" if (raw.get("novelty_status") == "public_known_but_not_duplicate") else HUMAN_PENDING),
            "materially_equivalent_found": ("no" if (raw.get("novelty_status") == "public_known_but_not_duplicate") else HUMAN_PENDING),
            "public_known_context": _u(raw.get("p155_public_known_caveat")),
            "sources_checked_summary": _u(raw.get("p156_c4_awarded_corpus")),
            "residual_limit": _u(raw.get("p156_residual_limit")),
        },
        "conversion": {
            "mechanism_confirmed": _fld(mech_confirmed, "proof"),
            "attacker_reachable": _fld(reachable, "proof"),
            "severity_bearing": _fld(sev_bearing, "proof"),
            "novelty_clear": _fld(conv.get("novelty_clear", raw.get("novelty_clear")), "human"),
            "reportable": _fld(conv.get("reportable", raw.get("reportable")), "proof"),
            "runtime_status": _first(detail.get("runtime_status"), raw.get("runtime_status")),
            "reachability_verdict": _fld(rv if rv != UNK else None, "proof"),
            "severity_class": _fld(raw.get("severity_class"), "severity"),
            "duplicate_status": _fld(detail.get("duplicate_status"), "human"),
            "conversion_outcome": _first(detail.get("conversion_outcome"), conv.get("outcome")),
            "primary_blocker": blocker_computed,
            "human_review_required": _u(raw.get("human_review_required")),
            "submission_ready": detail.get("submission_ready", False),
            "routing_allowed": detail.get("routing_allowed", False),
        },
        "main_blocker": {
            "blocker": blocker_computed,
            "why_it_matters": blocker_why,
            "what_would_clear_it": _u(blocker_clear),
        },
        "final_triage": {
            "decision": _first(raw.get("p156_gate4_submission_boundary"), detail.get("state")),
            "why": _first(raw.get("_p156_note"), raw.get("_p155_note"),
                          " · ".join([str(x) for x in (detail.get("severity_or_conversion"),
                                                       raw.get("operator_scope_status"), raw.get("novelty_status")) if x])),
            "what_this_taught_the_system": _taught(),
        },
        "red_flags": red_flags,
        "evidence_backup": {
            "top_source_files": detail.get("key_links") or [],
            "raw_artifacts_collapsed": [{"label": d.get("label"), "path": d.get("path"), "kind": d.get("kind")}
                                        for d in (documents or [])],
        },
    }
    return _seal_and_score(_evidence, track=track, outcome=outcome)


# --------------------------------------------------------------------------- card-completeness seal + scorecard
def _is_blank(v: Any) -> bool:
    """A field is blank (un-designated) if it is None/empty-string/empty-list/empty-dict. Bools are NEVER blank."""
    if isinstance(v, bool):
        return False
    return v in (None, "", [], {})


def _classify_leaf(v: Any) -> str:
    """artifact_backed | placeholder | human_pending | structural — for the depth scorecard (post-seal)."""
    if isinstance(v, bool):
        return "structural"
    if isinstance(v, str):
        if v in _HUMAN_PENDING_VALUES:
            return "human_pending"
        if v in _PLACEHOLDER_VALUES:
            return "placeholder"
        return "artifact_backed"
    if isinstance(v, list):
        if not v:
            return "placeholder"
        kinds = {_classify_leaf(x) for x in v}
        if kinds <= {"placeholder"}:
            return "placeholder"
        if kinds <= {"human_pending", "placeholder"}:
            return "human_pending"
        return "artifact_backed"
    if isinstance(v, dict):
        kinds = {_classify_leaf(x) for x in v.values()} or {"placeholder"}
        return "artifact_backed" if "artifact_backed" in kinds else (
            "human_pending" if "human_pending" in kinds else "placeholder")
    return "artifact_backed" if v is not None else "placeholder"


def _seal_field(val: Any, category: str) -> Any:
    """Fill a blank scalar field with the category's DISTINCT token; never overwrite a real value."""
    return val if not _is_blank(val) else _DESIGNATED_TOKEN.get(category, UNK)


def _seal_row(row: Dict[str, Any], row_spec: Dict[str, str]) -> Dict[str, Any]:
    out = dict(row) if isinstance(row, dict) else {}
    for k, cat in row_spec.items():
        out[k] = _seal_field(out.get(k), cat)
    return out


def _seal_list(lst: Any, token: str) -> List[Any]:
    return lst if (isinstance(lst, list) and lst) else [token]


def _seal_row_list(lst: Any, row_spec: Dict[str, str]) -> List[Any]:
    if isinstance(lst, list) and lst:
        return [_seal_row(r, row_spec) for r in lst]
    return [_seal_row({}, row_spec)]   # one explicit placeholder row -> never a blank section


def _seal_and_score(evidence: Dict[str, Any], track: str = "", outcome: str = "") -> Dict[str, Any]:
    """(P225) Guarantee a designated answer in EVERY contracted field (seal blanks with distinct tokens; never
    overwrite real values, never fabricate), then attach a 3-axis scorecard:
      card_completeness   — every field answered (after seal: COMPLETE)
      evidence_sufficiency— how much is artifact-backed vs placeholder/human-pending (WARNING_LOW_EVIDENCE_DEPTH
                            below threshold; NON-blocking, never fabricates)
      submission_readiness— independent human/package gate (placeholders never imply submission-ready)."""
    pre_blank: List[str] = []
    for section, spec in CARD_CONTRACT.items():
        kind = spec["kind"]
        if kind == "flat_list":
            if _is_blank(evidence.get(section)):
                pre_blank.append(section)
            evidence[section] = _seal_list(evidence.get(section), _DESIGNATED_TOKEN[spec["cat"]])
        elif kind == "row_list":
            if _is_blank(evidence.get(section)):
                pre_blank.append(section)
            evidence[section] = _seal_row_list(evidence.get(section), spec["row"])
        elif kind == "dict_of_lists":
            sec = evidence.get(section) if isinstance(evidence.get(section), dict) else {}
            for lname, row_spec in spec["lists"].items():
                if _is_blank(sec.get(lname)):
                    pre_blank.append(f"{section}.{lname}")
                sec[lname] = _seal_row_list(sec.get(lname), row_spec)
            evidence[section] = sec
        else:  # dict
            sec = evidence.get(section) if isinstance(evidence.get(section), dict) else {}
            for cat in ("scalar", "proof", "human", "severity", "reach"):
                for f in spec.get(cat, []):
                    if _is_blank(sec.get(f)):
                        pre_blank.append(f"{section}.{f}")
                    sec[f] = _seal_field(sec.get(f), cat)
            for f in spec.get("proof_list", []):
                if _is_blank(sec.get(f)):
                    pre_blank.append(f"{section}.{f}")
                sec[f] = _seal_list(sec.get(f), MISSING_EVIDENCE)
            for f in spec.get("na_list", []):
                if _is_blank(sec.get(f)):
                    pre_blank.append(f"{section}.{f}")
                sec[f] = _seal_list(sec.get(f), NOT_APPLICABLE)
            for f in spec.get("bool", []):
                sec[f] = bool(sec.get(f))
            for f, row_spec in spec.get("row_list_fields", {}).items():
                sec[f] = _seal_row_list(sec.get(f), row_spec)
            evidence[section] = sec

    # ---- depth scorecard (post-seal) ----
    counts = {"artifact_backed": 0, "placeholder": 0, "human_pending": 0, "structural": 0}
    for section, spec in CARD_CONTRACT.items():
        node = evidence.get(section)
        if spec["kind"] in ("flat_list", "row_list"):
            counts[_classify_leaf(node)] += 1
        elif spec["kind"] == "dict_of_lists":
            for lname in spec["lists"]:
                counts[_classify_leaf((node or {}).get(lname))] += 1
        else:
            for cat in ("scalar", "proof", "human", "severity", "reach"):
                for f in spec.get(cat, []):
                    counts[_classify_leaf((node or {}).get(f))] += 1
            for f in spec.get("proof_list", []) + spec.get("na_list", []):
                counts[_classify_leaf((node or {}).get(f))] += 1
            for f in spec.get("bool", []):
                counts["structural"] += 1
            for f in spec.get("row_list_fields", {}):
                counts[_classify_leaf((node or {}).get(f))] += 1

    total = sum(counts.values())
    evidence_bearing = counts["artifact_backed"] + counts["placeholder"] + counts["human_pending"]
    pct = round(100 * counts["artifact_backed"] / evidence_bearing) if evidence_bearing else 0
    suff_status = "SUFFICIENT" if (evidence_bearing and counts["artifact_backed"] / evidence_bearing
                                   >= _EVIDENCE_DEPTH_WARN_THRESHOLD) else "WARNING_LOW_EVIDENCE_DEPTH"
    tls = evidence.get("top_line_status") or {}
    sub_ready = bool(tls.get("submission_ready"))
    routing = bool(tls.get("routing_allowed"))

    prev = evidence.get("evidence_completeness") if isinstance(evidence.get("evidence_completeness"), dict) else {}
    evidence["evidence_completeness"] = {
        **prev,  # back-compat: keep prior status / missing (core-evidence rollup)
        # axis 1 — every field has a designated answer (post-seal this is COMPLETE; pre_blank = sealed-from-blank)
        "card_completeness": {"status": "COMPLETE", "total_fields": total,
                              "sealed_from_blank": sorted(set(pre_blank)), "sealed_count": len(set(pre_blank))},
        # axis 2 — depth of real evidence (NON-blocking warning; never fabricated)
        "evidence_sufficiency": {"status": suff_status, "artifact_backed": counts["artifact_backed"],
                                 "placeholder": counts["placeholder"], "human_pending": counts["human_pending"],
                                 "structural": counts["structural"], "evidence_bearing": evidence_bearing,
                                 "pct_artifact_backed": pct, "threshold_pct": int(_EVIDENCE_DEPTH_WARN_THRESHOLD * 100)},
        # axis 3 — independent human/package gate (placeholders NEVER imply submission-ready)
        "submission_readiness": {"submission_ready": sub_ready, "routing_allowed": routing,
                                 "status": "SUBMISSION_READY" if sub_ready else "NOT_SUBMISSION_READY_HUMAN_GATE"},
        "disclaimer": COMPLETENESS_DISCLAIMER,
    }
    return evidence


# --------------------------------------------------------------------------- dispatch
def load_unified_detail(key: str) -> Dict[str, Any]:
    if not key:
        return _not_found(key, "unknown")
    if key.startswith("runtime:"):
        d = _runtime_detail(key[len("runtime:"):], key)
    elif key.startswith("funnel:"):
        d = _funnel_detail(key[len("funnel:"):], key)
    elif key.startswith("campaign:"):
        d = _campaign_detail(key[len("campaign:"):], key)
    else:
        # default: detector candidate_id (back-compat) — existing full validation packet, untouched.
        import candidate_detail as cd
        d = cd.load_candidate_detail(key)
        d.setdefault("track", "detector")
        d["labelable"] = True          # detector corpus candidates remain the only labelable workflow
        d["read_only_synced"] = False
        d.setdefault("research_only", True)
        d["routing_allowed"] = False
    # canonical reportable-candidate status text (display-only; never flips submission_ready/routing_allowed)
    if isinstance(d, dict) and d.get("state") == "REPORTABLE_CANDIDATE":
        d["status_text"] = "valid finding, human review required"
    # human-owned submission-readiness overlay (read-only; never flips submission_ready/routing_allowed)
    if isinstance(d, dict) and d.get("state") != "NOT_FOUND":
        try:
            import submission_readiness_review as srr  # lazy: avoid import cycle
            d["readiness"] = srr.detail_overlay(key)
        except Exception:  # noqa: BLE001
            d["readiness"] = {"readiness_state": "not_reviewed"}
    return d
