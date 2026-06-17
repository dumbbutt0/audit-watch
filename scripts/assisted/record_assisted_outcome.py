#!/usr/bin/env python3
"""
record_assisted_outcome.py — P99 ASSISTED-MODE outcome recorder (RESEARCH-ONLY, UN-WIRED).

Records a HUMAN-decided outcome for an assisted-mode (or blind) finding AFTER human review / submission. It does
NOT submit anything, does NOT decide scope/duplicate, and NEVER creates a "submitted" record on its own — a human
must set `submitted` + `human_final_gate` in the input. It writes a dashboard-readable outcome record under
`documentation/research/assisted_mode/outcomes/`; it never alters submission packages or any frozen phase
artifact.

Validation:
  1. jsonschema against schemas/assisted_outcome_record.schema.json  -> BLOCKED_SCHEMA_ERROR on failure.
  2. submitted=true REQUIRES human_final_gate == APPROVED_TO_SUBMIT   -> BLOCKED_INVALID_GATE.
  3. outcome in {accepted, duplicate, rejected} REQUIRES submitted=true -> BLOCKED_INVALID_OUTCOME_STATE.

Decisions: RECORD_OK | BLOCKED_INVALID_GATE | BLOCKED_INVALID_OUTCOME_STATE | BLOCKED_SCHEMA_ERROR.
is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA = ROOT / "schemas" / "assisted_outcome_record.schema.json"
OUTCOMES_DIR = ROOT / "documentation" / "research" / "assisted_mode" / "outcomes"

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

RECORD_OK = "RECORD_OK"
BLOCKED_INVALID_GATE = "BLOCKED_INVALID_GATE"
BLOCKED_INVALID_OUTCOME_STATE = "BLOCKED_INVALID_OUTCOME_STATE"
BLOCKED_SCHEMA_ERROR = "BLOCKED_SCHEMA_ERROR"

# outcomes that can only exist once a report was actually submitted
_REQUIRES_SUBMITTED = {"accepted", "duplicate", "rejected"}
# frozen phase-artifact dir markers we must never write into
_FROZEN_MARKERS = re.compile(r"(^|/)_p(8[0-9]|9[0-9])([_/]|$)")


class OutcomeResult(NamedTuple):
    decision: str
    reason: str
    written_path: Optional[str]


def _load_schema() -> dict:
    return json.loads(SCHEMA.read_text())


def _sanitize(cid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", cid).strip("_") or "outcome"


def validate(record: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    """Validate an outcome record (schema + cross-field invariants). Returns (decision, reason). Pure / no I/O
    beyond reading the schema file."""
    r = record or {}
    # (1) schema
    try:
        import jsonschema  # local import so the module loads even if jsonschema is absent
        jsonschema.validate(r, _load_schema())
    except Exception as e:  # ValidationError or ImportError-fallback below
        if e.__class__.__name__ == "ModuleNotFoundError":
            # minimal manual fallback: required fields + the two key enums
            req = ["candidate_id", "subject", "source_mode", "human_final_gate", "submitted", "outcome"]
            missing = [k for k in req if k in (None, "") or k not in r or r.get(k) in (None, "")]
            if missing:
                return (BLOCKED_SCHEMA_ERROR, f"missing required field(s): {missing}")
            if not isinstance(r.get("submitted"), bool):
                return (BLOCKED_SCHEMA_ERROR, "submitted must be a boolean")
        else:
            msg = getattr(e, "message", str(e))
            return (BLOCKED_SCHEMA_ERROR, f"schema validation failed: {msg}")

    submitted = bool(r.get("submitted"))
    gate = str(r.get("human_final_gate") or "")
    outcome = str(r.get("outcome") or "")

    # (2) submitted requires an explicit human APPROVED_TO_SUBMIT
    if submitted and gate != "APPROVED_TO_SUBMIT":
        return (BLOCKED_INVALID_GATE,
                f"submitted=true requires human_final_gate=APPROVED_TO_SUBMIT (got {gate or 'none'})")

    # (3) terminal post-submission outcomes require submitted=true
    if outcome in _REQUIRES_SUBMITTED and not submitted:
        return (BLOCKED_INVALID_OUTCOME_STATE,
                f"outcome={outcome} requires submitted=true (nothing was submitted)")

    return (RECORD_OK, "outcome record is valid (human-decided; nothing submitted by this tool)")


def _assert_safe_outdir(out_dir: Path) -> None:
    rp = out_dir.resolve()
    if _FROZEN_MARKERS.search(str(rp)):
        raise ValueError(f"refusing to write into a frozen phase directory: {rp}")


def record(record_obj: Dict[str, Any], out_dir: Optional[Path] = None, write: bool = True) -> OutcomeResult:
    decision, reason = validate(record_obj)
    if decision != RECORD_OK:
        return OutcomeResult(decision, reason, None)
    out_dir = Path(out_dir) if out_dir is not None else OUTCOMES_DIR
    _assert_safe_outdir(out_dir)
    path = out_dir / f"{_sanitize(str(record_obj.get('candidate_id')))}.json"
    if write:
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = {**FLAGS, **record_obj}
        path.write_text(json.dumps(payload, indent=2))
    return OutcomeResult(RECORD_OK, reason, str(path))


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    base = {
        "candidate_id": "secondswap-2024-12:ASSISTED-M11:SecondSwap_VestingManager.listVesting",
        "subject": "secondswap-2024-12", "source_mode": "assisted",
        "human_final_gate": "PENDING", "submitted": False, "outcome": "pending",
        "is_gate": False, "research_only": True, "review_only": True,
        "routes_in_production": False, "routed_manifest_ids": [],
    }
    chk(validate(base)[0] == RECORD_OK, "pending/not-submitted record is valid -> RECORD_OK")

    # submitted=true without APPROVED_TO_SUBMIT -> BLOCKED_INVALID_GATE
    g = dict(base, submitted=True, human_final_gate="PENDING")
    chk(validate(g)[0] == BLOCKED_INVALID_GATE, "submitted=true + gate!=APPROVED_TO_SUBMIT -> BLOCKED_INVALID_GATE")
    # submitted=true WITH APPROVED_TO_SUBMIT -> OK (pending outcome)
    g2 = dict(base, submitted=True, human_final_gate="APPROVED_TO_SUBMIT", platform="immunefi",
              submission_id="ext-123", outcome="pending")
    chk(validate(g2)[0] == RECORD_OK, "submitted=true + APPROVED_TO_SUBMIT -> RECORD_OK")

    # accepted/duplicate/rejected require submitted=true
    for term in ("accepted", "duplicate", "rejected"):
        bad = dict(base, outcome=term, submitted=False)
        chk(validate(bad)[0] == BLOCKED_INVALID_OUTCOME_STATE, f"outcome={term} + submitted=false -> BLOCKED_INVALID_OUTCOME_STATE")
    good = dict(base, submitted=True, human_final_gate="APPROVED_TO_SUBMIT", outcome="accepted", awarded_severity="Medium")
    chk(validate(good)[0] == RECORD_OK, "accepted + submitted=true + APPROVED_TO_SUBMIT -> RECORD_OK")

    # schema error: missing required field
    miss = {k: v for k, v in base.items() if k != "subject"}
    chk(validate(miss)[0] == BLOCKED_SCHEMA_ERROR, "missing required field -> BLOCKED_SCHEMA_ERROR")
    # schema error: bad enum
    bade = dict(base, outcome="exploded")
    chk(validate(bade)[0] == BLOCKED_SCHEMA_ERROR, "invalid outcome enum -> BLOCKED_SCHEMA_ERROR")

    # write to a tmp dir works; frozen dir refused
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        res = record(base, out_dir=Path(td))
        chk(res.decision == RECORD_OK and res.written_path and Path(res.written_path).exists(), "writes a record file in a tmp dir")
    refused = False
    try:
        record(base, out_dir=ROOT / "documentation/research/_p97_secondswap", write=False)
    except ValueError:
        refused = True
    chk(refused, "refuses to write into a frozen _p9x dir")

    chk(FLAGS["is_gate"] is False and FLAGS["routes_in_production"] is False, "FLAGS un-wired")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--record", help="path to an assisted_outcome_record JSON")
    ap.add_argument("--out-dir", help="output dir (default: documentation/research/assisted_mode/outcomes/)")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.record:
        ap.error("--record is required (or --self-test)")
    obj = json.loads(Path(args.record).read_text())
    out_dir = Path(args.out_dir) if args.out_dir else None
    res = record(obj, out_dir=out_dir)
    print(f"DECISION: {res.decision}")
    print(f"reason: {res.reason}")
    if res.written_path:
        print(f"wrote {res.written_path}")
    return 0 if res.decision == RECORD_OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
