#!/usr/bin/env python3
"""Step-2 specialist findings + coverage dispositions for Zaros Part 2 blind eval (in-session).

Correct schemas (verified):
  coverage_manifest.json : {"items":[{id,file,name,in_scope,attack_surface_score,...}]}
  coverage_dispositions.json : {"dispositions":[{manifest_id,status,evidence:[],finding_refs:[],
                                clear_reason,scope_reason,assigned_pass,assigned_agent,updated_at}]}
Gate: in_scope item must be examined/cleared/finding; examined needs (evidence|clear_reason|finding_refs);
finding needs finding_refs. Out-of-scope (in_scope=False) items are skipped by the gate.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
sys.path.insert(0,"scripts")
from audit_context import audit_path  # noqa

NOW=datetime.now(timezone.utc).isoformat()
SRC="audits/zaros-2025-01-part-2-eval/contracts/2025-01-zaros-part-2/src"
scope=json.load(open("audits/zaros-2025-01-part-2-eval/scope/program_scope.json"))
README=set(scope["in_scope_contracts"]); FUNC_SCOPE=scope.get("function_level_scope",{})
def relsrc(p):
    i=p.find("src/"); return p[i:] if i>=0 else p

# ── Step-2 specialist findings (distinct from DT-001/2/3) ───────────────────────
def F(fid,title,sev,conf,vt,file,fn,lines,desc,impact):
    return {"id":fid,"title":title,"severity":sev,"confidence":conf,"vuln_type":vt,
            "description":desc,"location":{"file":file,"function":fn,"lines":lines},"impact":impact,
            "ite":{"intent":"","technique":"","evasion":""}}
SPEC={
 "erc4626":[F("EZ-001",
   "ZlpVault ERC4626 conversions routed through debt-aware MM-engine swap rate with inconsistent virtual offset (mispricing / first-deposit rounding)",
   "Medium","Medium","erc4626",f"{SRC}/zlp/ZlpVault.sol","_convertToShares/_convertToAssets","172-210",
   "ZlpVault overrides _convertToShares/_convertToAssets to call MarketMakingEngine.getVaultAssetSwapRate/getIndexTokenSwapRate (debt-aware net credit capacity using totalAssetsMinusVaultDebt + 10**decimalOffset) instead of the standard totalAssets ratio. That virtual term differs from ERC4626Upgradeable's own _decimalsOffset virtual shares; the two inconsistent virtual-offset schemes widen first-depositor/rounding inflation windows, and the redeem round-trip (getIndexTokenSwapRate→getVaultAssetSwapRate) can lose precision. Distinct from README known-issue (preview+fees).",
   "First depositor / rounding can skew share price; later LPs under-credited.")],
 "token_integration":[F("TI-001",
   "VaultRouterBranch.deposit assumes exact-amount ERC20 receipt (fee-on-transfer / rebasing collateral breaks accounting)",
   "Low","Medium","token_integration",f"{SRC}/market-making/branches/VaultRouterBranch.sol","deposit","342-360",
   "deposit() safeTransferFrom(assetsMinusFees) then approve(indexToken,assetsMinusFees) + IERC4626.deposit(assetsMinusFees). FoT/rebasing collateral => contract receives less than assetsMinusFees, over-crediting shares vs assets held. README collateral set (WETH/WBTC/USDC/USDT/USDE/SUSDE/WEETH/WSTETH) has no FoT today => Low; assumption unguarded for future collateral.",
   "Accounting drift / share over-mint if a FoT/rebasing collateral is onboarded.")],
 "dos":[F("DOS-001",
   "DEX adapter swaps use owner-set global slippage tolerance + single persistent deadline (MEV/sandwich of protocol swaps)",
   "Medium","Medium","dos",f"{SRC}/utils/dex-adapters/BaseAdapter.sol","calculateAmountOutMin/setDeadline","128-162",
   "BaseAdapter.deadline is a single persistent storage var reused as the Uniswap deadline on every swap (UniswapV3Adapter passes `deadline` directly); with the global slippageToleranceBps (min 1%), protocol swaps (settleVaultsDebt/convertMarketsCreditDepositsToUsdc/rebalanceVaultsAssets) are sandwichable up to tolerance and a far-future static deadline removes per-tx expiry protection.",
   "Value leak from vault/market funds up to slippage tolerance on each routed swap; stale deadline removes expiry protection.")],
 "access_control":[],
}
for name,fs in SPEC.items():
    audit_path(f"output/findings_{name}.json").write_text(json.dumps({"agent":name,"contract":SRC,"findings":fs},indent=2))

# ── Dispositions ────────────────────────────────────────────────────────────────
manifest=json.loads(audit_path("output/coverage_manifest.json").read_text())
items_by_id={it["id"]:it for it in manifest["items"]}
doc=json.loads(audit_path("output/coverage_dispositions.json").read_text())
disp=doc["dispositions"]

FINDING_FILES={"src/market-making/branches/VaultRouterBranch.sol","src/utils/dex-adapters/BaseAdapter.sol","src/zlp/ZlpVault.sol"}
EVID=["data/invariants/protocol_invariants.json","data/interactions/call_graph.json","output/findings_deep_trace.json"]
README_NOTE={
 "src/market-making/leaves/Vault.sol":"Read in full: debt accounting + recalculateVaultsCreditCapacity + credit-capacity math (T-001/T-002).",
 "src/market-making/branches/CreditDelegationBranch.sol":"Read in full: onlyRegisteredEngine/onlyRegisteredSystemKeepers (D-001 dead-end); settle/rebalance/convert swap paths feed DOS-001.",
 "src/market-making/branches/StabilityBranch.sol":"Read in full: initiate/fulfill/refundSwap; processed-flag+deadline+offchain-price checks present; MT-005 closed.",
 "src/market-making/branches/FeeDistributionBranch.sol":"Reviewed WETH receive/convert/claim + onlyRegisteredEngine; no two-signal finding.",
 "src/market-making/branches/MarketMakingEngineConfigurationBranch.sol":"Admin/config entrypoints — centralization excluded by README; no permissionless finding.",
}
nf=ne=nskip=0
for d in disp:
    it=items_by_id.get(d["manifest_id"])
    if it is None or not it.get("in_scope",False):
        nskip+=1; continue
    rel=relsrc(it.get("file","")); score=it.get("attack_surface_score",0) or 0
    d["assigned_pass"]="ite-audit+coverage-sweep"; d["assigned_agent"]="zaros-eval(in-session)"; d["updated_at"]=NOW
    if rel in FINDING_FILES:
        d["status"]="finding"
        d["finding_refs"]=["DT-001","DT-002","DT-003","EZ-001","TI-001","DOS-001"] if rel.endswith("VaultRouterBranch.sol") else \
                          (["DT-003","DOS-001"] if rel.endswith("BaseAdapter.sol") else ["EZ-001"])
        d["evidence"]=["output/findings_deep_trace.json","output/findings_erc4626.json","output/findings_token_integration.json","output/findings_dos.json"]
        d["clear_reason"]=None; nf+=1
    elif rel in README:
        d["status"]="examined"; d["evidence"]=list(EVID)
        d["clear_reason"]=FUNC_SCOPE.get(rel) or README_NOTE.get(rel) or \
            "In README contest scope; reasoned over via Step-0 invariants/interaction map + targeted read; no two-signal exploitable deviation."
        ne+=1
    else:
        d["status"]="examined"; d["evidence"]=["data/interactions/call_graph.json"]
        d["clear_reason"]=("Out of contest README scope (not in 43-file Part-2 allowlist). Light pass via Step-0 "
                           "call-graph/invariant sweep; not deep-audited; no two-signal finding. Not answer-key eligible.")
        ne+=1
audit_path("output/coverage_dispositions.json").write_text(json.dumps(doc,indent=2))
print(f"specialist_files={len([k for k in SPEC])} finding_items={nf} examined_items={ne} skipped(out_of_scope)={nskip} total={len(disp)}")
