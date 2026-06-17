"""Phase-19 smoke test for the resumable queue scheduler (deterministic, budgeted, callee-expanding)."""
import importlib, json, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_context  # noqa: E402
sched = importlib.import_module("deep_pass_schedule")

SRC = "contract C {\n  function a() public { b(); }\n  function b() internal { uint x=1; }\n  function c() public { }\n}\n"


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output" / "deep_pass").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    src = tmp_path / "C.sol"; src.write_text(SRC)
    items = [
        {"id": "f:C:a", "kind": "function", "name": "a", "contract": "C", "file": str(src), "in_scope": True, "source_span": {"start_line": 2}},
        {"id": "f:C:b", "kind": "function", "name": "b", "contract": "C", "file": str(src), "in_scope": True, "source_span": {"start_line": 3}},
        {"id": "f:C:c", "kind": "function", "name": "c", "contract": "C", "file": str(src), "in_scope": True, "source_span": {"start_line": 4}},
    ]
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"items": items}))
    (tmp_path / "output" / "deep_pass" / "candidate_queue.json").write_text(json.dumps(
        {"queue": [{"manifest_id": "f:C:a", "contract": "C", "function": "a"},
                   {"manifest_id": "f:C:c", "contract": "C", "function": "c"}]}))
    return tmp_path


def _run(argv):
    old = sys.argv; sys.argv = ["deep_pass_schedule"] + argv + ["--quiet"]
    try: return sched.main()
    finally: sys.argv = old


def test_budget_callee_expansion_and_resume(ws):
    _run(["--budget", "1", "--depth", "2"])                       # schedule 1 of 2
    s = json.loads((ws / "output/deep_pass/_schedule/schedule.json").read_text())
    assert s["scheduled_this_run"] == 1 and s["untraced"] == 2 and s["research_only"] is True
    # the scheduled candidate 'a' must include its callee 'b' (mandatory expansion)
    bndl = json.loads((ws / "output/deep_pass/_schedule/sched_0000.json").read_text())
    assert "b" in bndl["callees_available"]
    # reconcile a callee-complete trace for 'a' → ledger marks it traced
    (ws / "r.json").write_text(json.dumps({"decisions": [
        {"manifest_id": "f:C:a", "function_analyzed": True, "callees_available": ["b"], "callees_analyzed": ["b"], "decision_made": True}]}))
    _run(["--reconcile", str(ws / "r.json")])
    led = json.loads((ws / "output/deep_pass/trace_ledger.json").read_text())
    assert "f:C:a" in led["traced"]
    # re-run → skips 'a', schedules 'c' (resumable)
    _run(["--budget", "1"])
    s2 = json.loads((ws / "output/deep_pass/_schedule/schedule.json").read_text())
    assert s2["traced"] == 1 and s2["scheduled"][0]["function"] == "c"


def test_incomplete_callee_trace_not_marked(ws):
    # function_analyzed but callees NOT all analyzed → must NOT be marked traced
    (ws / "r.json").write_text(json.dumps({"decisions": [
        {"manifest_id": "f:C:a", "function_analyzed": True, "callees_available": ["b"], "callees_analyzed": [], "decision_made": True}]}))
    _run(["--reconcile", str(ws / "r.json")])
    led = json.loads((ws / "output/deep_pass/trace_ledger.json").read_text()) if (ws / "output/deep_pass/trace_ledger.json").exists() else {"traced": []}
    assert "f:C:a" not in led["traced"]
