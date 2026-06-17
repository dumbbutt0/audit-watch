"""Isolated read-only tests for the unified candidate-detail sync across all 3 research tracks."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import findings_overview as fo  # noqa: E402
import finding_detail as fd  # noqa: E402

H5 = "runtime:H5-abracadabra-lockingrewards-boost"
FUNNEL_KEY = "funnel:vultisig-2024-06:H-01:ILOPool.claim"


def test_every_findings_row_has_a_detail_link():
    o = fo.load_overview()
    assert o["rows"]
    for r in o["rows"]:
        assert r.get("key"), f"missing key: {r}"
        assert r.get("detail_href", "").startswith("/candidates?candidate_id="), r
        # only detector rows are labelable
        assert r["labelable"] is (r["track"] == "detector")


def test_h5_detail_has_no_needs_review_string():
    import json
    d = fd.load_unified_detail(H5)
    assert "needs review" not in json.dumps(d).lower(), "synced detail must use 'unknown', never 'needs review'"


H6 = "campaign:H6-pooltogether-prizevault-erc4626-rate-mismatch"


def test_reportable_normalization_predicate_exact_and_substring_safe():
    assert fo.is_reportable_candidate({"conversion_outcome": "reportable_candidate_needs_human_review"})
    assert fo.is_reportable_candidate({"conversion": {"outcome": "reportable_candidate_needs_human_review"}})
    assert fo.is_reportable_candidate({"p155_gate7_final_outcome": "remains_reportable_candidate_needs_human_review"})
    assert fo.is_reportable_candidate({"valid_finding": True, "human_review_required": True})
    # not promoted
    assert not fo.is_reportable_candidate({"conversion": {"outcome": "runtime_refuted"}})
    assert not fo.is_reportable_candidate({"conversion_outcome": "runtime_confirmed_but_privileged_only"})
    assert not fo.is_reportable_candidate({"conversion_outcome": "static_false_positive"})
    # substring-safety: phrase only inside a free-text field must NOT promote
    assert not fo.is_reportable_candidate(
        {"conversion_outcome": "runtime_refuted",
         "why": "... not reportable_candidate_needs_human_review ...",
         "summary": "reportable_candidate_needs_human_review mentioned"})
    # valid_finding requires BOTH flags
    assert not fo.is_reportable_candidate({"valid_finding": True})


def test_reportable_candidate_ranks_top():
    assert fo._STATE_RANK["REPORTABLE_CANDIDATE"] < min(
        fo._STATE_RANK[s] for s in ("RUNTIME_CONFIRMED", "READY_FOR_HUMAN_REVIEW", "LEAD",
                                    "STATIC_FALSE_POSITIVE", "RUNTIME_REFUTED"))


def test_unknown_key_is_graceful_not_crash():
    d = fd.load_unified_detail("runtime:does-not-exist")
    assert d["state"] == "NOT_FOUND"
    assert d["labelable"] is False and d["routing_allowed"] is False


# --------------------------------------------------------------------------- verifier hydration / consistency
FUNNEL_H1 = "funnel:vultisig-2024-06:H-01:ILOPool.claim"        # CLEAN_HIT
FUNNEL_H2 = "funnel:vultisig-2024-06:H-02:Whitelist.receive"   # ABSTAINED
FUNNEL_H3 = "funnel:vultisig-2024-06:H-03:ILOPool.launch"      # ADJACENT
_CONV_TOKENS = {"CLEAN_HIT", "ADJACENT", "ABSTAINED", "REJECTED", "SEVERITY_GATED", "POC_HANDOFF_STARTED"}


def test_funnel_details_stay_conservative_and_canonical_unchanged():
    for k in (FUNNEL_H1, FUNNEL_H2, FUNNEL_H3):
        d = fd.load_unified_detail(k)
        assert d["submission_ready"] is False and d["routing_allowed"] is False
        # readiness overlay never auto-marks ready
        assert d.get("readiness", {}).get("readiness_state", "not_reviewed") in (
            "not_reviewed", "needs_more_context", "blocked_by_scope", "blocked_by_severity_too_low")


# --------------------------------------------------------------------------- deep-link routing (API contract)
CAMPAIGN_KEY = "campaign:H6-pooltogether-prizevault-erc4626-rate-mismatch"


def _client():
    from fastapi.testclient import TestClient
    import dashboard
    return TestClient(dashboard.app)


def test_api_candidate_unknown_returns_404():
    c = _client()
    for bogus in ("runtime:NOPE-does-not-exist", "totally-bogus-detector-id"):
        r = c.get("/api/candidate", params={"candidate_id": bogus})
        assert r.status_code == 404, bogus
        assert "candidate not found" in r.json()["detail"]


def test_every_list_candidate_id_round_trips_to_detail():
    # the list keys and the detail keys must never diverge — every clickable row must resolve.
    c = _client()
    cands = c.get("/api/candidates").json()["candidates"]
    assert cands
    for row in cands:
        cid = row["candidate_id"]
        r = c.get("/api/candidate", params={"candidate_id": cid})
        assert r.status_code == 200, f"{cid} -> {r.status_code}"


# --------------------------------------------------------------------------- real-world funnel card hydration
# After the eval purge, the funnel track is sourced from the real-world hunt log. These replace the removed
# eval-fixture (vultisig / H4 / H5 / H6 / detector) tests: they assert the live card machinery hydrates the
# PoC-proven real candidates (40acres / Monolith / infiniFi) without ever marking them submittable.
import funnel as _fn  # noqa: E402

_REAL_CONV_TOKENS = {"CLEAN_HIT", "STRONG_PARTIAL", "ADJACENT", "ABSTAINED", "REJECTED", "REPRODUCED"}
_VALID_SEV = {"critical", "high", "medium", "low", "informational", "info"}


def _real_candidate_keys():
    return ["funnel:" + (r.get("finding_id") or r.get("record_id"))
            for r in _fn.load_records().get("records", []) if r.get("poc_status") == "REPRODUCED"]


def _first_clean_hit_key():
    for r in _fn.load_records().get("records", []):
        if r.get("conversion") == "CLEAN_HIT" and r.get("poc_status") == "REPRODUCED":
            return "funnel:" + (r.get("finding_id") or r.get("record_id"))
    return None


def test_real_funnel_records_resolve_read_only():
    keys = _real_candidate_keys()
    assert keys, "no real-world candidate findings"
    for k in keys:
        d = fd.load_unified_detail(k)
        assert d["track"] == "funnel"
        assert d["labelable"] is False and d["read_only_synced"] is True
        assert d["routing_allowed"] is False and d["submission_ready"] is False
        assert d.get("candidate_surface") and d.get("raw_record")
        assert d.get("verifier_evidence")


def test_real_severity_field_is_never_a_conversion_label():
    for k in _real_candidate_keys():
        ve = fd.load_unified_detail(k)["verifier_evidence"]
        assert ve["report_summary"]["severity_recommendation"] not in _REAL_CONV_TOKENS
        assert ve["impact_severity"]["severity_recommendation"] not in _REAL_CONV_TOKENS


def test_real_clean_hit_hydrates_funnel_evidence():
    k = _first_clean_hit_key()
    assert k, "no CLEAN_HIT real candidate"
    rs = fd.load_unified_detail(k)["verifier_evidence"]["report_summary"]
    assert str(rs["severity_recommendation"]).lower() in _VALID_SEV  # recorded severity, not the conversion label
    assert rs["affected_contracts"] and rs["affected_contracts"] != ["MISSING_EVIDENCE"]
    assert rs["affected_functions"] and rs["affected_functions"] != ["MISSING_EVIDENCE"]
    assert "unknown" not in str(rs["impact_summary"]).lower()  # hydrated from the record's impact


def test_real_novelty_and_duplicate_are_human_pending():
    for k in _real_candidate_keys():
        ve = fd.load_unified_detail(k)["verifier_evidence"]
        assert ve["report_summary"]["novelty_status"] == "HUMAN_PENDING"
        assert ve["novelty_duplicate"]["novelty_status"] == "HUMAN_PENDING"


def test_real_reportable_blocker_none_when_mechanism_and_reachability_confirmed():
    seen = False
    for k in _real_candidate_keys():
        ve = fd.load_unified_detail(k)["verifier_evidence"]
        if ve["conversion"]["attacker_reachable"] is True and ve["conversion"]["mechanism_confirmed"] is True:
            seen = True
            assert ve["main_blocker"]["blocker"].startswith("none (mechanism")
    assert seen, "expected at least one attacker-reachable confirmed real candidate"
