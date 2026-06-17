"""Recall Lab — looping protocol driver (scripts/recall_lab_loop.py).

Locks: queue build/order (leverage = reasoning-gap misses first), status transitions, cursor advance,
`done` refused on a red regression gate, exhaustion -> ingest, and idempotent rebuild preserving authored work.
The judgment steps (adjudication, prompt authoring) are mocked at the subprocess boundary — this tests the
DRIVER, not the heuristics (those are covered by test_auto_miss_detect.py).
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import recall_lab_loop as rll  # noqa: E402


def _adjudication(awarded):
    rows = []
    for i, (label, read_file) in enumerate(awarded):
        rows.append({"id": f"H-{i:02d}", "severity": "High", "title": f"finding {i}",
                     "label": label, "read_file": read_file, "mechanism_class": None,
                     "source": "auto-heuristic"})
    missed = [r for r in rows if r["label"] == "MISSED"]
    return {
        "audit_id": "X", "set": "training", "awarded_source": "report.md",
        "auto_heuristic": True, "awarded": rows, "candidates": [],
        "summary": {"awarded_total": len(rows), "misses_detected": len(missed),
                    "recall_of_surfaced": 0.0, "auto_adjudicated": len(rows)},
    }


def _mk_contest(root: Path, aid: str, awarded):
    d = root / "audits" / aid
    (d / "output" / "eval_ready").mkdir(parents=True, exist_ok=True)
    (d / "_sealed_answer_key").mkdir(parents=True, exist_ok=True)
    (d / "output" / "merged_findings.json").write_text(json.dumps({"findings": []}))
    (d / "_sealed_answer_key" / "report.md").write_text("# report")
    (d / "output" / "eval_ready" / "adjudication.json").write_text(json.dumps(_adjudication(awarded)))


@pytest.fixture
def tree(tmp_path, monkeypatch):
    root = tmp_path
    (root / "audits").mkdir()
    (root / "evals").mkdir()
    (root / "config").mkdir()
    (root / "config" / "mechanism_classes.json").write_text(json.dumps({"classes": {}}))
    (root / "evals" / "corpus.json").write_text(json.dumps(
        {"sets": {"training": [{"id": "alpha"}, {"id": "beta"}], "holdout": []}, "pending_key": []}))
    for name, val in [("ROOT", root), ("AUDITS", root / "audits"),
                      ("CORPUS", root / "evals" / "corpus.json"),
                      ("MECH", root / "config" / "mechanism_classes.json"),
                      ("STATE", root / "evals" / "loop_state.json"),
                      ("SCOREBOARD", root / "evals" / "scoreboard.json")]:
        monkeypatch.setattr(rll, name, val)
    return root


def test_build_orders_by_reasoning_gap_leverage(tree):
    # alpha: 1 reasoning + 4 coverage misses (5 total); beta: 3 reasoning, 0 coverage (3 total).
    # Leverage ordering must rank beta (more PROMPT-ADDRESSABLE misses) FIRST despite fewer total.
    _mk_contest(tree, "alpha", [("MISSED", True)] + [("MISSED", False)] * 4)
    _mk_contest(tree, "beta", [("MISSED", True)] * 3 + [("SAME_AREA", True)])
    rll.build()
    state = json.loads((tree / "evals" / "loop_state.json").read_text())
    assert [e["id"] for e in state["queue"]] == ["beta", "alpha"]
    assert state["queue"][0]["reasoning_misses"] == 3
    assert state["queue"][1]["reasoning_misses"] == 1 and state["queue"][1]["misses"] == 5
    assert state["stats"]["pending"] == 2 and state["cursor"] == 0


def test_next_mines_and_does_not_advance(tree, monkeypatch):
    _mk_contest(tree, "beta", [("MISSED", True)] * 2)
    rll.build()
    monkeypatch.setattr(rll.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    assert rll.nxt() == 0
    state = json.loads((tree / "evals" / "loop_state.json").read_text())
    assert state["queue"][0]["status"] == rll.STATUS_MINED
    assert state["cursor"] == 0  # next does NOT bank/advance


def test_done_refused_on_red_gate(tree, monkeypatch):
    _mk_contest(tree, "beta", [("MISSED", True)])
    rll.build()
    monkeypatch.setattr(rll.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    rll.nxt()
    # red regression gate -> done refused, status stays mined.
    monkeypatch.setattr(rll.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 1})())
    assert rll.done("beta", ["logic.md#99"], ["fake-class"]) == 1
    state = json.loads((tree / "evals" / "loop_state.json").read_text())
    assert state["queue"][0]["status"] == rll.STATUS_MINED
    assert not state["queue"][0]["sections_authored"]


def test_done_banks_and_advances_on_green_gate(tree, monkeypatch):
    _mk_contest(tree, "alpha", [("MISSED", True)])
    _mk_contest(tree, "beta", [("MISSED", True)] * 2)
    rll.build()
    monkeypatch.setattr(rll.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    rll.nxt()  # mines beta (leverage leader)
    assert rll.done("beta", ["logic.md#17"], ["cls-a"]) == 0
    state = json.loads((tree / "evals" / "loop_state.json").read_text())
    done = [e for e in state["queue"] if e["status"] == rll.STATUS_DONE]
    assert len(done) == 1 and done[0]["id"] == "beta"
    assert done[0]["sections_authored"] == ["logic.md#17"]
    assert state["cursor"] == 1  # advanced past the one banked (done pinned to front)
    assert state["stats"]["reincorporated"] == 1


def test_rebuild_idempotent_preserves_done(tree, monkeypatch):
    _mk_contest(tree, "alpha", [("MISSED", True)])
    _mk_contest(tree, "beta", [("MISSED", True)] * 2)
    rll.build()
    monkeypatch.setattr(rll.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    rll.nxt()
    rll.done("beta", ["logic.md#17"], ["cls-a"])
    rll.build()  # rebuild must NOT reset beta's reincorporated status / authored work
    state = json.loads((tree / "evals" / "loop_state.json").read_text())
    beta = [e for e in state["queue"] if e["id"] == "beta"][0]
    assert beta["status"] == rll.STATUS_DONE and beta["sections_authored"] == ["logic.md#17"]


def test_enqueue_ingest_only_when_drained(tree, monkeypatch, capsys):
    _mk_contest(tree, "beta", [("MISSED", True)])
    rll.build()
    rll.enqueue_ingest()  # still pending -> refuse
    assert "NOT drained" in capsys.readouterr().out
    monkeypatch.setattr(rll.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    rll.nxt()
    rll.done("beta", [], [])
    rll.enqueue_ingest()  # drained -> protocol
    assert "ingest_contest.py" in capsys.readouterr().out
