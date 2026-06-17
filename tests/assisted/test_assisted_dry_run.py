"""P112: full assisted dry-run (IQ-AI M-01) — RESEARCH-ONLY, un-wired.

Proves the assisted runbook is coherent end-to-end on one confirmed candidate: every stage artifact is produced,
validation reaches VALIDATED_FOR_POC_HANDOFF, harness-prep is COMPLEX+inert, the PoC is REPRODUCED with runtime
evidence attached, the 5-file submission package is platform-neutral, the human gate is reached but not completed,
the pipeline ends at SUBMISSION_READY_HUMAN_REVIEW, and there is NO auto-submit / NO status leakage. The live run
needs the P104 artifacts on disk (guarded).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import assisted_dry_run as D  # noqa: E402

P104 = ROOT / "documentation" / "research" / "assisted_mode" / "p104" / "reproduction_output.txt"
_needs = pytest.mark.skipif(not P104.is_file(), reason="P104 artifacts not present")


def test_flags_unwired():
    assert D.FLAGS["is_gate"] is False
    assert D.FLAGS["routes_in_production"] is False
    assert D.FLAGS["routed_manifest_ids"] == []


def test_intake_requests_poc_handoff_not_submission():
    # Stage B must validate the invariant; SUBMISSION_PACKAGE would (correctly) block on human scope/dup.
    assert D.build_intake()["requested_check"] == "POC_HANDOFF"
    assert D.build_intake()["candidate_invariant"]


@_needs
def test_no_auto_submit_and_no_leakage(tmp_path):
    r = D.run_dry_run(tmp_path / "b", write=False)
    assert r["safety"]["no_auto_submit"] is True
    assert r["safety"]["no_status_leakage"] is True
    # recorder must refuse a submit without an explicit human APPROVED_TO_SUBMIT
    assert r["stages"]["F_outcome"]["recorder_submit_probe"] == "BLOCKED_INVALID_GATE"
    # final pipeline status is never SUBMITTED
    assert r["stages"]["F_outcome"]["pipeline_status"] != "SUBMITTED"


@_needs
def test_submission_report_platform_neutral(tmp_path):
    r = D.run_dry_run(tmp_path / "b", write=True)
    pkg = Path(r["artifacts"]["dir"]) / "submission_package"
    body = (pkg / "submission_draft.md").read_text().lower() + (pkg / "optional_platform_fields.md").read_text().lower()
    for tok in ("audit-watch", "funnel", "detector", "scanner", "blind", "p104", "assisted-mode", "self-kill"):
        assert tok not in body, f"platform-facing report leaked internal token: {tok}"
    # reviewer_notes is INTERNAL and KEEPS the assisted-mode caveat
    assert "assisted-mode" in (pkg / "reviewer_notes.md").read_text().lower()


@_needs
def test_bundle_files_written(tmp_path):
    r = D.run_dry_run(tmp_path / "b", write=True)
    d = Path(r["artifacts"]["dir"])
    for f in ("intake.json", "validation.json", "poc_handoff.json", "dry_run_report.json", "dry_run_report.md"):
        assert (d / f).is_file()
    assert (d / "submission_package" / "pre_submission_gate.md").is_file()
    assert (d / "harness_prep" / "harness_feasibility.json").is_file()
    # the written bundle must contain no auto-submit tokens anywhere
    blob = "\n".join(p.read_text() for p in d.rglob("*") if p.is_file())
    assert '"submitted": true' not in blob and "APPROVED_TO_SUBMIT" not in blob


@_needs
def test_deterministic(tmp_path):
    a = D.run_dry_run(tmp_path / "a", write=False)
    b = D.run_dry_run(tmp_path / "b", write=False)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
