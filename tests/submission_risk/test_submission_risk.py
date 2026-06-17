"""Pre-READY submission-risk check (advisory-only). The first real-world outcomes showed valid PoCs bounce on
three axes unrelated to PoC validity: deployment-reachability, novelty, design-accepted. This scorer flags them.
Locks: (1) the 3 real-world design-accepted shapes match with their outcome_provenance; (2) token-boundary
matching avoids substring FPs ('nav' must not match 'navigation'); (3) reachability defaults to checklist when
undecidable; (4) THE ADVISORY-ONLY INVARIANT — max submission_risk never changes a finding's canonical state."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_context as ac  # noqa: E402
import submission_risk_audit as sra  # noqa: E402
import build_candidate_records as bcr  # noqa: E402


@pytest.fixture
def patched(tmp_path, monkeypatch):
    (tmp_path / "output" / "candidates").mkdir(parents=True)
    (tmp_path / "data" / "triage").mkdir(parents=True)
    (tmp_path / "data" / "runtime_poc").mkdir(parents=True)
    monkeypatch.setattr(ac, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(ac, "audit_language", lambda *a, **k: "solidity")
    monkeypatch.setattr(ac, "get_active_audit", lambda: {"audit_id": "t"})
    # audit_path("output") used by submission_risk_audit -> point at tmp
    import importlib
    monkeypatch.setattr(sra, "audit_path", lambda *p: tmp_path.joinpath(*p))
    return tmp_path


def _merged(tmp, findings):
    (tmp / "output" / "merged_findings.json").write_text(json.dumps({"findings": findings}))


def _risk(tmp, fid):
    d = json.loads((tmp / "output" / "submission_risk.json").read_text())
    return next(r for r in d["findings"] if r["finding_id"] == fid)


def test_design_shapes_match_with_provenance(patched):
    _merged(patched, [
        {"id": "S-1", "title": "Loosened NAV check in vault_withdraw allows overpay",
         "description": "1% upward tolerance lets a request-time NAV settle after the NAV dropped"},
        {"id": "S-2", "title": "reward/principal fund commingling drains principal",
         "description": "withdrawReward paid from the same balance; no reserve/solvency check"},
        {"id": "S-3", "title": "Vault undervalues ZO position via stale accumulator",
         "description": "the adaptor reads acc_reward_per_share without settling pending reward"},
    ])
    sra.build()
    assert _risk(patched, "S-1")["design_acceptance_risk"]["pattern"] == "nav_oracle_settlement_tolerance"
    assert "solvbtc" in _risk(patched, "S-1")["design_acceptance_risk"]["outcome_provenance"]
    assert _risk(patched, "S-2")["design_acceptance_risk"]["pattern"] == "reward_principal_commingling"
    assert _risk(patched, "S-3")["design_acceptance_risk"]["pattern"] == "adaptor_stale_accumulator"
    assert _risk(patched, "S-1")["overall"] == "high"


def test_token_boundary_avoids_substring_fp(patched):
    # 'nav' appears ONLY as a substring of 'navigation' (never standalone) -> the all=['nav'] gate must fail.
    _merged(patched, [{"id": "F-1", "title": "AerodromeAMO strict equality DoS in navigation logic",
                       "description": "navigation rounding inside the strategy; pure equality bug"}])
    sra.build()
    assert _risk(patched, "F-1")["design_acceptance_risk"]["level"] == "low"


def test_reachability_defaults_to_checklist(patched):
    _merged(patched, [{"id": "R-1", "title": "reentrancy in withdraw", "description": "classic reentrancy"}])
    sra.build()
    assert _risk(patched, "R-1")["deployment_reachability_risk"]["level"] == "checklist_required"


def _manifest(tmp, monkeypatch, m):
    (tmp / "deployment_manifest.json").write_text(json.dumps(m))
    monkeypatch.setattr(sra, "audit_path", lambda *p: tmp.joinpath(*p))


def test_manifest_marks_inactive_module_not_wired(patched, monkeypatch):
    # TipRun shape: perp Risk engine present in source but NOT wired in the predict deployment.
    _merged(patched, [{"id": "P-1", "title": "margin bypass in Risk.checkValidTransition",
                       "description": "maintenance-margin enforcement flaw",
                       "location": {"file": "src/core/risk/Risk.sol", "function": "checkValidTransition"}}])
    _manifest(patched, monkeypatch, {"inactive_modules": ["Risk"], "active_profiles": ["predict"],
                                     "noop_fallbacks": ["NullMarginCheck"]})
    sra.build()
    r = _risk(patched, "P-1")["deployment_reachability_risk"]
    assert r["level"] == "not_wired" and r["matched"]["term"] == "Risk"
    assert _risk(patched, "P-1")["overall"] == "high"
    assert any("LIKELY OUT OF SCOPE" in a for a in _risk(patched, "P-1")["advisories"])


def test_manifest_confirms_active_module_wired(patched, monkeypatch):
    _merged(patched, [{"id": "P-2", "title": "predict market settlement bug",
                       "description": "x", "location": {"file": "src/predict/Market.sol", "function": "settle"}}])
    _manifest(patched, monkeypatch, {"active_modules": ["Market"], "inactive_modules": ["Risk"]})
    sra.build()
    r = _risk(patched, "P-2")["deployment_reachability_risk"]
    assert r["level"] == "wired" and r["matched"]["term"] == "Market"
    # 'wired' does not raise overall on its own
    assert _risk(patched, "P-2")["overall"] in ("review", "low")


def test_reachability_flags_null_fallback(patched):
    _merged(patched, [{"id": "R-2", "title": "margin check bypass",
                       "description": "CAP_MARGIN_CHECK falls back to NullMarginCheck in the predict profile"}])
    sra.build()
    assert _risk(patched, "R-2")["deployment_reachability_risk"]["level"] == "flag"
    assert _risk(patched, "R-2")["overall"] == "high"


def test_advisory_only_invariant_does_not_change_state(patched):
    # A High that is confirmed + proved + submit + full report fields would be READY. Even with MAX submission
    # risk (design match + reachability flag), its canonical state MUST stay 'ready' — advisories never gate.
    f = {"id": "H-1", "severity": "High", "title": "Loosened NAV check falls back to NullMarginCheck",
         "description": "1% tolerance request-time settlement; predict profile no-op fallback",
         "location": {"function": "withdraw"}, "recommendation": "fix"}
    _merged(patched, [f])
    (patched / "output" / "findings_confirmed.json").write_text(json.dumps(
        {"findings": [{"id": "H-1", "confirmation_score": 1.0, "confirmation_passes": 3,
                       "human_review_required": False}]}))
    (patched / "data" / "runtime_poc" / "results.jsonl").write_text(
        json.dumps({"finding_id": "H-1", "status": "proved", "runtime_level": 3}) + "\n")
    (patched / "data" / "triage" / "submit.jsonl").write_text(json.dumps(
        {"finding_id": "H-1", "triage_status": "submit", "impact": {"victim": "LPs"},
         "attacker_model": {"attacker_type": "unprivileged"}}) + "\n")
    sra.build()                       # writes submission_risk.json (max risk for H-1)
    bcr.build()                       # builds canonical record, overlaying advisories
    rec = json.loads((patched / "output" / "candidates" / "H-1.json").read_text())
    assert rec["state"] == "ready"                     # advisory NEVER changes state
    assert rec["readiness_advisories"], "advisories should be populated"
    assert not rec["readiness_blockers"]               # and never leak into blockers
