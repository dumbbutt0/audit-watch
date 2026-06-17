"""P140 — tests for the value-provenance completion loop (manual /deep-pass result ingestion).

No protocol-specific strings. Proves: pending stays pending without an artifact, valid completion ->
completed, strong_clear renders cleared, finding renders advisory-only NOT confirmed, unsafe artifacts
(submission_ready / advisory_only=false) are quarantined, malformed/unmatched never mutate or block,
completed results never enter Validated Findings / change the confirmed count, the ingestion report is
accurate, a missing results dir is safe, and re-running ingestion is idempotent.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_value_provenance_advisories as rv  # noqa: E402
import generate_review_gate as grg  # noqa: E402

CFG = dict(rv.DEFAULT_CFG)


def _job(advisory_id="VP-LibOracle._getValue", contract="LibOracle", function="_getValue"):
    return {"advisory_id": advisory_id, "audit_id": "a", "contract": contract, "function": function,
            "file_path": "contracts/LibOracle.sol", "auto_run_status": "pending_manual_execution",
            "advisory_only": True, "submission_ready": False, "requires_human_review": True,
            "prompt_decision": "pending", "prompt_confidence": None, "mechanism_summary": "vp loop",
            "output_path": "output/value_provenance_jobs/VP-LibOracle._getValue.md"}


def _report(jobs=None):
    return {"ran": True, "results": jobs if jobs is not None else [_job()]}


def _art(job_id="VP-LibOracle._getValue", decision="finding", **over):
    a = {"job_id": job_id, "audit_id": "a", "contract": "LibOracle", "function": "_getValue",
         "file_path": "contracts/LibOracle.sol", "prompt_name": "deep_pass_value_provenance",
         "execution_mode": "manual_in_session", "completed_at": "2026-06-04T00:00:00+00:00",
         "reviewer_or_runner": "operator", "prompt_decision": decision, "confidence": "high",
         "mechanism_summary": "loop reuses stale subject", "source_evidence_summary": "line 2",
         "rejected_alternatives": "n/a", "impact_summary": "mispricing", "limitations": "needs PoC",
         "recommended_next_step": "human_review", "advisory_only": True, "submission_ready": False,
         "requires_human_review": True, "source_result_path": "docs/p137.md", "_file": "r.json"}
    a.update(over)
    return a


# 1. pending stays pending when no result exists
def test_pending_stays_pending_no_artifact():
    rep, ing = rv.ingest_results(_report(), [], CFG)
    assert rep["results"][0]["auto_run_status"] == "pending_manual_execution"
    assert ing["summary"]["accepted"] == 0 and ing["summary"]["pending_remaining"] == 1


# 2. valid completion updates job to completed (triplet preserved)
def test_valid_completion_to_completed():
    rep, ing = rv.ingest_results(_report(), [_art()], CFG)
    r = rep["results"][0]
    assert r["auto_run_status"] == "completed" and r["prompt_decision"] == "finding"
    assert r["advisory_only"] is True and r["submission_ready"] is False and r["requires_human_review"] is True
    assert r["prompt_confidence"] == "high" and r["reviewer_or_runner"] == "operator"
    assert ing["summary"]["accepted"] == 1 and ing["summary"]["by_decision"]["finding"] == 1


# 5. submission_ready=true is quarantined (job untouched)
def test_submission_ready_quarantined():
    rep, ing = rv.ingest_results(_report(), [_art(submission_ready=True)], CFG)
    assert rep["results"][0]["auto_run_status"] == "pending_manual_execution"
    assert ing["summary"]["rejected"] == 1 and "submission_ready" in ing["rejected"][0]["reason"]


# 6. advisory_only=false is quarantined
def test_advisory_only_false_quarantined():
    rep, ing = rv.ingest_results(_report(), [_art(advisory_only=False)], CFG)
    assert rep["results"][0]["auto_run_status"] == "pending_manual_execution"
    assert ing["summary"]["rejected"] == 1 and "advisory_only" in ing["rejected"][0]["reason"]


# 6b. forbidden confirmed=true / final_severity quarantined
def test_confirmed_and_severity_quarantined():
    _, ing1 = rv.ingest_results(_report(), [_art(confirmed=True)], CFG)
    _, ing2 = rv.ingest_results(_report(), [_art(final_severity="High")], CFG)
    assert ing1["summary"]["rejected"] == 1 and "confirmed" in ing1["rejected"][0]["reason"]
    assert ing2["summary"]["rejected"] == 1 and "final_severity" in ing2["rejected"][0]["reason"]
    # but a non-binding-labelled severity is allowed
    _, ing3 = rv.ingest_results(_report(), [_art(final_severity="High", final_severity_non_binding=True)], CFG)
    assert ing3["summary"]["accepted"] == 1


# 7. malformed result does not block
def test_malformed_no_block():
    rep, ing = rv.ingest_results(_report(), [{"_file": "bad.json", "_malformed": True}], CFG)
    assert rep["results"][0]["auto_run_status"] == "pending_manual_execution"
    assert ing["summary"]["rejected"] == 1 and ing["ran"] is True


# 8. unmatched result does not mutate jobs
def test_unmatched_no_mutation():
    rep, ing = rv.ingest_results(_report(), [_art(job_id="VP-Other.fn")], CFG)
    assert rep["results"][0]["auto_run_status"] == "pending_manual_execution"
    assert ing["summary"]["unmatched"] == 1 and ing["unmatched"] == ["VP-Other.fn"]


# 11. ingestion report records accepted/rejected/unmatched counts
def test_ingestion_report_counts():
    jobs = [_job(), _job(advisory_id="VP-Lib.g", function="g")]
    arts = [_art(), _art(job_id="VP-Other.fn"), _art(submission_ready=True), {"_file": "b.json", "_malformed": True}]
    rep, ing = rv.ingest_results(_report(jobs), arts, CFG)
    s = ing["summary"]
    assert s["accepted"] == 1 and s["unmatched"] == 1 and s["rejected"] == 2
    assert s["completed"] == 1 and s["pending_remaining"] == 1


# 12. missing results directory is safe
def test_missing_results_dir_safe(tmp_path):
    assert rv._load_manual_results(tmp_path / "does_not_exist") == []


# 13. rerun is idempotent
def test_rerun_idempotent():
    rep1, _ = rv.ingest_results(_report(), [_art()], CFG)
    rep2, ing2 = rv.ingest_results(rep1, [_art()], CFG)
    assert rep1["results"][0] == rep2["results"][0]
    assert ing2["summary"]["accepted"] == 1 and ing2["summary"]["completed"] == 1


# error decision -> failed status
def test_error_decision_failed():
    rep, _ = rv.ingest_results(_report(), [_art(decision="error", confidence=None)], CFG)
    assert rep["results"][0]["auto_run_status"] == "failed"


# --- review-gate rendering (3, 4, 9, 10) ---
def _setup_rg(tmp_path, monkeypatch, results, confirmed=0):
    out = tmp_path / "output"; out.mkdir()
    tri = tmp_path / "data" / "triage"; tri.mkdir(parents=True)
    for i in range(confirmed):
        (tri / f"F-{i}.md").write_text(f"# Confirmed {i}\n\nCONFIRMED\n")
    (out / "value_provenance_advisory_results.json").write_text(json.dumps({"ran": True, "results": results}))

    def ap(*parts):
        p = tmp_path.joinpath(*parts); p.parent.mkdir(parents=True, exist_ok=True); return p
    monkeypatch.setattr(grg, "audit_path", ap)
    monkeypatch.setattr(grg, "get_audit_meta", lambda: {"audit_id": "t", "name": "T"})
    monkeypatch.setattr(grg, "write_session", lambda d: None)
    return out


def _completed(decision="finding"):
    j = _job()
    j.update({"auto_run_status": "completed", "prompt_decision": decision, "prompt_confidence": "high",
              "recommended_next_step": "human_review", "mechanism_summary": "loop reuses stale subject"})
    return j


# 3. strong_clear completion renders safely (cleared)
def test_review_gate_strong_clear_cleared(tmp_path, monkeypatch):
    _setup_rg(tmp_path, monkeypatch, [_completed("strong_clear")])
    with pytest.raises(SystemExit):
        grg.main()
    doc = (tmp_path / "output" / "review_gate.md").read_text()
    assert "### Value Provenance Deep-Pass Results — advisory only" in doc
    assert "cleared advisory context" in doc


# 4. finding completion renders as advisory-only, NOT confirmed  /  9. not in Validated Findings
def test_review_gate_finding_not_confirmed(tmp_path, monkeypatch):
    _setup_rg(tmp_path, monkeypatch, [_completed("finding")], confirmed=1)
    with pytest.raises(SystemExit):
        grg.main()
    doc = (tmp_path / "output" / "review_gate.md").read_text()
    assert "finding — NOT confirmed" in doc
    vf = doc.split("## Validated Findings")[1].split("## ")[1] if "## Validated Findings" in doc else ""
    assert "LibOracle._getValue" not in vf


# 10. confirmed count unchanged by a completed value-provenance finding
def test_review_gate_confirmed_count_unchanged(tmp_path, monkeypatch, capsys):
    _setup_rg(tmp_path, monkeypatch, [_completed("finding")], confirmed=2)
    with pytest.raises(SystemExit):
        grg.main()
    assert "Confirmed findings: 2" in capsys.readouterr().out


# hide_strong_clear config -> cleared rows hidden (and section disappears if all hidden)
def test_review_gate_hide_strong_clear(tmp_path, monkeypatch):
    _setup_rg(tmp_path, monkeypatch, [_completed("strong_clear")])
    monkeypatch.setattr(grg.json, "loads", _loads_hide(grg.json.loads))
    with pytest.raises(SystemExit):
        grg.main()
    doc = (tmp_path / "output" / "review_gate.md").read_text()
    assert "Value Provenance Deep-Pass Results" not in doc


def _loads_hide(orig):
    """Wrap json.loads so the agent_policy read returns hide_strong_clear=true."""
    def _w(s, *a, **k):
        d = orig(s, *a, **k)
        if isinstance(d, dict) and "value_provenance_auto_run" in d:
            d["value_provenance_auto_run"]["auto_run_value_provenance_hide_strong_clear"] = True
        return d
    return _w


# main(--ingest-results) end-to-end: writes report + ingestion report, fail-open
def test_main_ingest_end_to_end(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    mr = out / "value_provenance_manual_results"; mr.mkdir()
    (out / "value_provenance_advisory_results.json").write_text(json.dumps(_report()))
    (mr / "r.json").write_text(json.dumps(_art()))
    monkeypatch.setattr(rv, "audit_path", lambda *p: tmp_path.joinpath(*p))
    monkeypatch.setattr(rv, "get_audit_meta", lambda: {"audit_id": "a"})
    monkeypatch.setattr(sys, "argv", ["x", "--ingest-results", "--quiet"])
    assert rv.main() == 0
    rep = json.loads((out / "value_provenance_advisory_results.json").read_text())
    ing = json.loads((out / "value_provenance_ingestion_report.json").read_text())
    assert rep["results"][0]["auto_run_status"] == "completed"
    assert ing["summary"]["accepted"] == 1
