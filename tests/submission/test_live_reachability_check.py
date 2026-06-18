"""live_reachability_check.py — on-chain evidence for the deployment-reachability axis. Fail-open without
on-chain coordinates / a backend; selector present -> wired; selector absent -> not_wired (the blocking
direction); proxy bytecode is resolved; a failed storage assertion downgrades to not_wired."""
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import live_reachability_check as lrc  # noqa: E402

SIG = "withdraw(uint256)"
SEL = lrc._selector(SIG)  # 4-byte selector hex, no 0x


def _manifest(tmp_path, onchain):
    m = {"schema": "deployment_manifest/v1"}
    if onchain is not None:
        m["onchain"] = onchain
    (tmp_path / "deployment_manifest.json").write_text(json.dumps(m))


def _fake_qn(bytecode_by_addr, storage=None):
    mod = types.ModuleType("quicknode_mcp")

    def get_bytecode(address, chain):
        bc = bytecode_by_addr.get(address)
        return bc if bc is not None else {}

    def get_storage_slots(address, chain, slots):
        return {"slots": {str(s): (storage or {}).get(s) for s in slots}}

    mod.get_bytecode = get_bytecode
    mod.get_storage_slots = get_storage_slots
    return mod


@pytest.fixture
def patch_audit(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(lrc, "audit_path", lambda *p: tmp_path.joinpath(*p))
    monkeypatch.setattr(sys, "argv", ["live_reachability_check.py", "--quiet"])
    return tmp_path


def _install_qn(monkeypatch, mod):
    monkeypatch.setitem(sys.modules, "quicknode_mcp", mod)


def test_no_coordinates_skips(patch_audit, monkeypatch):
    _manifest(patch_audit, None)
    assert lrc.main() == 0
    d = json.loads((patch_audit / "output" / "live_reachability.json").read_text())
    assert d["checked"] is False and d["findings"] == {}


def test_non_contract_degrades_to_checklist(patch_audit, monkeypatch):
    _manifest(patch_audit, {"address": "0xabc", "chain": "ethereum",
                            "targets": [{"finding_id": "F-1", "signature": SIG}]})
    _install_qn(monkeypatch, _fake_qn({"0xabc": {"is_contract": False}}))
    assert lrc.main() == 0
    d = json.loads((patch_audit / "output" / "live_reachability.json").read_text())
    assert d["checked"] is False
    assert d["findings"]["F-1"]["level"] == "checklist_required"


def test_selector_present_is_wired(patch_audit, monkeypatch):
    _manifest(patch_audit, {"address": "0xabc", "chain": "ethereum",
                            "targets": [{"finding_id": "F-1", "signature": SIG}]})
    code = "0x6080" + "63" + SEL + "ffff"  # PUSH4 <selector> in the dispatcher
    _install_qn(monkeypatch, _fake_qn({"0xabc": {"is_contract": True, "bytecode_hex": code}}))
    assert lrc.main() == 0
    d = json.loads((patch_audit / "output" / "live_reachability.json").read_text())
    assert d["checked"] is True and d["findings"]["F-1"]["level"] == "wired"


def test_selector_absent_is_not_wired(patch_audit, monkeypatch):
    _manifest(patch_audit, {"address": "0xabc", "chain": "ethereum",
                            "targets": [{"finding_id": "F-1", "signature": SIG}]})
    _install_qn(monkeypatch, _fake_qn({"0xabc": {"is_contract": True, "bytecode_hex": "0x60806040deadbeef"}}))
    assert lrc.main() == 0
    d = json.loads((patch_audit / "output" / "live_reachability.json").read_text())
    assert d["findings"]["F-1"]["level"] == "not_wired"


def test_proxy_implementation_bytecode_resolved(patch_audit, monkeypatch):
    _manifest(patch_audit, {"address": "0xproxy", "chain": "ethereum",
                            "targets": [{"finding_id": "F-1", "signature": SIG}]})
    impl_code = "0x" + "63" + SEL + "00"
    proxy = {"is_contract": True, "bytecode_hex": "0xdead", "implementation_address": "0ximpl"}
    impl = {"is_contract": True, "bytecode_hex": impl_code}
    _install_qn(monkeypatch, _fake_qn({"0xproxy": proxy, "0ximpl": impl}))
    assert lrc.main() == 0
    d = json.loads((patch_audit / "output" / "live_reachability.json").read_text())
    assert d["implementation_address"] == "0ximpl"
    assert d["findings"]["F-1"]["level"] == "wired"  # selector found in IMPL, not proxy


def test_inactive_storage_assertion_is_not_wired(patch_audit, monkeypatch):
    # selector present (wired) but the gating slot is zero -> downgrade to not_wired
    _manifest(patch_audit, {"address": "0xabc", "chain": "ethereum",
                            "targets": [{"finding_id": "F-1", "signature": SIG}],
                            "storage_assertions": [{"finding_id": "F-1", "slot": 3, "expect_nonzero": True}]})
    code = "0x63" + SEL + "00"
    _install_qn(monkeypatch, _fake_qn({"0xabc": {"is_contract": True, "bytecode_hex": code}},
                                      storage={3: "0x0000000000000000000000000000000000000000000000000000000000000000"}))
    assert lrc.main() == 0
    d = json.loads((patch_audit / "output" / "live_reachability.json").read_text())
    assert d["findings"]["F-1"]["level"] == "not_wired"
