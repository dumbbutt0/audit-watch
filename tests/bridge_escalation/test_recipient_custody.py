"""
Recipient/custody compatibility lens: safe delivery to a recipient with no receiver-capability check
(non_receiver_lock) routes to bridge/custody review (ArkProject AK-M2). A delivery that explicitly checks
the receiver is not high-risk (no FP).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
rc = importlib.import_module("recipient_custody_taxonomy")
audit = importlib.import_module("recipient_custody_audit")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _write(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return p


def _run(mod, argv):
    old = sys.argv
    sys.argv = [mod.__name__] + argv
    try:
        return mod.main()
    finally:
        sys.argv = old


SAFE_NO_CHECK = "function withdraw(address to, uint256 id) external { IERC721(c).safeTransferFrom(address(this), to, id); }"
SAFE_WITH_CHECK = ("function withdraw(address to, uint256 id) external { "
                   "require(IERC165(to).supportsInterface(type(IERC721Receiver).interfaceId)); "
                   "IERC721(c).safeTransferFrom(address(this), to, id); }")


# ---------- classify (unit) ----------

def test_safe_transfer_without_receiver_check_is_high_risk():
    c = rc.classify("withdraw", SAFE_NO_CHECK)
    assert c["recipient_custody_sensitive"] and c["category"] == "non_receiver_lock"
    assert rc.is_high_risk(c) is True


def test_safe_transfer_with_explicit_check_not_high_risk():
    c = rc.classify("withdraw", SAFE_WITH_CHECK)
    assert c["recipient_custody_sensitive"] is True
    assert rc.is_high_risk(c) is False          # explicit receiver check → no FP


def test_non_delivery_function_not_sensitive():
    c = rc.classify("getOwner", "function getOwner() view returns (address) { return owner; }")
    assert c["recipient_custody_sensitive"] is False


# ---------- runner ----------

def _item(contract, name, signature, mid=None):
    return {"id": mid or f"function:{contract}:{name}#0001", "kind": "function", "contract": contract,
            "file": f"{contract}.sol", "name": name, "signature": signature, "in_scope": True,
            "attack_surface_score": 4, "tags": [], "source_span": {}}


def test_runner_routes_non_receiver_lock_to_review(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("Bridge", "withdraw", SAFE_NO_CHECK)]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Bridge:withdraw#0001", "status": "cleared", "evidence": ["b.sol:1"], "clear_reason": "x"}]})
    assert _run(audit, ["--no-source"]) == 0
    rep = json.loads((ws / "output" / "recipient_custody_audit.json").read_text())
    assert "function:Bridge:withdraw#0001" in rep["routed_to_bridge_custody_review"]
    assert rep["detected"][0]["no_retry_recovery"] is True   # no recover/retry fn in the contract


def test_runner_recovery_path_present_clears_retry_flag(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("Bridge", "withdraw", SAFE_NO_CHECK),
        _item("Bridge", "recoverStuckToken", "function recoverStuckToken(uint256 id) external onlyOwner {}",
              mid="function:Bridge:recoverStuckToken#0002")]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": []})
    assert _run(audit, ["--no-source"]) == 0
    rep = json.loads((ws / "output" / "recipient_custody_audit.json").read_text())
    wd = next(d for d in rep["detected"] if d["name"] == "withdraw")
    assert wd["no_retry_recovery"] is False     # a recover* function exists in the contract
