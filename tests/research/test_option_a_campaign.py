"""Isolated tests for the research-only Option-A conversion ledger (outcomes-only, no authority)."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))          # for `import dashboard` / `from research import ...`
sys.path.insert(0, str(ROOT / "scripts" / "research"))
import option_a_campaign as oac  # noqa: E402


def _fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(oac, "LEDGER", tmp_path / "ledger.jsonl")
    return oac


def test_record_forces_research_flags(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    row = m.record({"candidate_id": "X1", "conversion_outcome": "runtime_refuted",
                    "routing_allowed": True, "submission_ready": True, "research_only": False})
    # the ledger can never assert routing/severity/submission authority
    assert row["research_only"] is True
    assert row["routing_allowed"] is False
    assert row["submission_ready"] is False


def test_record_is_idempotent_on_candidate_id(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    m.record({"candidate_id": "X1", "conversion_outcome": "runtime_refuted"})
    again = m.record({"candidate_id": "X1", "conversion_outcome": "reportable_candidate_needs_human_review"})
    assert again == {"skipped_existing": "X1"}
    assert m.summary()["candidates"] == 1  # not double-counted


def test_summary_funnel_never_marks_submittable(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    # a positive claim must carry harness evidence (fabrication invariant); supply harness_path
    m.record({"candidate_id": "X1", "runtime_status": "runtime_confirmed",
              "conversion_outcome": "reportable_candidate_needs_human_review", "harness_path": "pocs/xtest"})
    m.record({"candidate_id": "X2", "runtime_status": "runtime_refuted",
              "conversion_outcome": "runtime_refuted"})
    s = m.summary()
    assert s["candidates"] == 2
    assert s["funnel"]["runtime_confirmed"] == 1
    assert s["funnel"]["reportable_candidate_needs_human_review"] == 1
    assert s["funnel"]["submission_ready"] == 0
    assert s["research_only"] is True and s["routing_allowed"] is False


# --------------------------------------------------------------------------- P164 scorecard / invariant
def test_fabrication_invariant_rejects_unbacked_positive(tmp_path, monkeypatch):
    import pytest
    m = _fresh(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        m.record({"candidate_id": "FAKE", "conversion_outcome": "runtime_confirmed"})  # no evidence
    # a positive WITH harness evidence is accepted
    ok = m.record({"candidate_id": "REAL", "conversion_outcome": "runtime_confirmed", "harness_path": "pocs/p"})
    assert ok["candidate_id"] == "REAL" and ok["submission_ready"] is False


def test_derive_rejection_classes():
    assert oac._derive_rejection({"runtime_status": "runtime_refuted"}) == "runtime_refuted"
    assert oac._derive_rejection({"runtime_status": "not_run", "conversion_outcome": "static_false_positive",
                                  "deploy_complexity": "not_built_gate_refused (...)"}) == "gate_refuted"
    assert oac._derive_rejection({"runtime_status": "not_run", "conversion_outcome": "static_false_positive",
                                  "deploy_complexity": "too_heavy"}) == "source_refuted"
    assert oac._derive_rejection({"runtime_status": "runtime_confirmed",
                                  "conversion_outcome": "reportable_candidate_needs_human_review"}) == "none"
    assert oac._derive_rejection({"rejection_type": "gate_refuted"}) == "gate_refuted"  # explicit wins


def test_scorecard_counts_and_no_fabrication(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    m.record({"candidate_id": "P", "runtime_status": "runtime_confirmed",
              "conversion_outcome": "reportable_candidate_needs_human_review", "harness_path": "pocs/p"})
    m.record({"candidate_id": "G", "runtime_status": "not_run", "conversion_outcome": "static_false_positive",
              "deploy_complexity": "not_built_gate_refused"})
    m.record({"candidate_id": "S", "runtime_status": "not_run", "conversion_outcome": "static_false_positive",
              "deploy_complexity": "too_heavy"})
    sc = m.scorecard()
    assert sc["candidates"] == 3 and sc["reportable"] == 1
    assert sc["harnesses_built"] == 1 and sc["harnesses_avoided"] == 2
    assert sc["gate_refutations"] == 1 and sc["source_refutations"] == 1
    assert sc["fabrication_rate"] == "0/3" and sc["fabricated_count"] == 0
    assert sc["open_reportables"] == ["P"]
    assert sc["routing_allowed"] is False and sc["is_gate"] is False


def test_checkpoint_is_advisory_only(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    m.record({"candidate_id": "S", "runtime_status": "not_run", "conversion_outcome": "static_false_positive",
              "deploy_complexity": "too_heavy"})
    ck = m.checkpoint()
    assert ck["blocking"] is False and ck["routing_allowed"] is False
    assert "scorecard" in ck and "open_reportables" in ck


def test_dashboard_scorecard_endpoint_read_only():
    from fastapi.testclient import TestClient
    import dashboard
    c = TestClient(dashboard.app)
    r = c.get("/api/campaign-scorecard")
    assert r.status_code == 200
    j = r.json()
    assert "fabrication_rate" in j and j["routing_allowed"] is False


# --------------------------------------------------------------------------- P166 Protocol vNext (Step 5/6)
def _fresh_pred(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    monkeypatch.setattr(m, "PRED_LOG", tmp_path / "prediction_log.jsonl")
    return m


def test_log_prediction_validates_outcome(tmp_path, monkeypatch):
    import pytest
    m = _fresh_pred(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        m.log_prediction("H10", "totally_bogus", "x")
    row = m.log_prediction("H10", "static_false_positive", "expect a guard")
    assert row["predicted_outcome"] == "static_false_positive" and row["routing_allowed"] is False


def test_calibration_joins_prediction_and_outcome(tmp_path, monkeypatch):
    m = _fresh_pred(tmp_path, monkeypatch)
    # correct prediction (refuted predicted, refuted recorded)
    m.log_prediction("A", "static_false_positive", "guard")
    m.record({"candidate_id": "A", "runtime_status": "not_run", "conversion_outcome": "static_false_positive",
              "deploy_complexity": "too_heavy"})
    # wrong prediction (reportable predicted, refuted recorded)
    m.log_prediction("B", "reportable_candidate_needs_human_review", "looked strong")
    m.record({"candidate_id": "B", "runtime_status": "runtime_refuted", "conversion_outcome": "runtime_refuted"})
    # unresolved (predicted, not yet recorded)
    m.log_prediction("C", "runtime_confirmed", "pending")
    cal = m.calibration()
    assert cal["predictions"] == 3 and cal["resolved"] == 2 and cal["correct"] == 1
    assert cal["accuracy"] == "1/2" and cal["unresolved"] == ["C"]


def test_scorecard_has_protocol_metrics(tmp_path, monkeypatch):
    m = _fresh_pred(tmp_path, monkeypatch)
    m.log_prediction("P", "reportable_candidate_needs_human_review", "")
    m.record({"candidate_id": "P", "runtime_status": "runtime_confirmed",
              "conversion_outcome": "reportable_candidate_needs_human_review", "harness_path": "pocs/p",
              "attacker_recipient_status": "attacker_is_recipient", "profit_source": "reward_redistribution",
              "permission_model": "permissionless", "harness_built": True, "predicted_outcome": "reportable_candidate_needs_human_review"})
    sc = m.scorecard()
    assert sc["reportables_per_harness"] == "1/1"
    assert sc["prediction_accuracy"] == "1/1"
    assert sc["fabrication_rate"] == "0/1"


def test_record_accepts_learning_fields_and_still_blocks_fabrication(tmp_path, monkeypatch):
    import pytest
    m = _fresh_pred(tmp_path, monkeypatch)
    ok = m.record({"candidate_id": "L", "runtime_status": "not_run", "conversion_outcome": "static_false_positive",
                   "attacker_recipient_status": "value_to_fixed_party", "profit_source": "none",
                   "permission_model": "permissioned", "harness_built": False, "deploy_complexity": "too_heavy"})
    assert ok["permission_model"] == "permissioned" and ok["harness_built"] is False
    with pytest.raises(ValueError):
        m.record({"candidate_id": "FAB", "conversion_outcome": "runtime_confirmed"})  # positive, no evidence


def test_dashboard_calibration_endpoint_read_only():
    from fastapi.testclient import TestClient
    import dashboard
    c = TestClient(dashboard.app)
    r = c.get("/api/campaign-calibration")
    assert r.status_code == 200 and r.json()["routing_allowed"] is False
    sc = c.get("/api/campaign-scorecard").json()
    assert "reportables_per_harness" in sc and "prediction_accuracy" in sc


# --------------------------------------------------------------------------- P167 candidate-generation hygiene
def test_classify_signal_source():
    assert oac.classify_signal_source("lib/openzeppelin/contracts/mocks/ERC1271WalletMock.sol") == "vendored_lib"
    assert oac.classify_signal_source("contracts/mocks/MockToken.sol") == "mock"
    assert oac.classify_signal_source("test/Foo.t.sol") == "protocol_test"
    assert oac.classify_signal_source("src/Gauge.s.sol") == "protocol_test"   # Foundry script by filename
    assert oac.classify_signal_source("out/Math.sol") == "generated"
    assert oac.classify_signal_source("src/Vault.sol") == "protocol_src"


def test_scan_signals_excludes_vendored_and_mocks(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "lib" / "oz" / "mocks").mkdir(parents=True)
    (tmp_path / "test").mkdir()
    (tmp_path / "src" / "Vault.sol").write_text("function claim() { originalOwner; }")
    (tmp_path / "lib" / "oz" / "mocks" / "M.sol").write_text("address originalOwner;")
    (tmp_path / "test" / "T.t.sol").write_text("originalOwner test;")
    hits = oac.scan_signals(str(tmp_path), "originalOwner")
    assert len(hits) == 1 and hits[0]["signal_source"] == "protocol_src" and "Vault.sol" in hits[0]["path"]
    allh = oac.scan_signals(str(tmp_path), "originalOwner", include_nonprotocol=True)
    assert {h["signal_source"] for h in allh} == {"protocol_src", "vendored_lib", "protocol_test"}


def test_hygiene_gate_rejects_nonprotocol_signal(tmp_path, monkeypatch):
    import pytest
    m = _fresh(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        m.record({"candidate_id": "JUNK", "conversion_outcome": "static_false_positive",
                  "candidate_signal_source": "vendored_lib"})
    # research_override lets a documented-noise lesson (e.g. H10) be recorded
    ok = m.record({"candidate_id": "NOISE", "conversion_outcome": "static_false_positive",
                   "candidate_signal_source": "vendored_lib", "research_override": True})
    assert ok["candidate_signal_source"] == "vendored_lib"
    # a clean protocol_src candidate records normally
    ok2 = m.record({"candidate_id": "CLEAN", "conversion_outcome": "static_false_positive",
                    "candidate_signal_source": "protocol_src"})
    assert ok2["candidate_signal_source"] == "protocol_src"
    # legacy rows with no signal_source still record (backward-compatible)
    ok3 = m.record({"candidate_id": "LEGACY", "conversion_outcome": "runtime_refuted"})
    assert ok3["candidate_id"] == "LEGACY"


def test_h10_signal_would_be_filtered_live():
    # the real revert-lend originalOwner signal must drop to 0 protocol_src hits (proves H10 was junk input)
    hits = oac.scan_signals("audits/revert-lend-2024-03-strict-eval/contracts", "originalOwner")
    assert hits == []


# --------------------------------------------------------------------------- P169 bug_family field
def test_record_accepts_bug_family(tmp_path, monkeypatch):
    m = _fresh(tmp_path, monkeypatch)
    ok = m.record({"candidate_id": "MF", "conversion_outcome": "static_false_positive",
                   "candidate_signal_source": "protocol_src", "bug_family": "rounding_accounting_drift"})
    assert ok["bug_family"] == "rounding_accounting_drift" and ok["submission_ready"] is False
