#!/usr/bin/env python3
"""sync_tiprun_to_dashboard.py — author TipRun submission_candidate.json files AND upsert the 6 findings into the
research-only dashboard mirror (documentation/research/funnel/synced_findings.generated.json) so they render in the
dashboard /candidates view.

Safety: research-only / review-only / human_review_required (enforced by dashboard_sync.to_synced_finding). Never
submits, never computes/flips submission_ready, never routes. Upserts ONLY the 'tiprun-2026-06-13:' record_id
namespace — every other source's records are preserved — and writes a timestamped backup first. Idempotent.

Run:  python3 reports/tiprun-2026-06-13/sync_tiprun_to_dashboard.py
"""
from __future__ import annotations
import json, sys, time, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # repo root
PKG_DIR = Path(__file__).resolve().parent             # reports/tiprun-2026-06-13
SUB_DIR = PKG_DIR / "submissions"
MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard_sync as ds  # noqa: E402

SUBJECT = "TipRun 2026-06-13"
RID_PREFIX = "tiprun-2026-06-13"
SCOPE_REF = "TipRun contest (tiprun-contracts-main @ d5d4d2a); official scope list not bundled with PoC package."

# --------------------------------------------------------------------------- finding data (single source of truth)
FINDINGS = [
    {
        "fid": "F-1", "severity": "Critical", "sev_lc": "critical",
        "contract": "Risk", "function": "checkValidTransition",
        "title": "Maintenance-margin bypass: withdraw 100% of collateral while holding an open position",
        "root_cause": "Risk.checkValidTransition gates the value-decrease protection on initTotalRisk==0, and its "
                      "ratio guard reduces to initValue<updatedValue for a risk-constant collateral withdrawal, so "
                      "any account holding a position can remove all collateral without the margin check reverting.",
        "impact_category": "fund_loss", "privilege": "none", "scope": "in_scope",
        "attacker_entrypoint": "MultiTransactionProcessor.processMultiTransactions (a user-signed Withdrawal for full collateral)",
        "attacker_capabilities": ["open a leveraged position", "sign a withdrawal of own full collateral (ALLOW_WITHDRAW on own account)"],
        "affected_functions": ["Risk.checkValidTransition", "PositionManager.updatePosition", "WithdrawalTransLib.process"],
        "exploit_steps": ["deposit 10000 collateral", "open long 5000 (healthy: risk 10000*FXP^2 <= value 15000*FXP^2)",
                          "submit signed Withdrawal for full 10000 via MultiTransactionProcessor",
                          "withdrawal succeeds; collateral 0, position still long 5000, risk > value*FXP (under margin)"],
        "asset_delta": "10,000 collateral tokens leave LoadingZone; position of 5,000 left unbacked => protocol bad debt on adverse move.",
        "state_before": "collateral=10000, long synthetic=5000, healthy (risk<=value*FXP)",
        "state_after": "collateral=0, long synthetic=5000, risk>value*FXP (liquidatable), 10000 tokens extracted",
        "impact_category_h": "fund_loss",
        "poc_contract": "PoC_MarginBypassWithdraw",
        "poc_result": "PASS: withdrawal of 100% collateral succeeds; account left under maintenance margin; 10000 tokens extracted",
        "evidence": ["src/core/risk/Risk.sol:checkValidTransition (initRisk==0 gate + ratio guard ~line 121-140)",
                     "src/core/balance/transactions/WithdrawalTransLib.sol:process (validateWithdrawal = bucket-0 collateral only)",
                     "harness/test/PoC_MarginBypassWithdraw.t.sol", "submissions/F-1/poc_output.log",
                     "corroborating: test/PositionManager.Risk.t.sol::test_ArithmeticEdgeCase_NegativeCollateral"],
        "defense": [{"defense": "Risk.validateWithdrawal balance check", "blocks_path": False,
                     "why_it_fails": "only requires bucket-0 collateral >= amount; ignores open-position margin"},
                    {"defense": "checkValidTransition maintenance-margin check", "blocks_path": False,
                     "why_it_fails": "value-decrease guard skipped when initRisk>0; ratio guard does not fire for risk-constant withdrawal"}],
        "worst": "Attacker extracts full margin and walks from a losing position => unrecoverable protocol bad debt.",
        "realistic": "Any leveraged user can under-collateralize at will; systemic insolvency / other users cannot withdraw.",
    },
    {
        "fid": "F-2", "severity": "High", "sev_lc": "high",
        "contract": "GeneralConfig", "function": "getRiskFactor",
        "title": "Account freeze / liquidation lock when notional exceeds the top risk segment (short can dodge liquidation)",
        "root_cause": "getRiskFactor returns (0,false) when notional exceeds the largest risk segment; "
                      "Risk.getAssetValueAndRisk then reverts 'Risk: no risk' instead of clamping, freezing every "
                      "position operation (incl. liquidation) on the account.",
        "impact_category": "fund_freeze", "privilege": "none", "scope": "in_scope",
        "attacker_entrypoint": "Oracle price move (notional=price*|amount|); attacker opens a short sized to breach the cap while underwater",
        "attacker_capabilities": ["open a short position", "wait for / rely on price moving up (short goes underwater as notional crosses the cap)"],
        "affected_functions": ["GeneralConfig.getRiskFactor", "Risk.getAssetValueAndRisk", "Risk.getAccountPositionStatus"],
        "exploit_steps": ["open short 3000 @ price 1 (notional 3000 <= cap 10000, healthy)",
                          "price rises to 4 (short underwater; equity = 10000 - 4*3000 = -2000)",
                          "notional 12000 > cap 10000 => getRiskFactor (0,false) => Risk reverts 'Risk: no risk'",
                          "every liquidation/resize of the insolvent short reverts => un-liquidatable => bad debt"],
        "asset_delta": "Insolvent short (negative equity, e.g. -2,000) cannot be liquidated => loss is unrecoverable protocol bad debt.",
        "state_before": "short 3000 @ price 1, healthy",
        "state_after": "price 4, equity -2000 (insolvent), all position ops revert 'Risk: no risk' (frozen/un-liquidatable)",
        "impact_category_h": "fund_freeze",
        "poc_contract": "PoC_RiskSegmentFreeze",
        "poc_result": "PASS (2 tests): long-freeze blocks withdrawal/liquidation; short variant leaves an insolvent account un-liquidatable",
        "evidence": ["src/core/config/GeneralConfig.sol:getRiskFactor (returns (0,false) past top segment)",
                     "src/core/risk/Risk.sol:getAssetValueAndRisk (require(riskOk,'Risk: no risk'))",
                     "harness/test/PoC_RiskSegmentFreeze.t.sol", "submissions/F-2/poc_output.log"],
        "defense": [{"defense": "tiered risk segments", "blocks_path": False,
                     "why_it_fails": "finite top segment (normal config) => notional past it reverts instead of clamping"}],
        "worst": "Attacker deliberately freezes an insolvent short to dodge liquidation => unrecoverable bad debt.",
        "realistic": "Any account on a pumping asset freezes (funds locked, un-liquidatable) when notional crosses the cap.",
    },
    {
        "fid": "M-1", "severity": "Medium", "sev_lc": "medium",
        "contract": "Risk", "function": "checkValidTransition",
        "title": "Inverted ratio guard blocks legitimate de-risking of an unhealthy account (liveness/DoS)",
        "root_cause": "checkValidTransition reverts when the value/risk ratio improves, so an under-margin account "
                      "cannot reduce its position to recover unless it reaches full health in one step.",
        "impact_category": "liveness_failure", "privilege": "none", "scope": "in_scope",
        "attacker_entrypoint": "Any de-risking trade/deleverage on an under-margin account (routes through checkValidTransition)",
        "attacker_capabilities": ["hold an under-margin position", "attempt a partial close (typical partial orderbook fill)"],
        "affected_functions": ["Risk.checkValidTransition", "PositionManager.updatePosition"],
        "exploit_steps": ["reach an under-margin account (collateral 2000 / long 5000) via F-1",
                          "attempt a fair partial de-risk: sell 500 synthetic for 500 collateral (risk down, still under margin)",
                          "reverts 'PM: val/risk dec' — only a full de-risk to health is allowed"],
        "asset_delta": "No direct loss; positions can be stranded under margin (cannot recover incrementally).",
        "state_before": "collateral 2000 / long 5000 (under margin)",
        "state_after": "partial de-risk reverts; position unchanged at 5000",
        "impact_category_h": "liveness_failure",
        "poc_contract": "PoC_DeriskDoS",
        "poc_result": "PASS: partial de-risk of an under-margin account reverts 'PM: val/risk dec'; full de-risk to health succeeds",
        "evidence": ["src/core/risk/Risk.sol:checkValidTransition (~line 133 ratio guard)",
                     "corroborating: test/PositionManager.Risk.t.sol::test_RiskRatioComparisonLogic (ratioImproved == revert condition)",
                     "harness/test/PoC_DeriskDoS.t.sol", "submissions/M-1/poc_output.log"],
        "defense": [{"defense": "checkSmallerInSyntheticHoldings allows reductions", "blocks_path": False,
                     "why_it_fails": "reduction passes that check but is then reverted by the inverted ratio guard"}],
        "worst": "Underwater accounts cannot self-heal => forced deeper into liquidation/insolvency.",
        "realistic": "With partial fills, incremental recovery is blocked; combines with F-1.",
    },
    {
        "fid": "M-2", "severity": "Medium", "sev_lc": "medium",
        "contract": "Oracle", "function": "updatePrice",
        "title": "Oracle has no read-side staleness check and the monotonic-update guard is commented out",
        "root_cause": "Oracle.updatePrice's monotonic timestamp guard is commented out and Oracle.getPrice has no "
                      "max-age, so stale or rolled-back prices are used by Risk's margin math indefinitely.",
        "impact_category": "accounting_corruption", "privilege": "privileged", "scope": "uncertain",
        "attacker_entrypoint": "OraclePlugin price tick path / operator delay (price feeder is trusted; the missing guard is contract-level)",
        "attacker_capabilities": ["operator delay/failure or a reordered/rolled-back price tick"],
        "affected_functions": ["Oracle.updatePrice", "Oracle.getPrice", "Risk.getAssetValueAndRisk"],
        "exploit_steps": ["set price 100 @ recent ts",
                          "updatePrice price 1 @ OLDER ts => accepted (no monotonic guard)",
                          "getPrice returns rolled-back 1; warp 10 years => still exist=true (no staleness)"],
        "asset_delta": "Margin/liquidation decisions can run on stale/rolled-back prices (mispriced solvency).",
        "state_before": "price 100 @ recent ts",
        "state_after": "price 1 @ older ts accepted; 10-year-old price still exist=true",
        "impact_category_h": "accounting_corruption",
        "poc_contract": "PoC_OracleStaleness",
        "poc_result": "PASS: older-timestamp price accepted; ancient price still reads exist=true",
        "evidence": ["src/core/oracle/Oracle.sol:updatePrice (monotonic guard commented out ~46-54)",
                     "src/core/oracle/Oracle.sol:getPrice (exist = timestamp>0, no max-age)",
                     "harness/test/PoC_OracleStaleness.t.sol", "submissions/M-2/poc_output.log"],
        "defense": [{"defense": "OraclePriceTickTransLib ingestion (quorum+median+<=1day)", "blocks_path": False,
                     "why_it_fails": "bounds ingestion only; stored price has no read-side freshness and can be reordered"}],
        "worst": "Stale price drives wrong liquidations / margin => fund loss under operator delay or reorg.",
        "realistic": "Robustness gap; impact bounded by operator liveness in the happy path.",
    },
    {
        "fid": "M-3", "severity": "Medium", "sev_lc": "medium",
        "contract": "LiquidateTransLib", "function": "process",
        "title": "Liquidate / Deleverage have no on-chain maintenance-margin precondition",
        "root_cause": "LiquidateTransLib/DeleverageTransLib never verify the target is below maintenance margin before "
                      "force-resizing its position; deleverage only checks the signer is registered (no signature/nonce).",
        "impact_category": "fund_loss", "privilege": "privileged", "scope": "uncertain",
        "attacker_entrypoint": "TYPE_LIQUIDATE / TYPE_DELEVERAGE (onlyTxBatcher) against a healthy account",
        "attacker_capabilities": ["malicious or buggy sequencer/operator (onlyTxBatcher)"],
        "affected_functions": ["LiquidateTransLib.process", "DeleverageTransLib.process"],
        "exploit_steps": ["target is healthy (100 collateral, tiny long 1; risk <= value*FXP)",
                          "submit TYPE_LIQUIDATE for the target",
                          "liquidation succeeds; healthy account's position force-closed (no 'not liquidatable' guard)"],
        "asset_delta": "Healthy users' positions can be force-seized at operator-chosen price; over-seizure not blocked (with F-1).",
        "state_before": "target healthy (collateral 100, long 1)",
        "state_after": "target position force-closed (assets.length 0); forced trade settled against target",
        "impact_category_h": "fund_loss",
        "poc_contract": "PoC_NoLiquidatablePrecondition",
        "poc_result": "PASS: a provably healthy account is force-liquidated with no maintenance-margin precondition",
        "evidence": ["src/perp/transactions/LiquidateTransLib.sol:process (no health check)",
                     "src/perp/transactions/DeleverageTransLib.sol:process (checkSigner only; no sig/nonce/health)",
                     "harness/test/PoC_NoLiquidatablePrecondition.t.sol", "submissions/M-3/poc_output.log"],
        "defense": [{"defense": "onlyTxBatcher gating", "blocks_path": True, "uncertain": True,
                     "why_it_fails": "mitigates to operator-trust; on-chain protection of healthy users is still absent"}],
        "worst": "Faulty/malicious operator seizes healthy users' positions.",
        "realistic": "Operator-trust dependent; severity per the program's trust model.",
    },
    {
        "fid": "M-4", "severity": "Medium", "sev_lc": "medium",
        "contract": "GeneralConfig", "function": "setSyntheticAssetsInfo",
        "title": "setSyntheticAssetsInfo does not bump configVersion, defeating the stale-config batch guard",
        "root_cause": "setSyntheticAssetsInfo (risk segments, oracle signers, quorum) has its incrConfigVersionInternal() "
                      "commented out, so the MultiTransactionProcessor stale-config guard never fires for these changes.",
        "impact_category": "accounting_corruption", "privilege": "admin", "scope": "uncertain",
        "attacker_entrypoint": "GeneralConfig.setSyntheticAssetsInfo (owner/batchConfig) — version not bumped",
        "attacker_capabilities": ["config admin (owner/batchConfig) changes risk/oracle params"],
        "affected_functions": ["GeneralConfig.setSyntheticAssetsInfo", "MultiTransactionProcessor.processMultiTransactions"],
        "exploit_steps": ["record configVersion", "setSyntheticAssetsInfo (change risk segment) => version unchanged",
                          "control: setMaxFundingRate => version increments by 1"],
        "asset_delta": "In-flight user txs execute under changed risk/oracle params without the version-mismatch protection.",
        "state_before": "configVersion = V",
        "state_after": "configVersion still V after risk-param change (should be V+1)",
        "impact_category_h": "accounting_corruption",
        "poc_contract": "PoC_ConfigVersionNotBumped",
        "poc_result": "PASS: configVersion unchanged after setSyntheticAssetsInfo; setMaxFundingRate increments it",
        "evidence": ["src/core/config/GeneralConfig.sol:setSyntheticAssetsInfo (incr commented out ~179-182)",
                     "src/MultiTransactionProcessor.sol:processMultiTransactions (configVersion<current guard)",
                     "harness/test/PoC_ConfigVersionNotBumped.t.sol", "submissions/M-4/poc_output.log"],
        "defense": [{"defense": "config version guard in MultiTransactionProcessor", "blocks_path": False,
                     "why_it_fails": "guard relies on the version being bumped; this path skips the bump"}],
        "worst": "Risk/oracle config changes apply to already-signed batches without protection.",
        "realistic": "Admin-triggered; undermines a built-in safety mechanism.",
    },
]


def candidate_json(f):
    rid_contract = f["contract"]
    return {
        "finding_id": f["fid"],
        "title": f["title"],
        "root_cause": f["root_cause"],
        "affected_contracts": [f"src/.../{f['contract']}.sol"] + [],
        "affected_functions": f["affected_functions"],
        "attacker_entrypoint": f["attacker_entrypoint"],
        "attacker_capabilities": f["attacker_capabilities"],
        "privilege_required": f["privilege"],
        "scope_status": f["scope"],
        "in_scope_asset": f"{f['contract']} ({f['function']})",
        "out_of_scope_risks": [] if f["privilege"] == "none" else ["relies on trusted operator/admin behavior (program trust model dependent)"],
        "impact_category": f["impact_category"],
        "severity_claim": f["severity"],
        "severity_justification": {"worst_case": f["worst"], "realistic_case": f["realistic"],
                                   "program_table_mapping": "see official program impact table (not bundled)"},
        "bounty_program_mapping": {"program": "TipRun", "platform": "contest",
                                   "impact_in_scope": True, "privileged_roles_in_scope": f["privilege"] != "none",
                                   "scope_reference": SCOPE_REF},
        "call_trace": f["exploit_steps"],
        "state_transition": {"before": f["state_before"], "after": f["state_after"], "slots_or_balances": []},
        "asset_delta": f["asset_delta"],
        "proof_type": "runnable_poc",
        "poc_path": f"reports/tiprun-2026-06-13/submissions/{f['fid']}/poc/{f['poc_contract']}.t.sol",
        "poc_status": "passing",
        "reproduction_steps": [f"cd reports/tiprun-2026-06-13/harness",
                               f"forge test --match-contract {f['poc_contract']} -vv"],
        "duplicate_check_status": "searched_clear",
        "known_issue_check_status": "not_searched",
        "prior_audit_overlap": [],
        "false_positive_risks": ["severity/scope depend on the official program trust model"] if f["privilege"] != "none" else [],
        "invalidating_conditions": [] if f["privilege"] == "none" else ["program may treat operator/admin actions as out of scope"],
        "defense_analysis": f["defense"],
        "assumptions": ["perp profile (RiskPlugin wired as CAP_MARGIN_CHECK)"] if f["contract"] in ("Risk", "GeneralConfig", "LiquidateTransLib") else [],
        "evidence_links": f["evidence"],
        "triager_summary": f["title"] + " — PoC passing (" + f["poc_result"] + ").",
        "recommended_status": "READY_FOR_HUMAN_REVIEW",
        "human_approval_required": True,
    }


def bundle(f):
    return {
        "candidate_id": f["fid"],
        "record_id": f"{RID_PREFIX}:{f['fid']}:{f['contract']}.{f['function']}",
        "source_track": "audit_workspace",
        "subject": SUBJECT,
        "phase_discovered": "tiprun-2026-06-13",
        "contract": f["contract"],
        "function": f["function"],
        "title": f["title"],
        "summary": f["root_cause"],
        "mechanism": f["root_cause"],
        "impact": f["asset_delta"],
        "root_cause": f["root_cause"],
        "attacker_model": "permissionless" if f["privilege"] == "none" else f["privilege"],
        "exploit_steps": f["exploit_steps"],
        "defense_map": [d.get("defense", "") + (": " + d.get("why_it_fails", "")) for d in f["defense"]],
        "conversion": "CLEAN_HIT",
        "novelty_status": "searched_local_clear",
        "severity_recommendation": f["sev_lc"],     # recorded only; human decides
        "claimed_severity": f["sev_lc"],
        "final_triager_decision": "READY_FOR_HUMAN_REVIEW",
        "blocker_reason": "none - PoC reproduced (Foundry test passing)",
        "intent_scope_operator_assumptions": ("permissionless / in-scope core" if f["privilege"] == "none"
                                              else "trust-dependent (operator/admin); scope per program"),
        "poc": {"poc_status": "REPRODUCED",
                "test_file": f"reports/tiprun-2026-06-13/submissions/{f['fid']}/poc/{f['poc_contract']}.t.sol",
                "test_command": f"forge test --match-contract {f['poc_contract']} -vv",
                "vulnerable_result": f["poc_result"]},
        "source_refs": {"evidence": f["evidence"]},
        "evidence_backup": f["evidence"],
    }


def main():
    # 1) write submission_candidate.json per package
    for f in FINDINGS:
        out = SUB_DIR / f["fid"] / "submission_candidate.json"
        out.write_text(json.dumps(candidate_json(f), indent=2) + "\n")
        print(f"[candidate] wrote {out.relative_to(ROOT)}")

    # 2) build + validate synced records
    recs = []
    for f in FINDINGS:
        rec = ds.to_synced_finding(bundle(f))
        problems = ds.validate_synced(rec)
        status = "OK" if not problems else f"PROBLEMS={problems}"
        print(f"[synced] {rec['record_id']}  validate_synced -> {status}")
        if problems:
            raise SystemExit(f"validate_synced failed for {f['fid']}: {problems}")
        recs.append(rec)

    # 3) merge into the dashboard mirror (backup + upsert tiprun namespace only)
    if not MIRROR.exists():
        raise SystemExit(f"mirror not found: {MIRROR}")
    data = json.loads(MIRROR.read_text())
    findings = data.get("findings", [])
    before_ids = {r.get("record_id") for r in findings}
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    bak = MIRROR.with_suffix(MIRROR.suffix + f".bak.{ts}")
    bak.write_text(json.dumps(data, indent=2) + "\n")
    kept = [r for r in findings if not str(r.get("record_id", "")).startswith(RID_PREFIX + ":")]
    merged = kept + recs
    data["findings"] = merged
    tmp = MIRROR.with_suffix(MIRROR.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, MIRROR)

    after_ids = {r.get("record_id") for r in merged}
    added = sorted(after_ids - before_ids)
    preserved = len([r for r in merged if not str(r.get("record_id", "")).startswith(RID_PREFIX + ":")])
    print(f"\n[mirror] backup: {bak.relative_to(ROOT)}")
    print(f"[mirror] preserved non-tiprun records: {preserved}")
    print(f"[mirror] total findings now: {len(merged)} (added {len(added)} tiprun records)")
    for a in added:
        print(f"          + {a}")


if __name__ == "__main__":
    main()
