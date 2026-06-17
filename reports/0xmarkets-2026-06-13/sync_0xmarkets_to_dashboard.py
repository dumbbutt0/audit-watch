#!/usr/bin/env python3
"""sync_0xmarkets_to_dashboard.py — author 0xMarkets submission_candidate.json files AND upsert the findings into the
research-only dashboard mirror for the /candidates view. Namespace: 0xmarkets-2026-06-13.

Honest status: none of the 0xMarkets findings have a runnable standalone PoC (X-1 is a source-confirmed fact; I-1/I-2
need the full GMX build/machinery), so poc.poc_status stays NOT_STARTED with full evidence + an explicit main_blocker.
NEVER fakes REPRODUCED. Upserts ONLY the 0xmarkets- namespace (preserves zeta/size/tiprun/cartha); backs up first.

Run:  python3 reports/0xmarkets-2026-06-13/sync_0xmarkets_to_dashboard.py
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

SUBJECT = "0xMarkets (GMX fork) 2026-06-13"
RID_PREFIX = "0xmarkets-2026-06-13"
SCOPE_REF = "0xMarkets contest (0xMarkets_contract-main @ e94daee); GMX Synthetics fork (ships GMX audits)."

FINDINGS = [
    {
        "fid": "X-1", "severity": "Informational", "sev_lc": "informational", "impact": "info",
        "privilege": "none", "scope": "uncertain", "conversion": "CLEAN_HIT",
        "contract": "MarketUtils", "function": "getMarketTokenPrice",
        "title": "getMarketTokenPrice can return <= 0 (confirms Cartha C-1 reachability)",
        "root_cause": "getMarketTokenPrice returns 0 when poolValue==0 and negative when poolValue<0 (signed int256 "
                      "poolValue = pool USD +- impact - capped pending trader PnL). Cross-protocol: this is the "
                      "precondition for Cartha C-1 (gmPrice<=0 -> Cartha gmValueInUsdc=0 -> TVL reads 0).",
        "mechanism": "signed int256 poolValue; explicit `if (poolValue==0) return 0`; mulDiv(WEI_PRECISION,poolValue,supply) negative if poolValue<0.",
        "attacker_capabilities": ["no attacker on 0xM; deeply-in-profit traders / MAX_PNL_FACTOR path drive poolValue<=0 (a market state)"],
        "affected_contracts": ["contracts/market/MarketUtils.sol"],
        "affected_functions": ["MarketUtils.getMarketTokenPrice"],
        "exploit_steps": ["traders accumulate capped pending profit >= pool token value",
                          "poolValue <= 0; getMarketTokenPrice returns 0 (poolValue==0) or negative (poolValue<0)",
                          "an integrator mapping <=0 -> 0 (Cartha) reads TVL==0 while real GM value exists"],
        "asset_delta": "No direct 0xM loss (GMX-inherited, by design). Confirms Cartha C-1 (High) is reachable.",
        "state_before": "pool with capped pending trader PnL approaching pool token value",
        "state_after": "getMarketTokenPrice returns <= 0",
        "intent": "GMX-inherited behavior; informational for 0xM, but grounds Cartha C-1.",
        "blocker": "source-confirmed; a runnable PoC needs the full GMX build to drive getPoolValueInfo. Reported as a code-confirmed fact.",
        "defense": [{"defense": "integrators assuming GM price > 0", "blocks_path": False,
                     "why_it_fails": "price is signed int256 and <=0 by design under the MAX_PNL_FACTOR path"}],
        "evidence": ["contracts/market/MarketUtils.sol:getMarketTokenPrice (poolValue==0 -> return 0; signed mulDiv)",
                     "reports/cartha-2026-06-13/cartha-C1-reachability.md",
                     "reports/0xmarkets-2026-06-13/submissions/X-1/vulnerable/MarketUtils.sol"],
        "worst": "Integrators treating GM price as always-positive inherit a mispricing surface (e.g. Cartha C-1, High).",
        "realistic": "GMX-inherited / by design for 0xM; informational here, confirms Cartha C-1.",
        "proof_type": "static_proof", "poc_sc": "none", "poc_ds": "NOT_STARTED",
    },
    {
        "fid": "I-1", "severity": "Medium", "sev_lc": "medium", "impact": "reward_extraction",
        "privilege": "none", "scope": "in_scope", "conversion": "STRONG_PARTIAL",
        "contract": "InsuranceFundUtils", "function": "attemptInjectPool",
        "title": "Insurance injection compensates current LP holders, not drawdown-era holders (JIT capture)",
        "root_cause": "attemptInjectPool credits the live pool (applyDeltaToPoolAmount) on drawdown, raising the price "
                      "for whoever holds LP at injection time; the reserve was meant for LPs who bore the drawdown, so "
                      "a JIT LP depositing after the drawdown captures insurance compensation it never lost.",
        "mechanism": "pool-level compensation (no per-LP/per-epoch drawdown snapshot) => mis-distribution to current holders.",
        "attacker_capabilities": ["deposit LP after a realized drawdown, before/at injection (async GMX deposit)"],
        "affected_contracts": ["contracts/insurance/InsuranceFundUtils.sol", "contracts/position/DecreasePositionCollateralUtils.sol"],
        "affected_functions": ["InsuranceFundUtils.attemptInjectPool", "InsuranceFundUtils.getDrawdownFraction",
                               "DecreasePositionCollateralUtils.processCollateral (call site ~557)"],
        "exploit_steps": ["market realizes drawdown (traders win); reserve funded over the epoch",
                          "JIT LP deposits after the drawdown",
                          "attemptInjectPool injects reserve into the pool -> raises price for current holders incl. the JIT LP",
                          "JIT LP withdraws, capturing a share of insurance compensation it never lost"],
        "asset_delta": "Insurance reserve (meant for drawdown-era LPs) partially skimmed by JIT LPs.",
        "state_before": "reserve accrued; drawdown realized; intended beneficiaries = drawdown-era LPs",
        "state_after": "injection compensates current holders incl. a post-drawdown JIT LP",
        "intent": "custom insurance module wired into the GMX position-close path.",
        "blocker": "not standalone-reproducible without the full GMX deposit/withdrawal + keeper machinery; code-verified design finding.",
        "defense": [{"defense": "async + fee'd GMX deposits/withdrawals", "blocks_path": False, "uncertain": True,
                     "why_it_fails": "bounds single-block JIT but not the compensation-to-current-holders mismatch"}],
        "evidence": ["contracts/insurance/InsuranceFundUtils.sol:attemptInjectPool (credits pool, not per-LP snapshot)",
                     "contracts/position/DecreasePositionCollateralUtils.sol (call site ~line 557)",
                     "reports/0xmarkets-2026-06-13/submissions/I-1/vulnerable/InsuranceFundUtils.sol"],
        "worst": "JIT LPs systematically skim the insurance reserve from drawdown-era LPs.",
        "realistic": "Bounded by async deposit timing/fees; a real value-distribution flaw.",
        "proof_type": "static_proof", "poc_sc": "none", "poc_ds": "NOT_STARTED",
    },
    {
        "fid": "I-2", "severity": "Low", "sev_lc": "low", "impact": "accounting_corruption",
        "privilege": "admin", "scope": "in_scope", "conversion": "STRONG_PARTIAL",
        "contract": "InsuranceFundUtils", "function": "attemptInjectPool",
        "title": "triggerFactor unset-default of 0 means inject-on-any-drawdown (inverted-safe default)",
        "root_cause": "The off sentinel is type(uint256).max but the unset DataStore default is 0, which means inject on "
                      "any drawdown>0. A fee-collecting market whose insuranceFundDrawdownTriggerFactor isn't set to max "
                      "auto-drains its reserve on the slightest realized drawdown.",
        "mechanism": "fail-open default (0 = inject-always) instead of fail-safe (unset = disabled).",
        "attacker_capabilities": ["config admin leaves triggerFactor unset on a fee-collecting market"],
        "affected_contracts": ["contracts/insurance/InsuranceFundUtils.sol"],
        "affected_functions": ["InsuranceFundUtils.attemptInjectPool (~196-205)"],
        "exploit_steps": ["market collects insurance fees (reserve > 0)",
                          "insuranceFundDrawdownTriggerFactor never set to type(uint256).max (default 0)",
                          "any realized drawdown > 0 triggers injection -> reserve drained"],
        "asset_delta": "Insurance reserve silently drained into the pool for a misconfigured market (bounded by reserve).",
        "state_before": "reserve > 0, triggerFactor unset (=0)",
        "state_after": "reserve drained on slight drawdown",
        "intent": "custom insurance module; default-value direction inverted.",
        "blocker": "standalone PoC needs the full GMX build (@openzeppelin-v4 + MarketUtils/DataStore deps); code-verified config finding.",
        "defense": [{"defense": "deploy-script sets triggerFactor=max for non-onboarded markets", "blocks_path": True, "uncertain": True,
                     "why_it_fails": "relies on operator discipline; the on-chain default is fail-open"}],
        "evidence": ["contracts/insurance/InsuranceFundUtils.sol:attemptInjectPool lines ~196-205 (off=type(uint256).max; unset default 0)",
                     "reports/0xmarkets-2026-06-13/submissions/I-2/vulnerable/InsuranceFundUtils.sol"],
        "worst": "A misconfigured market silently auto-drains its insurance reserve.",
        "realistic": "Config footgun; admin/deploy-script dependent.",
        "proof_type": "static_proof", "poc_sc": "none", "poc_ds": "NOT_STARTED",
    },
]


def candidate_json(f):
    return {
        "finding_id": f["fid"], "title": f["title"], "root_cause": f["root_cause"],
        "affected_contracts": f["affected_contracts"], "affected_functions": f["affected_functions"],
        "attacker_entrypoint": f["exploit_steps"][0],
        "attacker_capabilities": f["attacker_capabilities"], "privilege_required": f["privilege"],
        "scope_status": f["scope"], "in_scope_asset": f"{f['contract']} ({f['function']})",
        "out_of_scope_risks": (["GMX-inherited behavior; not a 0xMarkets-specific bug"] if f["fid"] == "X-1" else []),
        "impact_category": f["impact"], "severity_claim": f["severity"],
        "severity_justification": {"worst_case": f["worst"], "realistic_case": f["realistic"],
                                   "program_table_mapping": "see official program impact table (not bundled)"},
        "bounty_program_mapping": {"program": "0xMarkets", "platform": "contest", "impact_in_scope": f["fid"] != "X-1",
                                   "privileged_roles_in_scope": f["privilege"] != "none", "scope_reference": SCOPE_REF},
        "call_trace": f["exploit_steps"],
        "state_transition": {"before": f["state_before"], "after": f["state_after"], "slots_or_balances": []},
        "asset_delta": f["asset_delta"], "proof_type": f["proof_type"], "poc_path": "", "poc_status": f["poc_sc"],
        "reproduction_steps": ["code analysis — see report.md + vulnerable/ source (no standalone PoC: " + f["blocker"] + ")"],
        "duplicate_check_status": "searched_clear", "known_issue_check_status": "not_searched",
        "prior_audit_overlap": (["GMX core is audited (ABDK/Certora/Dedaub/Guardian); this is the 0xMarkets delta / a GMX-inherited fact"]),
        "false_positive_risks": [f["realistic"]],
        "invalidating_conditions": [f["blocker"]],
        "defense_analysis": f["defense"], "assumptions": ["GMX Synthetics fork; insurance module is the 0xMarkets delta"],
        "evidence_links": f["evidence"],
        "triager_summary": f["title"] + " — " + ("source-confirmed (no runnable PoC)" if f["fid"] == "X-1" else "code-verified (no standalone PoC)"),
        "recommended_status": "READY_FOR_HUMAN_REVIEW", "human_approval_required": True,
    }


def bundle(f):
    return {
        "candidate_id": f["fid"], "record_id": f"{RID_PREFIX}:{f['fid']}:{f['contract']}.{f['function']}",
        "source_track": "audit_workspace", "subject": SUBJECT, "phase_discovered": "0xmarkets-2026-06-13",
        "contract": f["contract"], "function": f["function"], "title": f["title"],
        "summary": f["root_cause"], "mechanism": f["mechanism"], "impact": f["asset_delta"],
        "root_cause": f["root_cause"], "attacker_model": "permissionless" if f["privilege"] == "none" else f["privilege"],
        "exploit_steps": f["exploit_steps"],
        "defense_map": [d.get("defense", "") + ": " + d.get("why_it_fails", "") for d in f["defense"]],
        "conversion": f["conversion"], "novelty_status": "searched_local_clear",
        "severity_recommendation": f["sev_lc"], "claimed_severity": f["sev_lc"],
        "final_triager_decision": "READY_FOR_HUMAN_REVIEW",
        "intent_scope_operator_assumptions": f["intent"],
        "blocker_reason": f["blocker"],
        "poc": {"poc_status": f["poc_ds"], "test_file": None, "test_command": None,
                "vulnerable_result": "source-confirmed (no runnable PoC); see report.md + vulnerable/"},
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
    before = {r.get("record_id") for r in findings}
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    (MIRROR.with_suffix(MIRROR.suffix + f".bak.{ts}")).write_text(json.dumps(data, indent=2) + "\n")
    kept = [r for r in findings if not str(r.get("record_id", "")).startswith(RID_PREFIX + ":")]
    data["findings"] = kept + recs
    tmp = MIRROR.with_suffix(MIRROR.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, MIRROR)
    after = {r.get("record_id") for r in data["findings"]}
    print(f"\n[mirror] preserved non-0xmarkets: {len(kept)}; total now: {len(data['findings'])}")
    for a in sorted(after - before):
        print(f"          + {a}")


if __name__ == "__main__":
    main()
