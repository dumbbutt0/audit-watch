"""P181 research F3 hook_lifecycle selector — avoid-filter correctness + a true-positive (no LLM/network)."""
import importlib
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS / "research"))
f3 = importlib.import_module("hook_lifecycle_selector")

_REMOVE_BODY = ("function onAfterRemoveLiquidity(address router) public onlySelfRouter(router) {"
                " accruedFees[i] += feeAmount; uint currentFee = minWithdrawalFeeBps; poolsFeeData[pool] = x; }")


def test_research_flags_unwired():
    assert f3._FLAGS == {"research_only": True, "routes_in_production": False, "is_gate": False,
                         "re_surface_only": True}


def test_true_positive_onafterremoveliquidity():
    c = f3.classify("onAfterRemoveLiquidity", "function onAfterRemoveLiquidity(address router) public",
                    visibility="public", mutability="", contract="UpliftOnlyExample", snippet=_REMOVE_BODY)
    assert c["hook_lifecycle_sensitive"] is True
    assert "state_mutation" in c["signals"] and "lifecycle_ordering" in c["signals"]


def test_afterupdate_array_lifecycle_positive():
    body = ("function afterUpdate(address _from,address _to,uint id) public {"
            " FeeData[] storage a = poolsFeeData[p][_from]; for(uint i;i<a.length;++i){} a.push(x); }")
    c = f3.classify("afterUpdate", "function afterUpdate(address,address,uint) public",
                    visibility="public", mutability="", contract="UpliftOnlyExample", snippet=body)
    assert c["hook_lifecycle_sensitive"] is True


# ---- avoid filters ----
def test_view_hook_skipped():
    c = f3.classify("onBeforeAddLiquidity", "function onBeforeAddLiquidity(...) public view",
                    visibility="public", mutability="view", contract="UpliftOnlyExample",
                    snippet="return true;")
    assert c["hook_lifecycle_sensitive"] is False


def test_pure_gethookflags_skipped():
    c = f3.classify("getHookFlags", "function getHookFlags() public pure", visibility="public",
                    mutability="pure", contract="UpliftOnlyExample", snippet="HookFlags memory f; return f;")
    assert c["hook_lifecycle_sensitive"] is False


def test_admin_config_hook_skipped():
    c = f3.classify("setHookSwapFeePercentage",
                    "function setHookSwapFeePercentage(uint x) external onlyOwner",
                    visibility="external", mutability="", contract="UpliftOnlyExample",
                    snippet="hookSwapFeePercentage = x;")
    assert c["hook_lifecycle_sensitive"] is False


def test_generic_callback_noise_skipped():
    c = f3.classify("onERC721Received", "function onERC721Received(...) public", visibility="public",
                    mutability="", contract="UpliftOnlyExample", snippet="return this.onERC721Received.selector;")
    assert c["hook_lifecycle_sensitive"] is False


def test_non_hook_not_surfaced():
    c = f3.classify("transfer", "function transfer(address to,uint a) external", visibility="external",
                    mutability="", contract="UsdToken", snippet="balances[to]+=a;")
    assert c["hook_lifecycle_sensitive"] is False  # not a hook-lifecycle surface


def test_hook_without_state_skipped():
    # onRegister-shape: validates + emits, no accounting mutation → not sensitive (the M-11 honest miss)
    c = f3.classify("onRegister", "function onRegister(...) public onlyVault", visibility="public",
                    mutability="", contract="UpliftOnlyExample",
                    snippet="if(!liquidityManagement.enableDonation) revert X(); emit Registered(); return true;")
    assert c["hook_lifecycle_sensitive"] is False
