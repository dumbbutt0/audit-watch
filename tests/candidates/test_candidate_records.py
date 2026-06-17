"""Canonical per-finding record + the confirmation enforcement (review tasks 1+2). Hermetic: builds a tmp audit
workspace, monkeypatches audit_context, and asserts the single derived `state`. Locks the precision rule: an
unconfirmed High/Critical can NEVER be `ready` (it routes to human_pending), so skipping confirmation in the
default api-free mode no longer lets unconfirmed High/Critical look submission-ready."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_context as ac  # noqa: E402
import build_candidate_records as bcr  # noqa: E402


def _audit(tmp_path, findings, *, confirmed=None, triage=None, gates=None, fp=None, poc=None, minconf=None):
    out = tmp_path / "output"
    (out / "candidates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "fp_autopsies").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "triage").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "runtime_poc").mkdir(parents=True, exist_ok=True)
    (out / "merged_findings.json").write_text(json.dumps({"findings": findings}))
    if confirmed is not None:
        (out / "findings_confirmed.json").write_text(json.dumps(confirmed))
    if minconf is not None:
        (out / "min_confirm_gate.json").write_text(json.dumps(minconf))
    for name, rows in (("fp_autopsies/pattern_check_results.jsonl", fp),
                       ("triage/gate_results.jsonl", gates),
                       ("runtime_poc/results.jsonl", poc)):
        if rows:
            (tmp_path / "data" / name).write_text("".join(json.dumps(r) + "\n" for r in rows))
    if triage:
        for bucket, rows in triage.items():
            (tmp_path / "data" / "triage" / f"{bucket}.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in rows))


@pytest.fixture
def patched(tmp_path, monkeypatch):
    monkeypatch.setattr(ac, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(ac, "audit_language", lambda *a, **k: "rust")
    monkeypatch.setattr(ac, "get_active_audit", lambda: {"audit_id": "t"})
    return tmp_path


def _state(tmp_path, fid):
    return json.loads((tmp_path / "output" / "candidates" / f"{fid}.json").read_text())["state"]


def test_high_unconfirmed_is_human_pending(patched):
    _audit(patched, [{"id": "H-1", "severity": "High", "title": "x", "location": {}}])
    bcr.build()
    rec = json.loads((patched / "output" / "candidates" / "H-1.json").read_text())
    assert rec["state"] == "human_pending"
    assert any("unconfirmed High/Critical" in b for b in rec["readiness_blockers"])


def test_medium_unconfirmed_is_candidate(patched):
    # Medium does not require confirmation -> not blocked by it
    _audit(patched, [{"id": "M-1", "severity": "Medium", "title": "x", "location": {}}])
    bcr.build()
    assert _state(patched, "M-1") == "candidate"


_READY_FINDING = {"id": "H-1", "severity": "High", "title": "x", "location": {"function": "f"},
                  "recommendation": "add the guard"}  # suggested_fix present
_READY_TRIAGE = {"submit": [{"finding_id": "H-1", "triage_status": "submit",
                             "impact": {"victim": "LPs"}, "attacker_model": {"attacker_type": "unprivileged"}}]}


def test_high_confirmed_proved_submit_is_ready(patched):
    _audit(
        patched, [_READY_FINDING],
        confirmed={"findings": [{"id": "H-1", "confirmation_score": 1.0, "confirmation_passes": 3,
                                 "human_review_required": False}]},
        poc=[{"finding_id": "H-1", "status": "proved", "runtime_level": 3}],
        triage=_READY_TRIAGE,
    )
    bcr.build()
    assert _state(patched, "H-1") == "ready"


def test_high_confirmed_but_no_poc_is_poc_required(patched):
    _audit(
        patched, [_READY_FINDING],  # evidence fields present so we isolate the missing-PoC path
        confirmed={"findings": [{"id": "H-1", "confirmation_score": 1.0, "human_review_required": False}]},
        triage=_READY_TRIAGE,
    )
    bcr.build()
    assert _state(patched, "H-1") == "poc_required"  # High needs an L3 PoC even if confirmed+submit


def test_high_missing_who_loses_is_human_pending(patched):
    # confirmed + proved + submit, but no who_loses/who_gains/suggested_fix -> not ready (T10)
    _audit(
        patched, [{"id": "H-1", "severity": "High", "title": "x", "location": {"function": "f"}}],
        confirmed={"findings": [{"id": "H-1", "confirmation_score": 1.0, "human_review_required": False}]},
        poc=[{"finding_id": "H-1", "status": "proved", "runtime_level": 3}],
        triage={"submit": [{"finding_id": "H-1", "triage_status": "submit"}]},
    )
    bcr.build()
    rec = json.loads((patched / "output" / "candidates" / "H-1.json").read_text())
    assert rec["state"] == "human_pending"
    assert any("who_loses" in b for b in rec["readiness_blockers"])


def test_fp_reject_is_rejected(patched):
    _audit(patched, [{"id": "M-1", "severity": "Medium", "title": "x", "location": {}}],
           fp=[{"finding_id": "M-1", "recommended_action": "reject"}])
    bcr.build()
    assert _state(patched, "M-1") == "rejected"


def test_gate_fail_is_rejected(patched):
    _audit(patched, [{"id": "H-1", "severity": "High", "title": "x", "location": {}}],
           gates=[{"finding_id": "H-1", "gate_results": [{"name": "reachability", "verdict": "FAIL"}]}])
    bcr.build()
    assert _state(patched, "H-1") == "rejected"


def test_confirmation_skipped_blocks_high(patched):
    # api-free default: multi_pass writes skipped:true with empty findings -> High still can't be ready
    _audit(patched, [{"id": "H-1", "severity": "High", "title": "x", "location": {}}],
           confirmed={"skipped": True, "findings": []},
           triage={"submit": [{"finding_id": "H-1", "triage_status": "submit"}]},
           poc=[{"finding_id": "H-1", "status": "proved", "runtime_level": 3}])
    bcr.build()
    rec = json.loads((patched / "output" / "candidates" / "H-1.json").read_text())
    assert rec["state"] == "human_pending"
    assert any("SKIPPED" in b for b in rec["readiness_blockers"])
