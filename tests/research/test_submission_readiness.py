"""Isolated tests for the human-owned submission-readiness overlay (research-only, append-only)."""

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import submission_readiness_review as srr  # noqa: E402
import finding_detail as fd  # noqa: E402

H5 = "runtime:H5-abracadabra-lockingrewards-boost"
H6 = "campaign:H6-pooltogether-prizevault-erc4626-rate-mismatch"
H4 = "runtime:H4-ecg-multivotes-accounting"

PASS_ANSWERS = {
    "mechanism_confirmed": "yes", "reachability_confirmed": "yes", "severity_bearing": "yes",
    "poc_complete": "yes", "impact_not_overclaimed": "yes", "severity_recommendation": "Low",
    "scope_caveats_reviewed": "yes", "novelty": "public_known_but_not_duplicate",
    "report_draft_exists": "yes", "mitigation_included": "yes", "assumptions_included": "yes",
    "notes": "accept Low baseline / Medium only under sustained keeper failure; zero-sum redistribution; "
             "public_known_but_not_duplicate; keeper-liveness bounds severity",
}


@pytest.fixture
def tmp_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(srr, "LEDGER", tmp_path / "submission_readiness.jsonl")
    return srr


def _md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest() if Path(p).exists() else None


def test_unknown_candidate_rejected(tmp_ledger):
    with pytest.raises(ValueError):
        tmp_ledger.record_review("runtime:DOES-NOT-EXIST", "alice", PASS_ANSWERS, "not_ready")


# --------------------------------------------------------------------------- P165 derived display status
def test_display_submission_status_mapping():
    assert srr.display_submission_status("ready_for_submission_package") == "SUBMISSION_READY"
    assert srr.display_submission_status("not_reviewed") == "NOT_REVIEWED"
    assert srr.display_submission_status("needs_more_context") == "REVIEW_REQUIRED"
    assert srr.display_submission_status("not_ready") == "NOT_READY"
    assert srr.display_submission_status("blocked_by_scope") == "BLOCKED"
    assert srr.display_submission_status("blocked_by_duplicate") == "BLOCKED"


def test_effective_submission_ready_only_for_ready_state():
    assert srr.effective_submission_ready("ready_for_submission_package") is True
    for s in ("not_reviewed", "not_ready", "needs_more_context", "blocked_by_scope"):
        assert srr.effective_submission_ready(s) is False


def test_unreviewed_overlay_is_not_ready(tmp_ledger):
    ov = tmp_ledger.detail_overlay(H6)  # no review recorded for H6 (empty tmp ledger)
    assert ov["readiness_state"] == "not_reviewed"
    assert ov["submission_package_status"] == "NOT_REVIEWED"
    assert ov["effective_submission_ready"] is False
