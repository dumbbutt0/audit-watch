#!/usr/bin/env python3
"""Write Step-0 deep-analysis artifacts for the Zaros Part 2 blind eval (in-session, API-free).

Grounded in source actually read this session: VaultRouterBranch.sol (full), Vault.sol (full),
CreditDelegationBranch.sol (guards + depositCreditForMarket), StabilityBranch.sol (swap sigs),
BaseAdapter.sol (slippage/deadline), ZlpVault.sol (ERC4626/UUPS), README scope+known-issues.
Honest zero-trust: threads I could not fully trace are NEEDS_MORE_CONTEXT, not fabricated.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from audit_context import audit_path  # noqa

SRC = "audits/zaros-2025-01-part-2-eval/contracts/2025-01-zaros-part-2/src"

# ── 0a. Invariants ─────────────────────────────────────────────────────────────
INV = [
    {"invariant_id":"ACC-001","category":"ACCOUNTING",
     "statement":"A vault's net credit capacity (totalAssets - totalDebt) must be representable; redeem/deposit swap-rate must use a non-negative net asset figure.",
     "formal_expression":"getVaultCreditCapacity(v) consistent with sign(totalAssets - debtInAssets)",
     "state_variables_involved":["Vault.marketsRealizedDebtUsd","Vault.marketsUnrealizedDebtUsd","Vault.depositedUsdc","indexToken.totalAssets"],
     "mutating_functions":["VaultRouterBranch.deposit","VaultRouterBranch.redeem","Vault.recalculateVaultsCreditCapacity"],
     "violation_consequence":"If net is negative, SD59x18->uint256 conversion reverts/wraps → deposit/redeem DoS or mispriced shares.",
     "suspicion_score":5},
    {"invariant_id":"SOL-001","category":"SOLVENCY",
     "statement":"A redeem must not reduce the vault's credit capacity below its locked (markets-backing) capacity.",
     "formal_expression":"creditCapacityAfter >= lockedCreditCapacityBefore  (i.e. revert iff capacityBefore-capacityAfter > unlocked)",
     "state_variables_involved":["Vault credit capacity","Vault.lockedCreditRatio"],
     "mutating_functions":["VaultRouterBranch.redeem"],
     "violation_consequence":"LPs withdraw collateral that backs connected markets → market under-collateralization / bad debt.",
     "suspicion_score":5},
    {"invariant_id":"STATE-001","category":"STATE_MACHINE",
     "statement":"A withdrawal request can be redeemed at most once and only after withdrawalDelay.",
     "formal_expression":"redeem requires !req.fulfilled && now >= req.timestamp+delay; sets req.fulfilled=true",
     "state_variables_involved":["WithdrawalRequest.fulfilled","WithdrawalRequest.timestamp","Vault.withdrawalDelay"],
     "mutating_functions":["VaultRouterBranch.initiateWithdrawal","VaultRouterBranch.redeem"],
     "violation_consequence":"Double redemption or premature withdrawal drains vault.",
     "suspicion_score":3},
    {"invariant_id":"ARI-001","category":"ARITHMETIC",
     "statement":"DEX swaps executed by the protocol must enforce a minimum output derived from a trusted price, not a manipulable spot, and a fresh deadline.",
     "formal_expression":"amountOutMin = oraclePrice*amountIn*(1-slippageBps); deadline > block.timestamp",
     "state_variables_involved":["BaseAdapter.slippageToleranceBps","BaseAdapter.deadline"],
     "mutating_functions":["UniswapV3Adapter.swapExactInput","CurveAdapter.swapExactInput","StabilityBranch.settleSwap","CreditDelegationBranch.convertMarketsCreditDepositsToUsdc"],
     "violation_consequence":"MEV sandwich of protocol swaps; value leaks from vault/market funds.",
     "suspicion_score":4},
    {"invariant_id":"ACC-002","category":"ACCOUNTING",
     "statement":"ZLP (ERC4626) shares:assets conversion must resist first-depositor / donation inflation.",
     "formal_expression":"previewDeposit/Redeem monotonic; virtual offset prevents single-wei share price inflation",
     "state_variables_involved":["ZlpVault._decimalsOffset","ZlpVault.totalSupply","ZlpVault.totalAssets"],
     "mutating_functions":["ZlpVault.deposit","ZlpVault.redeem","VaultRouterBranch.deposit","VaultRouterBranch.redeem"],
     "violation_consequence":"Inflation attack steals deposits / rounds LP shares to zero.",
     "suspicion_score":4},
    {"invariant_id":"ACC-003","category":"ACCOUNTING",
     "statement":"Staking reward (WETH) distribution: a staker's claimable value must be preserved across stake/unstake; shares accounting must equal total staked.",
     "formal_expression":"sum(actor.shares) == distribution.totalShares; getActorValueChange consistent",
     "state_variables_involved":["Distribution.totalShares","Distribution.valuePerShare","Distribution.Actor.shares"],
     "mutating_functions":["VaultRouterBranch.stake","VaultRouterBranch.unstake","Vault.recalculateVaultsCreditCapacity"],
     "violation_consequence":"Reward theft or loss; unstake blocked by pending-reward check griefing.",
     "suspicion_score":3},
    {"invariant_id":"ACCESS-001","category":"ACCESS",
     "statement":"Engine-only / keeper-only entrypoints must reject arbitrary callers.",
     "formal_expression":"depositCreditForMarket: onlyRegisteredEngine; rebalanceVaultsAssets: onlyRegisteredSystemKeepers; ZlpVault upgrade: onlyOwner",
     "state_variables_involved":["registered engines","system keepers","ZlpVault owner"],
     "mutating_functions":["CreditDelegationBranch.depositCreditForMarket","CreditDelegationBranch.rebalanceVaultsAssets","ZlpVault._authorizeUpgrade"],
     "violation_consequence":"Unauthorized credit injection / asset rebalance / proxy takeover.",
     "suspicion_score":3},
    {"invariant_id":"XC-001","category":"CROSS_CONTRACT",
     "statement":"Market debt distributed to vaults must net to zero across the system (sum of per-vault realized/unrealized debt equals market totals).",
     "formal_expression":"sum_v distributedDebt(market,v) == market.realizedDebt+unrealizedDebt",
     "state_variables_involved":["Market.*PerVaultShare","CreditDelegation.lastVaultDistributed*"],
     "mutating_functions":["Vault._recalculateConnectedMarketsState","Market.distributeDebtToVaults"],
     "violation_consequence":"Debt mis-distribution → some vaults over/under charged → solvency drift.",
     "suspicion_score":4},
    {"invariant_id":"STATE-002","category":"STATE_MACHINE",
     "statement":"USD-token swap is a two-step commit/settle; settle must use the committed terms and refund correctly on failure/expiry.",
     "formal_expression":"settleSwap(reqId) consumes the request once; price/amount bounded by commit",
     "state_variables_involved":["UsdTokenSwapConfig swap requests"],
     "mutating_functions":["StabilityBranch.initiateSwap","StabilityBranch.settleSwap"],
     "violation_consequence":"Stale-price settlement or double-settle drains stability reserves.",
     "suspicion_score":4},
    {"invariant_id":"ARI-002","category":"ARITHMETIC",
     "statement":"Decimal conversions (collateral decimals ↔ SYSTEM_DECIMALS=18) must not underflow when collateral decimals > 18 or != expected.",
     "formal_expression":"decimalOffset = SYSTEM_DECIMALS - collateral.decimals >= 0",
     "state_variables_involved":["Collateral.decimals","Constants.SYSTEM_DECIMALS"],
     "mutating_functions":["VaultRouterBranch.getVaultCreditCapacity","Math.convert*"],
     "violation_consequence":"Underflow reverts on high-decimal collateral → DoS for that vault.",
     "suspicion_score":3},
]
audit_path("data/invariants/protocol_invariants.json").write_text(json.dumps(INV, indent=2))
audit_path("data/invariants/high_suspicion.json").write_text(json.dumps([i for i in INV if i["suspicion_score"]>=4], indent=2))
audit_path("data/invariants/medium_suspicion.json").write_text(json.dumps([i for i in INV if i["suspicion_score"]==3], indent=2))

# ── 0b. Interactions ───────────────────────────────────────────────────────────
CALL_GRAPH = {
 "call_graph":[
   {"caller_contract":"VaultRouterBranch","caller_function":"deposit","callee_contract":"ZlpVault(IERC4626)","callee_function":"deposit","call_type":"direct","state_read_before_call":["vault.depositFee","vault.collateral"],"state_written_after_call":["ZlpVault shares"],"trust_level":"trusted_external"},
   {"caller_contract":"VaultRouterBranch","caller_function":"deposit","callee_contract":"ERC20(collateral)","callee_function":"safeTransferFrom","call_type":"direct","state_read_before_call":["ctx.assetsMinusFees"],"state_written_after_call":[],"trust_level":"untrusted"},
   {"caller_contract":"VaultRouterBranch","caller_function":"redeem","callee_contract":"ZlpVault(IERC4626)","callee_function":"redeem","call_type":"direct","state_read_before_call":["withdrawalRequest.shares","vault credit capacity"],"state_written_after_call":["withdrawalRequest.fulfilled"],"trust_level":"trusted_external"},
   {"caller_contract":"VaultRouterBranch","caller_function":"deposit","callee_contract":"IReferral","callee_function":"registerReferral","call_type":"direct","state_read_before_call":["marketMakingEngineConfiguration.referralModule"],"state_written_after_call":[],"trust_level":"trusted_external"},
   {"caller_contract":"CreditDelegationBranch","caller_function":"depositCreditForMarket","callee_contract":"ERC20(collateral)","callee_function":"safeTransferFrom","call_type":"direct","state_read_before_call":["market delegated credit"],"state_written_after_call":["market.depositCredit"],"trust_level":"untrusted"},
   {"caller_contract":"CreditDelegationBranch","caller_function":"convertMarketsCreditDepositsToUsdc","callee_contract":"IDexAdapter","callee_function":"swapExactInput","call_type":"direct","state_read_before_call":["market credit deposits"],"state_written_after_call":["usdc balances"],"trust_level":"trusted_external"},
   {"caller_contract":"StabilityBranch","caller_function":"settleSwap","callee_contract":"IDexAdapter","callee_function":"swapExactInput","call_type":"direct","state_read_before_call":["swap request","price"],"state_written_after_call":["reserves"],"trust_level":"trusted_external"},
   {"caller_contract":"DexAdapter","caller_function":"swapExactInput","callee_contract":"UniswapV3/Curve Router","callee_function":"exactInput","call_type":"direct","state_read_before_call":["slippageToleranceBps","deadline","priceAdapter"],"state_written_after_call":[],"trust_level":"untrusted"},
   {"caller_contract":"Vault","caller_function":"recalculateVaultsCreditCapacity","callee_contract":"Market","callee_function":"distributeDebtToVaults","call_type":"direct","state_read_before_call":["market debt"],"state_written_after_call":["vault realized/unrealized debt"],"trust_level":"trusted_internal"},
 ],
 "interaction_chains":[
   {"chain_id":"CH-01","path":["VaultRouterBranch.redeem","Vault.recalculateVaultsCreditCapacity","VaultRouterBranch.getIndexTokenSwapRate","ZlpVault.redeem"],"shared_state":["vault credit capacity","withdrawalRequest"],"invariant_exposure":["SOL-001","ACC-001","STATE-001"],"reentrancy_surface":False,"stale_read_risk":True,"depth":4,"danger_score":5},
   {"chain_id":"CH-02","path":["VaultRouterBranch.deposit","Vault.recalculateVaultsCreditCapacity","VaultRouterBranch.getVaultAssetSwapRate","ZlpVault.deposit"],"shared_state":["vault credit capacity","ZlpVault totalSupply"],"invariant_exposure":["ACC-001","ACC-002","ARI-002"],"reentrancy_surface":False,"stale_read_risk":True,"depth":4,"danger_score":4},
   {"chain_id":"CH-03","path":["StabilityBranch.initiateSwap","StabilityBranch.settleSwap","DexAdapter.swapExactInput","UniswapV3.exactInput"],"shared_state":["swap request","slippageToleranceBps","deadline"],"invariant_exposure":["STATE-002","ARI-001"],"reentrancy_surface":False,"stale_read_risk":True,"depth":4,"danger_score":4},
   {"chain_id":"CH-04","path":["CreditDelegationBranch.convertMarketsCreditDepositsToUsdc","DexAdapter.swapExactInput","UniswapV3.exactInput"],"shared_state":["slippageToleranceBps","deadline"],"invariant_exposure":["ARI-001"],"reentrancy_surface":False,"stale_read_risk":False,"depth":3,"danger_score":4},
   {"chain_id":"CH-05","path":["Vault.recalculateVaultsCreditCapacity","Vault._recalculateConnectedMarketsState","Market.distributeDebtToVaults"],"shared_state":["per-vault debt shares"],"invariant_exposure":["XC-001"],"reentrancy_surface":False,"stale_read_risk":True,"depth":3,"danger_score":4},
 ],
 "trust_boundary_crossings":[
   {"location":"VaultRouterBranch.deposit (IReferral.registerReferral, ERC20.safeTransferFrom)","caller_state_at_crossing":"vault credit capacity just recalculated; no shares minted yet","what_untrusted_could_do":"malicious collateral token (FoT/reentrant) or referral module re-enters","invariants_temporarily_false":["ACC-002"]},
   {"location":"DexAdapter.swapExactInput → external router","caller_state_at_crossing":"protocol funds approved to router; amountOutMin from global slippage","what_untrusted_could_do":"sandwich within slippage tolerance","invariants_temporarily_false":["ARI-001"]},
 ],
}
audit_path("data/interactions/call_graph.json").write_text(json.dumps(CALL_GRAPH, indent=2))
audit_path("data/interactions/dangerous_chains.json").write_text(json.dumps([c for c in CALL_GRAPH["interaction_chains"] if c["danger_score"]>=4], indent=2))

# ── 0c/0d. Threads ─────────────────────────────────────────────────────────────
PROMISING = [
 {"thread_id":"T-001","invariant_id":"SOL-001","chain_id":"CH-01","verdict":"HIGH_THREAD",
  "entry_conditions":"Permissionless LP with a pending withdrawal request past delay calls redeem on a vault that backs markets (has locked credit).",
  "violation_path":[
    "redeem() recalculates capacity, computes assets",
    "unlocked-credit guard at L556-563: `if (capacityBefore.sub(capacityAfter).lte(lockedBefore)) revert NotEnoughUnlockedCreditCapacity()`",
    "delta = capacityBefore - capacityAfter is the reduction caused by THIS redeem; check reverts when delta <= locked and PASSES when delta > locked",
    "=> large redeems that consume MORE than locked capacity pass; small/normal redeems revert"],
  "attacker_class":"unprivileged",
  "impact_estimate":"Inverted guard: LPs can withdraw collateral that should stay locked to back connected markets (market under-collateralization), while legitimate small redeems are DoS'd. Vault/market solvency invariant broken.",
  "evidence":"VaultRouterBranch.redeem L556-563 (read this session). Compare intended semantics in @dev: 'if the credit capacity delta is greater than the locked credit capacity ... revert' — code uses .lte not .gt, and compares delta to locked instead of after<locked."},
 {"thread_id":"T-002","invariant_id":"ACC-001","chain_id":"CH-01","verdict":"MEDIUM_THREAD",
  "entry_conditions":"Vault is in net debt (totalDebt > totalAssets) so net credit capacity is negative.",
  "violation_path":[
    "getVaultCreditCapacity computes totalAssetsMinusVaultDebtX18 (SD59x18, can be negative)",
    "vault.collateral.convertSd59x18ToTokenAmount(negative) — convert to uint256",
    "if conversion of negative reverts/underflows, deposit/redeem/swap-rate revert"],
  "attacker_class":"unprivileged (state arises from normal market losses)",
  "impact_estimate":"Deposit/redeem/stake/unstake DoS for any vault in net debt; users cannot exit precisely when they most need to.",
  "evidence":"VaultRouterBranch.getVaultCreditCapacity L70-101 (read). Net add(1 unit) then sub(debt) can be negative; downstream conversion sign-unsafe."},
 {"thread_id":"T-003","invariant_id":"ARI-001","chain_id":"CH-03","verdict":"MEDIUM_THREAD",
  "entry_conditions":"Protocol DEX swap (settleSwap / convertMarketsCreditDepositsToUsdc) executes through an adapter with a single owner-set global slippageToleranceBps and a shared `deadline` storage var.",
  "violation_path":[
    "DexAdapter.swapExactInput builds amountOutMinimum from priceAdapter*amountIn*(1-slippageBps)",
    "shared `deadline` storage (not per-tx) may be stale/large → no effective deadline",
    "searcher sandwiches the swap within slippage tolerance"],
  "attacker_class":"unprivileged MEV (Arbitrum sequencer window; Monad)",
  "impact_estimate":"Value leak from protocol/vault funds on every routed swap up to slippage tolerance; magnified by stale deadline.",
  "evidence":"BaseAdapter: slippageToleranceBps + deadline are storage vars set by owner (read L20-29). swapExactInput uses them."},
 {"thread_id":"T-004","invariant_id":"ACC-002","chain_id":"CH-02","verdict":"NEEDS_MORE_CONTEXT",
  "entry_conditions":"First deposit into a fresh ZlpVault (ERC4626Upgradeable) with attacker as first depositor + direct asset donation.",
  "violation_path":[
    "ZlpVault uses _decimalsOffset = sharesDecimals - assetDecimals",
    "VaultRouterBranch.deposit enforces shares>0 (mitigates zero-share), but rounding/donation inflation across the virtual-offset still to be confirmed",
    "need to read ZlpVault deposit/_convertToShares + previewDeposit override"],
  "attacker_class":"unprivileged",
  "impact_estimate":"Possible first-depositor inflation / rounding theft (overlaps README known-issue about EIP4626 preview+fees).",
  "evidence":"ZlpVault L19-60 (ERC4626Upgradeable, decimalsOffset). Full deposit/convertToShares not read — honest NEEDS_MORE_CONTEXT."},
 {"thread_id":"MT-005","invariant_id":"STATE-002","chain_id":"CH-03","verdict":"NEEDS_MORE_CONTEXT",
  "entry_conditions":"User initiates a USD-token swap (commit) then it is settled in a later tx by a keeper.",
  "violation_path":[
    "initiateSwap records request; settleSwap consumes it after delay",
    "price used at settle vs commit, refund-on-expiry, and double-settle protection need full settleSwap body"],
  "attacker_class":"unprivileged / keeper",
  "impact_estimate":"If settle uses live price or request can be replayed, stability reserves can be drained or users front-run.",
  "evidence":"StabilityBranch.initiateSwap/settleSwap signatures (read); bodies truncated — NEEDS_MORE_CONTEXT for /ite-audit economic+logic specialists."},
]
DEAD_ENDS = [
 {"thread_id":"D-001","invariant_id":"ACCESS-001","chain_id":"CH-04","verdict":"DEAD_END",
  "entry_conditions":"Arbitrary caller attempts depositCreditForMarket / rebalanceVaultsAssets.",
  "violation_path":["depositCreditForMarket has onlyRegisteredEngine(marketId)","rebalanceVaultsAssets has onlyRegisteredSystemKeepers"],
  "attacker_class":"unprivileged","impact_estimate":"None — guarded.",
  "evidence":"CreditDelegationBranch L113-148 onlyRegisteredEngine; L207 onlyRegisteredSystemKeepers (read). Access enforced; not a finding by itself."},
]
audit_path("data/threads/promising_threads.jsonl").write_text("\n".join(json.dumps(t) for t in PROMISING)+"\n")
audit_path("data/threads/dead_ends.jsonl").write_text("\n".join(json.dumps(t) for t in DEAD_ENDS)+"\n")

# ── 0d. findings_deep_trace.json ───────────────────────────────────────────────
def ice(corrupt, consumers, highest, level, proven, esc, ceiling, conf="medium"):
    return {"corrupted_state":corrupt,"consumers_found":consumers,"consumer_search_confidence":conf,
            "highest_consumer_reached":highest,"poc_level_achieved":level,"directly_proven_impact":proven,
            "plausible_escalation":esc,"severity_ceiling":ceiling,"recommended_next_poc_step":"Foundry test asserting the storage/balance flip",
            "hold":False,"needs_manual_review":False,"triager_objections":[],"defenses_checked":[]}

FINDINGS = [
 {"id":"DT-001","title":"VaultRouterBranch.redeem: inverted unlocked-credit-capacity check lets LPs withdraw locked credit (and DoSes normal redeems)",
  "severity":"High","confidence":"High","vuln_type":"logic_error",
  "description":"The guard at redeem L556-563 reverts when (capacityBefore - capacityAfter) <= lockedCapacityBefore. The NatSpec intends to revert when the redeem consumes more than the *unlocked* capacity, i.e. when capacityAfter < locked. As written it reverts on small redeems (delta <= locked) and ALLOWS large redeems (delta > locked) — the opposite of the intended protection. LPs can pull collateral that must stay locked to back connected markets.",
  "location":{"file":f"{SRC}/market-making/branches/VaultRouterBranch.sol","function":"redeem","lines":"556-563"},
  "impact":"Vault credit that backs markets can be withdrawn → market under-collateralization / bad debt; legitimate small withdrawals are bricked.",
  "ite":{"intent":"protect locked credit backing markets","technique":"redeem with delta>locked passes the inverted check","evasion":"none needed"},
  "ice_chain":"redeem → inverted guard → ZlpVault.redeem releases collateral → market loses backing",
  "ice":ice("withdrawalRequest fulfilled + vault credit capacity reduced below locked",
            [{"file":"VaultRouterBranch.sol","function":"redeem","action_type":"withdraw"}],
            "VaultRouterBranch.redeem (withdraw)",3,
            "Guard math is inverted vs documented intent","LP drains locked credit → market bad debt","High","high")},
 {"id":"DT-002","title":"VaultRouterBranch.getVaultCreditCapacity: sign-unsafe SD59x18→uint256 conversion DoSes vaults in net debt",
  "severity":"Medium","confidence":"Medium","vuln_type":"arithmetic",
  "description":"getVaultCreditCapacity computes totalAssetsMinusVaultDebtX18 which is negative when a vault's debt exceeds its assets, then converts it to uint256 token amount. A negative→unsigned conversion reverts/wraps, blocking deposit/redeem/stake/unstake (all call recalculate + swap-rate) precisely when the vault is underwater.",
  "location":{"file":f"{SRC}/market-making/branches/VaultRouterBranch.sol","function":"getVaultCreditCapacity","lines":"70-101"},
  "impact":"Denial of service of all vault user operations for an underwater vault.",
  "ite":{"intent":"compute net credit capacity","technique":"drive vault to net debt via market losses","evasion":"none"},
  "ice_chain":"market losses → vault net debt → negative net → conversion revert → vault ops DoS",
  "ice":ice("getVaultCreditCapacity return path",[{"file":"VaultRouterBranch.sol","function":"deposit/redeem","action_type":"state_read"}],
            "deposit/redeem (DoS)",2,"Negative net feeds unsigned conversion","Full vault DoS while underwater","Medium")},
 {"id":"DT-003","title":"DEX adapter swaps use a single owner-set global slippage tolerance and shared deadline → MEV/sandwich of protocol swaps",
  "severity":"Medium","confidence":"Medium","vuln_type":"economic_attack",
  "description":"BaseAdapter stores slippageToleranceBps and a single `deadline` as owner-set storage. Protocol-initiated swaps (StabilityBranch.settleSwap, CreditDelegationBranch.convertMarketsCreditDepositsToUsdc) route through the adapter using these globals to derive amountOutMinimum and the deadline. A wide tolerance and/or stale shared deadline allow sandwich extraction on every routed swap.",
  "location":{"file":f"{SRC}/utils/dex-adapters/BaseAdapter.sol","function":"calculateAmountOutMin/swapExactInput","lines":"20-29"},
  "impact":"Value leak from vault/market funds up to slippage tolerance on each routed swap.",
  "ite":{"intent":"bounded-slippage protocol swaps","technique":"sandwich within tolerance; exploit stale deadline","evasion":"stay within bps"},
  "ice_chain":"protocol swap → adapter amountOutMin from global bps → searcher sandwich → value to attacker",
  "ice":ice("swap output (amountOut) below fair value",[{"file":"BaseAdapter.sol","function":"swapExactInput","action_type":"transfer"}],
            "DEX swap (transfer)",2,"Global slippage + shared deadline","MEV extraction per swap","Medium")},
]
audit_path("output/findings_deep_trace.json").write_text(json.dumps(
  {"agent":"deep_trace","contract":SRC,"findings":FINDINGS}, indent=2))

print(f"OK invariants={len(INV)} high={len([i for i in INV if i['suspicion_score']>=4])} "
      f"chains={len(CALL_GRAPH['interaction_chains'])} promising={len(PROMISING)} dead={len(DEAD_ENDS)} "
      f"deep_findings={len(FINDINGS)}")
