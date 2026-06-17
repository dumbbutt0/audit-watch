"""
Cross-artifact lifecycle lens: an in-scope contract that deploys/owns/upgrades an artifact keeps that
artifact's lifecycle audit-relevant THROUGH the controller, even when the artifact file is out of strict
scope (ArkProject AK-H4). No false positive on a safe lifecycle. No flag without an in-scope controller.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
cal = importlib.import_module("cross_artifact_lifecycle_taxonomy")
audit = importlib.import_module("cross_artifact_lifecycle_audit")


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


DEPLOY_NO_OWNERSHIP = ("function deployCollection() public { address impl = address(new ERC721Bridgeable()); "
                       "return address(new ERC1967Proxy(impl, abi.encodeWithSelector(ERC721Bridgeable.initialize.selector))); }")
SAFE_LIFECYCLE = ("function deployManaged(address bridgeOwner) external { Managed impl = new Managed(); "
                  "impl._disableInitializers(); address p = address(new ERC1967Proxy(address(impl), data)); "
                  "Managed(p).transferOwnership(bridgeOwner); Managed(p).upgradeToAndCall(address(impl), \"\"); }")


# ---------- classify (unit) ----------

def test_deployer_without_ownership_is_risk():
    c = cal.classify("deployCollection", DEPLOY_NO_OWNERSHIP)
    assert c["cross_artifact_sensitive"] is True
    assert c["role"] in ("deployer", "factory")
    assert "ownership_transfer_to_controller" in c["missing_lifecycle"]
    assert "disable_initializers" in c["missing_lifecycle"]
    assert cal.is_high_risk(c) is True


def test_safe_lifecycle_no_missing_steps():
    c = cal.classify("deployManaged", SAFE_LIFECYCLE)
    assert c["cross_artifact_sensitive"] is True
    assert c["missing_lifecycle"] == []          # disable_init + ownership + upgrade all present
    assert cal.is_high_risk(c) is False           # no false positive


def test_memory_allocation_not_a_deploy():
    # `new string(...)` / `new bytes(...)` are memory allocations, NOT contract deploys (case-sensitive guard)
    c = cal.classify("uint256AsciiToString", "function f() pure { string memory s = new string(len); bytes memory b = new bytes(3); }")
    assert c["cross_artifact_sensitive"] is False


def test_plain_function_not_cross_artifact():
    c = cal.classify("getOwner", "function getOwner() view returns (address) { return owner; }")
    assert c["cross_artifact_sensitive"] is False


# ---------- audit runner (end-to-end, --no-source; signal in signature) ----------

def _item(contract, name, signature, mid=None, status="unassigned", in_scope=True):
    return {"id": mid or f"function:{contract}:{name}#0001", "kind": "function", "contract": contract,
            "file": f"{contract}.sol", "name": name, "signature": signature, "in_scope": in_scope,
            "attack_surface_score": 4, "tags": [], "source_span": {}}


def test_runner_flags_under_escalated_not_discarded_by_scope(ws):
    # the deployed ERC721Bridgeable is NOT in the manifest (out of strict scope) — the lens must still flag
    # the in-scope deployer as lifecycle_under_escalated (no finding references it).
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("CollectionDeployer", "deployCollection", DEPLOY_NO_OWNERSHIP)]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:CollectionDeployer:deployCollection#0001", "status": "cleared",
         "evidence": ["x.sol:1"], "clear_reason": "deploys collection"}]})
    assert _run(audit, ["--no-source"]) == 0
    rep = json.loads((ws / "output" / "cross_artifact_lifecycle_audit.json").read_text())
    assert "function:CollectionDeployer:deployCollection#0001" in rep["lifecycle_under_escalated"]


def test_runner_safe_lifecycle_no_false_positive(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("SafeDeployer", "deployManaged", SAFE_LIFECYCLE)]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:SafeDeployer:deployManaged#0001", "status": "cleared",
         "evidence": ["x.sol:1"], "clear_reason": "safe"}]})
    assert _run(audit, ["--no-source"]) == 0
    rep = json.loads((ws / "output" / "cross_artifact_lifecycle_audit.json").read_text())
    assert rep["lifecycle_under_escalated"] == []   # safe lifecycle is not under-escalated
    statuses = {d["manifest_id"]: d["status"] for d in rep["detected"]}
    assert statuses["function:SafeDeployer:deployManaged#0001"] == "lifecycle_cleared_with_local_proof"


def test_runner_out_of_scope_artifact_without_controller_not_flagged(ws):
    # an out-of-scope upgradeable artifact with NO in-scope controller deploying it → not flagged
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("StandaloneToken", "_authorizeUpgrade", "function _authorizeUpgrade(address) internal {}",
              status="deferred", in_scope=False)]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:StandaloneToken:_authorizeUpgrade#0001", "status": "deferred_out_of_scope",
         "scope_reason": "out of scope"}]})
    assert _run(audit, ["--no-source"]) == 0
    rep = json.loads((ws / "output" / "cross_artifact_lifecycle_audit.json").read_text())
    assert rep["total_cross_artifact_sensitive"] == 0   # out-of-scope item is not classified as a controller


def test_runner_scope_links_deferred_artifact(ws):
    # if the deployed artifact IS a deferred_out_of_scope manifest contract, record the scope link
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("CollectionDeployer", "deployCollection", DEPLOY_NO_OWNERSHIP),
        _item("ERC721Bridgeable", "initialize", "function initialize(bytes) {}",
              mid="function:ERC721Bridgeable:initialize#dead", in_scope=False)]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:CollectionDeployer:deployCollection#0001", "status": "unassigned"},
        {"manifest_id": "function:ERC721Bridgeable:initialize#dead", "status": "deferred_out_of_scope", "scope_reason": "oos"}]})
    assert _run(audit, ["--no-source"]) == 0
    rep = json.loads((ws / "output" / "cross_artifact_lifecycle_audit.json").read_text())
    links = rep["cross_artifact_scope_linked"]
    assert any(l["manifest_id"] == "function:CollectionDeployer:deployCollection#0001"
               and any(x["artifact"] == "ERC721Bridgeable" and x["out_of_scope"] for x in l["links"]) for l in links)
