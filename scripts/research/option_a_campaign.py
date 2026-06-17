"""option_a_campaign — minimal, research-only conversion ledger for the Option-A candidate campaign.

Records OUTCOMES ONLY, one row per Option-A candidate, so we can measure what converts / downgrades / why
across the campaign. This ledger is **NOT** a source of truth for severity, routing, or submission — the
value-provenance sidecar (`output_research/value_provenance_eval/runtime_status.jsonl`) remains the canonical
runtime-row source. This module only appends validated rows and prints summary counts.

INVARIANTS (mirrors the other research tools): un-wired (no run_pipeline/agent_policy/routing reference);
reads/writes only `output_research/`; every row is forced `research_only=true`, `routing_allowed=false`,
`submission_ready=false`; fail-open (never raises into a caller). No dashboard wiring, no model scoring, no
auto-selection, no writeback to existing rows.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER = ROOT / "output_research/option_a_campaign/ledger.jsonl"
# canonical runtime-evidence source (read-only cross-check for the fabrication invariant)
SIDECAR = ROOT / "output_research/value_provenance_eval/runtime_status.jsonl"
# Protocol vNext Step 5 — append-only prediction log (logged BEFORE investigation)
PRED_LOG = ROOT / "output_research/option_a_campaign/prediction_log.jsonl"

# outcome-only fields (no severity/routing/submission authority)
FIELDS = [
    "candidate_id", "phase", "audit", "architecture", "mechanism_class", "surface_function",
    "deploy_complexity", "severity_ceiling_estimate", "selection_reason", "runtime_status",
    "conversion_outcome", "severity_recommendation", "reachability_verdict", "primary_blocker",
    "duplicate_status", "novelty_status", "why",
    # P164 (named-gate rejection recording): explicit refutation provenance for new records.
    # Old rows lack these (-> None) and are classified read-only by _derive_rejection().
    "rejection_type", "first_failed_gate",
    # P166 (Protocol vNext Step 6 — campaign learning): additive; old rows -> None, NOT backfilled.
    "attacker_recipient_status", "profit_source", "permission_model", "harness_built", "predicted_outcome",
    # P167 (candidate-generation hygiene): provenance of the signal that produced the candidate.
    "candidate_signal_source",
    # P169 (multi-family sweep): which of the 15 bug families the candidate was selected under.
    "bug_family",
]

# Protocol vNext Step 5 — the only outcomes a prediction may name
PREDICTION_OUTCOMES = {
    "runtime_confirmed", "runtime_refuted", "reportable_candidate_needs_human_review", "static_false_positive",
}

# ----------------------------------------------------------------- P167 candidate-generation hygiene
# A candidate's signal must originate in protocol source — not vendored libs, tests, mocks, or build output.
SIGNAL_SOURCES = {"protocol_src", "protocol_test", "vendored_lib", "mock", "generated"}
_VENDORED_DIRS = {"lib", "vendor", "node_modules", "dependencies", "deps"}
_MOCK_DIRS = {"mock", "mocks"}
_TEST_DIRS = {"test", "tests"}
_GENERATED_DIRS = {"out", "cache", "build", "dist", "artifacts", "examples", "scripts", ".git", "broadcast"}


def classify_signal_source(path: str) -> str:
    """Classify where a candidate-generation signal came from, by path. protocol_src is the only
    quality input; everything else is excluded by the hygiene gate (vendored libs, tests, mocks, build out)."""
    parts = {p.lower() for p in Path(str(path)).parts}
    if parts & _VENDORED_DIRS:
        return "vendored_lib"
    if parts & _MOCK_DIRS:
        return "mock"
    if parts & _TEST_DIRS:
        return "protocol_test"
    if parts & _GENERATED_DIRS:
        return "generated"
    # a *.t.sol / *.s.sol Foundry test/script by filename even outside a test/ dir
    name = Path(str(path)).name.lower()
    if name.endswith((".t.sol", ".s.sol")):
        return "protocol_test"
    return "protocol_src"


def scan_signals(corpus_root: str, pattern: str, include_nonprotocol: bool = False) -> List[Dict[str, Any]]:
    """Hygiene-filtered candidate-signal scan: walk *.sol under corpus_root, regex-match `pattern`, classify
    each hit's provenance, and (by default) return ONLY protocol_src hits. Read-only, fail-open."""
    import re as _re
    try:
        rx = _re.compile(pattern)
    except Exception:  # noqa: BLE001
        return []
    out: List[Dict[str, Any]] = []
    root = Path(corpus_root)
    if not root.exists():
        return out
    for f in root.rglob("*.sol"):
        src_class = classify_signal_source(str(f))
        if src_class != "protocol_src" and not include_nonprotocol:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                out.append({"path": str(f), "line": i, "match": line.strip()[:160],
                            "signal_source": src_class})
    return out

# outcomes that ASSERT a positive (must be backed by harness/sidecar evidence — fabrication invariant)
_POSITIVE_OUTCOMES = {"runtime_confirmed", "reportable_candidate_needs_human_review"}


def _sidecar_runtime_confirmed_ids() -> set:
    """Read-only: candidate ids the canonical sidecar records as runtime_confirmed."""
    ids: set = set()
    if not SIDECAR.exists():
        return ids
    for line in SIDECAR.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if r.get("runtime_status") == "runtime_confirmed":
            ids.add(r.get("item_id") or r.get("bug_id"))
    return ids


def _is_positive(row: Dict[str, Any]) -> bool:
    return (row.get("conversion_outcome") in _POSITIVE_OUTCOMES
            or row.get("runtime_status") == "runtime_confirmed")


def _has_harness_evidence(row: Dict[str, Any], confirmed_ids: set) -> bool:
    if row.get("harness_path") or row.get("real_contract_deployed") is True:
        return True
    if "real contract" in str(row.get("deploy_complexity") or "").lower():
        return True
    return row.get("candidate_id") in confirmed_ids


def _is_fabricated(row: Dict[str, Any], confirmed_ids: set) -> bool:
    """A positive claim with no harness evidence AND no canonical sidecar confirmation."""
    return _is_positive(row) and not _has_harness_evidence(row, confirmed_ids)


def _derive_rejection(row: Dict[str, Any]) -> str:
    """Classify a row's refutation provenance read-only (prefers the explicit field on new rows)."""
    explicit = row.get("rejection_type")
    if explicit:
        return explicit
    rt = row.get("runtime_status")
    if rt == "runtime_refuted":
        return "runtime_refuted"
    outcome = str(row.get("conversion_outcome") or "").lower()
    is_refuted = ("refuted" in outcome) or ("static_false_positive" in outcome)
    if rt == "not_run" and is_refuted:
        if "gate_refused" in str(row.get("deploy_complexity") or "").lower():
            return "gate_refuted"
        return "source_refuted"
    return "none"


# ----------------------------------------------------------------- Protocol vNext Step 5: prediction logging
def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:  # noqa: BLE001
            continue
    return rows


def _read_predictions() -> List[Dict[str, Any]]:
    return _read_jsonl(PRED_LOG)


def log_prediction(candidate_id: str, predicted_outcome: str, rationale: str) -> Dict[str, Any]:
    """Append a pre-investigation prediction (Step 5). Logged BEFORE any harness/outcome. Append-only."""
    if predicted_outcome not in PREDICTION_OUTCOMES:
        raise ValueError(f"invalid predicted_outcome: {predicted_outcome} (allowed: {sorted(PREDICTION_OUTCOMES)})")
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidate_id": candidate_id,
        "predicted_outcome": predicted_outcome,
        "rationale": rationale or "",
        "research_only": True, "routing_allowed": False,
    }
    PRED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with PRED_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


_REPORTABLE = "reportable_candidate_needs_human_review"


def _outcome_class(outcome: str) -> str:
    """Collapse reportable aliases so predicted vs actual compare on the same class."""
    o = str(outcome or "")
    return _REPORTABLE if o in (_REPORTABLE, "reportable") else o


def calibration() -> Dict[str, Any]:
    """Join pre-investigation predictions with recorded ledger outcomes (Step 5). Read-only."""
    preds = {}  # last prediction per candidate wins
    for p in _read_predictions():
        cid = p.get("candidate_id")
        if cid:
            preds[cid] = p.get("predicted_outcome")
    actuals = {r.get("candidate_id"): r.get("conversion_outcome") for r in _read()}
    resolved = 0
    correct = 0
    by_predicted: Dict[str, Dict[str, int]] = {}
    unresolved: List[str] = []
    for cid, predicted in preds.items():
        bucket = by_predicted.setdefault(predicted, {"resolved": 0, "correct": 0})
        if cid in actuals:
            resolved += 1
            bucket["resolved"] += 1
            if _outcome_class(actuals[cid]) == _outcome_class(predicted):
                correct += 1
                bucket["correct"] += 1
        else:
            unresolved.append(cid)
    return {
        "predictions": len(preds),
        "resolved": resolved,
        "correct": correct,
        "accuracy": f"{correct}/{resolved}" if resolved else "0/0",
        "by_predicted": by_predicted,
        "unresolved": unresolved,
        "research_only": True, "routing_allowed": False, "is_gate": False,
    }


def _read() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not LEDGER.exists():
        return rows
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:  # noqa: BLE001
            continue
    return rows


def record(row: Dict[str, Any]) -> Dict[str, Any]:
    """Append one validated, flag-forced row. Idempotent on candidate_id (skips if already present).

    Fabrication invariant (hard rule): a row asserting a positive outcome (runtime_confirmed /
    reportable_candidate) MUST carry harness evidence (harness_path / real_contract_deployed /
    'real contract' in deploy_complexity) OR be confirmed by the canonical runtime sidecar. A positive
    claim without evidence is fabrication and is REJECTED (ValueError) — it is never written.
    """
    out = {k: row.get(k) for k in FIELDS}
    # carry harness-evidence fields through if the caller supplied them (used by the invariant + scorecard)
    for k in ("harness_path", "real_contract_deployed"):
        if k in row:
            out[k] = row[k]
    # idempotency first — never re-evaluate or rewrite an already-recorded candidate
    existing = _read()
    if any(r.get("candidate_id") == out["candidate_id"] for r in existing):
        return {"skipped_existing": out["candidate_id"]}
    # P167 candidate-generation hygiene — a non-protocol_src signal (vendored lib / test / mock / build) is
    # junk input and must not become a candidate, unless explicitly flagged research_override (e.g. to record
    # a documented-noise lesson like H10). A None/unset signal_source is legacy and does not trip the gate.
    css = out.get("candidate_signal_source")
    if css is not None and css != "protocol_src" and not row.get("research_override"):
        raise ValueError(
            f"candidate-generation hygiene: signal_source '{css}' is not protocol_src; vendored/test/mock/"
            f"generated signals are excluded — pass research_override=true to record a documented-noise lesson")
    # fabrication invariant (hard rule) — a positive claim with no evidence is never written
    if _is_fabricated(out, _sidecar_runtime_confirmed_ids()):
        raise ValueError(
            f"fabricated positive rejected: '{out.get('candidate_id')}' claims "
            f"{out.get('conversion_outcome') or out.get('runtime_status')} but has no harness evidence "
            f"and is not runtime_confirmed in the canonical sidecar")
    # forced research flags — this ledger can never assert routing/severity/submission authority
    out["research_only"] = True
    out["routing_allowed"] = False
    out["submission_ready"] = False
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(out) + "\n")
    return out


def summary() -> Dict[str, Any]:
    rows = _read()
    def _count(key: str) -> Dict[str, int]:
        c: Dict[str, int] = {}
        for r in rows:
            c[str(r.get(key))] = c.get(str(r.get(key)), 0) + 1
        return c
    # honest conversion funnel across the campaign
    runtime_confirmed = sum(1 for r in rows if r.get("runtime_status") == "runtime_confirmed")
    reportable = sum(1 for r in rows if r.get("conversion_outcome") == "reportable_candidate_needs_human_review")
    return {
        "candidates": len(rows),
        "by_conversion_outcome": _count("conversion_outcome"),
        "by_severity_recommendation": _count("severity_recommendation"),
        "by_primary_blocker": _count("primary_blocker"),
        "funnel": {
            "candidates": len(rows),
            "runtime_confirmed": runtime_confirmed,
            "reportable_candidate_needs_human_review": reportable,
            "submission_ready": 0,  # this ledger never marks anything submittable
        },
        "research_only": True, "routing_allowed": False, "is_gate": False, "routes_in_production": False,
    }


def _frac(k: int, n: int) -> str:
    """Report rates as 'k/n' strings, never a tuned percentage (small-n honesty — see P163)."""
    return f"{k}/{n}"


def scorecard() -> Dict[str, Any]:
    """Campaign scorecard — the P163 'metrics that matter more than raw finding count'. Read-only;
    derives everything from the ledger (+ a read-only sidecar cross-check) and never marks anything
    submittable. Rates are 'k/n' strings; fabrication_rate must be 0."""
    rows = _read()
    n = len(rows)
    confirmed_ids = _sidecar_runtime_confirmed_ids()
    runtime_confirmed = sum(1 for r in rows if r.get("runtime_status") == "runtime_confirmed")
    reportable_rows = [r for r in rows if r.get("conversion_outcome") == "reportable_candidate_needs_human_review"]
    reportable = len(reportable_rows)
    rej = [_derive_rejection(r) for r in rows]
    source_refutations = rej.count("source_refuted")
    gate_refutations = rej.count("gate_refuted")
    runtime_refutations = rej.count("runtime_refuted")
    harnesses_built = sum(1 for r in rows if _has_harness_evidence(r, confirmed_ids))
    # a harness was AVOIDED when a candidate was refuted (source/gate) without building one
    harnesses_avoided = sum(1 for r, t in zip(rows, rej)
                            if t in ("source_refuted", "gate_refuted") and not _has_harness_evidence(r, confirmed_ids))
    fabricated = sum(1 for r in rows if _is_fabricated(r, confirmed_ids))
    return {
        "n": n,
        "candidates": n,
        "runtime_confirmed": runtime_confirmed,
        "reportable": reportable,
        "submission_ready": 0,  # this ledger never marks anything submittable
        "harnesses_built": harnesses_built,
        "harnesses_avoided": harnesses_avoided,
        "source_refutations": source_refutations,
        "gate_refutations": gate_refutations,
        "runtime_refutations": runtime_refutations,
        "conversion_rate": _frac(runtime_confirmed, n) if n else "0/0",
        "reportable_rate": _frac(reportable, n) if n else "0/0",
        "precision_proxy": _frac(reportable, harnesses_built) if harnesses_built else "0/0",
        # Protocol vNext primary success metric: reportables per harness built
        "reportables_per_harness": _frac(reportable, harnesses_built) if harnesses_built else "0/0",
        "prediction_accuracy": calibration()["accuracy"],
        "fabrication_rate": _frac(fabricated, n) if n else "0/0",
        "fabricated_count": fabricated,
        "open_reportables": [r.get("candidate_id") for r in reportable_rows],
        "caveat": f"point estimates over n={n} campaign candidates; descriptive, NOT a tuned operating point",
        "research_only": True, "routing_allowed": False, "is_gate": False, "routes_in_production": False,
    }


def checkpoint() -> Dict[str, Any]:
    """Lightweight, ADVISORY pre-campaign checkpoint (P163 §10 P1). Surfaces the scorecard + open
    reportables; never hard-blocks (P163 explicitly rejected a hard pause)."""
    sc = scorecard()
    return {
        "scorecard": sc,
        "open_reportables": sc["open_reportables"],
        "blocking": False,
        "message": ("Before opening a new campaign: review the latest retrospective (P163) and decide "
                    "submit / hold / continue for each open reportable. Advisory only — not a hard pause."),
        "research_only": True, "routing_allowed": False, "is_gate": False,
    }


def main(argv: List[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "summary"
    if cmd == "summary":
        print(json.dumps(summary(), indent=2))
    elif cmd == "scorecard":
        print(json.dumps(scorecard(), indent=2))
    elif cmd == "checkpoint":
        print(json.dumps(checkpoint(), indent=2))
    elif cmd == "calibration":
        print(json.dumps(calibration(), indent=2))
    elif cmd == "predict":
        p = json.loads(sys.stdin.read())
        print(json.dumps(log_prediction(p["candidate_id"], p["predicted_outcome"], p.get("rationale", "")), indent=2))
    elif cmd == "scan":
        p = json.loads(sys.stdin.read())
        print(json.dumps(scan_signals(p["corpus_root"], p["pattern"], p.get("include_nonprotocol", False)), indent=2))
    elif cmd == "record":
        row = json.loads(sys.stdin.read())
        print(json.dumps(record(row), indent=2))
    else:
        print("usage: option_a_campaign.py [summary|scorecard|checkpoint|calibration|predict|scan|record]")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
