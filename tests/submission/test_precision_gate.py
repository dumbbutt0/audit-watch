"""precision_gate.py — the real-world submission precision gate. Mirrors confirm_gate's contract:
eval mode NEVER blocks (exit 0); submission mode HARD-FAILS only on a confident negative
(not_wired / design-match / confirmed-duplicate) for a READY High/Critical finding; checklist_required
WARNs; the override env forces exit 0. It never mutates finding state."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import precision_gate as pg  # noqa: E402


def _setup(tmp_path, *, reach="checklist_required", design="low", dupe_action=None,
           severity="High", state="ready"):
    out = tmp_path / "output"
    (out / "candidates").mkdir(parents=True, exist_ok=True)
    (out / "submission_risk.json").write_text(json.dumps({"findings": [
        {"finding_id": "F-1",
         "deployment_reachability_risk": {"level": reach, "rationale": "r"},
         "design_acceptance_risk": ({"level": "match", "name": "nav_tolerance"} if design == "match"
                                    else {"level": "low"}),
         "novelty_risk": {"level": "checklist_required"}},
    ]}))
    (out / "merged_findings.json").write_text(json.dumps({"findings": [
        {"id": "F-1", "severity": severity},
    ]}))
    (out / "candidates" / "F-1.json").write_text(json.dumps(
        {"id": "F-1", "state": state, "classification": {"severity": severity}}))
    if dupe_action:
        td = tmp_path / "data" / "triage"
        td.mkdir(parents=True, exist_ok=True)
        (td / "dupe_screen_results.jsonl").write_text(
            json.dumps({"finding_id": "F-1", "action": dupe_action, "registry_match": None,
                        "registry_score": 0.0}) + "\n")
    return out


@pytest.fixture
def patch_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(pg, "audit_path", lambda *p: tmp_path.joinpath(*p))
    return tmp_path


def _run(monkeypatch, mode, override=False):
    argv = ["precision_gate.py", "--mode", mode, "--quiet"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.delenv("AUDITWATCH_PRECISION_OVERRIDE", raising=False)
    if override:
        monkeypatch.setenv("AUDITWATCH_PRECISION_OVERRIDE", "1")
    return pg.main()


def _gate_doc(tmp_path):
    return json.loads((tmp_path / "output" / "precision_gate.json").read_text())


def test_eval_never_blocks_even_on_not_wired(patch_audit, monkeypatch):
    _setup(patch_audit, reach="not_wired")
    assert _run(monkeypatch, "eval") == 0
    d = _gate_doc(patch_audit)
    assert d["blocked"] is False and d["blocking"] == []
    assert d["would_block"] and d["would_block"][0]["finding_id"] == "F-1"


def test_submission_blocks_not_wired(patch_audit, monkeypatch):
    _setup(patch_audit, reach="not_wired")
    assert _run(monkeypatch, "submission") == 1
    d = _gate_doc(patch_audit)
    assert d["blocked"] is True
    assert d["blocking"][0]["axes"][0]["axis"] == "deployment_reachability"


def test_submission_blocks_design_match(patch_audit, monkeypatch):
    _setup(patch_audit, design="match")
    assert _run(monkeypatch, "submission") == 1
    assert _gate_doc(patch_audit)["blocking"][0]["axes"][0]["axis"] == "design_acceptance"


def test_submission_blocks_confirmed_duplicate(patch_audit, monkeypatch):
    _setup(patch_audit, dupe_action="human_review")
    assert _run(monkeypatch, "submission") == 1
    assert _gate_doc(patch_audit)["blocking"][0]["axes"][0]["axis"] == "novelty"


def test_checklist_required_warns_not_blocks(patch_audit, monkeypatch):
    _setup(patch_audit, reach="checklist_required")
    assert _run(monkeypatch, "submission") == 0
    d = _gate_doc(patch_audit)
    assert d["blocked"] is False and d["warnings"]


def test_dupe_warn_does_not_block(patch_audit, monkeypatch):
    _setup(patch_audit, dupe_action="warn")
    assert _run(monkeypatch, "submission") == 0
    assert _gate_doc(patch_audit)["blocked"] is False


def test_override_forces_pass(patch_audit, monkeypatch):
    _setup(patch_audit, reach="not_wired")
    assert _run(monkeypatch, "submission", override=True) == 0
    d = _gate_doc(patch_audit)
    assert d["blocked"] is False and d["override"] is True


def test_medium_severity_not_blocked(patch_audit, monkeypatch):
    _setup(patch_audit, reach="not_wired", severity="Medium")
    assert _run(monkeypatch, "submission") == 0
    assert _gate_doc(patch_audit)["blocked"] is False


def test_non_ready_state_not_blocked(patch_audit, monkeypatch):
    _setup(patch_audit, reach="not_wired", state="human_pending")
    assert _run(monkeypatch, "submission") == 0
    assert _gate_doc(patch_audit)["blocked"] is False


def test_missing_submission_risk_raises(patch_audit, monkeypatch):
    (patch_audit / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sys, "argv", ["precision_gate.py", "--mode", "submission"])
    with pytest.raises(SystemExit):
        pg.main()
