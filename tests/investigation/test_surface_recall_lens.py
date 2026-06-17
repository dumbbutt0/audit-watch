"""Phase-81b tests for the surface-recall lead lens (RESEARCH-ONLY). Includes the no-subject-names (no
answer-key-hardcoding) assertion and the protected-module no-drift hashes."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation import surface_recall_lens as L  # noqa: E402
from investigation.lead_schema import is_valid_lead  # noqa: E402

FIXTURE = """
interface IThing { function poke(uint256 x) external; }
contract Vault {
    address owner; address router;
    function setRouter(address r) public onlyOwner { router = r; }
    function execute(address target, bytes memory data) external returns (bool) {
        (bool success, ) = target.call(data); return success;
    }
    function sgReceive(uint16 c, bytes memory src, uint n, address t, uint amt, bytes memory payload) external onlyExecutor {
        IERC20(t).transfer(recipient, amt);
    }
    function collectFees(uint v, bytes memory info, bytes memory sig) public onlyUtb { feeBalance += v; }
    function refundLeftover(address to) public { to.call{value: leftover}(""); }
    function totalAssets() public view returns (uint) { return x; }
    function _internalHelper() internal { x += 1; }
}
"""


def _leads():
    return L.lens_to_leads(L.enumerate_functions(FIXTURE, "fix.sol"))


def test_1_emitted_leads_are_valid_static_leads():
    leads = _leads()
    assert leads
    assert all(is_valid_lead(l) for l in leads)


def test_2_surface_classes_assigned():
    by = {l["candidate_id"]: l for l in _leads()}
    assert "admin_config_setter" in by["Vault.setRouter"]["surface_classes"]
    assert "external_executor" in by["Vault.execute"]["surface_classes"]
    assert "bridge_receive" in by["Vault.sgReceive"]["surface_classes"]
    assert "fee_path" in by["Vault.collectFees"]["surface_classes"]
    assert "refund_path" in by["Vault.refundLeftover"]["surface_classes"]


def test_3_excludes_getters_interfaces_and_internal():
    ids = {l["candidate_id"] for l in _leads()}
    assert "Vault.totalAssets" not in ids       # pure/view getter, no class
    assert "IThing.poke" not in ids             # interface declaration
    assert "Vault._internalHelper" not in ids   # internal visibility


def test_4_unguarded_config_setter_is_captured():
    # P81f recall repair (case a): an UNGUARDED state-changing config setter (the missing-access-control bug class,
    # e.g. H-01 unguarded setRouter) MUST be captured, and flagged auth_gated=False.
    src = """
    contract C {
        address router;
        function setRouter(address r) public { router = r; }          // unguarded -> the bug
        function setGuarded(address r) public onlyOwner { router = r; } // guarded
        function settings() public view returns (address) { return router; } // view 'set'-named getter
    }
    """
    by = {l["candidate_id"]: l for l in L.lens_to_leads(L.enumerate_functions(src, "c.sol"))}
    # (a) unguarded setter advances as an admin_config_setter surface, marked not auth-gated
    assert "C.setRouter" in by and "admin_config_setter" in by["C.setRouter"]["surface_classes"]
    assert by["C.setRouter"]["signals"]["auth_gated"] is False
    # (b) guarded setter is also a surface but flagged auth_gated=True (downstream deep_pass rejects it via the defense ledger)
    assert "C.setGuarded" in by and "admin_config_setter" in by["C.setGuarded"]["surface_classes"]
    assert by["C.setGuarded"]["signals"]["auth_gated"] is True
    # view 'set'-named getter is excluded (exclude_view_pure)
    assert "C.settings" not in by or "admin_config_setter" not in by["C.settings"]["surface_classes"]


def test_4b_guarded_setter_rejected_downstream():
    # (b) end-to-end: a guarded (onlyOwner) setter, run through the UNCHANGED deep_pass with the defense ledger,
    # is REJECTED (defense blocks) — an unguarded setter with no blocking defense is not.
    from investigation.deep_pass import run as deep_run, FALSIFIERS
    from investigation.lead_schema import normalize_lead
    lead = normalize_lead({"candidate_id": "C.setGuarded", "detector_family": "surface_recall_lens",
                           "contract": "C", "function": "setGuarded"})
    b = deep_run(lead, {"context": {"source_resolved": True},
                        "defense_ledger": {"access_control": {"classification": "blocks_candidate", "evidence": "onlyOwner"}}})
    assert b["final_decision"] == "REJECTED"


def test_5_all_leads_research_only_unwired():
    for l in _leads():
        assert l["routes_in_production"] is False and l["research_only"] is True
        assert l["is_gate"] is False and l["routed_manifest_ids"] == []


def test_6_no_subject_specific_names_in_config_or_module():
    # "no answer-key-derived hardcoding": the lens config + module must not contain subject contract/function ids.
    forbidden = ["receivefrombridge", "dcnteth", "decentbridgeexecutor", "decenteth", "utbfeecollector",
                 "swapnopath", "stargatebridgeadapter", "uniswapper", "positionregistry", "dolomiteconnector",
                 "_getpositiontvl", "noya", "beanstalk", "sendtokenstotrustedaddress"]
    cfg = (ROOT / "config" / "surface_recall_lens.json").read_text().lower()
    mod = (ROOT / "scripts" / "investigation" / "surface_recall_lens.py").read_text().lower()
    for tok in forbidden:
        assert tok not in cfg, f"subject token {tok!r} in config"
        assert tok not in mod, f"subject token {tok!r} in module"


def test_7_self_test_passes():
    assert L._self_test() == 0


def test_9_bridge_receive_precision_no_view_math():
    # P81c: a view/math function that merely decodes data must NOT be tagged bridge_receive;
    # a real bridge-callback name (or cross-chain shape) still must be.
    src = """
    contract C {
        function _getPositionTVL(bytes memory d) public view returns (uint256) {
            (uint a, uint b) = abi.decode(d, (uint, uint)); return a + b;
        }
        function sgReceive(uint16 srcChainId, bytes memory srcAddress, uint n, address t, uint amt, bytes memory payload) external {
            execute(payload);
        }
        function onMathThing(bytes memory d) external view returns (uint) { return abi.decode(d, (uint)); }
    }
    """
    by = {l["candidate_id"]: l for l in L.lens_to_leads(L.enumerate_functions(src, "c.sol"))}
    assert "C._getPositionTVL" not in by or "bridge_receive" not in by["C._getPositionTVL"]["surface_classes"]
    assert "bridge_receive" in by["C.sgReceive"]["surface_classes"]
    # a view fn that only abi.decodes is not a bridge_receive surface
    assert "C.onMathThing" not in by or "bridge_receive" not in by["C.onMathThing"]["surface_classes"]


def test_10_decent_recall_preserved_after_tightening():
    # the frozen Decent run must still cover all 9 awarded incl the two named functions after P81c
    import json
    from investigation import surface_recall_score as S
    base = ROOT / "documentation" / "research" / "_p81b" / "decent"
    if not (base / "leads.json").exists():
        return
    leads = json.loads((base / "leads.json").read_text())["leads"]
    awarded = json.loads((base / "awarded_map.json").read_text())["awarded"]
    r = S.score(leads, awarded, required_functions=["UTB.receiveFromBridge", "DecentBridgeExecutor.execute"])
    assert r["totals"]["direct"] >= 8        # must not drop below 8/9 (actually 9/9)
    assert all(r["required_functions"].values())


def test_8_protected_modules_no_drift():
    def h(rel):
        return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16]
    assert h("scripts/investigation/deep_pass.py") == "57c29fff73803fbc"
    assert h("scripts/investigation/lead_schema.py") == "3c57f04e2f8b6332"
    assert h("scripts/investigation/transitions.py") == "2c00069cb49362e3"
    assert h("scripts/investigation/hygiene_validate.py") == "b9e18f299571f34b"
    assert h("scripts/investigation/abc_eval.py") == "5e0d855d84503022"
    assert h("scripts/access_control_missing_auth_detector.py") == "f9ec0bff8de53cf0"
    assert h("scripts/signature_replay_nonce_detector.py") == "e72b9994100d35e7"
    assert h("scripts/value_flow_surface.py").startswith("aca9125a")
