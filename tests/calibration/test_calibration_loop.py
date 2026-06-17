"""Close-the-calibration-loop proof. Two things:
(1) compute_metrics goes from 'unmeasured' to a real FP/recall number the moment a human ground-truth record
    exists for a pipeline-accepted finding — i.e. the loop is operational; it only awaits human outcomes.
(2) calibration_worklist enumerates accepted real-world findings with no recorded outcome (and skips ones that
    DO have an outcome) — the actionable human worklist. Hermetic: tmp audits, monkeypatched audit set."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import compute_metrics as cm  # noqa: E402
import calibration_worklist as cw  # noqa: E402


def _audit(adir: Path, *, accepted=(), ground_truth=()):
    (adir / "data" / "triage").mkdir(parents=True, exist_ok=True)
    (adir / "data" / "evaluation").mkdir(parents=True, exist_ok=True)
    (adir / "data" / "runtime_poc").mkdir(parents=True, exist_ok=True)
    (adir / "output").mkdir(parents=True, exist_ok=True)
    (adir / "meta.json").write_text(json.dumps({"audit_id": adir.name}))
    if accepted:
        (adir / "data" / "triage" / "submit.jsonl").write_text(
            "".join(json.dumps({"finding_id": fid}) + "\n" for fid in accepted))
        (adir / "output" / "merged_findings.json").write_text(json.dumps(
            {"findings": [{"id": fid, "title": f"t{fid}", "severity": "high"} for fid in accepted]}))
    if ground_truth:
        (adir / "data" / "evaluation" / "ground_truth.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in ground_truth))


@pytest.fixture
def realworld(tmp_path, monkeypatch):
    """A single real-world (non-eval) audit, wired into compute_metrics + calibration_worklist."""
    audits = tmp_path / "audits"
    adir = audits / "hunt-2026-06"          # no eval suffix -> counts as real-world
    adir.mkdir(parents=True)
    for mod in (cm, cw):
        monkeypatch.setattr(mod, "_AUDITS_DIR", audits)
    monkeypatch.setattr(cm, "list_audits", lambda: [{"audit_id": "hunt-2026-06"}])
    monkeypatch.setattr(cm, "_PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(cw, "_PROJECT_ROOT", tmp_path)
    return adir


def test_unmeasured_until_an_outcome_is_recorded(realworld):
    # Accepted finding, no ground truth -> FP/recall unmeasured.
    _audit(realworld, accepted=["F-1"])
    m = cm.compute()
    assert m["false_positive_rate"]["state"].startswith("unmeasured")
    assert m["recall_on_valid"]["state"].startswith("unmeasured")


def test_recorded_valid_outcome_makes_recall_measured(realworld):
    # Human records F-1 as accepted/valid -> recall becomes measured (1/1), FP measured (0/1).
    _audit(realworld, accepted=["F-1"],
           ground_truth=[{"finding_id": "F-1", "ground_truth_outcome": "accepted",
                          "ground_truth_severity": "high", "agent": "logic", "vuln_type": "reentrancy"}])
    m = cm.compute()
    assert m["recall_on_valid"]["value"] == 1.0 and m["recall_on_valid"]["n"] == 1
    assert m["false_positive_rate"]["value"] == 0.0 and m["false_positive_rate"]["n"] == 1


def test_recorded_invalid_outcome_counts_as_false_positive(realworld):
    # Pipeline accepted F-1 but human says invalid -> FP rate 1/1.
    _audit(realworld, accepted=["F-1"],
           ground_truth=[{"finding_id": "F-1", "ground_truth_outcome": "invalid",
                          "ground_truth_severity": "invalid", "agent": "logic", "vuln_type": "x"}])
    m = cm.compute()
    assert m["false_positive_rate"]["value"] == 1.0 and m["false_positive_rate"]["n"] == 1


def test_worklist_lists_unrecorded_and_skips_recorded(realworld):
    _audit(realworld, accepted=["F-1", "F-2"],
           ground_truth=[{"finding_id": "F-1", "ground_truth_outcome": "accepted",
                          "ground_truth_severity": "high"}])
    doc = cw.build()
    ids = {p["finding_id"] for p in doc["pending"]}
    assert ids == {"F-2"}                       # F-1 has an outcome -> not pending
    assert doc["pending_total"] == 1
    assert (realworld.parent.parent / "documentation" / "metrics" / "outcome_worklist.md").exists()
