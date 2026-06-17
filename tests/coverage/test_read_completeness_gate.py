"""
P245 #3 — coverage read-completeness gate regression tests (default-off).

Mirrors tests/coverage/test_coverage_gate.py: redirect the active-audit workspace to a tmp dir via
audit_context.get_audit_root, write a tiny manifest + dispositions, and drive the real gate main().

Covers: read_state allowed values; critical incomplete -> block; non-critical incomplete -> warning
only; BLOCKED_BY_BUILD + reason + ack -> allowed; default-off preserves the existing workflow.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
rcu = importlib.import_module("read_completeness_utils")
gate = importlib.import_module("coverage_completeness_gate")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    # neutralize policy file influence: point the gate's policy reader at an empty policy
    monkeypatch.setattr(gate, "_policy", lambda: {})
    return tmp_path


def _crit_item(iid="function:V:mint#1"):
    # public external state-mutating token fn -> critical
    return {"id": iid, "kind": "function", "contract": "V", "file": "V.sol", "name": "mint",
            "signature": "function mint(address to) external", "visibility": "external",
            "mutability": "nonpayable", "modifiers": [], "tags": ["token"],
            "attack_surface_score": 4, "in_scope": True}


def _noncrit_item(iid="function:V:getX#2"):
    # public view getter, no risk tag -> NOT critical
    return {"id": iid, "kind": "function", "contract": "V", "file": "V.sol", "name": "getX",
            "signature": "function getX() public view returns (uint)", "visibility": "public",
            "mutability": "view", "modifiers": [], "tags": [], "attack_surface_score": 1,
            "in_scope": True}


def _disp(iid, status="cleared", read_state=None, **extra):
    d = {"manifest_id": iid, "status": status, "evidence": ["V.sol:1 ok"], "clear_reason": "no path",
         "attacker_reachability": "n/a", "guard_or_invariant": "n/a", "no_impact_reason": "n/a",
         "finding_refs": []}
    if read_state is not None:
        d["read_state"] = read_state
    d.update(extra)
    return d


def _setup(ws, items, disps):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"items": items}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": disps}))


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["coverage_completeness_gate.py", *argv])
    rc = gate.main()
    return rc


def test_read_state_allowed_values_constant():
    assert rcu.ALLOWED_READ_STATES == {
        "READ_FULL", "READ_PARTIAL", "NOT_IN_SCOPE", "GENERATED_INTERFACE_ONLY",
        "DUPLICATE_WRAPPER", "BLOCKED_BY_SIZE", "BLOCKED_BY_BUILD", "BLOCKED_BY_MISSING_SOURCE"}


def test_default_off_preserves_workflow(ws, monkeypatch):
    """With the flag OFF, a fully-dispositioned manifest passes even though read_state is absent."""
    items = [_crit_item(), _noncrit_item()]
    disps = [_disp("function:V:mint#1"), _disp("function:V:getX#2")]
    _setup(ws, items, disps)
    rc = _run(monkeypatch)  # no --enforce-read-completeness
    rep = json.loads((ws / "output" / "coverage_gate.json").read_text())
    assert rc == 0 and rep["passed"] is True
    assert rep["read_completeness"]["enforced"] is False


def test_critical_incomplete_blocks(ws, monkeypatch):
    """Flag ON: a critical item without READ_FULL blocks; the non-critical one does not."""
    items = [_crit_item(), _noncrit_item()]
    disps = [_disp("function:V:mint#1", read_state="READ_PARTIAL"),
             _disp("function:V:getX#2", read_state="READ_PARTIAL")]
    _setup(ws, items, disps)
    rc = _run(monkeypatch, "--enforce-read-completeness")
    rep = json.loads((ws / "output" / "coverage_gate.json").read_text())
    assert rc == 1 and rep["passed"] is False
    blocked_ids = {b["manifest_id"] for b in rep["blocking_items"]}
    assert "function:V:mint#1" in blocked_ids          # critical -> blocked
    assert "function:V:getX#2" not in blocked_ids       # non-critical -> NOT blocked
    # non-critical unread surfaces only warn
    assert rep["read_completeness"]["noncritical_unread_warned"] >= 1


def test_critical_read_full_passes(ws, monkeypatch):
    items = [_crit_item(), _noncrit_item()]
    disps = [_disp("function:V:mint#1", read_state="READ_FULL"),
             _disp("function:V:getX#2", read_state="READ_FULL")]
    _setup(ws, items, disps)
    rc = _run(monkeypatch, "--enforce-read-completeness")
    rep = json.loads((ws / "output" / "coverage_gate.json").read_text())
    assert rc == 0 and rep["passed"] is True
    assert rep["read_completeness"]["critical_read_full"] == 1


def test_blocked_by_build_requires_reason_and_ack(ws, monkeypatch):
    items = [_crit_item()]
    # missing ack -> still blocks
    _setup(ws, items, [_disp("function:V:mint#1", read_state="BLOCKED_BY_BUILD",
                             read_block_reason="foundry deps not vendored")])
    assert _run(monkeypatch, "--enforce-read-completeness") == 1

    # reason + human ack -> allowed
    _setup(ws, items, [_disp("function:V:mint#1", read_state="BLOCKED_BY_BUILD",
                             read_block_reason="foundry deps not vendored", read_block_ack=True)])
    rc = _run(monkeypatch, "--enforce-read-completeness")
    rep = json.loads((ws / "output" / "coverage_gate.json").read_text())
    assert rc == 0 and rep["passed"] is True


def test_duplicate_wrapper_requires_canonical_target(ws, monkeypatch):
    items = [_crit_item()]
    _setup(ws, items, [_disp("function:V:mint#1", read_state="DUPLICATE_WRAPPER")])
    assert _run(monkeypatch, "--enforce-read-completeness") == 1
    _setup(ws, items, [_disp("function:V:mint#1", read_state="DUPLICATE_WRAPPER",
                             duplicate_of="function:W:mint#9")])
    assert _run(monkeypatch, "--enforce-read-completeness") == 0
