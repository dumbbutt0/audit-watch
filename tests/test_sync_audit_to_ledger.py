"""sync_audit_to_ledger.py — keeps the real-world ledger in sync with an audit's PoC-proven findings,
NON-DESTRUCTIVELY. Pins: real-world gate (eval/blind skip), contract dedup vs curated entries, human
outcome_class preserved + never fabricated on new cards, and idempotent (clean no-op second run)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_audit_to_ledger as sal  # noqa: E402


def _audit(tmp, audit_id, meta, candidates, poc_rows):
    a = tmp / "audits" / audit_id
    (a / "output" / "candidates").mkdir(parents=True, exist_ok=True)
    (a / "data" / "runtime_poc").mkdir(parents=True, exist_ok=True)
    (a / "meta.json").write_text(json.dumps(meta))
    for c in candidates:
        (a / "output" / "candidates" / f"{c['id']}.json").write_text(json.dumps(c))
    (a / "data" / "runtime_poc" / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in poc_rows))
    return a


def _cand(fid, sev, contract, fn, proved, state="ready", title=None):
    return {"id": fid, "state": state, "title": title or f"{fid} finding",
            "classification": {"severity": sev}, "location": {"contract": contract, "function": fn},
            "manifest_refs": [f"src/{contract}.sol:{fn}"], "poc": {"proved": proved}}


@pytest.fixture
def patched(tmp_path, monkeypatch):
    rw = tmp_path / "documentation" / "real_world_results.json"
    rw.parent.mkdir(parents=True, exist_ok=True)
    # curated ledger: one human-adjudicated TipRun entry on contract "Risk"
    rw.write_text(json.dumps({"candidate_findings": [
        {"target": "TipRun", "title": "curated F-1", "outcome_class": "in_review",
         "outcome_provenance": "human triage", "verifier": {"target": "Risk.checkValidTransition"}},
    ], "targets": [{"target": "TipRun", "notes": "curated human note"}], "summary": {}}))
    monkeypatch.setattr(sal, "ROOT", tmp_path)
    monkeypatch.setattr(sal, "RW", rw)
    return tmp_path, rw


def test_realworld_gate_skips_eval_blind(patched, monkeypatch):
    tmp, rw = patched
    _audit(tmp, "x-eval", {"platform": "C4"}, [_cand("F1", "High", "Foo", "bar", True)],
           [{"finding_id": "F1", "test_contract": "PoC_X", "test_file": "t.sol"}])
    monkeypatch.setattr(sys, "argv", ["x", "--audit", "x-eval", "--quiet"])
    assert sal.main() == 0
    assert "x-eval:F1" not in rw.read_text()  # eval audit never writes to the ledger


def test_adds_new_contract_skips_dup_preserves_outcome(patched, monkeypatch):
    tmp, rw = patched
    cands = [
        _cand("BSA-001", "High", "PermissionsTransLib", "processAdminSetSignerPermissions", True),  # NEW contract
        _cand("LOG-001", "High", "Risk", "checkValidTransition", True),  # dup contract -> skip
        _cand("PC-01", "Medium", "TransactionProcessor", "registerPlugin", False, state="poc_required"),  # non-PoC -> note
    ]
    poc = [{"finding_id": "BSA-001", "test_contract": "PoC_Esc", "test_file": "e.sol", "evidence": "drained"},
           {"finding_id": "LOG-001", "test_contract": "PoC_M", "test_file": "m.sol"}]
    _audit(tmp, "tiprun-rw", {"platform": "HackenProof", "ledger_target": "TipRun", "ledger_sync": True}, cands, poc)
    monkeypatch.setattr(sys, "argv", ["x", "--audit", "tiprun-rw", "--quiet"])
    assert sal.main() == 0
    d = json.loads(rw.read_text())
    cf = d["candidate_findings"]
    # curated entry untouched (outcome preserved)
    cur = [c for c in cf if c.get("title") == "curated F-1"][0]
    assert cur["outcome_class"] == "in_review" and cur["outcome_provenance"] == "human triage"
    # exactly one new owned card: BSA-001 (new contract), REPRODUCED, NO fabricated outcome_class
    owned = [c for c in cf if str(c.get("candidate_id", "")).startswith("tiprun-rw:")]
    assert [c["candidate_id"] for c in owned] == ["tiprun-rw:BSA-001"]
    assert owned[0]["verifier"]["poc_status"] == "REPRODUCED"
    assert "outcome_class" not in owned[0] or owned[0]["outcome_class"] is None
    # LOG-001 (dup contract "Risk") was NOT added
    assert not any(c.get("candidate_id") == "tiprun-rw:LOG-001" for c in cf)
    # non-PoC PC-01 -> target reaudit_note, never a card; curated note preserved
    tgt = [t for t in d["targets"] if t["target"] == "TipRun"][0]
    assert tgt["notes"] == "curated human note" and "PC-01" in tgt["reaudit_note"]


def test_idempotent_second_run_is_clean_noop(patched, monkeypatch):
    tmp, rw = patched
    cands = [_cand("BSA-001", "High", "PermissionsTransLib", "processAdminSetSignerPermissions", True)]
    poc = [{"finding_id": "BSA-001", "test_contract": "PoC_Esc", "test_file": "e.sol"}]
    _audit(tmp, "tiprun-rw", {"platform": "HackenProof", "ledger_target": "TipRun", "ledger_sync": True}, cands, poc)
    monkeypatch.setattr(sys, "argv", ["x", "--audit", "tiprun-rw", "--quiet"])
    assert sal.main() == 0
    first = rw.read_text()
    assert sal.main() == 0
    assert rw.read_text() == first  # second run writes nothing (no churn)
    # and a human outcome added later is preserved across a re-sync
    d = json.loads(rw.read_text())
    for c in d["candidate_findings"]:
        if c.get("candidate_id") == "tiprun-rw:BSA-001":
            c["outcome_class"] = "paid"
    rw.write_text(json.dumps(d))
    assert sal.main() == 0
    d2 = json.loads(rw.read_text())
    owned = [c for c in d2["candidate_findings"] if c.get("candidate_id") == "tiprun-rw:BSA-001"][0]
    assert owned["outcome_class"] == "paid"  # human field preserved on re-sync
