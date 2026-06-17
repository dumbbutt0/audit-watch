#!/usr/bin/env python3
"""sync_realworld_candidates.py — add the TipRun/Cartha/0xMarkets hunt results to the live dashboard source
documentation/real_world_results.json (the honest hunt log that funnel.load_records() reads for /candidates,
/funnel, /findings). Additive + idempotent (re-run replaces only our entries); timestamped backup first.

HONESTY: candidate_findings[] are POC_REPRODUCED by definition, so ONLY the 8 PoC-backed findings go there
(each has a passing Foundry PoC). The 4 analysis-only findings (Cartha L-1; 0xM X-1/I-1/I-2) are recorded at
TARGET level (honest notes), never as fake REPRODUCED candidates. Touches ONLY real_world_results.json (+ bak);
never the eval corpus (frozen_corpus/funnel_records/ground_truth/scoreboards).
"""
from __future__ import annotations
import json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RW = ROOT / "documentation/real_world_results.json"
OUR_TARGET_PREFIXES = ("TipRun", "Cartha", "0xMarkets")


def V(**kw):
    """Build a full verifier block with the Monolith-template defaults; kw overrides per finding."""
    d = {
        "target": "", "surface_function": "", "suspected_mechanism": "", "mechanism_class": "",
        "impact": "", "severity_recommendation": "", "claimed_severity": "",
        "mechanism_confirmed": True, "attacker_reachable": True, "severity_bearing": True, "reportable": True,
        "human_review_required": "confirm severity + scope against the program's rules/trust model",
        "human_review_focus": "severity calibration + scope",
        "reachability_class": "UNPRIVILEGED_REACHABLE",
        "privilege_required": "none", "victim_action_required": "none",
        "self_remediation": "none", "operator_or_keeper_dependency": "none",
        "attacker_controls": [], "attacker_does_not_control": [],
        "function_map": [], "attacker_model": "", "exploit_steps": [], "defense_map": [],
        "real_contract_deployed": True, "production_source_modified": False,
        "poc_command": "", "poc_status": "REPRODUCED", "harness_path": "",
        "vulnerable_output": "", "corrected_output": "", "control_case": "", "runtime_delta": "",
        "who_loses": "", "who_gains": "", "asset_or_value": "", "loss_type": "",
        "permanence": "", "repeatability": "", "limitations": "",
    }
    d.update(kw)
    return d


def CF(target, title, severity, status, evidence, poc_path, poc_command, verifier):
    return {
        "target": target, "source": "blind", "severity": severity, "title": title,
        "status": status, "submitted": False, "human_verified": False,
        "evidence": evidence, "poc_path": poc_path,
        "writeup": f"reports/{'tiprun' if target=='TipRun' else 'cartha'}-2026-06-13/submissions/"
                   f"{verifier['target'].split('.')[0]}/report.md",
        "verifier": verifier,
    }


TH = "reports/tiprun-2026-06-13/harness/test"
CH = "reports/cartha-2026-06-13/harness/test"

CANDIDATES = [
    # ---------------- TipRun ----------------
    CF("TipRun", "Maintenance-margin bypass: withdraw 100% collateral while holding an open position",
       "Critical", "PoC reproduced", "8/8 PoC tests pass; corroborated by the repo's own test_ArithmeticEdgeCase_NegativeCollateral",
       f"{TH}/PoC_MarginBypassWithdraw.t.sol", "forge test --match-contract PoC_MarginBypassWithdraw -vv",
       V(target="Risk.checkValidTransition",
         surface_function="checkValidTransition(AccountPosition init, AccountPosition updated, uint64 acct, uint64 cpIndex)",
         suspected_mechanism="The 'value must not decrease' guard is gated on initTotalRisk==0, and the ratio guard reduces to initValue<updatedValue for a risk-constant collateral withdrawal, so any account holding a position can withdraw all collateral without the maintenance-margin check reverting.",
         mechanism_class="margin-check bypass (value-decrease guard gated on risk==0)",
         impact="A perp user opens a leveraged position then withdraws 100% of collateral out of custody, leaving the position unbacked => protocol bad debt.",
         severity_recommendation="Critical", claimed_severity="Critical",
         privilege_required="none (user-signed Withdrawal with ALLOW_WITHDRAW on own account)",
         attacker_controls=["deposit amount", "position size", "withdrawal amount/timing"],
         attacker_does_not_control=["other users' balances"],
         function_map=[{"role":"user entrypoint","function":"WithdrawalTransLib.process","permission":"user-signed (ALLOW_WITHDRAW)","why":"reduces collateral then pays out; margin enforced by PositionManager.updatePosition->Risk.checkValidTransition","source":"src/core/balance/transactions/WithdrawalTransLib.sol"},
                       {"role":"margin check","function":"Risk.checkValidTransition","permission":"internal","why":"value-decrease guard only runs when initRisk==0; ratio guard ineffective for risk-constant withdrawals","source":"src/core/risk/Risk.sol"}],
         attacker_model="Permissionless: a user opens a leveraged position, then signs a Withdrawal for their full collateral; the margin check does not block it.",
         exploit_steps=["deposit 10000 collateral","open long 5000 (healthy: risk 10000*FXP^2 <= value 15000*FXP^2)","submit signed Withdrawal for full 10000 via MultiTransactionProcessor","withdrawal succeeds; collateral 0, position still long 5000, risk>value*FXP (under margin); 10000 tokens leave custody"],
         defense_map=[{"defense":"Risk.validateWithdrawal balance check","location":"Risk.sol","classification":"ineffective","reason":"checks only bucket-0 raw collateral, ignores open-position margin"},
                      {"defense":"checkValidTransition maintenance margin","location":"Risk.sol","classification":"ineffective","reason":"value-decrease guard skipped when initRisk>0; ratio guard doesn't fire for risk-constant withdrawal"}],
         poc_command="forge test --match-contract PoC_MarginBypassWithdraw -vv",
         harness_path=f"{TH}/PoC_MarginBypassWithdraw.t.sol",
         vulnerable_output="test_PoC_withdrawAllCollateralWhileHoldingPosition: collateral 10000->0, position 5000 intact, risk>value*FXP, 10000 tokens extracted",
         corrected_output="withdrawal that pushes the account below maintenance margin should revert",
         control_case="an account with no position (initRisk==0) is blocked from value-decreasing withdrawal by the line-136 guard",
         runtime_delta="value 15000*FXP -> 5000*FXP while position/ risk unchanged; account left under maintenance margin",
         who_loses="protocol / counterparties (bad debt on the unbacked position)", who_gains="the withdrawing user (extracts margin, keeps directional exposure)",
         asset_or_value="collateral (USDC) + protocol solvency", loss_type="protocol insolvency / bad debt",
         permanence="until liquidation (which the bypass also frustrates)", repeatability="any leveraged account",
         limitations="perp profile (RiskPlugin wired as CAP_MARGIN_CHECK)")),
    CF("TipRun", "Risk-segment freeze: insolvent short becomes un-liquidatable (liquidation lock)",
       "High", "PoC reproduced", "2/2 PoC tests pass (long-freeze + short liquidation-dodge)",
       f"{TH}/PoC_RiskSegmentFreeze.t.sol", "forge test --match-contract PoC_RiskSegmentFreeze -vv",
       V(target="GeneralConfig.getRiskFactor",
         surface_function="getRiskFactor(uint64 assetId, int256 absBalance, int256 priceFxp)",
         suspected_mechanism="getRiskFactor returns (0,false) when notional exceeds the top risk segment; Risk.getAssetValueAndRisk then reverts 'Risk: no risk' instead of clamping, freezing every position op (incl. liquidation) on the account.",
         mechanism_class="revert-instead-of-clamp on over-cap notional => account freeze",
         impact="A short sized so its maintenance-margin breach is above the segment cap becomes simultaneously insolvent and un-liquidatable; attacker walks from the loss => protocol bad debt.",
         severity_recommendation="High", claimed_severity="High",
         privilege_required="none (open a short; price rises drive notional past the cap)",
         attacker_controls=["short size (so the cap breach coincides with insolvency)"],
         attacker_does_not_control=["the oracle price path"],
         function_map=[{"role":"risk valuation","function":"Risk.getAssetValueAndRisk","permission":"internal","why":"require(riskOk) reverts when notional>top segment","source":"src/core/risk/Risk.sol"},
                       {"role":"risk factor","function":"GeneralConfig.getRiskFactor","permission":"view","why":"returns (0,false) past the last segment","source":"src/core/config/GeneralConfig.sol"}],
         attacker_model="Permissionless: open a short sized so that, by the time it is underwater, its notional exceeds the top risk segment => every liquidation/resize reverts.",
         exploit_steps=["open short 3000 @ price 1 (notional 3000 <= cap 10000, healthy)","price rises to 4 (short underwater; equity = 10000 - 4*3000 = -2000)","notional 12000 > cap 10000 => getRiskFactor (0,false) => Risk reverts 'Risk: no risk'","every liquidation/resize of the insolvent short reverts => un-liquidatable"],
         defense_map=[{"defense":"tiered risk segments","location":"GeneralConfig","classification":"ineffective","reason":"a finite top segment (normal config) makes over-cap notional revert instead of clamping"}],
         poc_command="forge test --match-contract PoC_RiskSegmentFreeze -vv",
         harness_path=f"{TH}/PoC_RiskSegmentFreeze.t.sol",
         vulnerable_output="test_PoC_shortDodgesLiquidationByFreezing: short 3000 @price4 equity -2000 (insolvent) yet getAccountPositionStatus / resize / liquidation all revert 'Risk: no risk'",
         corrected_output="risk factor should clamp to the top tier; an under-margin account must remain liquidatable",
         control_case="long-freeze variant: account frozen, withdrawal + liquidation revert once notional>cap",
         runtime_delta="account reaches negative equity and is permanently un-liquidatable until price falls back under the cap",
         who_loses="protocol / LPs (unrecoverable bad debt)", who_gains="the short holder (dodges liquidation)",
         asset_or_value="protocol solvency", loss_type="protocol insolvency / bad debt + fund freeze",
         permanence="until price falls under the cap or admin reconfigures", repeatability="any account on a pumping asset",
         limitations="requires a finite top risk segment (the normal tiered-margin setup)")),
    CF("TipRun", "Inverted ratio guard blocks legitimate de-risking of an unhealthy account (liveness/DoS)",
       "Medium", "PoC reproduced", "PoC passes; same root cause as F-1",
       f"{TH}/PoC_DeriskDoS.t.sol", "forge test --match-contract PoC_DeriskDoS -vv",
       V(target="Risk.checkValidTransition",
         surface_function="checkValidTransition(...) (ratio guard ~line 133)",
         suspected_mechanism="In the unhealthy branch the ratio guard reverts when the value/risk ratio IMPROVES, so an under-margin account cannot reduce its position to recover unless it reaches full health in one step.",
         mechanism_class="inverted value/risk ratio guard (liveness)",
         impact="An underwater account cannot incrementally de-risk (partial orderbook fills) => stranded / forced deeper toward insolvency.",
         severity_recommendation="Medium", claimed_severity="Medium",
         privilege_required="none",
         attacker_controls=["partial close size"], attacker_does_not_control=["available counterparty fill"],
         function_map=[{"role":"margin check","function":"Risk.checkValidTransition","permission":"internal","why":"reverts on ratio improvement in the unhealthy branch","source":"src/core/risk/Risk.sol"}],
         attacker_model="Any underwater account attempting a fair partial de-risk hits the inverted guard.",
         exploit_steps=["reach an under-margin account (collateral 2000 / long 5000) via F-1","attempt a fair partial de-risk: sell 500 synthetic for 500 collateral (risk down, still under margin)","reverts 'PM: val/risk dec' — only a full de-risk to health is allowed"],
         defense_map=[{"defense":"checkSmallerInSyntheticHoldings allows reductions","location":"Risk.sol","classification":"ineffective","reason":"reduction passes that check then is reverted by the inverted ratio guard"}],
         poc_command="forge test --match-contract PoC_DeriskDoS -vv", harness_path=f"{TH}/PoC_DeriskDoS.t.sol",
         vulnerable_output="test_PoC_cannotPartiallyDeriskUnhealthyAccount: partial de-risk reverts 'PM: val/risk dec'; full de-risk to health succeeds",
         corrected_output="risk-reducing transitions on an unhealthy account should be allowed",
         control_case="a single-step de-risk to full health succeeds (early healthy-return)",
         runtime_delta="position cannot be reduced incrementally; stays at 5000",
         who_loses="underwater users (cannot self-heal)", who_gains="n/a (liveness)",
         asset_or_value="position recoverability", loss_type="liveness / DoS",
         permanence="until a single full-health de-risk is possible", repeatability="any underwater account",
         limitations="reached via F-1 (or any unhealthy state)")),
    CF("TipRun", "Oracle: no read-side staleness check and the monotonic-update guard is commented out",
       "Medium", "PoC reproduced", "PoC passes",
       f"{TH}/PoC_OracleStaleness.t.sol", "forge test --match-contract PoC_OracleStaleness -vv",
       V(target="Oracle.updatePrice",
         surface_function="updatePrice(uint64 assetId, OraclePrice newPrice) / getPrice(uint64)",
         suspected_mechanism="updatePrice's monotonic timestamp guard is commented out and getPrice has no max-age, so stale or rolled-back prices are used by Risk's margin math indefinitely.",
         mechanism_class="missing staleness + monotonic guard",
         impact="Margin/liquidation decisions run on stale or rolled-back prices.",
         severity_recommendation="Medium", claimed_severity="Medium",
         privilege_required="privileged (price feeder); the missing guard is contract-level",
         reachability_class="PRIVILEGED_ONLY_REACHABLE",
         attacker_controls=["price tick timing/ordering (operator)"], attacker_does_not_control=["other state"],
         function_map=[{"role":"oracle write","function":"Oracle.updatePrice","permission":"authorized caller","why":"monotonic guard commented out","source":"src/core/oracle/Oracle.sol"},
                       {"role":"oracle read","function":"Oracle.getPrice","permission":"view","why":"exist=timestamp>0, no max-age","source":"src/core/oracle/Oracle.sol"}],
         attacker_model="Operator delay/failure or a reordered/rolled-back price tick yields stale pricing in margin.",
         exploit_steps=["set price 100 @ recent ts","updatePrice price 1 @ OLDER ts => accepted (no monotonic guard)","getPrice returns rolled-back 1; warp 10 years => still exist=true (no staleness)"],
         defense_map=[{"defense":"OraclePriceTickTransLib ingestion (quorum+median+<=1day)","location":"OraclePriceTickTransLib.sol","classification":"ineffective","reason":"bounds ingestion only; stored price has no read freshness and can be reordered"}],
         poc_command="forge test --match-contract PoC_OracleStaleness -vv", harness_path=f"{TH}/PoC_OracleStaleness.t.sol",
         vulnerable_output="test_PoC_priceCanBeRolledBackAndIsNeverStale: older-timestamp price accepted; 10-year-old price still exist=true",
         corrected_output="reject non-monotonic timestamps and enforce a max-age on read",
         control_case="n/a", runtime_delta="stored price rolled back to an older value; never flagged stale",
         who_loses="users mispriced/mis-liquidated on stale data", who_gains="whoever benefits from the stale price",
         asset_or_value="margin/liquidation correctness", loss_type="accounting corruption",
         permanence="until a fresh price is pushed", repeatability="per stale/reordered tick",
         limitations="bounded by operator liveness in the happy path")),
    CF("TipRun", "Liquidate/Deleverage have no on-chain maintenance-margin precondition",
       "Medium", "PoC reproduced", "PoC liquidates a provably-healthy account",
       f"{TH}/PoC_NoLiquidatablePrecondition.t.sol", "forge test --match-contract PoC_NoLiquidatablePrecondition -vv",
       V(target="LiquidateTransLib.process",
         surface_function="LiquidateTransLib.process(...) / DeleverageTransLib.process(...)",
         suspected_mechanism="Liquidate/Deleverage never check the target is below maintenance margin before force-resizing its position; deleverage only checks the signer is registered (no signature/nonce).",
         mechanism_class="missing liquidatable precondition",
         impact="A faulty/malicious operator can force-trade/seize positions of healthy, fully-collateralized accounts.",
         severity_recommendation="Medium", claimed_severity="Medium",
         privilege_required="privileged (onlyTxBatcher); operator-trust dependent",
         reachability_class="PRIVILEGED_ONLY_REACHABLE",
         attacker_controls=["which account, price, amounts (operator)"], attacker_does_not_control=["a health gate (absent)"],
         function_map=[{"role":"liquidation","function":"LiquidateTransLib.process","permission":"onlyTxBatcher","why":"no health check before force-resize","source":"src/perp/transactions/LiquidateTransLib.sol"},
                       {"role":"deleverage","function":"DeleverageTransLib.process","permission":"onlyTxBatcher","why":"only checkSigner; no sig/nonce/health","source":"src/perp/transactions/DeleverageTransLib.sol"}],
         attacker_model="A malicious/buggy sequencer liquidates or deleverages a healthy account.",
         exploit_steps=["target is healthy (100 collateral, tiny long 1; risk<=value*FXP)","submit TYPE_LIQUIDATE for the target","liquidation succeeds; healthy account's position force-closed (no 'not liquidatable' guard)"],
         defense_map=[{"defense":"onlyTxBatcher gating","location":"plugins","classification":"mitigating-only","reason":"reduces to operator trust; on-chain protection of healthy users is absent"}],
         poc_command="forge test --match-contract PoC_NoLiquidatablePrecondition -vv", harness_path=f"{TH}/PoC_NoLiquidatablePrecondition.t.sol",
         vulnerable_output="test_PoC_canLiquidatePerfectlyHealthyAccount: healthy account (risk<=value*FXP) force-liquidated, position zeroed",
         corrected_output="require the target to be below maintenance margin before liquidation/deleverage",
         control_case="n/a", runtime_delta="healthy target's position force-closed; collateral settled against it",
         who_loses="healthy users (seized positions)", who_gains="liquidator/operator",
         asset_or_value="user positions", loss_type="fund loss (trust-dependent)",
         permanence="immediate", repeatability="any account (operator-driven)",
         limitations="operator-trust dependent (onlyTxBatcher); severity per program trust model")),
    CF("TipRun", "setSyntheticAssetsInfo does not bump configVersion, defeating the stale-config batch guard",
       "Medium", "PoC reproduced", "PoC: configVersion unchanged after setSyntheticAssetsInfo",
       f"{TH}/PoC_ConfigVersionNotBumped.t.sol", "forge test --match-contract PoC_ConfigVersionNotBumped -vv",
       V(target="GeneralConfig.setSyntheticAssetsInfo",
         surface_function="setSyntheticAssetsInfo(uint64[] assetIds, SyntheticAssetInfo[] infos)",
         suspected_mechanism="setSyntheticAssetsInfo (risk segments, oracle signers, quorum) has its incrConfigVersionInternal() commented out, while every other mutator bumps it, so the MultiTransactionProcessor stale-config guard never fires for these changes.",
         mechanism_class="missing config-version bump",
         impact="In-flight user txs execute under changed risk/oracle params without the version-mismatch protection.",
         severity_recommendation="Medium", claimed_severity="Medium",
         privilege_required="admin (owner/batchConfig)", reachability_class="PRIVILEGED_ONLY_REACHABLE",
         attacker_controls=["config change (admin)"], attacker_does_not_control=["the version guard (skipped)"],
         function_map=[{"role":"config","function":"GeneralConfig.setSyntheticAssetsInfo","permission":"owner/batchConfig","why":"incr commented out","source":"src/core/config/GeneralConfig.sol"},
                       {"role":"batch guard","function":"MultiTransactionProcessor.processMultiTransactions","permission":"onlyTxBatcher","why":"reverts only if configVersion<current","source":"src/MultiTransactionProcessor.sol"}],
         attacker_model="Admin changes risk/oracle params; the version guard users rely on doesn't trigger.",
         exploit_steps=["record configVersion","setSyntheticAssetsInfo (change risk segment) => version unchanged","control: setMaxFundingRate => version increments by 1"],
         defense_map=[{"defense":"config-version guard","location":"MultiTransactionProcessor.sol","classification":"ineffective","reason":"relies on the version being bumped; this path skips the bump"}],
         poc_command="forge test --match-contract PoC_ConfigVersionNotBumped -vv", harness_path=f"{TH}/PoC_ConfigVersionNotBumped.t.sol",
         vulnerable_output="test_PoC_setSyntheticAssetsInfo_doesNotBumpConfigVersion: configVersion unchanged after setSyntheticAssetsInfo; setMaxFundingRate increments it",
         corrected_output="setSyntheticAssetsInfo should call incrConfigVersionInternal() (parity with other setters)",
         control_case="setMaxFundingRate bumps configVersion by 1",
         runtime_delta="configVersion stays V after a risk-param change (should be V+1)",
         who_loses="users whose signed batches execute under changed params", who_gains="n/a",
         asset_or_value="config-change protection", loss_type="accounting corruption / safety-mechanism bypass",
         permanence="per unbumped config change", repeatability="every setSyntheticAssetsInfo call",
         limitations="admin-triggered")),
    # ---------------- Cartha ----------------
    CF("Cartha", "Stale/zero-TVL share mispricing lets a depositor steal existing holders' PnL",
       "High", "PoC reproduced", "PoC passes; reachability confirmed via 0xMarkets getMarketTokenPrice (X-1)",
       f"{CH}/PoC_StaleTvlMint.t.sol", "forge test --match-contract PoC_StaleTvlMint -vv",
       V(target="CarthaVault._convertToShares",
         surface_function="_convertToShares(uint256 assets) / _totalValueLocked()",
         suspected_mechanism="_convertToShares falls back to the first-deposit 1e12-offset rate whenever _totalValueLocked() reads 0 even when totalSupply>0; gmValueInUsdc returns 0 when the 0xM GM price is <=0, so idle~0 + gmPrice<=0 with real GM value => TVL reads 0 => a permissionless depositAndLock mints at the stale rate and dilutes existing holders.",
         mechanism_class="first-deposit-rate fallback at TVL==0 with supply>0",
         impact="Permissionless theft of existing depositors' accrued PnL during a zero-TVL read.",
         severity_recommendation="High", claimed_severity="High",
         privilege_required="none (depositAndLock)",
         human_review_required="reachability confirmed: 0xMarkets MarketUtils.getMarketTokenPrice returns <=0 when poolValue<=0",
         attacker_controls=["deposit amount/timing during a TVL==0 read"], attacker_does_not_control=["the GM oracle value"],
         function_map=[{"role":"share math","function":"CarthaVault._convertToShares","permission":"internal","why":"TVL==0 -> first-deposit 1e12 branch with supply>0","source":"src/CarthaVault.sol"},
                       {"role":"GM value","function":"PoolDeployLib.gmValueInUsdc","permission":"view","why":"returns 0 when 0xM gmPrice<=0","source":"src/libraries/PoolDeployLib.sol"}],
         attacker_model="Permissionless depositor during a TVL==0 read (idle deployed + 0xM GM price <=0 while real GM value exists).",
         exploit_steps=["victim deposits 100k; keeper deploys to 0xM (idle->0); GM grows to 150k","0xM GM price reads <=0 => gmValueInUsdc=0 => _totalValueLocked()==0 (supply>0)","attacker depositAndLock(100k) mints at the 1e12 first-deposit rate","GM price recovers => TVL 250k; attacker claims 125k for 100k; victim 150k->125k"],
         defense_map=[{"defense":"1e12 decimal offset","location":"CarthaVault.sol","classification":"ineffective","reason":"blunts donation rounding-to-zero, not the TVL==0 first-deposit fallback"},
                      {"defense":"lock + cooldown","location":"CarthaVault.sol","classification":"ineffective","reason":"dilution is locked in at mint time; realized after lock"},
                      {"defense":"assumed GM price > 0","location":"PoolDeployLib.sol","classification":"ineffective","reason":"0xM getMarketTokenPrice is signed int256 and returns 0/negative by design when poolValue<=0 (confirmed in 0xM source)"}],
         poc_command="forge test --match-contract PoC_StaleTvlMint -vv", harness_path=f"{CH}/PoC_StaleTvlMint.t.sol",
         vulnerable_output="test_PoC_staleTvlZeroRead_stealsPnL: attacker deposited 100000 -> claim 125000; victim before 150000 -> after 125000 (25k stolen)",
         corrected_output="do not fall back to first-deposit rate when totalSupply>0; treat gmPrice<=0/stale as a hard error",
         control_case="with a correct live price the attacker would mint ~0.667*shares and capture no PnL",
         runtime_delta="attacker claim 100k->125k; victim 150k->125k (25k transferred)",
         who_loses="existing Cartha depositors (accrued PnL)", who_gains="the stale-rate depositor",
         asset_or_value="vault share value (USDC)", loss_type="fund loss (PnL theft)",
         permanence="realized on the attacker's release after lock", repeatability="each TVL==0 window with PnL",
         limitations="needs the child's idle ~fully deployed and 0xM gmPrice<=0 (confirmed reachable, see X-1)")),
    CF("Cartha", "Child shares transferable post-lock but only redeemable via a Position (orphan shares)",
       "Low", "PoC reproduced", "PoC: transferred shares non-redeemable",
       f"{CH}/PoC_OrphanShares.t.sol", "forge test --match-contract PoC_OrphanShares -vv",
       V(target="CarthaVault._update",
         surface_function="_update(from,to,value) / release / requestRelease",
         suspected_mechanism="CarthaVault has no position-independent redeem; redemption is position-bound, but shares are ERC20-transferable once the lock expires, so shares moved to a no-position address are non-redeemable yet still counted in totalSupply.",
         mechanism_class="transferable-but-position-bound-redeem (orphan shares)",
         impact="A holder who acquires child shares by transfer cannot redeem them; orphan supply dilutes share price.",
         severity_recommendation="Low", claimed_severity="Low",
         privilege_required="none",
         attacker_controls=["transfer shares post-lock"], attacker_does_not_control=["recipient's (absent) position"],
         function_map=[{"role":"transfer gate","function":"CarthaVault._update","permission":"internal","why":"blocks transfer only while locked","source":"src/CarthaVault.sol"},
                       {"role":"redeem","function":"CarthaVault.release/requestRelease","permission":"position-bound","why":"no redeem-by-shares; reverts without a Position","source":"src/CarthaVault.sol"}],
         attacker_model="Any holder transfers/sells child shares after the lock expires.",
         exploit_steps=["user1 deposits+locks -> shares + Position","lock expires -> shares transferable","user1 transfers half its shares to user3 (no Position)","user3 holds shares but release/requestRelease revert (no Position); no redeem(shares) exists -> shares stuck; totalSupply unchanged"],
         defense_map=[{"defense":"lock-gated _update","location":"CarthaVault.sol","classification":"ineffective","reason":"only blocks while locked; post-lock transfers create orphan shares"}],
         poc_command="forge test --match-contract PoC_OrphanShares -vv", harness_path=f"{CH}/PoC_OrphanShares.t.sol",
         vulnerable_output="test_PoC_transferredSharesAreOrphaned: user3 holds 50000e21 transferred shares; release/requestRelease revert (no Position); totalSupply unchanged",
         corrected_output="make shares soulbound to the position, or add a position-independent redeem(shares)",
         control_case="the original holder (with a Position) can still release up to balanceOf",
         runtime_delta="orphaned 50k*1e12 shares non-redeemable, still in totalSupply",
         who_loses="anyone acquiring child shares by transfer", who_gains="remaining holders (orphan supply dilution)",
         asset_or_value="child vault shares", loss_type="fund freeze / user fund loss",
         permanence="permanent for the orphan holder", repeatability="per post-lock transfer",
         limitations="footgun; matters if child shares are traded")),
]

TARGETS = [
    {"target": "TipRun", "source": "contest (tiprun-contracts-main @ d5d4d2a)", "verdict": "candidate_finding",
     "notes": "Off-chain-match / on-chain-settlement perp+orderbook+predict exchange. 6 PoC-reproduced findings: "
              "F-1 Critical margin-bypass (withdraw 100% collateral with open position), F-2 High risk-segment freeze "
              "(insolvent short un-liquidatable), M-1 inverted ratio de-risk DoS, M-2 oracle staleness, M-3 no "
              "liquidatable precondition, M-4 configVersion not bumped. Investigated-and-disproven: negative-amount "
              "Transfer theft (BalancePlugin amount>0 guard). Sound: EIP-712 locks, conservation, upgrade/diamond auth."},
    {"target": "Cartha", "source": "contest (cartha-vaults-main @ 4c51f2a)", "verdict": "candidate_finding",
     "notes": "Bittensor SN35 liquidity vaults over 0xMarkets GM pools. C-1 High (PoC) stale/zero-TVL share mispricing "
              "-> PnL theft (reachability confirmed via 0xMarkets getMarketTokenPrice<=0). L-2 Low (PoC) orphan shares. "
              "L-1 Low (code-verified, no PoC): parent withdraw/release dust underpayment. Sound: cross-vault "
              "conservation, EIP-712 locks, upgrade/init/diamond auth, classic 1e12 inflation mitigated."},
    {"target": "0xMarkets", "source": "contest (0xMarkets_contract-main @ e94daee; GMX Synthetics fork)", "verdict": "honest_negative",
     "notes": "GMX Synthetics fork (ships GMX audits). Audited the 0xMarkets delta (custom insurance module). No "
              "PoC-reproduced bug. X-1 (source-confirmed, GMX-inherited): getMarketTokenPrice returns <=0 when "
              "poolValue<=0 -> confirms Cartha C-1 reachability. I-1 Medium (code-verified): insurance injection "
              "compensates current LP holders not drawdown-era (JIT capture). I-2 Low (code-verified): triggerFactor "
              "unset-default 0 = inject-on-any-drawdown. I-1/I-2/X-1 need the full GMX build to PoC standalone -> "
              "honest non-reproduced, documented in reports/0xmarkets-2026-06-13/."},
]


def main():
    data = json.loads(RW.read_text())
    cfs = data.get("candidate_findings") or []
    tgs = data.get("targets") or []
    before_cf, before_tg = len(cfs), len(tgs)

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    (RW.with_suffix(RW.suffix + f".bak.{ts}")).write_text(json.dumps(data, indent=2) + "\n")

    # idempotent: drop our prior entries, then append fresh
    cfs = [c for c in cfs if not str(c.get("target", "")).startswith(OUR_TARGET_PREFIXES)]
    tgs = [t for t in tgs if not str(t.get("target", "")).startswith(OUR_TARGET_PREFIXES)]
    preserved_cf, preserved_tg = len(cfs), len(tgs)
    cfs.extend(CANDIDATES)
    tgs.extend(TARGETS)
    data["candidate_findings"] = cfs
    data["targets"] = tgs

    # refresh summary counts
    s = data.get("summary") or {}
    s["targets_engaged"] = len(tgs)
    s["poc_proven_candidate_findings"] = len(cfs)
    s["honest_negatives"] = sum(1 for t in tgs if t.get("verdict") == "honest_negative")
    data["summary"] = s

    RW.write_text(json.dumps(data, indent=2) + "\n")

    # verifier completeness check vs the Monolith template
    template_keys = set(next(c for c in cfs if "Monolith" in str(c.get("target", ""))).get("verifier", {}).keys())
    print(f"[real_world] preserved candidate_findings: {preserved_cf} (+{len(CANDIDATES)} ours) -> {len(cfs)}")
    print(f"[real_world] preserved targets: {preserved_tg} (+{len(TARGETS)} ours) -> {len(tgs)}")
    print(f"[real_world] summary: {s}")
    bad = 0
    for c in CANDIDATES:
        missing = template_keys - set(c["verifier"].keys())
        if missing:
            bad += 1
            print(f"  !! {c['target']} {c['verifier']['target']} missing verifier keys: {missing}")
        if c["verifier"]["poc_status"] != "REPRODUCED":
            print(f"  !! {c['verifier']['target']} poc_status != REPRODUCED")
    print(f"[real_world] verifier completeness: {'OK (all 8 match template, all REPRODUCED)' if bad==0 else 'PROBLEMS'}")


if __name__ == "__main__":
    main()
