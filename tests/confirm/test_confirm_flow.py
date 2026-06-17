"""Credit-free /confirm flow (api-free Step 3.5): confirm_prepare stages ONLY High/Critical; confirm_write
computes confirmation_score = yes/run + human_review_required vs threshold, validates against staged bundles, and
refuses to invent confirmations. Hermetic via per-module audit_path patching."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import confirm_prepare as cp  # noqa: E402
import confirm_write as cw  # noqa: E402


@pytest.fixture
def audit(tmp_path, monkeypatch):
    def ap(*parts):
        return tmp_path.joinpath(*parts)
    monkeypatch.setattr(cp, "audit_path", ap)
    monkeypatch.setattr(cw, "audit_path", ap)
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    return tmp_path, ap


def _merged(audit, findings):
    tmp, ap = audit
    ap("output", "merged_findings.json").write_text(json.dumps({"findings": findings}))


def test_prepare_stages_high_critical_only(audit, monkeypatch):
    tmp, ap = audit
    _merged(audit, [
        {"id": "H-1", "severity": "High", "title": "h", "location": {}},
        {"id": "C-1", "severity": "Critical", "title": "c", "location": {}},
        {"id": "M-1", "severity": "Medium", "title": "m", "location": {}},
    ])
    monkeypatch.setattr(sys, "argv", ["confirm_prepare"])
    assert cp.main() == 0
    idx = json.loads(ap("output", "confirm", "_bundles", "index.json").read_text())
    ids = {r["finding_id"]: r for r in idx}
    assert set(ids) == {"H-1", "C-1"}            # Medium not staged
    assert ids["H-1"]["passes_required"] == 3    # High = 3 passes
    assert ids["C-1"]["passes_required"] == 5    # Critical = 5 passes


def test_write_computes_score_and_human_review(audit, monkeypatch):
    tmp, ap = audit
    _merged(audit, [{"id": "H-1", "severity": "High", "title": "h", "location": {}},
                    {"id": "H-2", "severity": "High", "title": "h2", "location": {}}])
    monkeypatch.setattr(sys, "argv", ["confirm_prepare"])
    cp.main()
    ap("output", "confirm", "_decisions.json").write_text(json.dumps([
        {"id": "H-1", "passes_run": 3, "passes_yes": 3},   # 1.0 -> confirmed
        {"id": "H-2", "passes_run": 3, "passes_yes": 1},   # 0.33 -> human review
    ]))
    monkeypatch.setattr(sys, "argv", ["confirm_write"])
    assert cw.main() == 0
    out = {f["id"]: f for f in json.loads(ap("output", "findings_confirmed.json").read_text())["findings"]}
    assert out["H-1"]["confirmation_score"] == 1.0 and out["H-1"]["human_review_required"] is False
    assert out["H-2"]["confirmation_score"] == 0.333 and out["H-2"]["human_review_required"] is True


def test_write_rejects_unstaged_and_invalid(audit, monkeypatch):
    tmp, ap = audit
    _merged(audit, [{"id": "H-1", "severity": "High", "title": "h", "location": {}}])
    monkeypatch.setattr(sys, "argv", ["confirm_prepare"])
    cp.main()
    # X-9 was never staged (not High/Critical) -> rejected; H-1 passes_run mismatch -> rejected
    ap("output", "confirm", "_decisions.json").write_text(json.dumps([
        {"id": "X-9", "passes_run": 3, "passes_yes": 3},
        {"id": "H-1", "passes_run": 2, "passes_yes": 2},   # required is 3
    ]))
    monkeypatch.setattr(sys, "argv", ["confirm_write"])
    rc = cw.main()
    assert rc == 2  # nothing valid written
    assert not ap("output", "findings_confirmed.json").exists()
