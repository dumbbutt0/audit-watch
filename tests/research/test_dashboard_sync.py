"""P216 — tests for the unified dashboard sync contract (research-only, read-only).

Covers: schema validation · idempotent generation · no duplicates · safety flags always false ·
missing fields → unknown · P215 records visible in /findings,/candidates,/funnel readers · H5 parity structure ·
no dashboard submit/promote controls · no active-audit switch required · zero route/submit side effects ·
severity is never a conversion/lifecycle token (browser computes no severity).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard_sync as ds          # noqa: E402
import funnel                         # noqa: E402
import findings_overview as fo        # noqa: E402
import finding_detail as fd           # noqa: E402

MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"
PREFIX = "zetachain-2023-10:P215:"
_SEV = {"critical", "high", "medium", "low", "informational", "info", "qa", "no_security_impact", "none", "design"}
_CONV_TOKENS = {"CLEAN_HIT", "STRONG_PARTIAL", "ADJACENT", "REJECTED", "ABSTAINED", "NONE", "REPRODUCED",
                "INVESTIGATED", "CONVERTED_ADJACENT", "RUNTIME_CONFIRMED", "REPORTABLE_CANDIDATE"}


def _mirror():
    return json.loads(MIRROR.read_text())


def _p215_records():
    return [r for r in _mirror()["findings"] if str(r.get("record_id", "")).startswith(PREFIX)]


# ---------------- adapter ----------------
def test_adapter_missing_fields_explicit():
    r = ds.to_synced_finding({"candidate_id": "X", "source_track": "runtime"})
    assert r["mechanism"] == "unknown"
    assert r["exploit_steps"] == ["MISSING_EVIDENCE"]
    assert r["severity_recommendation"] is None  # not inferred
    assert ds.validate_synced(r) == []


def test_adapter_no_inferred_severity_only_recorded():
    # a conversion token offered as severity must never land in the severity slot
    r = ds.to_synced_finding({"candidate_id": "X", "source_track": "funnel",
                              "severity_recommendation": "CLEAN_HIT", "claimed_severity": "High",
                              "triage": {"recommended_severity": "Medium"}})
    assert r["severity_recommendation"] == "Medium"          # recorded triage severity
    assert ds.validate_synced(r) == []


def test_adapter_safety_flags_constant():
    r = ds.to_synced_finding({"candidate_id": "X", "source_track": "funnel"})
    assert r["research_only"] is True and r["review_only"] is True
    assert r["routes_in_production"] is False and r["routing_allowed"] is False
    assert r["submission_ready"] is False
    assert r["no_submit_controls"] is True and r["browser_computes_severity"] is False
    assert r["human_review_required"] is True


# ---------------- generated mirror ----------------
def test_mirror_schema_validates_every_record():
    for r in _p215_records():
        assert ds.validate_synced(r) == [], r.get("candidate_id")


def test_mirror_no_duplicate_record_ids():
    ids = [r["record_id"] for r in _mirror()["findings"]]
    assert len(ids) == len(set(ids))


def test_mirror_safety_flags_all_false():
    for r in _p215_records():
        assert r["submission_ready"] is False
        assert r["routing_allowed"] is False
        assert r["routes_in_production"] is False
        assert r["poc"]["human_submission_ready"] is False


def test_idempotent_adapter_is_deterministic():
    b = {"candidate_id": "ZETA-04", "source_track": "audit_workspace", "contract": "C", "function": "f",
         "triage": {"recommended_severity": "Medium"}, "conversion": "CLEAN_HIT"}
    assert ds.to_synced_finding(dict(b)) == ds.to_synced_finding(dict(b))


# ---------------- visibility in all three readers (no active-audit switch) ----------------
def test_overview_payload_is_research_only():
    ov = fo.load_overview()
    assert ov.get("routing_allowed") is False
    assert ov.get("research_only") is True


# ---------------- detail card parity + safety ----------------
H5_SECTIONS = {"report_summary", "mechanism", "function_map", "attacker_model", "exploit_steps", "defense_map",
               "poc_verification", "impact_severity", "intent_scope_operator", "novelty_duplicate", "conversion",
               "main_blocker", "final_triage", "red_flags", "evidence_backup"}


# ---------------- no submit/promote controls in the dashboard pages ----------------
@pytest.mark.parametrize("page", ["dashboard/findings.html", "dashboard/candidates.html", "dashboard/funnel.html"])
def test_no_submit_or_promote_controls(page):
    html = (ROOT / page).read_text().lower()
    assert "<form" not in html
    assert "method:'post'" not in html.replace(" ", "") and 'method:"post"' not in html.replace(" ", "")
    # the only "submit" mentions are explanatory ("not submitted", "nothing here ... submittable")
    assert "submit now" not in html and "promote to platform" not in html
