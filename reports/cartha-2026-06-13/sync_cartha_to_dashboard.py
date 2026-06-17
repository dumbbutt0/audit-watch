#!/usr/bin/env python3
"""sync_cartha_to_dashboard.py — author Cartha submission_candidate.json files AND upsert the findings into the
research-only dashboard mirror (documentation/research/funnel/synced_findings.generated.json) for the /candidates view.

Safety: research-only / review-only / human_review_required (enforced by dashboard_sync.to_synced_finding). Never
submits, never flips submission_ready, never routes. Upserts ONLY the 'cartha-2026-06-13:' record_id namespace —
every other source's records (zeta, size, tiprun) are preserved — and writes a timestamped backup first. Idempotent.

Run:  python3 reports/cartha-2026-06-13/sync_cartha_to_dashboard.py
"""
from __future__ import annotations
import json, sys, time, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent
SUB_DIR = PKG_DIR / "submissions"
MIRROR = ROOT / "documentation/research/funnel/synced_findings.generated.json"
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard_sync as ds  # noqa: E402

SUBJECT = "Cartha Vaults 2026-06-13"
RID_PREFIX = "cartha-2026-06-13"
SCOPE_REF = "Cartha contest (cartha-vaults-main @ 4c51f2a); official scope list not bundled with PoC package."

FINDINGS = [
    {
        "fid": "C-1", "severity": "High", "sev_lc": "high",
        "contract": "CarthaVault", "function": "_convertToShares",
        "title": "Stale/zero-TVL share mispricing lets a depositor steal existing holders' PnL",
        "root_cause": "_convertToShares falls back to the first-deposit 1e12-offset rate whenever _totalValueLocked() "
                      "reads 0 even when totalSupply>0; _totalValueLocked=idle+gmValueInUsdc and gmValueInUsdc returns "
                      "0 when the 0xM market token price is <=0, so idle<=~0 + gmPrice<=0 with real GM value => TVL "
                      "reads 0 => permissionless depositAndLock mints at the stale rate and dilutes existing holders.",
        "impact_category": "fund_loss", "privilege": "none", "scope": "in_scope",
        "attacker_entrypoint": "CarthaVault.depositAndLock (permissionless) during a TVL==0 read",
        "attacker_capabilities": ["deposit USDC permissionlessly while the 0xM GM price reads <=0 and child idle is deployed"],
        "affected_contracts": ["src/CarthaVault.sol", "src/libraries/PoolDeployLib.sol"],
        "affected_functions": ["CarthaVault._convertToShares", "CarthaVault._totalValueLocked", "PoolDeployLib.gmValueInUsdc"],
        "exploit_steps": ["victim deposits 100k; keeper deploys to 0xM (idle->0); GM grows to 150k",
                          "0xM GM price reads <=0 => gmValueInUsdc returns 0 => _totalValueLocked()==0 (supply>0)",
                          "attacker depositAndLock(100k) mints at 1e12 first-deposit rate (not live price)",
                          "GM price recovers => TVL 250k; attacker claims 125k for 100k; victim 150k->125k"],
        "asset_delta": "Attacker claims 125k for a 100k deposit; victim 150k->125k => 25k of existing holders' PnL stolen.",
        "state_before": "victim alone worth 150k (GM value, idle drained)",
        "state_after": "attacker shares claim 125k (deposited 100k); victim claim 125k (was 150k)",
        "proof_type": "runnable_poc", "poc_status_sc": "passing", "poc_status_ds": "REPRODUCED",
        "poc_contract": "PoC_StaleTvlMint",
        "poc_result": "PASS: attacker deposits 100k at stale rate -> claims 125k; victim 150k->125k (25k stolen)",
        "evidence": ["src/CarthaVault.sol:_convertToShares (TVL==0 -> first-deposit 1e12 branch with supply>0)",
                     "src/libraries/PoolDeployLib.sol:gmValueInUsdc (if gmPrice<=0 return 0)",
                     "test/vault/CarthaVaultPool.t.sol::test_TVL_HandlesNegativeGmPrice (repo treats <=0 GM price as expected)",
                     "CONFIRMED reachable: 0xMarkets MarketUtils.getMarketTokenPrice returns 0 when poolValue==0 and "
                     "negative when poolValue<0 (int256 poolValue = pool USD - capped pending trader PnL); Cartha uses "
                     "maximize=false (minimize) which makes <=0 more likely",
                     "reports/cartha-2026-06-13/cartha-C1-reachability.md",
                     "reports/0xmarkets-2026-06-13/FINDINGS.md (X-1)",
                     "reports/cartha-2026-06-13/submissions/C-1/poc/PoC_StaleTvlMint.t.sol",
                     "reports/cartha-2026-06-13/submissions/C-1/poc_output.log"],
        "defense": [{"defense": "1e12 decimal offset (classic inflation mitigation)", "blocks_path": False,
                     "why_it_fails": "blunts donation rounding-to-zero, but the TVL==0 first-deposit fallback is the bug here"},
                    {"defense": "lock + cooldown (blocks atomic oracle sandwich)", "blocks_path": False,
                     "why_it_fails": "dilution is locked in at mint time; attacker realizes it after the lock expires"},
                    {"defense": "assumed GM price always > 0", "blocks_path": False,
                     "why_it_fails": "0xMarkets getMarketTokenPrice is signed int256 and returns 0/negative by design "
                                     "when poolValue<=0 (confirmed in 0xM source) -> gmValueInUsdc returns 0 -> TVL==0"}],
        "worst": "Permissionless theft of existing holders' accrued PnL during a zero-TVL read.",
        "realistic": "CONFIRMED reachable (0xM getMarketTokenPrice returns <=0 when poolValue<=0, a real market state; "
                     "Cartha minimize=false makes it more likely); needs the child's idle ~fully deployed (idle~0) at the read.",
    },
    {
        "fid": "L-1", "severity": "Low", "sev_lc": "low",
        "contract": "CarthaParentVault", "function": "withdraw",
        "title": "Parent withdraw/releaseFromParent burn full shares but can underpay on rounding",
        "root_cause": "withdraw burns roundUp(assets) and releaseFromParent burns full lockedShares, but the payout is "
                      "min(value,balance) after _withdrawFromChildren which does a single proportional, per-child-floored "
                      "pass (no remainder loop), guarded only by a +10 wei tolerance -> bounded dust underpayment.",
        "impact_category": "accounting_corruption", "privilege": "none", "scope": "in_scope",
        "attacker_entrypoint": "CarthaParentVault.withdraw / releaseFromParent (normal user exit)",
        "attacker_capabilities": ["exit when parent idle is short and children are pulled proportionally"],
        "affected_contracts": ["src/CarthaParentVault.sol"],
        "affected_functions": ["CarthaParentVault.withdraw", "CarthaParentVault.releaseFromParent",
                               "CarthaParentVault._prepareSharePayout", "CarthaParentVault._withdrawFromChildren"],
        "exploit_steps": ["user exits requiring a pull from children",
                          "_withdrawFromChildren floors each child's proportional pull (single pass)",
                          "full shares burned but payout = min(value, balance) -> caller receives slightly less"],
        "asset_delta": "Bounded dust loss to the withdrawer (retained by vault / remaining holders).",
        "state_before": "user holds shares worth `assets`",
        "state_after": "shares for `assets` burned; payout < `assets` by rounding dust",
        "proof_type": "static_proof", "poc_status_sc": "none", "poc_status_ds": "NOT_STARTED",
        "poc_contract": "", "poc_result": "code analysis (dust magnitude; no runnable PoC)",
        "blocker": "bounded dust rounding; code-verified. Runnable PoC not pursued - dust-level loss + legacy withdraw-path reachability is murky (low value).",
        "evidence": ["src/CarthaParentVault.sol:withdraw (burn roundUp(assets), pay min(assets,balance))",
                     "src/CarthaParentVault.sol:_withdrawFromChildren (single proportional pass, per-child floor)",
                     "src/CarthaParentVault.sol:_prepareSharePayout",
                     "reports/cartha-2026-06-13/submissions/L-1/vulnerable/CarthaParentVault.sol"],
        "defense": [{"defense": "_availableFromChildren()+10 < needed revert", "blocks_path": False,
                     "why_it_fails": "tolerates ~10 wei; per-child floors can still leave a small remainder"}],
        "worst": "Repeatable small underpayment to withdrawers.",
        "realistic": "Dust-level; accounting wart.",
    },
    {
        "fid": "L-2", "severity": "Low", "sev_lc": "low",
        "contract": "CarthaVault", "function": "_update",
        "title": "Child shares transferable post-lock but only redeemable via a Position (orphan shares)",
        "root_cause": "CarthaVault exposes no position-independent redeem; redemption is position-bound, but shares are "
                      "ERC20-transferable once the lock expires (_update only blocks while locked). Shares moved to an "
                      "address without a Position are non-redeemable yet still count in totalSupply.",
        "impact_category": "fund_freeze", "privilege": "none", "scope": "in_scope",
        "attacker_entrypoint": "CarthaVault ERC20 transfer of shares post-lock to a non-position address",
        "attacker_capabilities": ["transfer/sell child shares after the lock expires"],
        "affected_contracts": ["src/CarthaVault.sol"],
        "affected_functions": ["CarthaVault._update", "CarthaVault.release", "CarthaVault.forceExit",
                               "CarthaVault.processQueuedWithdrawals"],
        "exploit_steps": ["user's lock expires; user transfers/sells child shares",
                          "recipient has no Position; no redeem(shares) exists",
                          "recipient's shares are orphaned (non-redeemable) but still in totalSupply"],
        "asset_delta": "Acquired-by-transfer shares are unrecoverable for the holder; orphan supply skews share price.",
        "state_before": "holder owns transferable child shares without a Position",
        "state_after": "shares non-redeemable (no position-independent redeem path)",
        "proof_type": "runnable_poc", "poc_status_sc": "passing", "poc_status_ds": "REPRODUCED",
        "poc_contract": "PoC_OrphanShares",
        "poc_result": "PASS: transferred shares orphaned - recipient holds 50k*1e12 shares, release/requestRelease revert (no Position), totalSupply unchanged",
        "blocker": "none - PoC reproduced (Foundry test passing)",
        "evidence": ["src/CarthaVault.sol:_update (transfers allowed once unlocked)",
                     "src/CarthaVault.sol (release/forceExit/processQueuedWithdrawals are position-bound; no redeem-by-shares)",
                     "reports/cartha-2026-06-13/submissions/L-2/vulnerable/CarthaVault.sol"],
        "defense": [{"defense": "lock-gated _update", "blocks_path": False,
                     "why_it_fails": "only blocks while locked; post-lock transfers create orphan shares"}],
        "worst": "User who acquires shares by transfer cannot redeem them.",
        "realistic": "Footgun; matters if child shares are traded.",
    },
]


def candidate_json(f):
    return {
        "finding_id": f["fid"], "title": f["title"], "root_cause": f["root_cause"],
        "affected_contracts": f["affected_contracts"], "affected_functions": f["affected_functions"],
        "attacker_entrypoint": f["attacker_entrypoint"], "attacker_capabilities": f["attacker_capabilities"],
        "privilege_required": f["privilege"], "scope_status": f["scope"],
        "in_scope_asset": f"{f['contract']} ({f['function']})",
        "out_of_scope_risks": [],
        "impact_category": f["impact_category"], "severity_claim": f["severity"],
        "severity_justification": {"worst_case": f["worst"], "realistic_case": f["realistic"],
                                   "program_table_mapping": "see official program impact table (not bundled)"},
        "bounty_program_mapping": {"program": "Cartha", "platform": "contest", "impact_in_scope": True,
                                   "privileged_roles_in_scope": False, "scope_reference": SCOPE_REF},
        "call_trace": f["exploit_steps"],
        "state_transition": {"before": f["state_before"], "after": f["state_after"], "slots_or_balances": []},
        "asset_delta": f["asset_delta"], "proof_type": f["proof_type"],
        "poc_path": (f"reports/cartha-2026-06-13/submissions/{f['fid']}/poc/{f['poc_contract']}.t.sol"
                     if f["poc_contract"] else ""),
        "poc_status": f["poc_status_sc"],
        "reproduction_steps": ([f"cd reports/cartha-2026-06-13/harness",
                                f"forge test --match-contract {f['poc_contract']} -vv"] if f["poc_contract"]
                               else ["code analysis — see report.md + vulnerable/ source"]),
        "duplicate_check_status": "searched_clear", "known_issue_check_status": "not_searched",
        "prior_audit_overlap": [], "false_positive_risks": [f["realistic"]],
        "invalidating_conditions": (["only if the child's idle USDC is NOT meaningfully deployed (idle large) so TVL never reads 0"]
                                    if f["fid"] == "C-1" else []),
        "defense_analysis": f["defense"], "assumptions": ["perp deployment with 0xM pool wired (reader/oracle set)"],
        "evidence_links": f["evidence"],
        "triager_summary": f["title"] + " — " + f["poc_result"],
        "recommended_status": "READY_FOR_HUMAN_REVIEW", "human_approval_required": True,
    }


def bundle(f):
    return {
        "candidate_id": f["fid"], "record_id": f"{RID_PREFIX}:{f['fid']}:{f['contract']}.{f['function']}",
        "source_track": "audit_workspace", "subject": SUBJECT, "phase_discovered": "cartha-2026-06-13",
        "contract": f["contract"], "function": f["function"], "title": f["title"],
        "summary": f["root_cause"], "mechanism": f["root_cause"], "impact": f["asset_delta"],
        "root_cause": f["root_cause"],
        "attacker_model": "permissionless" if f["privilege"] == "none" else f["privilege"],
        "exploit_steps": f["exploit_steps"],
        "defense_map": [d.get("defense", "") + ": " + d.get("why_it_fails", "") for d in f["defense"]],
        "conversion": "CLEAN_HIT" if f["poc_contract"] else "STRONG_PARTIAL",
        "novelty_status": "searched_local_clear", "severity_recommendation": f["sev_lc"], "claimed_severity": f["sev_lc"],
        "final_triager_decision": "READY_FOR_HUMAN_REVIEW",
        "blocker_reason": f.get("blocker", "none - PoC reproduced (Foundry test passing)"),
        "intent_scope_operator_assumptions": "permissionless / in-scope core vault accounting",
        "poc": {"poc_status": f["poc_status_ds"],
                "test_file": (f"reports/cartha-2026-06-13/submissions/{f['fid']}/poc/{f['poc_contract']}.t.sol"
                              if f["poc_contract"] else None),
                "test_command": (f"forge test --match-contract {f['poc_contract']} -vv" if f["poc_contract"] else None),
                "vulnerable_result": f["poc_result"]},
        "source_refs": {"evidence": f["evidence"]}, "evidence_backup": f["evidence"],
    }


def main():
    for f in FINDINGS:
        out = SUB_DIR / f["fid"] / "submission_candidate.json"
        out.write_text(json.dumps(candidate_json(f), indent=2) + "\n")
        print(f"[candidate] wrote {out.relative_to(ROOT)}")

    recs = []
    for f in FINDINGS:
        rec = ds.to_synced_finding(bundle(f))
        problems = ds.validate_synced(rec)
        print(f"[synced] {rec['record_id']}  validate_synced -> {'OK' if not problems else problems}")
        if problems:
            raise SystemExit(f"validate_synced failed for {f['fid']}: {problems}")
        recs.append(rec)

    data = json.loads(MIRROR.read_text())
    findings = data.get("findings", [])
    before_ids = {r.get("record_id") for r in findings}
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    (MIRROR.with_suffix(MIRROR.suffix + f".bak.{ts}")).write_text(json.dumps(data, indent=2) + "\n")
    kept = [r for r in findings if not str(r.get("record_id", "")).startswith(RID_PREFIX + ":")]
    data["findings"] = kept + recs
    tmp = MIRROR.with_suffix(MIRROR.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, MIRROR)
    after_ids = {r.get("record_id") for r in data["findings"]}
    print(f"\n[mirror] backup written; preserved non-cartha: {len(kept)}; total now: {len(data['findings'])}")
    for a in sorted(after_ids - before_ids):
        print(f"          + {a}")


if __name__ == "__main__":
    main()
