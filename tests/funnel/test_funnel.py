"""
Tests for the Blind-to-Reproducible Funnel pure-logic module (scripts/funnel.py).

Covers req-9: promotion gates, reject-first (REPRODUCED != SUBMITTED), NOT_RUN exclusion from
denominators, backward compatibility (missing PoC/submission fields), the seeded Vultisig 2024-06
H-01 record, and loader read-only-ness. Vultisig H-01 is used ONLY as a seeded example/fixture;
all gate logic is generic.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import funnel  # noqa: E402

SEED = ROOT / "documentation/research/funnel/funnel_records.json"


# ------------------------------------------------------------------- fixtures
def _clean_hit_record(**over):
    """A P81e-style CLEAN_HIT, safety-clean record (handoff-eligible)."""
    rec = {
        "record_id": "t:clean",
        "subject": "TestProto",
        "phase_discovered": "P-test",
        "finding_id": "X-01",
        "contract": "Vault",
        "function": "withdraw",
        "conversion": "CLEAN_HIT",
        "mechanism_correctness": "correct",
        "severity_gate": "passed",
        "adversarial_result": "PASS",
        "severity_fp": False,
        "safety": {"source_false": False, "unsupported_ready": False, "hard_fail": False},
    }
    rec.update(over)
    return rec


def _reproduced_record(**over):
    """A CLEAN_HIT that also has a complete REPRODUCED PoC."""
    rec = _clean_hit_record(record_id="t:repro")
    rec["poc"] = {
        "poc_status": "REPRODUCED",
        "poc_phase": "P-test",
        "test_file": "documentation/research/funnel/funnel_records.json",  # any existing repo file
        "test_command": "forge test --match-test testX -vv",
        "vulnerable_result": "fails as intended",
        "patched_result": "passes under patch",
        "unrelated_tests_result": "all other tests pass",
        "minimal_patch_validated": True,
        "source_chain_complete": True,
        "unsupported_claims_present": False,
        "remaining_blockers": [],
        "human_submission_ready": True,
    }
    rec.update(over)
    return rec


def _submission_ready_record():
    rec = _reproduced_record(record_id="t:subready")
    rec["submission"] = {
        "submission_status": "READY_FOR_HUMAN_REVIEW",
        "evidence_bundle_path": "documentation/research/funnel/funnel_records.json",
        "pre_submission_gate_path": "documentation/research/funnel/funnel_records.json",
        "duplicate_check_status": "CLEAR",
        "scope_check_status": "IN_SCOPE",
        "severity_check_status": "SUPPORTED",
        "final_human_gate": "PENDING",
    }
    return rec


# ----------------------------------------------------- req-9: handoff promotion
def test_clean_hit_safety_clean_promotes_to_poc_handoff():
    rec = _clean_hit_record()
    ok, reasons = funnel.can_promote_to_poc_handoff(rec)
    assert ok, reasons
    assert funnel.compute_pipeline_status(rec) in {"POC_HANDOFF_STARTED", "CONVERTED_CLEAN_HIT"}
    # With no PoC started yet but all handoff gates satisfied, status is POC_HANDOFF_STARTED.
    assert funnel.compute_pipeline_status(rec) == "POC_HANDOFF_STARTED"


def test_severity_fp_blocks_poc_handoff():
    rec = _clean_hit_record(severity_fp=True)
    ok, reasons = funnel.can_promote_to_poc_handoff(rec)
    assert not ok
    assert any("severity FP" in r for r in reasons)
    assert funnel.compute_pipeline_status(rec) != "POC_HANDOFF_STARTED"


def test_source_false_blocks_poc_handoff():
    rec = _clean_hit_record(safety={"source_false": True, "unsupported_ready": False, "hard_fail": False})
    ok, reasons = funnel.can_promote_to_poc_handoff(rec)
    assert not ok and any("SOURCE_FALSE" in r for r in reasons)


def test_unsupported_ready_blocks_poc_handoff():
    rec = _clean_hit_record(safety={"source_false": False, "unsupported_ready": True, "hard_fail": False})
    ok, reasons = funnel.can_promote_to_poc_handoff(rec)
    assert not ok and any("unsupported READY" in r for r in reasons)


def test_adjacent_conversion_does_not_promote_to_handoff():
    rec = _clean_hit_record(conversion="ADJACENT")
    ok, _ = funnel.can_promote_to_poc_handoff(rec)
    assert not ok


# -------------------------------------------------- req-9: reproduced promotion
def test_reproduced_record_promotes_to_poc_reproduced():
    rec = _reproduced_record()
    ok, reasons = funnel.can_promote_to_poc_reproduced(rec)
    assert ok, reasons
    assert funnel.compute_pipeline_status(rec) == "POC_REPRODUCED"


def test_reproduced_requires_executable_test():
    rec = _reproduced_record()
    rec["poc"]["test_file"] = None
    rec["poc"]["test_command"] = None
    ok, reasons = funnel.can_promote_to_poc_reproduced(rec)
    assert not ok and any("executable test" in r for r in reasons)


def test_reproduced_requires_complete_source_chain():
    rec = _reproduced_record()
    rec["poc"]["source_chain_complete"] = False
    ok, reasons = funnel.can_promote_to_poc_reproduced(rec)
    assert not ok and any("bug chain" in r for r in reasons)


def test_reproduced_blocked_if_patch_present_but_unvalidated():
    rec = _reproduced_record()
    rec["poc"]["minimal_patch_validated"] = False  # patched_result is present
    ok, reasons = funnel.can_promote_to_poc_reproduced(rec)
    assert not ok and any("patched variant" in r for r in reasons)


# --------------------------------------------- req-9 + req-8: reject-first / SUBMITTED
def test_reproduced_poc_does_not_auto_become_submitted():
    """A REPRODUCED PoC with submission NOT_STARTED stays POC_REPRODUCED, never SUBMITTED."""
    rec = _reproduced_record()  # default submission = NOT_STARTED
    assert funnel.compute_pipeline_status(rec) == "POC_REPRODUCED"
    assert funnel.submission_badge(rec) == "NOT_STARTED"
    ok, _ = funnel.can_promote_to_submission_ready(rec)
    assert not ok  # missing evidence/gate/severity-supported


def test_submitted_only_when_human_recorded():
    rec = _submission_ready_record()
    # Ready for review but the human has NOT recorded SUBMITTED yet.
    assert funnel.submission_badge(rec) == "READY_FOR_HUMAN_REVIEW"
    assert funnel.compute_pipeline_status(rec) == "SUBMISSION_READY_HUMAN_REVIEW"
    # Now a human records SUBMITTED.
    rec["submission"]["submission_status"] = "SUBMITTED"
    assert funnel.submission_badge(rec) == "SUBMITTED"
    # SUBMITTED is not a pipeline status — pipeline maxes at human-review.
    assert "SUBMITTED" not in funnel.PIPELINE_STATUS
    assert funnel.compute_pipeline_status(rec) == "SUBMISSION_READY_HUMAN_REVIEW"


# ------------------------------------------------ req-9: submission-ready gating
def test_submission_ready_when_all_checks_pass():
    rec = _submission_ready_record()
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert ok, reasons


def test_duplicate_confirmed_blocks_submission_ready():
    rec = _submission_ready_record()
    rec["submission"]["duplicate_check_status"] = "DUPLICATE_CONFIRMED"
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert not ok and any("duplicate confirmed" in r for r in reasons)


def test_out_of_scope_blocks_submission_ready():
    rec = _submission_ready_record()
    rec["submission"]["scope_check_status"] = "OUT_OF_SCOPE"
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert not ok and any("out of scope" in r for r in reasons)


def test_unsupported_severity_blocks_submission_ready():
    rec = _submission_ready_record()
    rec["submission"]["severity_check_status"] = "UNSUPPORTED"
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert not ok and any("severity check" in r for r in reasons)


def test_missing_evidence_bundle_blocks_submission_ready():
    rec = _submission_ready_record()
    rec["submission"]["evidence_bundle_path"] = None
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert not ok and any("evidence bundle" in r for r in reasons)


def test_missing_pre_submission_gate_blocks_submission_ready():
    rec = _submission_ready_record()
    rec["submission"]["pre_submission_gate_path"] = None
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert not ok and any("pre-submission gate" in r for r in reasons)


def test_not_reproduced_cannot_be_submission_ready():
    """Even with all submission paths present, a non-reproduced PoC cannot be submission-ready."""
    rec = _submission_ready_record()
    rec["poc"]["poc_status"] = "NOT_STARTED"
    ok, reasons = funnel.can_promote_to_submission_ready(rec)
    assert not ok and any("not POC_REPRODUCED" in r for r in reasons)


# ----------------------------------------------------- req-9: NOT_RUN exclusion
def test_not_run_excluded_from_denominators():
    recs = [_reproduced_record(), {"record_id": "t:notrun", "not_run": True, "conversion": "NONE"}]
    m = funnel.compute_funnel_metrics(recs)
    assert m["not_run"] == 1
    # denominator excludes NOT_RUN: only the reproduced record counts as a surfaced lead
    assert m["total_leads_surfaced"] == 1
    assert m["pocs_reproduced"] == 1
    assert funnel.compute_pipeline_status({"record_id": "z", "not_run": True}) == "NOT_RUN"


# ---------------------------------------------------- backward compatibility
def test_missing_poc_and_submission_default_to_not_started():
    rec = {"record_id": "bc", "subject": "X", "contract": "C", "function": "f"}
    norm = funnel.normalize_record(rec)
    assert norm["poc"]["poc_status"] == "NOT_STARTED"
    assert norm["submission"]["submission_status"] == "NOT_STARTED"
    # does not crash; resolves to a low pipeline stage
    assert funnel.compute_pipeline_status(rec) in funnel.PIPELINE_STATUS
    row = funnel.build_finding_row(rec)
    assert row["poc_status"] == "NOT_STARTED"
    assert row["submission_badge"] == "NOT_STARTED"


def test_invalid_enum_rejected():
    with pytest.raises(funnel.FunnelValidationError):
        funnel.normalize_record({"record_id": "x", "conversion": "BOGUS"})
    with pytest.raises(funnel.FunnelValidationError):
        funnel.normalize_record({"record_id": "x", "poc": {"poc_status": "BOGUS"}})


# ----------------------------------------------------- seeded Vultisig H-01 record
def test_seed_file_loads():
    assert SEED.is_file()
    payload = funnel.load_records(SEED)
    assert payload["record_count"] >= 1


def test_seeded_h01_reproduced_and_ready_for_human_review_not_submitted():
    """After P83 the H-01 package exists; the record is SUBMISSION_READY_HUMAN_REVIEW but NEVER SUBMITTED
    (reject-first): the SUBMITTED badge only appears when a human records it."""
    payload = funnel.load_records(SEED)
    h01 = next(r for r in payload["records"] if r["finding_id"] == "H-01")
    assert h01["subject"] == "Vultisig 2024-06"
    assert h01["contract_function"] == "ILOPool.claim"
    assert h01["poc_status"] == "REPRODUCED"
    assert h01["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW"
    assert h01["submission_badge"] == "READY_FOR_HUMAN_REVIEW"
    assert h01["submission_badge"] != "SUBMITTED"
    assert h01["test_command"] == "forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv"
    # ready gate passes ONLY because dupe/scope are PENDING (not negative).
    assert h01["gates"]["submission_ready"]["ok"] is True
    assert h01["submission"]["duplicate_check_status"] == "PENDING"
    assert h01["submission"]["scope_check_status"] == "PENDING"


def test_seeded_h01_blocks_if_human_check_is_negative():
    """The only thing keeping H-01 ready is that the human checks are not negative."""
    payload = funnel.load_records(SEED)
    raw = funnel._read_json(SEED)["findings"][0]
    for field, val in (("duplicate_check_status", "DUPLICATE_CONFIRMED"), ("scope_check_status", "OUT_OF_SCOPE")):
        r = dict(raw)
        r["submission"] = dict(raw["submission"])
        r["submission"][field] = val
        ok, reasons = funnel.can_promote_to_submission_ready(r)
        assert ok is False and reasons


def test_seeded_metrics_include_poc_handoff_and_submission_ready_counts():
    payload = funnel.load_records(SEED)
    m = payload["metrics"]
    assert m["clean_hits"] >= 1
    assert m["poc_handoffs_started"] >= 1
    assert m["pocs_reproduced"] >= 0  # H-01 has advanced past POC_REPRODUCED to submission-ready
    # Vultisig H-01 (blind) + ASSISTED-M11 (assisted, human-supplied invariant) are both submission-ready.
    assert m["submission_packages_ready_for_human_review"] == 2


# ----------------------------------------------------------- loader is read-only
def test_loader_performs_no_writes():
    fdir = SEED.parent
    before = {p: p.stat().st_mtime_ns for p in fdir.rglob("*") if p.is_file()}
    funnel.load_records(SEED)
    funnel.load_records()  # default path
    after = {p: p.stat().st_mtime_ns for p in fdir.rglob("*") if p.is_file()}
    assert before == after


def test_missing_file_is_graceful(tmp_path):
    payload = funnel.load_records(tmp_path / "does_not_exist.json")
    assert payload["record_count"] == 0
    assert payload["records"] == []
    assert payload["metrics"]["total_leads_surfaced"] == 0


# ----------------------------------------------------- P98 assisted-mode (additive)
def _assisted_record(**over):
    """A human-supplied assisted candidate that validated for PoC handoff."""
    rec = _clean_hit_record(record_id="t:assisted", conversion="STRONG_PARTIAL")
    rec.update({
        "source": "assisted",
        "supplied_by": "human",
        "candidate_invariant": "a user cannot sell more than maxSellPercent of their allocation",
        "assisted_validation_status": "VALIDATED_FOR_POC_HANDOFF",
        "requested_check": "VALIDATE",
    })
    rec.update(over)
    return rec


def test_blind_records_default_source():
    """A record without `source` normalizes to blind and carries no candidate_invariant."""
    rec = funnel.normalize_record(_clean_hit_record())
    assert rec["source"] == "blind"
    assert rec["candidate_invariant"] is None
    assert rec["assisted_validation_status"] is None
    row = funnel.build_finding_row(_clean_hit_record())
    assert row["source"] == "blind"
    assert row["candidate_invariant_present"] is False


def test_assisted_record_surfaces_fields():
    row = funnel.build_finding_row(_assisted_record())
    assert row["source"] == "assisted"
    assert row["assisted_validation_status"] == "VALIDATED_FOR_POC_HANDOFF"
    assert row["candidate_invariant_present"] is True
    assert row["ready_for_poc_handoff"] is True  # reuses can_promote_to_poc_handoff


def test_metrics_split_blind_vs_assisted():
    recs = [_clean_hit_record(record_id="b1"), _clean_hit_record(record_id="b2"), _assisted_record()]
    m = funnel.compute_funnel_metrics(recs)
    assert m["blind_records"] == 2
    assert m["assisted_records"] == 1
    assert m["by_source"]["assisted"] == 1 and m["by_source"]["blind"] == 2
    assert m["assisted_validated_for_poc_handoff"] == 1


def test_invalid_source_rejected():
    with pytest.raises(funnel.FunnelValidationError):
        funnel.normalize_record(_clean_hit_record(source="bogus"))


def test_invalid_assisted_status_rejected():
    with pytest.raises(funnel.FunnelValidationError):
        funnel.normalize_record(_assisted_record(assisted_validation_status="NOPE"))


def test_assisted_record_does_not_auto_submit():
    """An assisted-validated record is never SUBMITTED automatically."""
    row = funnel.build_finding_row(_assisted_record())
    assert row["submission_badge"] != "SUBMITTED"
    assert funnel.compute_pipeline_status(_assisted_record()) != "SUBMISSION_READY_HUMAN_REVIEW"


def test_seed_has_blind_and_assisted_and_blind_intact():
    """The 7 historical blind records still render; the seeded assisted record is distinguished."""
    payload = funnel.load_records(SEED)
    rows = payload["records"]
    blind = [r for r in rows if r["source"] == "blind"]
    assisted = [r for r in rows if r["source"] == "assisted"]
    assert len(blind) == 7  # the historical autonomous-eval records, intact
    assert len(assisted) == 1
    assert payload["metrics"]["blind_records"] == 7
    assert payload["metrics"]["assisted_records"] == 1
    # no record anywhere is auto-SUBMITTED
    assert all(r["submission_badge"] != "SUBMITTED" for r in rows)
    # the statuses block advertises the new enums
    assert "source_kind" in payload["statuses"]
    assert "VALIDATED_FOR_POC_HANDOFF" in payload["statuses"]["assisted_validation_status"]


# ----------------------------------------------------- P99 human-final-gate + outcome (additive)
def test_outcome_defaults_pending_not_submitted():
    """A row with NO joined outcome defaults to pending / not-submitted / gate PENDING."""
    row = funnel.build_finding_row(_clean_hit_record())
    assert row["human_final_gate"] == "PENDING"
    assert row["submitted"] is False
    assert row["outcome"] == "pending"


def test_dashboard_ready_without_submitted():
    """A submission-ready record with no outcome shows READY_FOR_HUMAN_REVIEW and is NOT submitted."""
    rec = _submission_ready_record()
    row = funnel.build_finding_row(rec)  # no outcome joined
    assert row["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW"
    assert row["submission_badge"] != "SUBMITTED"
    assert row["submitted"] is False


def test_submitted_only_from_outcome_record():
    """SUBMITTED is shown ONLY when an explicit outcome record sets submitted=true (never inferred)."""
    rec = _submission_ready_record()
    outcome = {"candidate_id": rec["record_id"], "submitted": True, "human_final_gate": "APPROVED_TO_SUBMIT",
               "outcome": "accepted", "platform": "immunefi", "submission_id": "X-1", "awarded_severity": "Medium"}
    row = funnel.build_finding_row(rec, outcome)
    assert row["submitted"] is True
    assert row["outcome"] == "accepted"
    assert row["platform"] == "immunefi"
    assert row["awarded_severity"] == "Medium"
    # without the outcome, the same record is not submitted
    assert funnel.build_finding_row(rec)["submitted"] is False


def test_load_outcomes_joins_seeded_records():
    outcomes = funnel.load_outcomes()
    assert "vultisig-2024-06:H-01:ILOPool.claim" in outcomes
    assert "secondswap-2024-12:ASSISTED-M11:SecondSwap_VestingManager.listVesting" in outcomes
    # both seeded as pending / not submitted
    for cid, o in outcomes.items():
        if "ASSISTED-M11" in cid or "ILOPool" in cid:
            assert o["submitted"] is False
            assert o["human_final_gate"] == "PENDING"
            assert o["outcome"] == "pending"


def test_seed_proven_packages_pending_human_review():
    payload = funnel.load_records(SEED)
    rows = {r["finding_id"]: r for r in payload["records"]}
    for fid in ("H-01", "ASSISTED-M11"):
        # there can be multiple H-01s; pick the submission-ready one
        cands = [r for r in payload["records"] if r["finding_id"] == fid
                 and r["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW"]
        assert cands, fid
        r = cands[0]
        assert r["submitted"] is False
        assert r["human_final_gate"] == "PENDING"
        assert r["outcome"] == "pending"
        assert r["submission_badge"] != "SUBMITTED"


def test_no_submitted_anywhere_in_seed():
    payload = funnel.load_records(SEED)
    assert all(r["submitted"] is False for r in payload["records"])
    assert all(r["submission_badge"] != "SUBMITTED" for r in payload["records"])


def test_p99_metrics_present_and_zero_submitted():
    m = funnel.load_records(SEED)["metrics"]
    for k in ("ready_for_human_review_count", "approved_to_submit_count", "submitted_count", "accepted_count",
              "duplicate_count", "rejected_count", "pending_count", "invalid_count",
              "assisted_to_reproduced_count", "reproduced_to_submission_ready_count",
              "submission_ready_to_submitted_count"):
        assert k in m, k
    assert m["submitted_count"] == 0
    assert m["ready_for_human_review_count"] >= 2
    assert m["assisted_to_reproduced_count"] >= 1  # SecondSwap M-11


def test_invalid_outcome_enum_rejected_in_view():
    with pytest.raises(funnel.FunnelValidationError):
        funnel.build_finding_row(_clean_hit_record(), {"candidate_id": "x", "outcome": "nope"})


# ----------------------------------------------------- P100 dashboard truth (additive)
def test_p100_row_exposes_all_documented_fields():
    """Every /api/funnel row exposes the documented top-level fields (P100 review)."""
    fields = ["candidate_id", "subject", "source_mode", "supplied_by", "finding_title", "pipeline_status",
              "poc_status", "submission_status", "human_final_gate", "submitted", "outcome", "claimed_severity",
              "awarded_severity", "duplicate_check", "scope_check", "severity_check", "final_human_gate",
              "poc_command", "blocker_reason"]
    for r in funnel.load_records(SEED)["records"]:
        for f in fields:
            assert f in r, f
        assert "submission" in r and "artifact_links" in r  # package paths


def test_p100_poc_reproduced_total_counts_advanced_pocs():
    """poc_reproduced_total counts reproduced PoCs even after they advance to submission-ready (the
    human-facing count); the legacy stage-count under-counts."""
    m = funnel.load_records(SEED)["metrics"]
    assert m["poc_reproduced_total"] == 2
    assert m["poc_reproduced_total"] >= m["pocs_reproduced"]


def test_p100_finding_title_from_outcome():
    rows = {(r["finding_id"], r["pipeline_status"]): r for r in funnel.load_records(SEED)["records"]}
    h01 = rows[("H-01", "SUBMISSION_READY_HUMAN_REVIEW")]
    m11 = rows[("ASSISTED-M11", "SUBMISSION_READY_HUMAN_REVIEW")]
    assert "ILOPool" in h01["finding_title"]
    assert "maxSellPercent" in m11["finding_title"]
    assert h01["source_mode"] == "blind" and m11["source_mode"] == "assisted"


def test_p100_ready_for_human_review_split_by_source():
    recs = funnel.load_records(SEED)["records"]
    ready = [r for r in recs if r["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW"]
    assert len(ready) == 2
    by_src = {}
    for r in ready:
        by_src[r["source_mode"]] = by_src.get(r["source_mode"], 0) + 1
    assert by_src == {"blind": 1, "assisted": 1}
    # ready does NOT imply submitted
    assert all(r["submitted"] is False for r in ready)


# ----------------------------------------- P100 metric/row sync (cannot-drift)
def _scan(rows, pred):
    return sum(1 for r in rows if pred(r))


def test_p100_tiles_cannot_drift_from_rows():
    """Every displayed headline metric in the served payload equals the count obtained by scanning the SAME
    rows the table renders. This is the structural guarantee against metric/row drift."""
    payload = funnel.load_records(SEED)
    rows, m = payload["records"], payload["metrics"]
    poc = lambda r: (r.get("poc") or {}).get("poc_status")
    src = lambda r: (r.get("source_mode") or r.get("source"))
    assert m["poc_reproduced_total"] == _scan(rows, lambda r: poc(r) == "REPRODUCED")
    assert m["ready_for_human_review_count"] == _scan(rows, lambda r: r["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW")
    assert m["pending_count"] == _scan(rows, lambda r: (r.get("outcome") or "pending") == "pending")
    assert m["submitted_count"] == _scan(rows, lambda r: r.get("submitted") is True)
    assert m["blind_records"] == _scan(rows, lambda r: src(r) == "blind")
    assert m["assisted_records"] == _scan(rows, lambda r: src(r) == "assisted")
    assert m["accepted_count"] == _scan(rows, lambda r: r.get("outcome") == "accepted")
    assert m["submission_packages_ready_for_human_review"] == m["ready_for_human_review_count"]


def test_p100_reproduced_counts_after_advance():
    m = funnel.load_records(SEED)["metrics"]
    assert m["poc_reproduced_total"] == 2          # both advanced past the stage but stay reproduced
    assert m["ready_for_human_review_count"] == 2
    assert m["submitted_count"] == 0
    assert m["blind_records"] >= 1 and m["assisted_records"] >= 1


def test_p100_proven_rows_pending_not_submitted():
    rows = funnel.load_records(SEED)["records"]
    proven = [r for r in rows if r["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW"]
    assert len(proven) == 2
    assert all(r["submitted"] is False for r in proven)
    assert all(r["outcome"] == "pending" for r in proven)
    assert all(r["submission_badge"] != "SUBMITTED" for r in proven)


def test_p100_submitted_count_reflects_explicit_outcome():
    """submitted_count is 0 without a submitted outcome, and rises only with an explicit submitted=true row."""
    base_rows = [funnel.build_finding_row(_submission_ready_record())]
    assert funnel._metrics_from_rows(base_rows)["submitted_count"] == 0
    submitted_outcome = {"candidate_id": "t:subready", "submitted": True,
                         "human_final_gate": "APPROVED_TO_SUBMIT", "outcome": "accepted"}
    sub_rows = [funnel.build_finding_row(_submission_ready_record(), submitted_outcome)]
    mm = funnel._metrics_from_rows(sub_rows)
    assert mm["submitted_count"] == 1 and mm["accepted_count"] == 1


# ----------------------------------------- P100 Focused view (non-destructive filter)
def test_focused_records_is_assisted_or_ready():
    rows = funnel.load_records(SEED)["records"]
    foc = funnel.focused_records(rows)
    for r in foc:
        assert (r.get("source_mode") or r.get("source")) == "assisted" \
            or r["pipeline_status"] == "SUBMISSION_READY_HUMAN_REVIEW"
    # on the seed that is exactly the two proven findings
    ids = sorted(r["finding_id"] for r in foc)
    assert ids == ["ASSISTED-M11", "H-01"]


def test_focused_excludes_legacy_blind_scaffolds():
    rows = funnel.load_records(SEED)["records"]
    foc_ids = {r["finding_id"] for r in funnel.focused_records(rows)}
    # blind PoC-scaffold rows (handoff-started, not ready) are NOT in the focused view
    scaffolds = [r for r in rows if r["pipeline_status"] == "POC_HANDOFF_STARTED"]
    assert scaffolds, "expected some legacy scaffold rows in the corpus"
    for r in scaffolds:
        assert r["finding_id"] not in foc_ids or r["focused"] is False


def test_focused_count_and_per_row_flag():
    payload = funnel.load_records(SEED)
    assert payload["focused_count"] == 2
    assert payload["focused_count"] <= payload["record_count"]
    by_state = {f"{r.get('finding_id')}:{r['pipeline_status']}": r["focused"] for r in payload["records"]}
    assert by_state["H-01:SUBMISSION_READY_HUMAN_REVIEW"] is True
    assert by_state["ASSISTED-M11:SUBMISSION_READY_HUMAN_REVIEW"] is True
    # a legacy scaffold row is not focused
    assert any(r["focused"] is False for r in payload["records"])


def test_focused_filter_does_not_change_metric_totals():
    """The Focused view filters table rows only; metric tiles stay full totals (no drift)."""
    m = funnel.load_records(SEED)["metrics"]
    assert m["poc_reproduced_total"] == 2
    assert m["ready_for_human_review_count"] == 2
    assert m["submitted_count"] == 0
    assert m["blind_records"] == 7
    assert m["assisted_records"] == 1
