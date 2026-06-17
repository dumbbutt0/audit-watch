"""P142 — tests for the value-provenance eval harness (research-only, un-wired).

Proves: research flags + queue_origin on seed; ingest completes via the P140 safety merge (forced advisory
triplet, never confirmed/submission-ready); scorecard reproduces the P138/P141 baseline with 0 clean false
findings; routed inputs refused; writes only under the research workspace; missing corpus / malformed row safe;
idempotent; scorecard --append grows the time-series; provenance-less rows refused (no fabrication); and the
harness is NOT wired into run_pipeline.sh / agent_policy.json.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "research"))
import value_provenance_eval_harness as h  # noqa: E402

FLAGS = ("is_gate", "research_only", "routes_in_production", "routed_manifest_ids", "routing_allowed")


def _real_cfg():
    return h.load_cfg()


def _tmp_corpus(tmp_path, rows):
    p = tmp_path / "corpus.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows))
    cfg = dict(h.DEFAULT_CFG)
    cfg["corpus_path"] = str(p)
    return cfg


def _row(item_id="X1", arch="noya", contract="C", function="f", label="buggy",
         decision="finding", prov="docs/p138.md#agentX", **over):
    r = {"item_id": item_id, "arch": arch, "audit_id": "a", "contract": contract, "function": function,
         "file_path": "c.sol", "label": label, "expected_shape": "shape",
         "recorded_decision": decision, "confidence": "high",
         "source_phase": "P138", "blind_output_ref": prov}
    r.update(over)
    return r


# 1. seed entries carry the 4 flags + queue_origin + advisory triplet + pending
def test_seed_flags(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row()])
    h.seed(cfg, tmp_path / "wd", None)
    q = json.loads((tmp_path / "wd" / "noya" / "value_provenance_advisory_results.json").read_text())
    assert q["queue_origin"] == "eval_only_manual_queue"
    for f in FLAGS:
        assert f in q
    e = q["results"][0]
    assert e["queue_origin"] == "eval_only_manual_queue"
    assert e["auto_run_status"] == "pending_manual_execution" and e["prompt_decision"] == "pending"
    assert e["advisory_only"] is True and e["submission_ready"] is False and e["requires_human_review"] is True
    assert all(f in e for f in FLAGS)


# 2. ingest completes via the safety merge; forces the triplet; never confirmed/submission-ready
def test_ingest_completes_forced_triplet(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(decision="finding")])
    h.seed(cfg, tmp_path / "wd", None)
    h.ingest(cfg, tmp_path / "wd", None)
    q = json.loads((tmp_path / "wd" / "noya" / "value_provenance_advisory_results.json").read_text())
    e = q["results"][0]
    assert e["auto_run_status"] == "completed" and e["prompt_decision"] == "finding"
    assert e["advisory_only"] is True and e["submission_ready"] is False and e["requires_human_review"] is True
    assert e.get("confirmed") is not True and "final_severity" not in e


# 3 + 4. scorecard reproduces the real P138/P141 baseline + 0 clean false findings
def test_scorecard_baseline(tmp_path):
    cfg = _real_cfg()
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None)
    h.ingest(cfg, wd, None)
    out = h.scorecard(cfg, wd, append=False)
    t = out["totals"]
    assert t["queued"] == 11 and t["completed"] == 11
    assert t["finding"] == 3 and t["needs_human"] == 1 and t["strong_clear"] == 7 and t["error"] == 0
    assert t["clean_false_finding"] == 0 and t["clean_false_finding_rate"] == 0.0
    assert t["useful_recall"] == 0.8 and t["strict_recall"] == 0.6


# 5. refuse routed / non-research input
def test_refuse_routed():
    with pytest.raises(SystemExit):
        h._refuse_if_routed({"routing_allowed": True}, "x")
    with pytest.raises(SystemExit):
        h._refuse_if_routed({"routing_allowed": False, "routes_in_production": True}, "x")
    with pytest.raises(SystemExit):
        h._refuse_if_routed({"routing_allowed": False, "routed_manifest_ids": ["m1"]}, "x")
    h._refuse_if_routed({"routing_allowed": False}, "ok")  # no raise


# 6. writes ONLY under the research workspace (no audits/ path)
def test_writes_only_workspace(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(arch="noya")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None); h.scorecard(cfg, wd, append=True)
    written = list(wd.rglob("*"))
    assert written, "nothing written"
    assert all(str(wd) in str(p) for p in written)
    # no production-path USAGE: the harness must not import audit_context or call audit_path(),
    # and must not write into an audits/ tree (docstring prose mentioning these is fine).
    src = (ROOT / "scripts" / "research" / "value_provenance_eval_harness.py").read_text()
    assert "audit_path(" not in src
    assert "import audit_context" not in src
    assert "audits/" not in src


# 7. missing corpus is safe
def test_missing_corpus_safe(tmp_path):
    cfg = dict(h.DEFAULT_CFG); cfg["corpus_path"] = str(tmp_path / "nope.jsonl")
    assert h._load_corpus(cfg) == []
    rep = h.seed(cfg, tmp_path / "wd", None)
    assert rep["ran"] is True and rep["seeded"] == {}


# 8. malformed row skipped (fail-open)
def test_malformed_row_skipped(tmp_path):
    p = tmp_path / "corpus.jsonl"
    p.write_text('{"item_id":"ok","arch":"noya","contract":"C","function":"f"}\nNOT JSON\n{}\n')
    cfg = dict(h.DEFAULT_CFG); cfg["corpus_path"] = str(p)
    rows = h._load_corpus(cfg)
    assert len(rows) == 1 and rows[0]["item_id"] == "ok"


# 9. idempotent ingest
def test_idempotent(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row()])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    a = (wd / "noya" / "value_provenance_advisory_results.json").read_text()
    h.ingest(cfg, wd, None)
    b = (wd / "noya" / "value_provenance_advisory_results.json").read_text()
    # results entries identical (timestamps on the queue header may differ, entries must not)
    ra = json.loads(a)["results"]; rb = json.loads(b)["results"]
    assert ra == rb


# 10. scorecard --append grows the time-series
def test_scorecard_append_grows_runs(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row()])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    h.scorecard(cfg, wd, append=True)
    out2 = h.scorecard(cfg, wd, append=True)
    assert len(out2["runs"]) == 2


# 11. row missing provenance is refused (no fabrication)
def test_missing_provenance_refused(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="NOPROV", contract="N", function="g", prov=None)])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None)
    rep = h.ingest(cfg, wd, None)
    assert "VP-N.g" in rep["refused_no_provenance"]
    q = json.loads((wd / "noya" / "value_provenance_advisory_results.json").read_text())
    assert q["results"][0]["auto_run_status"] == "pending_manual_execution"  # not completed


# 11b. invalid recorded_decision is refused (no artifact built)
def test_invalid_decision_refused(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(decision="confirmed")])  # not an allowed decision
    assert h._artifact_from_row(_row(decision="confirmed")) is None


# 12. NOT wired into production (grep run_pipeline.sh + agent_policy.json)
def test_no_production_wiring():
    rp = (ROOT / "run_pipeline.sh").read_text()
    ap = (ROOT / "config" / "agent_policy.json").read_text()
    assert "value_provenance_eval_harness" not in rp
    assert "value_provenance_eval_harness" not in ap


# 13. scorecard carries the research flags
def test_scorecard_research_flags(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row()])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    out = h.scorecard(cfg, wd, append=False)
    assert out["research_only"] is True and out["routing_allowed"] is False and out["is_gate"] is False
    assert out["routes_in_production"] is False and out["routed_manifest_ids"] == []


# 14. clean control does not false-find (a clean row -> strong_clear -> 0 clean_false_finding)
def test_clean_control_no_false_finding(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="CL", label="clean", decision="strong_clear",
                                      clean_label_confidence="HIGH")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    out = h.scorecard(cfg, wd, append=False)
    assert out["totals"]["clean"] == 1 and out["totals"]["clean_false_finding"] == 0


# ===================== P146 runtime evidence panel =====================
def _tmp_sidecar(tmp_path, rows):
    p = tmp_path / "runtime_status.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows))
    return str(p)


# P146-1: default not_run/none for every item when no sidecar exists; all routing/submission false.
def test_panel_defaults_not_run(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="X1"), _row(item_id="X2", label="clean", decision="strong_clear")])
    cfg["runtime_status_path"] = str(tmp_path / "nope.jsonl")  # missing
    panel = h.build_runtime_panel(cfg)
    assert panel["summary"]["rows"] == 2
    assert all(r["runtime_status"] == "not_run" and r["runtime_confidence"] == "none" for r in panel["rows"])
    assert all(r["routing_allowed"] is False and r["submission_ready"] is False for r in panel["rows"])


# P146-2: sidecar backfills a matching item; forces routing_allowed/submission_ready False even if sidecar says True.
def test_panel_backfill_and_forced_flags(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1"), _row(item_id="X2")])
    cfg["runtime_status_path"] = _tmp_sidecar(tmp_path, [{
        "item_id": "B1", "runtime_status": "runtime_confirmed", "runtime_confidence": "high",
        "architecture": "noya", "bug_class": "stale_loop_variable", "duplicate_status": "duplicate_known",
        "routing_allowed": True, "submission_ready": True,  # must be forced False
    }])
    panel = h.build_runtime_panel(cfg)
    rows = {r["bug_id"]: r for r in panel["rows"]}
    assert rows["B1"]["runtime_status"] == "runtime_confirmed" and rows["B1"]["runtime_confidence"] == "high"
    assert rows["B1"]["routing_allowed"] is False and rows["B1"]["submission_ready"] is False
    assert rows["X2"]["runtime_status"] == "not_run"
    assert panel["integrity"]["routing_allowed_all_false"] is True
    assert panel["integrity"]["submission_ready_all_false"] is True


# P146-3: out-of-vocab status/confidence are coerced into the allowed sets.
def test_panel_vocab_coercion(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1")])
    cfg["runtime_status_path"] = _tmp_sidecar(tmp_path, [{
        "item_id": "B1", "runtime_status": "totally_proven", "runtime_confidence": "certain"}])
    r = h.build_runtime_panel(cfg)["rows"][0]
    assert r["runtime_status"] in h.RUNTIME_STATUS and r["runtime_status"] == "inconclusive"
    assert r["runtime_confidence"] in h.RUNTIME_CONFIDENCE and r["runtime_confidence"] == "none"


# P146-4 INTEGRITY: the panel never perturbs the prompt-derived metrics (per_arch/totals/runs value-for-value).
def test_integrity_prompt_metrics_unchanged(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1", arch="noya"),
                                 _row(item_id="C1", arch="noya", label="clean", decision="strong_clear")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    cfg_empty = dict(cfg); cfg_empty["runtime_status_path"] = str(tmp_path / "absent.jsonl")
    cfg_full = dict(cfg); cfg_full["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "B1", "runtime_status": "runtime_confirmed", "runtime_confidence": "high"}])
    a = h.scorecard(cfg_empty, wd, append=False)
    b = h.scorecard(cfg_full, wd, append=False)
    assert a["per_arch"] == b["per_arch"]
    assert a["totals"] == b["totals"]
    assert [r["totals"] for r in a["runs"]] == [r["totals"] for r in b["runs"]]
    # but the panel DID change (B1 backfilled in the full run only)
    conf = lambda out: sum(1 for r in out["runtime_panel"]["rows"] if r["runtime_status"] == "runtime_confirmed")
    assert conf(a) == 0 and conf(b) == 1


# P146-5: runtime_panel writes only under the workspace; scorecard gains the runtime_panel key.
def test_panel_written_only_workspace_and_in_scorecard(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1")])
    cfg["runtime_status_path"] = str(tmp_path / "none.jsonl")
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    out = h.scorecard(cfg, wd, append=False)
    assert "runtime_panel" in out and out["runtime_panel"]["rows"]
    assert (wd / "runtime_panel.json").exists()
    assert all(str(wd) in str(p) for p in wd.rglob("*"))


# P146-6: the REAL deliverable — load_cfg backfills B1 and B5 (corpus items) as runtime_confirmed/high;
# every OTHER corpus item (runtime_only=False) is not_run. (Runtime-only holdout rows are checked separately.)
# ===================== P147 runtime-only (non-duplicate) panel rows =====================
# P147-1: a sidecar item NOT in the corpus surfaces as a runtime_only panel row; corpus rows unaffected.
def test_runtime_only_row_surfaces(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1")])
    cfg["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "B1", "runtime_status": "runtime_confirmed", "runtime_confidence": "high"},
        {"item_id": "H9-holdout", "architecture": "someholdout", "runtime_status": "runtime_confirmed",
         "runtime_confidence": "high", "duplicate_status": "duplicate_unknown"},
    ])
    panel = h.build_runtime_panel(cfg)
    rows = {r["bug_id"]: r for r in panel["rows"]}
    assert rows["B1"]["runtime_only"] is False
    assert "H9-holdout" in rows and rows["H9-holdout"]["runtime_only"] is True
    assert rows["H9-holdout"]["runtime_status"] == "runtime_confirmed"
    assert panel["integrity"]["runtime_only_rows"] == ["H9-holdout"]


# P147-2: the non-duplicate runtime row is NOT duplicate_known and stays routing/submission false.
def test_nondup_runtime_only_not_duplicate_known(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1")])
    cfg["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "H9", "runtime_status": "runtime_confirmed", "duplicate_status": "duplicate_unknown",
         "routing_allowed": True, "submission_ready": True}])
    r = {x["bug_id"]: x for x in h.build_runtime_panel(cfg)["rows"]}["H9"]
    assert r["duplicate_status"] != "duplicate_known"
    assert r["routing_allowed"] is False and r["submission_ready"] is False


# P147-3 INTEGRITY: a runtime-only sidecar row does NOT perturb prompt metrics (corpus unchanged).
def test_runtime_only_does_not_perturb_prompt_metrics(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1", arch="noya"),
                                 _row(item_id="C1", arch="noya", label="clean", decision="strong_clear")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    cfg_empty = dict(cfg); cfg_empty["runtime_status_path"] = str(tmp_path / "absent.jsonl")
    cfg_extra = dict(cfg); cfg_extra["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "H9-holdout", "runtime_status": "runtime_confirmed", "duplicate_status": "duplicate_unknown"}])
    a = h.scorecard(cfg_empty, wd, append=False)
    b = h.scorecard(cfg_extra, wd, append=False)
    assert a["per_arch"] == b["per_arch"]
    assert a["totals"] == b["totals"]
    assert [r["totals"] for r in a["runs"]] == [r["totals"] for r in b["runs"]]
    # the runtime-only row appears only in the extra run's panel
    rids = lambda out: {r["bug_id"] for r in out["runtime_panel"]["rows"]}
    assert "H9-holdout" in rids(b) and "H9-holdout" not in rids(a)


# P147-4: the REAL deliverable — the centrifuge holdout surfaces as a non-dup runtime_confirmed row,
# the P138 prompt baseline is unchanged, and B1/B5 remain duplicate_known.
# ===================== P148 runtime-refuted (negative control) =====================
# P148-1: a runtime_refuted runtime-only row surfaces; status preserved; flags forced false.
def test_runtime_refuted_row_surfaces(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1")])
    cfg["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "H9-neg", "architecture": "someholdout", "runtime_status": "runtime_refuted",
         "runtime_confidence": "high", "duplicate_status": "duplicate_unknown",
         "routing_allowed": True, "submission_ready": True}])  # both must be forced false
    panel = h.build_runtime_panel(cfg)
    r = {x["bug_id"]: x for x in panel["rows"]}["H9-neg"]
    assert r["runtime_status"] == "runtime_refuted" and r["runtime_only"] is True
    assert r["duplicate_status"] != "duplicate_known"
    assert r["routing_allowed"] is False and r["submission_ready"] is False
    assert panel["summary"]["by_status"].get("runtime_refuted") == 1


# P148-2 INTEGRITY: a runtime_refuted runtime-only row does NOT perturb prompt metrics.
def test_runtime_refuted_does_not_perturb_prompt_metrics(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1", arch="noya"),
                                 _row(item_id="C1", arch="noya", label="clean", decision="strong_clear")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    cfg_empty = dict(cfg); cfg_empty["runtime_status_path"] = str(tmp_path / "absent.jsonl")
    cfg_ref = dict(cfg); cfg_ref["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "H9-neg", "runtime_status": "runtime_refuted", "duplicate_status": "duplicate_unknown"}])
    a = h.scorecard(cfg_empty, wd, append=False)
    b = h.scorecard(cfg_ref, wd, append=False)
    assert a["per_arch"] == b["per_arch"] and a["totals"] == b["totals"]
    assert [r["totals"] for r in a["runs"]] == [r["totals"] for r in b["runs"]]


# P148-3: the REAL deliverable — velodrome H2 row is runtime_refuted/duplicate_unknown/runtime_only; confirmed
# rows unchanged; baseline corpus untouched.
# ===================== P149 intent-judgment record (H1-centrifuge) =====================
def _load_sidecar_rows():
    p = ROOT / "output_research" / "value_provenance_eval" / "runtime_status.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


# P149-1: the H1 sidecar row carries the P149 judgment, and the runtime status/flags are NOT flipped by it.
# P149-2: the panel still surfaces H1 as runtime_confirmed with flags false (judgment enrichment is inert to panel).
# ===================== P150 second non-duplicate holdout (H3-decent) =====================
# P150-1: the decent H3 runtime-only row surfaces with its status + flags forced false.
# P150-2 INTEGRITY: the decent runtime-only row does NOT perturb prompt metrics.
def test_decent_row_does_not_perturb_prompt_metrics(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1", arch="noya"),
                                 _row(item_id="C1", arch="noya", label="clean", decision="strong_clear")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    cfg_empty = dict(cfg); cfg_empty["runtime_status_path"] = str(tmp_path / "absent.jsonl")
    cfg_h3 = dict(cfg); cfg_h3["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "H3-decent-utbfeecollector-sigbind", "architecture": "decent",
         "runtime_status": "runtime_confirmed", "duplicate_status": "duplicate_unknown"}])
    a = h.scorecard(cfg_empty, wd, append=False)
    b = h.scorecard(cfg_h3, wd, append=False)
    assert a["per_arch"] == b["per_arch"] and a["totals"] == b["totals"]
    assert [r["totals"] for r in a["runs"]] == [r["totals"] for r in b["runs"]]


# ===================== P151 reachability/severity review (H3-decent) =====================
# ===================== P152 third non-dup holdout (ecg) + conversion schema =====================
_CONVERSION_OUTCOMES = {
    "reportable_candidate_needs_human_review", "runtime_confirmed_but_reachability_unknown",
    "runtime_confirmed_but_privileged_only", "runtime_confirmed_but_severity_too_low",
    "runtime_confirmed_but_duplicate_unknown", "runtime_refuted", "not_run_too_heavy",
    "static_false_positive", "needs_context",
}


# conversion schema present + valid on every runtime-only row (H1..H4)
# the H4 enrichment does not perturb prompt metrics
def test_ecg_row_does_not_perturb_prompt_metrics(tmp_path):
    cfg = _tmp_corpus(tmp_path, [_row(item_id="B1", arch="noya"),
                                 _row(item_id="C1", arch="noya", label="clean", decision="strong_clear")])
    wd = tmp_path / "wd"
    h.seed(cfg, wd, None); h.ingest(cfg, wd, None)
    cfg_empty = dict(cfg); cfg_empty["runtime_status_path"] = str(tmp_path / "absent.jsonl")
    cfg_h4 = dict(cfg); cfg_h4["runtime_status_path"] = _tmp_sidecar(tmp_path, [
        {"item_id": "H4-ecg-multivotes-accounting", "architecture": "ecg", "runtime_status": "runtime_refuted",
         "duplicate_status": "duplicate_unknown", "conversion": {"outcome": "runtime_refuted"}}])
    a = h.scorecard(cfg_empty, wd, append=False)
    b = h.scorecard(cfg_h4, wd, append=False)
    assert a["per_arch"] == b["per_arch"] and a["totals"] == b["totals"]
    assert [r["totals"] for r in a["runs"]] == [r["totals"] for r in b["runs"]]
