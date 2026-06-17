"""P139 — tests for run_value_provenance_advisories (auto-route scaffold) + review-gate rendering.

No protocol-specific strings. Proves: config gating, H-03-class trigger, exclusions, caps, fail-open,
advisory-only/submission_ready=false, pending_manual_execution honesty, and review_gate isolation.
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


def _rec(contract="LibOracle", function="_getValue", file="contracts/LibOracle.sol", line=1,
         prompt="deep_pass_value_provenance", status="advisory"):
    return {"source_detector": "deep_pass_router", "detector_status": status, "advisory_only": True,
            "submission_ready": False, "requires_human_review": True, "review_context": True,
            "contract": contract, "function": function, "file_path": file, "line": line,
            "mechanism_class": "value_provenance_loop", "recommended_prompt": prompt}


def _ctx(recs):
    return {"surfaced": True, "deep_pass_recommendations": recs}


def _src(tmp, rel, body):
    p = ROOT / rel
    # write under a tmp-rooted relative path the script resolves against ROOT
    target = ROOT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)
    return rel


# A value-provenance loop body (loop + value call) — triggers.
VP_BODY = ("function _getValue() internal view returns (uint v) {\n"
           "  for (uint i; i < sources.length; i++) { v = getValue(asset, sources[i], v); }\n"
           "  return v;\n}\n")
TRIVIAL_BODY = "function f() external {}\n"


def _cfg(**over):
    c = dict(CFG)
    c.update(over)
    c["_eval_mode"] = over.get("_eval_mode", False)
    return c


# 1. config off -> no run
def test_config_off_no_run(tmp_path):
    rep = rv.build(_cfg(auto_run_value_provenance_advisories=False), tmp_path, "a", _ctx([_rec()]))
    assert rep["ran"] is False and rep["results"] == []


def test_mode_off_no_run(tmp_path):
    rep = rv.build(_cfg(auto_run_value_provenance_mode="off"), tmp_path, "a", _ctx([_rec()]))
    assert rep["ran"] is False


# 13. eval_only mode honesty
def test_eval_only_requires_eval_flag(tmp_path):
    assert rv.build(_cfg(auto_run_value_provenance_mode="eval_only"), tmp_path, "a", _ctx([_rec()]))["ran"] is False
    rep = rv.build(_cfg(auto_run_value_provenance_mode="eval_only", _eval_mode=True), tmp_path, "a", _ctx([_rec()]))
    assert rep["ran"] is True


# 2. H-03-class rec triggers a job (pending) — and 7/13: advisory-only + pending honesty
def test_h03_rec_triggers_pending_job(tmp_path, monkeypatch):
    rel = _src(tmp_path, "tmp_p139/LibOracle.sol", VP_BODY)
    rep = rv.build(_cfg(), tmp_path, "a", _ctx([_rec(file=rel)]))
    assert rep["ran"] and len(rep["results"]) == 1
    r = rep["results"][0]
    assert r["auto_run_status"] == "pending_manual_execution"
    assert r["prompt_decision"] == "pending"            # no fabricated decision
    assert r["advisory_only"] is True and r["submission_ready"] is False and r["requires_human_review"] is True
    (ROOT / rel).unlink()


# 3. generic advisory without recommended_prompt does not trigger
def test_no_recommended_prompt_no_trigger(tmp_path):
    rep = rv.build(_cfg(), tmp_path, "a", _ctx([_rec(prompt=None)]))
    assert rep["results"] == []


# 4. mock/test/trivial does not trigger
def test_mock_excluded(tmp_path):
    rel = _src(tmp_path, "tmp_p139/MockOracle.sol", VP_BODY)
    rep = rv.build(_cfg(), tmp_path, "a", _ctx([_rec(contract="MockOracle", file=rel)]))
    assert rep["results"] == []
    (ROOT / rel).unlink()


def test_trivial_excluded(tmp_path):
    rel = _src(tmp_path, "tmp_p139/Trivial.sol", TRIVIAL_BODY)
    rep = rv.build(_cfg(), tmp_path, "a", _ctx([_rec(file=rel)]))
    assert rep["results"] == []
    (ROOT / rel).unlink()


# 5. cap respected
def test_max_total_cap(tmp_path):
    rel = _src(tmp_path, "tmp_p139/Many.sol", VP_BODY)
    recs = [_rec(function=f"f{i}", file=rel) for i in range(10)]
    rep = rv.build(_cfg(auto_run_value_provenance_max_total=3), tmp_path, "a", _ctx(recs))
    assert len(rep["results"]) == 3
    (ROOT / rel).unlink()


# 6. malformed/None context does not block
def test_malformed_context_no_block(tmp_path):
    rep = rv.build(_cfg(), tmp_path, "a", None)
    assert rep["ran"] is True and rep["results"] == []


# research-only excluded unless enabled
def test_research_only_excluded_by_default(tmp_path):
    rel = _src(tmp_path, "tmp_p139/Lib2.sol", VP_BODY)
    assert rv.build(_cfg(), tmp_path, "a", _ctx([_rec(file=rel, status="research_only")]))["results"] == []
    rep = rv.build(_cfg(auto_run_value_provenance_surface_research_only=True), tmp_path, "a",
                   _ctx([_rec(file=rel, status="research_only")]))
    assert len(rep["results"]) == 1
    (ROOT / rel).unlink()


# 8. failed prompt-run path does not block (fail-open at main level)
def test_main_failopen(tmp_path, monkeypatch):
    monkeypatch.setattr(rv, "audit_path", lambda *p: tmp_path.joinpath(*p))
    monkeypatch.setattr(rv, "get_audit_meta", lambda: {"audit_id": "a"})
    monkeypatch.setattr(rv, "build", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    (tmp_path / "output").mkdir()
    monkeypatch.setattr(sys, "argv", ["x", "--quiet"])
    assert rv.main() == 0  # never raises
    rep = json.loads((tmp_path / "output" / "value_provenance_advisory_results.json").read_text())
    assert rep["ran"] is False and "boom" in rep["error"]


# 10/11/12. review_gate renders the subsection separately; not in Validated Findings; confirmed count unchanged
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


VP_RESULT = {"contract": "LibOracle", "function": "_getValue", "auto_run_status": "pending_manual_execution",
             "prompt_decision": "pending", "mechanism_summary": "multi-hop value loop",
             "output_path": "output/value_provenance_jobs/VP-LibOracle._getValue.md"}


def test_review_gate_renders_vp_subsection(tmp_path, monkeypatch):
    _setup_rg(tmp_path, monkeypatch, [VP_RESULT], confirmed=1)
    with pytest.raises(SystemExit):
        grg.main()
    doc = (tmp_path / "output" / "review_gate.md").read_text()
    assert "### Value Provenance Deep-Pass Results — advisory only" in doc
    assert "LibOracle._getValue" in doc and "pending_manual_execution" in doc
    # not in Validated Findings table
    vf = doc.split("## Validated Findings")[1].split("## ")[1] if "## Validated Findings" in doc else ""
    assert "LibOracle._getValue" not in vf


def test_review_gate_vp_absent_when_no_results(tmp_path, monkeypatch):
    _setup_rg(tmp_path, monkeypatch, [])
    with pytest.raises(SystemExit):
        grg.main()
    doc = (tmp_path / "output" / "review_gate.md").read_text()
    assert "Value Provenance Deep-Pass Results" not in doc


def test_review_gate_confirmed_count_unchanged(tmp_path, monkeypatch, capsys):
    _setup_rg(tmp_path, monkeypatch, [VP_RESULT], confirmed=2)
    with pytest.raises(SystemExit):
        grg.main()
    assert "Confirmed findings: 2" in capsys.readouterr().out
