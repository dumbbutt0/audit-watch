"""P218 — tests for the completion guard (scripts/validate_hunt_sync_completion.py) and the mandatory hook.

Failure-mode tests use the PURE `run_checks` (+ injectable card/reader loaders) with crafted in-memory data, so they
are fast and hermetic. Proves completion FAILS on: missing candidate · unsafe flags · High without L3 PASS/blocker ·
dry-run-queue entry without synced record · duplicate record_ids · malformed/invalid record · missing package link
(strict) · detail card cannot load. Plus a happy-path pass.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard_sync as ds                  # noqa: E402
import validate_hunt_sync_completion as vc    # noqa: E402


def _rec(cid, **over):
    """A valid, safe synced record for candidate cid."""
    b = {"candidate_id": cid, "source_track": "audit_workspace", "subject": "T", "phase_discovered": "P215",
         "contract": "C", "function": "f", "title": f"{cid} title", "conversion": "NONE",
         "triage": {"triage_status": "submit"}, "final_triager_decision": "submit",
         "source_refs": {"dry_run_queue": f"output_research/dry_run_submission_queue/{cid}.json"}}
    r = ds.to_synced_finding(b)
    r.setdefault("human_review_priority", "NONE")  # P222: CARD_INJECT supplies this on every real synced record
    r.update(over)
    return r


def _cands(*ids, sev=None):
    return [{"id": i, "claimed_severity": (sev or {}).get(i)} for i in ids]


# ---------------- happy path ----------------
def test_happy_path_passes():
    cands = _cands("ZETA-01", "ZETA-02")
    recs = [_rec("ZETA-01"), _rec("ZETA-02")]
    fails, warns, rep = vc.run_checks(cands, recs, drq_ids=set(), opts={})
    assert fails == [], fails
    assert rep["ok"] is True


# ---------------- failure modes ----------------
def test_missing_candidate_fails():
    cands = _cands("ZETA-01", "ZETA-02")
    recs = [_rec("ZETA-01")]               # ZETA-02 missing
    fails, _, _ = vc.run_checks(cands, recs, set(), {})
    assert any("ZETA-02: missing from synced mirror" in f for f in fails)


def test_unsafe_flags_fail():
    cands = _cands("ZETA-01")
    bad = _rec("ZETA-01", routing_allowed=True)   # unsafe
    fails, _, _ = vc.run_checks(cands, [bad], set(), {})
    assert any("unsafe flags" in f for f in fails)


def test_high_without_l3_pass_or_blocker_fails():
    cands = _cands("ZETA-01", sev={"ZETA-01": "High"})
    # High, high_promotion_allowed True, l3 not PASS -> must fail
    bad = _rec("ZETA-01", l3_status="NEEDS_HARNESS", high_promotion_allowed=True)
    fails, _, _ = vc.run_checks(cands, [bad], set(), {})
    assert any("without L3 PASS" in f for f in fails)


def test_high_blocked_without_blocker_fails():
    cands = _cands("ZETA-01", sev={"ZETA-01": "High"})
    bad = _rec("ZETA-01", l3_status="NEEDS_HARNESS", high_promotion_allowed=False, high_promotion_blocker="")
    fails, _, _ = vc.run_checks(cands, [bad], set(), {})
    assert any("no high_promotion_blocker" in f for f in fails)


def test_dry_run_queue_without_synced_record_fails():
    # reviewer-added acceptance check
    cands = _cands("ZETA-01")
    recs = [_rec("ZETA-01")]
    fails, _, _ = vc.run_checks(cands, recs, drq_ids={"ZETA-99"}, opts={})
    assert any("dry-run-queue entry ZETA-99 has no synced dashboard record" in f for f in fails)


def test_duplicate_record_ids_fail():
    cands = _cands("ZETA-01")
    r1 = _rec("ZETA-01"); r2 = _rec("ZETA-01")
    r2["record_id"] = r1["record_id"]      # force duplicate
    fails, _, _ = vc.run_checks(cands, [r1, r2], set(), {})
    assert any("duplicate record_ids" in f for f in fails)


def test_malformed_record_fails():
    cands = _cands("ZETA-01")
    bad = {"candidate_id": "ZETA-01"}       # missing schema/safety fields
    fails, _, _ = vc.run_checks(cands, [bad], set(), {})
    assert any("schema invalid" in f or "unsafe flags" in f for f in fails)


def test_missing_package_link_warns_and_strict_fails_hook_level():
    cands = _cands("ZETA-01")
    r = _rec("ZETA-01", source_refs={})    # queued but no package/queue link
    fails, warns, _ = vc.run_checks(cands, [r], drq_ids={"ZETA-01"}, opts={})
    assert fails == []                      # not a hard failure
    assert any("no package/queue link" in w for w in warns)   # warning -> strict fails at main()


def test_stale_extra_record_fails():
    cands = _cands("ZETA-01")
    extra = _rec("ZETA-99")
    extra["record_id"] = "zetachain-2023-10:P215:ZETA-99:C.f"
    fails, _, _ = vc.run_checks(cands, [_rec("ZETA-01"), extra], set(),
                                {"prefix": "zetachain-2023-10:P215:"})
    assert any("stale synced record not in register" in f for f in fails)


# ---------------- detail-card load failure (injectable loader) ----------------
def test_detail_card_cannot_load_fails():
    def broken_loader(key):
        raise RuntimeError("card boom")
    fails = vc.check_cards(["ZETA-01"], loader=broken_loader)
    assert any("failed to load" in f for f in fails)


def test_detail_card_missing_sections_fails():
    def thin_loader(key):
        return {"verifier_evidence": {"report_summary": {}}, "submission_ready": False, "routing_allowed": False}
    fails = vc.check_cards(["ZETA-01"], loader=thin_loader)
    assert any("missing sections" in f for f in fails)


# ---------------- live integration (real mirror) ----------------
def test_live_real_p215_passes():
    # P224: the shared mirror is now MULTI-SOURCE (ZETA + Size Credit SC-* + any future source). This is a
    # per-source completion check, so scope to the P215 (zeta) records by record_id prefix rather than asserting
    # the whole mirror is exactly 12. The presence of other sources must NOT break the per-source check.
    import json
    reg = json.loads((ROOT / "documentation/research/assisted_mode/p215_full_funnel_rehearsal/CANDIDATE_REGISTER.json").read_text())
    mirror = json.loads((ROOT / "documentation/research/funnel/synced_findings.generated.json").read_text())
    prefix = "zetachain-2023-10:P215:"
    p215_recs = [r for r in mirror["findings"] if str(r.get("record_id", "")).startswith(prefix)]
    drq = {p.stem for p in (ROOT / "output_research/dry_run_submission_queue").glob("ZETA-*.json")}
    fails, warns, rep = vc.run_checks(reg["candidates"], p215_recs, drq,
                                      {"phase": "P215", "prefix": prefix})
    assert fails == [], fails
    assert rep["register_candidates"] == 12 and rep["synced_unique_candidates"] == 12
