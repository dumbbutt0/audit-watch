#!/usr/bin/env python3
"""In-session eval-ready root-cause dedup for Zaros Part 2 (API-free; NOT the Beanstalk-hardcoded
build_eval_inventory.py). 6 merged candidates → 5 root causes (DOS-001 merged into DT-003).
Schema mirrors audits/beanstalk-2024-05-eval2/output/eval_ready/*."""
import json, sys
from datetime import datetime, timezone
sys.path.insert(0,"scripts")
from audit_context import audit_path
NOW=datetime.now(timezone.utc).isoformat()
SCOPE="Zaros Part 2 (2025-01-zaros-part-2) — README 43-file market-making scope; merged candidate layer"

ROOTS=[
 {"eval_id":"EVAL-001","root_cause_id":"vaultrouter-redeem-inverted-locked-credit-check","merged":["DT-001"],
  "title":"VaultRouterBranch.redeem inverted unlocked-credit-capacity check allows withdrawing locked (market-backing) credit",
  "classification":"confirmed_eval_finding","severity_ceiling":"High","confidence":"High",
  "affected_contracts":["src/market-making/branches/VaultRouterBranch.sol"],
  "match_terms":["redeem","NotEnoughUnlockedCreditCapacity","locked credit capacity","lockedCreditRatio","unlocked credit"]},
 {"eval_id":"EVAL-002","root_cause_id":"vaultcreditcapacity-negative-signed-to-unsigned-dos","merged":["DT-002"],
  "title":"getVaultCreditCapacity sign-unsafe SD59x18->uint256 conversion DoSes underwater vaults",
  "classification":"confirmed_eval_finding","severity_ceiling":"Medium","confidence":"Medium",
  "affected_contracts":["src/market-making/branches/VaultRouterBranch.sol"],
  "match_terms":["getVaultCreditCapacity","totalAssetsMinusVaultDebt","convertSd59x18ToTokenAmount","negative net","underwater vault DoS"]},
 {"eval_id":"EVAL-003","root_cause_id":"dexadapter-global-slippage-and-persistent-deadline-mev","merged":["DT-003","DOS-001"],
  "title":"DEX adapter global slippage tolerance + single persistent deadline -> MEV/sandwich of protocol swaps",
  "classification":"confirmed_eval_finding","severity_ceiling":"Medium","confidence":"Medium",
  "affected_contracts":["src/utils/dex-adapters/BaseAdapter.sol","src/utils/dex-adapters/UniswapV3Adapter.sol","src/utils/dex-adapters/CurveAdapter.sol","src/utils/dex-adapters/UniswapV2Adapter.sol"],
  "match_terms":["slippageToleranceBps","deadline","calculateAmountOutMin","amountOutMinimum","sandwich","MEV","setDeadline"]},
 {"eval_id":"EVAL-004","root_cause_id":"zlpvault-erc4626-inconsistent-virtual-offset-mispricing","merged":["EZ-001"],
  "title":"ZlpVault ERC4626 conversions via debt-aware MM-engine swap rate with inconsistent virtual offset (mispricing / first-deposit rounding)",
  "classification":"partial_eval_finding","severity_ceiling":"Medium","confidence":"Medium",
  "affected_contracts":["src/zlp/ZlpVault.sol","src/market-making/branches/VaultRouterBranch.sol"],
  "match_terms":["_convertToShares","_convertToAssets","_decimalsOffset","getVaultAssetSwapRate","getIndexTokenSwapRate","inflation","previewDeposit"]},
 {"eval_id":"EVAL-005","root_cause_id":"vaultrouter-deposit-exact-amount-erc20-assumption","merged":["TI-001"],
  "title":"VaultRouterBranch.deposit assumes exact-amount ERC20 receipt (FoT/rebasing collateral accounting drift)",
  "classification":"confirmed_eval_finding","severity_ceiling":"Low","confidence":"Medium",
  "affected_contracts":["src/market-making/branches/VaultRouterBranch.sol"],
  "match_terms":["deposit","safeTransferFrom","fee on transfer","rebasing","balance delta"]},
]
eval_findings=[{"eval_id":r["eval_id"],"root_cause_id":r["root_cause_id"],"title":r["title"],
    "classification":r["classification"],"severity_ceiling":r["severity_ceiling"],"confidence":r["confidence"],
    "affected_contracts":r["affected_contracts"],"duplicate_of":None,"source_leads":r["merged"],
    "match_terms":r["match_terms"]} for r in ROOTS]
audit_path("output/eval_ready/eval_findings.json").write_text(json.dumps(
    {"generated_at":NOW,"scope":SCOPE,"eval_findings":eval_findings}, indent=2))

RAW={"DT-001":"EVAL-001","DT-002":"EVAL-002","DT-003":"EVAL-003","EZ-001":"EVAL-004","TI-001":"EVAL-005","DOS-001":"EVAL-003"}
RC={e["eval_id"]:e["root_cause_id"] for e in eval_findings}
merged=json.loads(audit_path("output/merged_findings.json").read_text())["findings"]
mby={f["id"]:f for f in merged}
candidates=[{"raw_id":rid,"source":"merged_findings","root_cause_id":RC[ev],"eval_id":ev,
    "title":mby.get(rid,{}).get("title",""),"severity":mby.get(rid,{}).get("severity",""),
    "classification":"duplicate_of_pipeline_finding" if rid=="DOS-001" else "primary",
    "include_in_eval_findings": rid!="DOS-001"} for rid,ev in RAW.items()]
audit_path("output/eval_ready/eval_candidate_inventory.json").write_text(json.dumps(
    {"generated_at":NOW,"scope":SCOPE,"candidates":candidates}, indent=2))
audit_path("output/eval_ready/eval_duplicate_map.json").write_text(json.dumps(
    {"generated_at":NOW,"mapping":{rid:RC[ev] for rid,ev in RAW.items()},
     "duplicate_pairs":[{"raw_id":"DOS-001","duplicate_of":"DT-003","root_cause_id":RC["EVAL-003"]}]}, indent=2))
audit_path("output/eval_ready/eval_exclusions.json").write_text(json.dumps(
    {"generated_at":NOW,"scope":SCOPE,"exclusions":[
        {"raw_id":"DOS-001","reason":"duplicate root cause of DT-003 (DEX adapter slippage/deadline MEV)","classification":"duplicate_of_existing"}]}, indent=2))
print(f"eval_findings={len(eval_findings)} candidates={len(candidates)} exclusions=1(DOS-001->DT-003)")
