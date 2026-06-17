"""
Candidate-detail adapter — READ-ONLY view model for the candidate→PoC validation pipeline.

Reads the per-candidate artifact folder designed in
`documentation/architecture/candidate_validation_to_poc_blueprint.md`:
    documentation/research/candidates/<audit_id>/<candidate_hash>/<artifact>.json

and normalizes it into a UI-safe `CandidateDetail`. The validation pipeline itself is not built yet, so:
  - missing artifacts are reported gracefully (status="missing", never crash);
  - candidates that have no folder but ARE known frozen-corpus bundles are returned as a RAW_CANDIDATE shell.

SAFETY: this module NEVER writes, promotes, generates a PoC/report, or mutates any artifact / detector output /
production gate / frozen corpus. It separates the four confidences (detector / validation / exploit / impact) and
exposes POC_READY only as "local PoC task allowed" — never as a severity/validity/submission verdict.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import human_validation as hv

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES_REL = "documentation/research/candidates"
FROZEN_CORPUS = ROOT / "documentation/evals/judge_corpus/frozen_corpus.json"
# (real-world) The honest hunt log — its PoC-proven candidate findings are surfaced as candidate rows so the
# dashboard's /candidates view reflects real activity (the eval frozen corpus above is deleted). Read-only.
REAL_RESULTS_PATH = ROOT / "documentation/real_world_results.json"
# Eval/synthetic audit ids whose leftover candidate folders must NOT appear on the live (default-root)
# /candidates view — mirrors scripts/compute_metrics.py's eval exclusion. On-disk files are left untouched.
_EVAL_AUDIT_IDS = {"beanstalk-2024-05", "size-credit-2024-06"}

# artifact filename → CandidateDetail section key
ARTIFACTS = [
    "raw_candidate.json", "candidate_manifest.json", "source_resolution.json", "reachability_map.json",
    "callable_surface.json", "state_mutation_map.json", "defense_map.json", "invariant_analysis.json",
    "sequence_candidates.json", "negative_tests.json", "validation_scorecard.json", "promotion_decision.json",
    "poc_ready.lock.json", "report_ready.lock.json", "notes.md", "verdict.md",
]
_JSON_ARTIFACTS = [a for a in ARTIFACTS if a.endswith(".json")]

# timeline order (artifact → human-readable stage)
_TIMELINE = [
    ("raw_candidate.json", "raw detector candidate"),
    ("source_resolution.json", "source resolved"),
    ("reachability_map.json", "reachability checked"),
    ("state_mutation_map.json", "context mapped"),
    ("defense_map.json", "defenses mapped"),
    ("invariant_analysis.json", "invariant analyzed"),
    ("sequence_candidates.json", "sequences generated"),
    ("negative_tests.json", "negative tests run"),
    ("promotion_decision.json", "promotion decision"),
    ("poc_ready.lock.json", "PoC lock created"),
    ("report_ready.lock.json", "report lock created"),
]

_NEXT_ACTION = {
    "RAW_CANDIDATE": "resolve source",
    "RESOLVED_SOURCE": "map reachability",
    "REACHABLE": "generate context map",
    "CONTEXT_MAPPED": "map defenses (request human review #1)",
    "DEFENSE_MAPPED": "define invariant",
    "INVARIANT_ANALYZED": "create sequence candidates",
    "SEQUENCE_CANDIDATE": "run negative tests (request human review #2)",
    "NEGATIVE_TESTED": "score certainty",
    "VALIDATION_READY": "request human review #3 before POC_READY",
    "POC_READY": "create local PoC task (allowed) — not a submission",
    "REPORT_READY": "human report drafting (separate gate)",
    "KILLED": "kill candidate — no further action",
    "NEEDS_CONTEXT": "continue investigation / acquire missing context",
    "PARTIAL": "continue investigation",
}


def candidates_root() -> Path:
    return ROOT / CANDIDATES_REL


def _read_json(p: Path) -> Optional[Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _read_text(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


def parse_candidate_id(candidate_id: str) -> Dict[str, str]:
    """`<detector>:<contract>:<function>:<shape>:<hash8>` → parts. Tolerant of extra colons."""
    parts = candidate_id.split(":")
    detector = parts[0] if parts else ""
    chash = parts[-1] if len(parts) >= 2 else ""
    surface = ""
    if len(parts) >= 4:
        surface = f"{parts[1]}.{parts[2]}"
    return {"detector": detector, "candidate_hash": chash, "candidate_surface": surface}


# --------------------------------------------------------------- corpus shell (RAW)
_corpus_cache: Optional[Dict[str, Dict[str, Any]]] = None


def _corpus_bundles() -> Dict[str, Dict[str, Any]]:
    global _corpus_cache
    if _corpus_cache is None:
        _corpus_cache = {}
        try:
            c = hv.load_corpus(FROZEN_CORPUS)
            for b in c["bundles"]:
                _corpus_cache[b["candidate_id"]] = b
        except Exception:  # noqa: BLE001 — corpus optional
            _corpus_cache = {}
    return _corpus_cache


def _source_roots() -> List[Path]:
    roots = [ROOT]
    aud = ROOT / "audits"
    if aud.is_dir():
        roots += sorted(d for d in aud.glob("*") if d.is_dir())
    return roots


# --------------------------------------------------------------- folder discovery
def find_candidate_dir(candidate_id: str, root: Optional[Path] = None) -> Optional[Path]:
    """Locate <root>/<audit_id>/<candidate_hash>/ by matching candidate_hash (and confirming via manifest/raw)."""
    root = root or candidates_root()
    if not root.is_dir():
        return None
    chash = parse_candidate_id(candidate_id)["candidate_hash"]
    if not chash:
        return None
    for audit_dir in sorted(root.glob("*")):
        cand = audit_dir / chash
        if cand.is_dir():
            return cand
    return None


def _section(folder: Optional[Path], fname: str) -> Dict[str, Any]:
    """{status, data} for one artifact. status ∈ present|missing|failed."""
    if folder is None:
        return {"status": "missing", "data": None}
    p = folder / fname
    if not p.exists():
        return {"status": "missing", "data": None}
    if fname.endswith(".md"):
        txt = _read_text(p)
        return {"status": "present" if txt is not None else "failed", "data": txt}
    data = _read_json(p)
    if data is None:
        return {"status": "failed", "data": None}
    st = data.get("status") if isinstance(data, dict) else None
    return {"status": "present", "data": data, "gate_status": st}


# --------------------------------------------------------------- main loader
def load_candidate_detail(candidate_id: str, root: Optional[Path] = None) -> Dict[str, Any]:
    root = root or candidates_root()
    folder = find_candidate_dir(candidate_id, root)
    ids = parse_candidate_id(candidate_id)
    sections = {a: _section(folder, a) for a in ARTIFACTS}

    manifest = sections["candidate_manifest.json"]["data"] or {}
    raw = sections["raw_candidate.json"]["data"] or {}
    srcres = sections["source_resolution.json"]["data"] or {}
    scorecard = sections["validation_scorecard.json"]["data"] or {}
    promo = sections["promotion_decision.json"]["data"] or {}
    poc_data = sections["poc_ready.lock.json"]["data"]
    report_data = sections["report_ready.lock.json"]["data"]

    bundle = _corpus_bundles().get(candidate_id)
    illustrative = any(
        isinstance(sections[a]["data"], dict) and sections[a]["data"].get("_illustrative")
        for a in _JSON_ARTIFACTS
    )

    # ---- shell from corpus bundle when no folder/manifest ----
    have_folder = folder is not None
    if not have_folder and bundle is None:
        # unknown candidate entirely
        detector = ids["detector"]
        surface = ids["candidate_surface"]
        location, snippet, rationale, det_conf, sev = {}, None, None, None, None
    elif not have_folder and bundle is not None:
        detector = bundle.get("detector", ids["detector"])
        surface = bundle.get("candidate_surface", ids["candidate_surface"])
        location = bundle.get("location", {})
        snippet = bundle.get("code_snippet")
        rationale = bundle.get("rationale")
        det_conf = bundle.get("confidence")
        sev = bundle.get("declared_severity_potential")
    else:
        detector = manifest.get("detector") or raw.get("detector") or (bundle or {}).get("detector") or ids["detector"]
        surface = manifest.get("candidate_surface") or raw.get("candidate_surface") or ids["candidate_surface"]
        location = manifest.get("location") or (bundle or {}).get("location") or {}
        snippet = srcres.get("code_snippet") or (bundle or {}).get("code_snippet")
        rationale = raw.get("reason") or (bundle or {}).get("rationale")
        det_conf = manifest.get("detector_confidence") or raw.get("confidence") or (bundle or {}).get("confidence")
        sev = manifest.get("declared_severity_potential") or (bundle or {}).get("declared_severity_potential")

    audit_id = manifest.get("audit_id") or raw.get("audit_id") or (
        folder.parent.name if folder is not None else None)

    # lifecycle / outcome
    lifecycle_state = manifest.get("lifecycle_state") or ("RAW_CANDIDATE" if not have_folder else "RAW_CANDIDATE")
    outcome = manifest.get("outcome") or (promo.get("to_state") if promo else None)
    if not have_folder:
        outcome = None

    # four confidences — ALWAYS four distinct keys; detector carried verbatim, others require artifacts
    conf = scorecard.get("confidences") or {}
    confidence = {
        "detector_confidence": det_conf,
        "validation_confidence": conf.get("validation_confidence"),
        "exploit_confidence": conf.get("exploit_confidence"),
        "impact_confidence": conf.get("impact_confidence"),
    }

    # missing artifacts + hard blockers
    missing_artifacts = [a for a in ARTIFACTS if sections[a]["status"] == "missing"]
    hard_blockers = []
    if isinstance(scorecard.get("hard_blockers"), list):
        hard_blockers = scorecard["hard_blockers"]

    # source panel
    file_rel = location.get("file") if isinstance(location, dict) else None
    line = location.get("start_line") if isinstance(location, dict) else None
    abs_path = hv.abs_source(file_rel, _source_roots()) if file_rel else None
    source = {
        "file": file_rel, "line": line,
        "function_signature": srcres.get("function_signature"),
        "code_snippet": snippet,
        "source_hash": srcres.get("source_hash") or manifest.get("source_hash"),
        "abs_path": abs_path,
        "resolution_status": sections["source_resolution.json"]["status"],
    }

    # evidence timeline
    timeline = [{"stage": label, "present": sections[a]["status"] == "present", "artifact": a}
                for a, label in _TIMELINE]

    poc_ready = {"exists": isinstance(poc_data, dict),
                 "authorizes": (poc_data or {}).get("authorizes"),
                 "warning": "POC_READY permits local PoC task creation only. It is not a severity verdict or submission approval.",
                 "data": poc_data}
    report_ready = {"exists": isinstance(report_data, dict), "data": report_data}

    return {
        "candidate_id": candidate_id,
        "audit_id": audit_id,
        "candidate_hash": ids["candidate_hash"],
        "detector": detector,
        "candidate_surface": surface,
        "declared_severity_potential": sev,
        "lifecycle_state": lifecycle_state,
        "outcome": outcome,
        "status_group": status_group(lifecycle_state, outcome),
        "routing_allowed": False,
        "research_only": True,
        "illustrative": illustrative,
        "has_folder": have_folder,
        "source": source,
        "confidence": confidence,
        "rationale": rationale,
        "rationale_evidence": raw.get("evidence_signals") or (bundle or {}).get("evidence_signals") or {},
        "reachability": sections["reachability_map.json"]["data"],
        "callable_surface": sections["callable_surface.json"]["data"],
        "state_mutation_map": sections["state_mutation_map.json"]["data"],
        "defense_map": sections["defense_map.json"]["data"],
        "invariant_analysis": sections["invariant_analysis.json"]["data"],
        "exploit_sequences": (sections["sequence_candidates.json"]["data"] or {}).get("sequences", []),
        "negative_tests": sections["negative_tests.json"]["data"],
        "scorecard": scorecard or None,
        "promotion_decision": promo or None,
        "poc_ready": poc_ready,
        "report_ready": report_ready,
        "notes_md": sections["notes.md"]["data"],
        "verdict_md": sections["verdict.md"]["data"],
        "evidence_timeline": timeline,
        "missing_artifacts": missing_artifacts,
        "hard_blockers": hard_blockers,
        "next_action": _NEXT_ACTION.get(outcome) or _NEXT_ACTION.get(lifecycle_state, "continue investigation"),
        "sections": {a: {"status": sections[a]["status"]} for a in ARTIFACTS},
        "raw": {a: sections[a]["data"] for a in _JSON_ARTIFACTS if sections[a]["data"] is not None},
    }


def status_group(lifecycle_state: Optional[str], outcome: Optional[str]) -> str:
    s = outcome or lifecycle_state or "RAW_CANDIDATE"
    if s in ("KILLED",):
        return "KILLED"
    if s in ("REPORT_READY",):
        return "REPORT_READY"
    if s in ("POC_READY",):
        return "POC_READY"
    if s in ("VALIDATION_READY", "NEGATIVE_TESTED"):
        return "VALIDATION_READY"
    if s in ("PARTIAL",):
        return "PARTIAL"
    if s in ("CONTEXT_MAPPED", "DEFENSE_MAPPED", "INVARIANT_ANALYZED", "SEQUENCE_CANDIDATE",
             "RESOLVED_SOURCE", "REACHABLE"):
        return "CONTEXT_MAPPED"
    return "RAW/NEEDS_CONTEXT"


def _rw_slug(subject: str) -> str:
    s = "".join(c.lower() if c.isalnum() else "-" for c in (subject or "target"))
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "target"


def real_world_candidate_rows() -> List[Dict[str, Any]]:
    """The PoC-proven candidate findings from the real-world hunt log, in the _row_from_detail row shape.

    These are honest, UNCONFIRMED, UNSUBMITTED candidates (flagged for human verification): POC_READY means a
    local PoC exists, NOT a severity/submission verdict. Read-only; never fabricates an outcome."""
    data = _read_json(REAL_RESULTS_PATH)
    rows: List[Dict[str, Any]] = []
    if not isinstance(data, dict):
        return rows
    for i, cf in enumerate(data.get("candidate_findings") or []):
        if not isinstance(cf, dict):
            continue
        subject = cf.get("target") or f"candidate-{i}"
        cid = f"real:{_rw_slug(subject)}:{i}"
        poc_path = cf.get("poc_path")
        rows.append({
            "candidate_id": cid,
            "candidate_id_short": (cid[:34] + "…") if len(cid) > 35 else cid,
            "audit_id": subject,
            "detector": "real_world_hunt",
            "candidate_surface": cf.get("title"),
            "source_location": poc_path,
            "lifecycle_state": "POC_READY",
            "outcome": "PoC-proven candidate",
            "status_group": "POC_READY",
            "confidence": {},
            "hard_blockers_count": 0,
            "missing_artifacts_count": 0,
            "latest_promotion_decision": None,
            "poc_lock": True,
            "report_lock": False,
            "illustrative": False,
        })
    return rows


def list_candidates(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Every candidate folder + every frozen-corpus bundle without a folder (as RAW_CANDIDATE), plus the
    real-world hunt log's PoC-proven candidate findings (default root only)."""
    root = root or candidates_root()
    rows: List[Dict[str, Any]] = []
    seen = set()

    _is_default_root = root == candidates_root()
    if root.is_dir():
        for audit_dir in sorted(root.glob("*")):
            if not audit_dir.is_dir():
                continue
            # On the live default view, hide leftover eval/synthetic audit folders (files stay on disk).
            if _is_default_root and audit_dir.name in _EVAL_AUDIT_IDS:
                continue
            for cand in sorted(audit_dir.glob("*")):
                if not cand.is_dir():
                    continue
                cid = _candidate_id_of_folder(cand)
                if not cid:
                    continue
                seen.add(cid)
                rows.append(_row_from_detail(load_candidate_detail(cid, root)))

    for cid, b in _corpus_bundles().items():
        if cid in seen:
            continue
        rows.append(_row_from_detail(load_candidate_detail(cid, root)))

    # (real-world) Append PoC-proven candidates from the honest hunt log — only on the default candidates root
    # (an explicit/tmp root means a test fixture, which must stay unaffected).
    if root == candidates_root():
        for r in real_world_candidate_rows():
            if r["candidate_id"] not in seen:
                seen.add(r["candidate_id"])
                rows.append(r)

    rows.sort(key=lambda r: (r["status_group"], r["candidate_id"]))
    return rows


def _candidate_id_of_folder(cand: Path) -> Optional[str]:
    for f in ("candidate_manifest.json", "raw_candidate.json"):
        d = _read_json(cand / f)
        if isinstance(d, dict) and d.get("candidate_id"):
            return d["candidate_id"]
    return None


def _row_from_detail(d: Dict[str, Any]) -> Dict[str, Any]:
    promo = d.get("promotion_decision") or {}
    cid = d["candidate_id"]
    return {
        "candidate_id": cid,
        "candidate_id_short": (cid[:34] + "…") if len(cid) > 35 else cid,
        "audit_id": d["audit_id"],
        "detector": d["detector"],
        "candidate_surface": d["candidate_surface"],
        "source_location": (f'{d["source"]["file"]}:{d["source"]["line"]}'
                            if d["source"].get("file") else None),
        "lifecycle_state": d["lifecycle_state"],
        "outcome": d["outcome"],
        "status_group": d["status_group"],
        "confidence": d["confidence"],
        "hard_blockers_count": len(d["hard_blockers"]),
        "missing_artifacts_count": len(d["missing_artifacts"]),
        "latest_promotion_decision": (f'{promo.get("from_state")}→{promo.get("to_state")}' if promo else None),
        "poc_lock": d["poc_ready"]["exists"],
        "report_lock": d["report_ready"]["exists"],
        "illustrative": d["illustrative"],
    }
