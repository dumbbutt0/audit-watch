"""P210 — tests for the dark L3 HIGH readiness gate in submission_readiness_review.py.

Covers: flag-off output-equivalence, flag-on High/Critical enforcement, Medium pass-through, malformed/empty
fail-closed, human-override-needs-reason, parity with the P208 backtest, and the no-submit guard.
All advisory; nothing is submitted/routed.
"""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import submission_readiness_review as srr  # noqa: E402

P208 = ROOT / "documentation/research/assisted_mode/p208_l3_high_policy_dryrun"
P210FX = ROOT / "documentation/research/assisted_mode/p210_l3_dark_wiring/fixtures"


def _load(p):
    return json.loads(Path(p).read_text())


def _good_answers(sev="High"):
    return {
        "mechanism_confirmed": "yes", "reachability_confirmed": "yes", "severity_bearing": "yes",
        "poc_complete": "yes", "impact_not_overclaimed": "yes", "severity_recommendation": sev,
        "scope_caveats_reviewed": "yes", "novelty": "novelty_clear", "report_draft_exists": "yes",
        "mitigation_included": "yes", "assumptions_included": "yes", "notes": "ok",
    }


def _good_facts(cid="cand-x"):
    return {"reportable": True, "mechanism_confirmed": True, "attacker_reachable": True,
            "severity_bearing": True, "candidate_id": cid}


@pytest.fixture(autouse=True)
def _clean_flag():
    saved = os.environ.pop("AUDITWATCH_L3_READINESS", None)
    yield
    os.environ.pop("AUDITWATCH_L3_READINESS", None)
    if saved is not None:
        os.environ["AUDITWATCH_L3_READINESS"] = saved


# ---------------------------------------------------------------- flag OFF: output-equivalent to pre-P210
def test_flag_off_evaluate_has_no_l3_blocker():
    eligible, failed = srr.evaluate(_good_answers("High"), _good_facts())
    assert eligible is True
    assert not any("l3" in f for f in failed)


def test_flag_off_no_l3_key_in_overlay(monkeypatch):
    # detail_overlay must not carry an `l3` key when the flag is off
    monkeypatch.setattr(srr, "latest_row", lambda cid: None)
    monkeypatch.setattr(srr, "_facts", lambda cid: _good_facts(cid))
    out = srr.detail_overlay("cand-x")
    assert "l3" not in out


# ---------------------------------------------------------------- flag ON: High/Critical enforcement
def test_flag_on_high_without_record_blocks(monkeypatch):
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    monkeypatch.setattr(srr, "_load_l3_record", lambda cid: None)
    eligible, failed = srr.evaluate(_good_answers("High"), _good_facts())
    assert eligible is False
    assert any(f.startswith("blocked_by_missing_l3_poc") for f in failed)


def test_flag_on_high_with_pass_clears(monkeypatch):
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    rec = _load(P208 / "backtest/decent_H01_setRouter_mint.json")
    monkeypatch.setattr(srr, "_load_l3_record", lambda cid: rec)
    eligible, failed = srr.evaluate(_good_answers("High"), _good_facts())
    assert not any("l3" in f for f in failed)
    assert eligible is True


def test_l3_gate_applies_to_critical_target():
    # The L3 gate covers both High and Critical (pure-function level). NB: the module's q6 checklist vocabulary
    # (_SEVERITIES) does not include "Critical", so Critical is independently un-submittable via evaluate() today;
    # this asserts the L3 policy itself treats Critical as a gated target.
    assert srr.l3_evaluate({}, "Critical")["applies"] is True
    assert srr.l3_evaluate({}, "Critical")["high_promotion_allowed"] is False
    assert srr.l3_evaluate({}, "Low")["applies"] is False


def test_flag_on_vultisig_h01_clears(monkeypatch):
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    rec = _load(P208 / "backtest/vultisig_H01_claim_fee_loss.json")
    monkeypatch.setattr(srr, "_load_l3_record", lambda cid: rec)
    eligible, failed = srr.evaluate(_good_answers("High"), _good_facts())
    assert eligible is True


@pytest.mark.parametrize("fx", ["decent_M03_receiveFromBridge.json", "vultisig_M03_cap_bypass.json"])
def test_flag_on_fail_records_block_high(monkeypatch, fx):
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    rec = _load(P208 / "backtest" / fx)
    monkeypatch.setattr(srr, "_load_l3_record", lambda cid: rec)
    eligible, failed = srr.evaluate(_good_answers("High"), _good_facts())
    assert eligible is False
    assert any(f.startswith("blocked_by_missing_l3_poc") for f in failed)


def test_flag_on_medium_unaffected(monkeypatch):
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    # even with no L3 record, a Medium target is never gated by L3
    monkeypatch.setattr(srr, "_load_l3_record", lambda cid: None)
    eligible, failed = srr.evaluate(_good_answers("Medium"), _good_facts())
    assert eligible is True
    assert not any("l3" in f for f in failed)


@pytest.mark.parametrize("rec", [None, {}, {"l3_status": "GARBAGE"}, {"not": "a record"}])
def test_flag_on_malformed_high_fails_closed(monkeypatch, rec):
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    monkeypatch.setattr(srr, "_load_l3_record", lambda cid: rec)
    eligible, failed = srr.evaluate(_good_answers("High"), _good_facts())
    assert eligible is False
    assert any(f.startswith("blocked_by_missing_l3_poc") for f in failed)


def test_human_override_with_reason_allowed():
    rec = _load(P210FX / "human_override_with_reason.json")
    assert srr.l3_evaluate(rec, "High")["high_promotion_allowed"] is True


def test_human_override_without_reason_blocked():
    rec = _load(P210FX / "human_override_without_reason.json")
    r = srr.l3_evaluate(rec, "High")
    assert r["high_promotion_allowed"] is False
    assert r["human_override_required"] is False  # status IS override, but reason missing -> still blocked by decide()


def test_static_high_no_poc_blocked():
    rec = _load(P208 / "regression/static_high_no_poc.json")
    assert srr.l3_evaluate(rec, "High")["high_promotion_allowed"] is False


# ---------------------------------------------------------------- parity with P208 backtest (decide is target-independent)
def test_parity_with_p208_fixtures():
    files = list((P208 / "backtest").glob("*.json")) + list((P208 / "regression").glob("*.json"))
    assert len(files) == 10
    for f in files:
        rec = _load(f)
        exp = rec.get("expected", {})
        got = srr.l3_evaluate(rec, "High")["high_promotion_allowed"]
        assert got == exp.get("high_promotion_allowed"), f"parity mismatch on {f.name}"


# ---------------------------------------------------------------- no-submit guard
def test_l3_outputs_are_advisory_only():
    rec = _load(P208 / "backtest/decent_H01_setRouter_mint.json")
    r = srr.l3_evaluate(rec, "High")
    assert r["research_only"] is True
    assert r["routing_allowed"] is False
    assert "submission_ready" not in r


def test_l3_source_has_no_submit_or_route_calls():
    src = (ROOT / "scripts/submission_readiness_review.py").read_text()
    # the L3 region must not introduce routing/submission side effects
    start = src.index("P210: L3 HIGH readiness")
    end = src.index("def _read_rows")
    l3_region = src[start:end]
    for forbidden in ("submission_ready = True", "routing_allowed = True", "final_submission_pack",
                      "route(", "submit("):
        assert forbidden not in l3_region, f"forbidden token in L3 region: {forbidden}"


def test_record_review_never_sets_canonical_flags():
    # invariant preserved: the overlay still never flips canonical flags
    src = (ROOT / "scripts/submission_readiness_review.py").read_text()
    assert '"routing_allowed": False' in src
    assert "submission_ready is intentionally never set true" in src
