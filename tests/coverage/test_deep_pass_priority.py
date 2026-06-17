"""
Task 3 — deep-pass priority scheduler + ledger.

The queue must rank advisory-escalation hits and special-focus-with-asset-movement clusters ahead of
generic backlog, and the ledger must account for executed vs skipped deep passes and BLOCK freeze when a
high-priority (tier 1-2) deep pass was skipped without a budget waiver (the Panoptic 9-Medium backlog).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
deep_queue = importlib.import_module("deep_pass_queue")
ledger = importlib.import_module("deep_pass_ledger")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(mid, contract, name, score=4, tags=None, ext=False):
    return {"id": mid, "kind": "function", "contract": contract, "file": f"{contract}.sol", "name": name,
            "signature": f"function {name}() external", "in_scope": True, "attack_surface_score": score,
            "tags": tags or [], "external_calls": ext, "source_span": {}}


def _deep(mid, agent="logic", routed_reason=None, advisory=False):
    d = {"manifest_id": mid, "status": "assigned", "assigned_pass": "deep", "assigned_agent": agent}
    if routed_reason:
        d["routed_reason"] = routed_reason
    if advisory:
        d["advisory_escalation"] = {"source_lens": "checkpoint_liveness"}
    return d


def _setup(ws, items, disps):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": disps}))


def _run(mod, argv=None):
    old = sys.argv
    sys.argv = [mod.__name__] + (argv or [])
    try:
        return mod.main()
    finally:
        sys.argv = old


def test_advisory_hit_ranked_tier1_before_backlog(ws):
    adv = _item("function:CT:withdraw#1", "CT", "withdraw", tags=["accounting"])
    misc = _item("function:Lib:helper#2", "Lib", "helper", score=3, tags=[])
    _setup(ws, [adv, misc],
           [_deep(adv["id"], agent="dos", routed_reason="advisory_escalation: high-risk checkpoint_liveness", advisory=True),
            _deep(misc["id"], agent="logic")])
    assert _run(deep_queue) == 0
    q = json.loads((ws / "output" / "deep_pass_queue.json").read_text())
    first = q["clusters"][0]
    assert first["priority_tier"] == 1 and "CT" in first["cluster_id"]
    assert first["execution_position"] == 1
    assert q["summary"]["high_priority_clusters"] >= 1


def test_ledger_accounts_executed_and_skipped(ws):
    a = _item("function:CT:withdraw#1", "CT", "withdraw", tags=["accounting"], ext=True)
    b = _item("function:Risk:liquidate#2", "Risk", "liquidate", tags=[])
    # Both are queued as needs_deep_pass. a is special-focus+external (tier2), b is liquidation (tier3).
    _setup(ws, [a, b], [_deep(a["id"], agent="dos"), _deep(b["id"], agent="logic")])
    assert _run(deep_queue) == 0            # queue captures both
    # Now EXECUTE a's deep pass (resolve it) and leave b pending.
    disps = json.loads((ws / "output" / "coverage_dispositions.json").read_text())
    for d in disps["dispositions"]:
        if d["manifest_id"] == a["id"]:
            d.update({"status": "cleared", "evidence": ["x"], "clear_reason": "done",
                      "attacker_reachability": "x", "guard_or_invariant": "y", "no_impact_reason": "z"})
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(disps))
    rc = _run(ledger)
    led = json.loads((ws / "output" / "deep_pass_budget_summary.json").read_text())
    assert led["executed"] == 1 and led["skipped"] == 1
    skipped = json.loads((ws / "output" / "skipped_deep_passes_with_reason.json").read_text())["skipped"]
    assert any(s["manifest_id"] == b["id"] and "tier-3" in s["reason"] for s in skipped)
    assert rc == 0                          # a (tier-2) executed; only tier-3 (b) skipped → no block


def test_ledger_blocks_on_skipped_high_priority(ws):
    adv = _item("function:CT:withdraw#1", "CT", "withdraw", tags=["accounting"])
    _setup(ws, [adv], [_deep(adv["id"], agent="dos",
                             routed_reason="advisory_escalation: high-risk checkpoint_liveness", advisory=True)])
    assert _run(deep_queue) == 0
    assert _run(ledger) == 1                # tier-1 cluster skipped, no waiver → BLOCK
    # withdraw is high-risk (vault_accounting): a CLUSTER waiver is now rejected; a valid PER-SINK waiver unblocks
    (ws / "output" / "deep_pass_waiver.json").write_text(json.dumps(
        {"waivers": [{"manifest_id": adv["id"], "function": "withdraw", "sink": "safeTransfer(asset)",
                      "risk_class": "vault_accounting", "reason": "budget; follow-up scheduled",
                      "no_impact_justification": "allowance + liquidity checks; moves only caller's own assets",
                      "answer_independent_reviewer": "lead", "follow_up": "2024-04-01"}]}))
    assert _run(ledger) == 0
