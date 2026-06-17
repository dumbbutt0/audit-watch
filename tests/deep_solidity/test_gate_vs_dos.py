"""
Task 4 — gate-vs-DoS adversarial check.

A clear that frames a revert/underflow as an "intended gate" must carry a liveness disproof (does the
same revert block a legitimate actor on a critical path?). Without it → routed to needs_deep_pass with
status `intended_gate_requires_liveness_disproof`. This is the Panoptic M-01 near-miss: the underflow that
"prevents liquidating solvent accounts" is also a liquidation DoS for distribution-insolvent accounts.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
gdu = importlib.import_module("gate_dos_utils")
sweep_write = importlib.import_module("coverage_sweep_write")


# ---------------- unit tests on the validator ----------------

def test_detects_intended_gate_language():
    assert gdu.is_intended_gate_clear({"clear_reason": "the underflow prevents liquidating solvent accounts; intended gate"})
    assert gdu.is_intended_gate_clear({"no_impact_reason": "reverts as expected when balance is too low"})
    assert not gdu.is_intended_gate_clear({"clear_reason": "pure getter, returns a constant"})


def test_missing_disproof_flagged():
    cls = gdu.classify({"clear_reason": "solvent accounts underflow here — that's the intended gate"})
    assert cls["status"] == "missing_liveness_disproof"
    assert set(gdu.REQUIRED_LIVENESS_FIELDS).issubset(set(cls["missing"]))


def test_full_disproof_ok():
    cls = gdu.classify({
        "clear_reason": "underflow reverts by design",
        "who_can_trigger": "only the liquidatee's own already-solvent state",
        "blocks_critical_path": "liquidation",
        "one_user_blocks_others": "no — each account's revert is isolated to its own liquidation",
        "affects_liveness_path": "yes, liquidation, but only when the account is actually solvent",
        "recovery_exists": "account becomes liquidatable again once truly insolvent",
        "bounded_or_permanent": "bounded — clears as soon as solvency changes",
    })
    assert cls["status"] == "ok"


def test_unrecognized_critical_path_flagged():
    cls = gdu.classify({
        "clear_reason": "this check acts as a gate",
        "who_can_trigger": "anyone", "blocks_critical_path": "some unrelated thing",
        "one_user_blocks_others": "no", "affects_liveness_path": "no",
        "recovery_exists": "n/a", "bounded_or_permanent": "bounded"})
    assert cls["status"] == "missing_liveness_disproof"
    assert any("blocks_critical_path" in m for m in cls["missing"])


# ---------------- integration via coverage_sweep_write ----------------

@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "coverage_sweep").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(mid, name, score=2):
    return {"id": mid, "kind": "function", "contract": "RiskEngine", "file": "RiskEngine.sol",
            "name": name, "signature": f"function {name}() external", "in_scope": True,
            "attack_surface_score": score, "tags": [], "source_span": {}}


def _setup(ws, item, decision):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": [item]}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": item["id"], "status": "unassigned"}]}))
    (ws / "data" / "coverage_sweep" / "_decisions.json").write_text(json.dumps({"decisions": [decision]}))


def _run():
    old = sys.argv
    sys.argv = ["coverage_sweep_write"]
    try:
        return sweep_write.main()
    finally:
        sys.argv = old


def _status(ws, mid):
    d = json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]
    return next(x["status"] for x in d if x["manifest_id"] == mid)


def test_intended_gate_clear_routed_to_deep_pass(ws):
    it = _item("function:RiskEngine:getLiquidationBonus#01", "getLiquidationBonus", score=2)
    _setup(ws, it, {"manifest_id": it["id"], "disposition": "cleared",
                    "evidence": ["RiskEngine.sol:516"],
                    "reason": "thresholdCross-balanceCross underflow reverts for solvent accounts — intended gate"})
    assert _run() == 0
    assert _status(ws, it["id"]) == "assigned"   # routed to needs_deep_pass, not cleared


def test_intended_gate_with_disproof_clears(ws):
    it = _item("function:RiskEngine:getLiquidationBonus#01", "getLiquidationBonus", score=2)
    oracle_liq_fields = next(fields for name, _, fields in __import__("spec_checklist_utils").SURFACES
                             if name == "oracle_liquidation")
    dec = {"manifest_id": it["id"], "disposition": "cleared",
           "evidence": ["RiskEngine.sol:516"],
           "reason": "underflow reverts by design",
           "who_can_trigger": "the account's own solvent state",
           "blocks_critical_path": "liquidation",
           "one_user_blocks_others": "no",
           "affects_liveness_path": "only when account is genuinely solvent",
           "recovery_exists": "becomes liquidatable when insolvent",
           "bounded_or_permanent": "bounded"}
    # getLiquidationBonus is also an oracle_liquidation spec surface → it needs that checklist too.
    # Concrete (non-boilerplate) so the adversarial spec-checklist validator accepts it.
    dec.update({f: "getLiquidationBonus at RiskEngine.sol:516 reads the negative tick; rounding does not "
                   "inflate the reference price; the revert occurs only when the account is solvent"
                for f in oracle_liq_fields})
    _setup(ws, it, dec)
    assert _run() == 0
    assert _status(ws, it["id"]) == "cleared"


def test_ordinary_clear_untouched(ws):
    it = _item("function:RiskEngine:vegoid#01", "vegoid", score=1)
    _setup(ws, it, {"manifest_id": it["id"], "disposition": "cleared",
                    "evidence": ["RiskEngine.sol:2292"], "reason": "pure getter returns a stored constant"})
    assert _run() == 0
    assert _status(ws, it["id"]) == "cleared"
