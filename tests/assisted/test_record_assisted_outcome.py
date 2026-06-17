"""P99 tests for the assisted-mode outcome recorder (RESEARCH-ONLY, un-wired).

Proves the reject-first invariants: submitted=true requires APPROVED_TO_SUBMIT; accepted/duplicate/rejected
require submitted=true; schema errors are caught; the recorder writes only when valid and never mutates frozen
artifacts or submission packages; no auto-submission path exists.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import record_assisted_outcome as R  # noqa: E402


def _base(**over):
    rec = {
        "candidate_id": "secondswap-2024-12:ASSISTED-M11:SecondSwap_VestingManager.listVesting",
        "subject": "secondswap-2024-12",
        "source_mode": "assisted",
        "human_final_gate": "PENDING",
        "submitted": False,
        "outcome": "pending",
        "is_gate": False, "research_only": True, "review_only": True,
        "routes_in_production": False, "routed_manifest_ids": [],
    }
    rec.update(over)
    return rec


def test_self_test_passes():
    assert R._self_test() == 0


def test_pending_record_ok():
    assert R.validate(_base())[0] == R.RECORD_OK


def test_submitted_without_approved_gate_blocked():
    assert R.validate(_base(submitted=True, human_final_gate="PENDING"))[0] == R.BLOCKED_INVALID_GATE
    assert R.validate(_base(submitted=True, human_final_gate="DO_NOT_SUBMIT_SCOPE"))[0] == R.BLOCKED_INVALID_GATE


def test_submitted_with_approved_gate_ok():
    assert R.validate(_base(submitted=True, human_final_gate="APPROVED_TO_SUBMIT"))[0] == R.RECORD_OK


@pytest.mark.parametrize("term", ["accepted", "duplicate", "rejected"])
def test_terminal_outcome_requires_submitted(term):
    assert R.validate(_base(outcome=term, submitted=False))[0] == R.BLOCKED_INVALID_OUTCOME_STATE


def test_terminal_outcome_with_submitted_ok():
    rec = _base(outcome="accepted", submitted=True, human_final_gate="APPROVED_TO_SUBMIT", awarded_severity="Medium")
    assert R.validate(rec)[0] == R.RECORD_OK


def test_schema_error_missing_field():
    rec = _base()
    del rec["subject"]
    assert R.validate(rec)[0] == R.BLOCKED_SCHEMA_ERROR


def test_schema_error_bad_enum():
    assert R.validate(_base(outcome="exploded"))[0] == R.BLOCKED_SCHEMA_ERROR
    assert R.validate(_base(human_final_gate="MAYBE"))[0] == R.BLOCKED_SCHEMA_ERROR


def test_recorder_writes_only_when_valid(tmp_path):
    ok = R.record(_base(), out_dir=tmp_path)
    assert ok.decision == R.RECORD_OK and ok.written_path and Path(ok.written_path).exists()
    # an invalid record is not written
    bad = R.record(_base(submitted=True, human_final_gate="PENDING"), out_dir=tmp_path)
    assert bad.decision == R.BLOCKED_INVALID_GATE and bad.written_path is None


def test_recorder_refuses_frozen_dir():
    with pytest.raises(ValueError):
        R.record(_base(), out_dir=ROOT / "documentation/research/_p97_secondswap", write=False)
    with pytest.raises(ValueError):
        R.record(_base(), out_dir=ROOT / "documentation/research/_p82_h01_claim_poc", write=False)


def test_recorder_does_not_touch_submission_package(tmp_path):
    pkg = ROOT / "documentation/research/assisted_mode/pilot_m11/submission_package"
    before = {p: p.stat().st_mtime_ns for p in pkg.rglob("*") if p.is_file()}
    R.record(_base(), out_dir=tmp_path)
    after = {p: p.stat().st_mtime_ns for p in pkg.rglob("*") if p.is_file()}
    assert before == after


def test_no_auto_submission_default():
    # the default record never sets submitted; a record cannot become submitted without an explicit human field.
    assert R.validate(_base())[0] == R.RECORD_OK
    assert _base()["submitted"] is False


def test_flags_unwired():
    assert R.FLAGS["is_gate"] is False
    assert R.FLAGS["routes_in_production"] is False
    assert R.FLAGS["routed_manifest_ids"] == []
