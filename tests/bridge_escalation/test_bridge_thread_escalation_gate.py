"""
Bridge thread escalation guard: a bridge-relevant promising thread may not be silently dropped — it must
be escalated to a finding OR carry a concrete invalidation. Non-bridge low-confidence threads are still
droppable. Override downgrades block→warn. (ArkProject AK-M3 / Swan-Dria H-03.)
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
gate = importlib.import_module("bridge_thread_escalation_gate")
bt = importlib.import_module("bridge_terms")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "threads").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")          # strict path on
    monkeypatch.delenv("AUDITWATCH_BRIDGE_THREAD_OVERRIDE", raising=False)
    return tmp_path


def _threads(ws, *threads):
    p = ws / "data" / "threads" / "promising_threads.jsonl"
    p.write_text("".join(json.dumps(t) + "\n" for t in threads))


def _findings(ws, findings):
    (ws / "output" / "merged_findings.json").write_text(json.dumps({"findings": findings}, indent=2))


def _dispositions(ws, dispositions):
    (ws / "data" / "threads" / "_bridge_thread_dispositions.json").write_text(
        json.dumps({"dispositions": dispositions}, indent=2))


def _run(argv):
    old = sys.argv
    sys.argv = ["bridge_thread_escalation_gate"] + argv
    try:
        return gate.main()
    finally:
        sys.argv = old


BRIDGE_THREAD = {"thread_id": "T-04", "verdict": "MEDIUM_THREAD",
                 "entry_conditions": "withdraw releases NFT via safeTransferFrom; recipient hook re-enters the bridge",
                 "violation_path": ["Bridge.withdraw releases from escrow", "onERC721Received re-enters"],
                 "evidence": "Escrow._withdrawFromEscrow; no reentrancy guard"}
NONBRIDGE_THREAD = {"thread_id": "T-99", "verdict": "MEDIUM_THREAD",
                    "entry_conditions": "integer rounding in an internal average helper",
                    "violation_path": ["avg() truncates"], "evidence": "no funds, pure math"}


def test_bridge_thread_no_finding_no_justification_blocks(ws):
    _threads(ws, BRIDGE_THREAD)
    _findings(ws, [])                                   # not escalated
    assert _run(["--quiet"]) == 1                       # BLOCK
    rep = json.loads((ws / "output" / "bridge_thread_escalation_gate.json").read_text())
    assert rep["blocked"] == 1 and rep["blocks"][0]["thread_id"] == "T-04"
    # routed to human queue (no silent drop)
    hq = (ws / "data" / "triage" / "human_review_queue.jsonl").read_text()
    assert "T-04" in hq


def test_bridge_thread_escalated_to_finding_passes(ws):
    _threads(ws, BRIDGE_THREAD)
    _findings(ws, [{"id": "DT-009", "thread_refs": ["T-04"]}])   # escalated
    assert _run(["--quiet"]) == 0


def test_bridge_thread_with_concrete_invalidation_passes(ws):
    _threads(ws, BRIDGE_THREAD)
    _findings(ws, [])
    _dispositions(ws, [{"thread_id": "T-04",
                        "exact_sink": "Escrow._withdrawFromEscrow safeTransferFrom (Escrow.sol:79)",
                        "attacker_entrypoint": "Bridge.withdraw(request) by listing recipient",
                        "resolution": {"type": "bounded",
                                       "reason": "escrow slot zeroed before the external call (CEI); reentrant withdraw finds _escrow==0 and returns false"}}])
    assert _run(["--quiet"]) == 0


def test_vague_invalidation_still_blocks(ws):
    _threads(ws, BRIDGE_THREAD)
    _findings(ws, [])
    _dispositions(ws, [{"thread_id": "T-04", "exact_sink": "", "attacker_entrypoint": "",
                        "resolution": {"type": "", "reason": "low confidence, already covered"}}])
    assert _run(["--quiet"]) == 1


def test_nonbridge_low_confidence_thread_droppable(ws):
    _threads(ws, NONBRIDGE_THREAD)                      # no bridge terms
    _findings(ws, [])                                    # dropped, no justification
    assert _run(["--quiet"]) == 0                        # normal rules: not a bridge thread, can be dropped
    rep = json.loads((ws / "output" / "bridge_thread_escalation_gate.json").read_text())
    assert rep["total_bridge_threads"] == 0


def test_override_downgrades_block_to_warn(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_BRIDGE_THREAD_OVERRIDE", "1")
    _threads(ws, BRIDGE_THREAD)
    _findings(ws, [])
    assert _run(["--quiet"]) == 0                        # override → pass (warn)
    rep = json.loads((ws / "output" / "bridge_thread_escalation_gate.json").read_text())
    assert rep["blocked"] == 1 and rep["override_active"] is True


def test_strict_off_does_not_block(ws, monkeypatch):
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)   # not full-audit, default strict flag false
    _threads(ws, BRIDGE_THREAD)
    _findings(ws, [])
    assert _run(["--quiet"]) == 0                        # advisory when strict not effective
