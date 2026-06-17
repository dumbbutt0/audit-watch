"""Task 2 consumer rewire: the dashboard and the submission pack must read READY/state from the ONE
canonical record (output/candidates/<id>.json), not re-derive it. This locks the three-way agreement —
record.state, the dashboard's `submission_ready`, and the pack's kept-submit set all match — plus the
graceful fallback (no record => caller's legacy `submission_ready` is left untouched)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_context as ac  # noqa: E402
import build_candidate_records as bcr  # noqa: E402
import candidate_records as cr  # noqa: E402


def _audit(tmp_path, findings, *, confirmed=None, triage=None, poc=None):
    out = tmp_path / "output"
    (out / "candidates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "triage").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "runtime_poc").mkdir(parents=True, exist_ok=True)
    (out / "merged_findings.json").write_text(json.dumps({"findings": findings}))
    if confirmed is not None:
        (out / "findings_confirmed.json").write_text(json.dumps(confirmed))
    if poc:
        (tmp_path / "data" / "runtime_poc" / "results.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in poc))
    if triage:
        for bucket, rows in triage.items():
            (tmp_path / "data" / "triage" / f"{bucket}.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in rows))


@pytest.fixture
def patched(tmp_path, monkeypatch):
    monkeypatch.setattr(ac, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(ac, "audit_language", lambda *a, **k: "solidity")
    monkeypatch.setattr(ac, "get_active_audit", lambda: {"audit_id": "t"})
    return tmp_path


# H-1: confirmed + proved + submit + full report fields -> canonical READY.
# H-2: same triage submit BUT unconfirmed -> canonical human_pending (the desync the rewire kills).
_FINDINGS = [
    {"id": "H-1", "severity": "High", "title": "a", "location": {"function": "f"}, "recommendation": "fix"},
    {"id": "H-2", "severity": "High", "title": "b", "location": {"function": "g"}, "recommendation": "fix"},
]
_CONFIRMED = {"findings": [{"id": "H-1", "confirmation_score": 1.0, "confirmation_passes": 3,
                            "human_review_required": False}]}
_POC = [{"finding_id": "H-1", "status": "proved", "runtime_level": 3}]
_TRIAGE = {"submit": [
    {"finding_id": "H-1", "triage_status": "submit",
     "impact": {"victim": "LPs"}, "attacker_model": {"attacker_type": "unprivileged"}},
    {"finding_id": "H-2", "triage_status": "submit",
     "impact": {"victim": "LPs"}, "attacker_model": {"attacker_type": "unprivileged"}},
]}


def test_dashboard_overlay_matches_record_state(patched):
    _audit(patched, _FINDINGS, confirmed=_CONFIRMED, poc=_POC, triage=_TRIAGE)
    bcr.build()
    records = cr.load_records(patched / "output")
    assert records["H-1"]["state"] == "ready"
    assert records["H-2"]["state"] == "human_pending"

    # Dashboard would compute submission_ready=True for BOTH via the legacy triage heuristic (both submit).
    # The canonical overlay must FORCE it to the record's definition: H-1 ready, H-2 not.
    for fid in ("H-1", "H-2"):
        # pretend the legacy triage heuristic said "ready" (submission_ready=True) for both
        f = cr.overlay({"submission_ready": True}, records[fid])
        assert f["state"] == records[fid]["state"]
        assert f["submission_ready"] is cr.is_ready(records[fid])
        assert f["who_loses"] == records[fid]["evidence"]["who_loses"]
    assert cr.overlay({"submission_ready": True}, records["H-2"])["submission_ready"] is False


def test_pack_keeps_only_canonical_ready(patched):
    _audit(patched, _FINDINGS, confirmed=_CONFIRMED, poc=_POC, triage=_TRIAGE)
    bcr.build()
    records = cr.load_records(patched / "output")
    submit_rows = [{"finding_id": "H-1"}, {"finding_id": "H-2"}]
    ready, held = cr.apply_canonical_ready(submit_rows, records)
    assert [r["finding_id"] for r in ready] == ["H-1"]
    assert [h["finding_id"] for h in held] == ["H-2"]
    assert held[0]["_canonical_state"] == "human_pending"


def test_three_way_agreement(patched):
    _audit(patched, _FINDINGS, confirmed=_CONFIRMED, poc=_POC, triage=_TRIAGE)
    bcr.build()
    records = cr.load_records(patched / "output")
    record_ready = {fid for fid, r in records.items() if cr.is_ready(r)}
    dash_ready = {fid for fid, r in records.items()
                  if cr.overlay({"submission_ready": False}, r)["submission_ready"]}
    pack_ready = {r["finding_id"]
                  for r in cr.apply_canonical_ready([{"finding_id": f} for f in records], records)[0]}
    assert record_ready == dash_ready == pack_ready == {"H-1"}


def test_graceful_fallback_when_no_record():
    # No canonical record -> load returns {}, overlay leaves the caller's submission_ready untouched,
    # apply_canonical_ready passes everything through (legacy behavior preserved on old audits).
    assert cr.load_records(Path("/nonexistent/output")) == {}
    f = cr.overlay({"submission_ready": True}, None)
    assert f["submission_ready"] is True and f["state"] is None and f["readiness_blockers"] == []
    rows = [{"finding_id": "X"}]
    assert cr.apply_canonical_ready(rows, {}) == (rows, [])
