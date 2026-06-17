#!/usr/bin/env python3
"""validate_p189.py — READ-ONLY cross-corpus adjudication validation (P189).

Reconstructs DEEP_RUN_BUT_MISSED per corpus (answer-key MISS whose function is in the deep-pass candidate
queue), records the pre-registered bounded sample, and the answer-aware classification of each blind
re-adjudication output. Emits replay_results.json, corpus_breakdown.json, metrics.json. Never mutates corpora /
answer keys / dispositions; reads them only to recompute the miss denominators.

Scoring scale (per the spec):
  SELECTED            awarded mechanism carried as a primary selected mechanism
  HARNESS_ESCALATED   awarded mechanism carried in unresolved_mechanisms with NEEDS_HARNESS
  ENUMERATED_ONLY     awarded mechanism (or its core) appears but is not carried as selected/harness
  UNCHANGED_MISS      awarded mechanism still not surfaced
  FALSE_CARRY         a new, clearly-unsupported mechanism carried
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
PD = ROOT / "documentation/research/assisted_mode/p189_cross_corpus_adjudication_validation"

CORPORA = {
 "zaros": ("zaros-2025-01-part-2-eval", "answer_key/answer_key_normalized.json",
           "output/eval_ready/eval_match_matrix.json"),
 "revert-lend": ("revert-lend-2024-03-strict-eval", "output/eval_ready/answer_key_normalization.json",
                 "output/eval_ready/match_matrix.json"),
 "panoptic": ("panoptic-2025-12-strict-eval", "output/eval_ready/answer_key_normalization.json",
              "output/eval_ready/match_matrix.json"),
 "ark": ("ark-project-2024-07-strict-eval", "output/answer_key/answer_key.json",
         "output/eval_ready/match_matrix.json"),
}

def load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None
def funcset(f):
    s=set()
    for k in ("affected_functions","functions"):
        v=f.get(k)
        if isinstance(v,list): s|=set(v)
        elif isinstance(v,str): s|=set(re.split(r"[\/,\s]+",v))
    loc=f.get("affected") or f.get("location") or ""
    s|=set(re.findall(r"[A-Za-z_]\w{2,}",str(loc)))
    return {x for x in s if x and len(x)>2}
def qfuncset(q):
    qit=q if isinstance(q,list) else (q.get("queue") or q.get("candidates") if isinstance(q,dict) else None)
    if not qit and isinstance(q,dict):
        for v in q.values():
            if isinstance(v,list): qit=v; break
    return set(it.get("function") for it in (qit or []) if isinstance(it,dict) and it.get("function"))

def deep_run_misses(corpus):
    cdir,akp,mmp = CORPORA[corpus]
    ak=load(ROOT/"audits"/cdir/akp); mm=load(ROOT/"audits"/cdir/mmp)
    q=load(ROOT/"audits"/cdir/"output/deep_pass/candidate_queue.json")
    akf=ak.get("findings") or ak.get("families")
    rows=mm["rows"] if isinstance(mm,dict) and "rows" in mm else mm
    miss={(r.get("answer_key_id") or r.get("ak_id")) for r in rows
          if str(r.get("category") or r.get("verdict")).upper() in ("MISS","UNRECOVERED")}
    qf=qfuncset(q)
    hits=[]
    for f in akf:
        fid=f.get("answer_key_id") or f.get("ak_id")
        if fid in miss and (funcset(f)&qf):
            hits.append({"id":fid,"severity":f.get("severity")})
    return len(miss), hits

# Pre-registered sample (High->Medium, function-level; written before scoring) + answer-aware outcomes.
# outcome + the P183-P188 feature responsible (for recoveries) / failure reason (for misses).
SCORES = {
 "zaros": [
   {"id":"H-01","traced":"FeeDistributionBranch._handleWethRewardDistribution","outcome":"SELECTED",
    "feature":"mechanism-inventory+carry-forward (selected mis-split / depositors-get-zero as incorrect WETH distribution)",
    "note":"awarded RC terse ('weth reward not distributed correctly'); selected mechanisms address incorrect split"},
   {"id":"H-02","traced":"VaultRouterBranch.stake","outcome":"ENUMERATED_ONLY",
    "feature":"enumeration surfaced accumulateActor-before-setActorShares ordering",
    "note":"awarded 'restake wipes accumulated value' framed by blind as reward-index theft/reentrancy, not the loss-of-value framing"},
   {"id":"H-07","traced":"Market.getCreditDepositsValueUsd","outcome":"UNCHANGED_MISS",
    "feature":None,"reason":"sibling-trace: awarded locus is Market.getRealizedDebtUsd; extractor traced sibling getCreditDepositsValueUsd",
    "sibling_caveat":True},
   {"id":"H-09","traced":"Vault.getUnsettledRealizedDebt","outcome":"UNCHANGED_MISS",
    "feature":None,"reason":"sibling-trace: awarded 'rebalanceVaultsAssets always reverts'; extractor traced leaf getUnsettledRealizedDebt; blind found decimal-mismatch not the revert",
    "sibling_caveat":True},
 ],
 "revert-lend": [
   {"id":"H-02","traced":"V3Vault.onERC721Received","outcome":"HARNESS_ESCALATED",
    "feature":"harness-escalation: reentrancy via _cleanupLoan NFT-before-state carried as NEEDS_HARNESS (also found a distinct AC-replacement bug)",
    "note":"awarded RC '_cleanupLoan sends NFT before completing state updates' carried unresolved NEEDS_HARNESS"},
   {"id":"H-04","traced":"V3Utils.execute","outcome":"SELECTED",
    "feature":"mechanism-inventory: missing caller/ownership check selected #1 (exact match)"},
   {"id":"H-05","traced":"V3Oracle._getReferencePoolPriceX96","outcome":"HARNESS_ESCALATED",
    "feature":"harness-escalation: tick integer-division truncation (negative-delta rounding) carried NEEDS_HARNESS with correct who-loses",
    "note":"awarded 'no round-down for negative tick deltas -> inflated price' == carried truncation mechanism"},
   {"id":"H-06","traced":"V3Vault._cleanupLoan","outcome":"SELECTED",
    "feature":"mechanism-inventory+severity-floor: onERC721Received callback-revert blocks liquidation selected #2 (exact match)"},
 ],
 "panoptic": [
   {"id":"H-02","traced":"CollateralTracker.settleLiquidation","outcome":"ENUMERATED_ONLY",
    "feature":"phantom-asset inflation surfaced+selected (the accounting substrate of the awarded phantom-shares drain)",
    "note":"awarded reentrancy trigger (ETH refund before settlement) lives in untraced sibling PanopticPool._liquidate"},
   {"id":"H-03","traced":"CollateralTracker.settleBurn","outcome":"UNCHANGED_MISS",
    "feature":None,"reason":"specific-mechanism miss: blind found emit-mislog + split-sum, not the awarded realizedPremium==0 commission-skip"},
   {"id":"M-02","traced":"RiskEngine._getRequiredCollateralAtTickSinglePosition","outcome":"SELECTED",
    "feature":"mechanism-inventory: credits-overwritten-not-accumulated selected #1 (exact match)"},
   {"id":"M-03","traced":"RiskEngine.twapEMA","outcome":"UNCHANGED_MISS",
    "feature":None,"reason":"specific-mechanism miss: blind found int24 overflow + truncation, not the awarded wrong-order destructuring of getEMAs"},
 ],
 "ark": [
   {"id":"AK-M2","traced":"Bridge.withdrawTokens","outcome":"UNCHANGED_MISS",
    "feature":None,"reason":"specific-mechanism miss: blind found replay/ownerL1/gas-DoS, not the awarded non-onERC721Received recipient -> stuck NFT"},
 ],
}
SELECTION_RULE = ("Per corpus: from DEEP_RUN_BUT_MISSED take <=4, High->Medium, function-level locus first. "
                  "Pre-registered before any blind output was scored.")

def main():
    breakdown={}; agg={"SELECTED":0,"HARNESS_ESCALATED":0,"ENUMERATED_ONLY":0,"UNCHANGED_MISS":0,"FALSE_CARRY":0}
    arch_improved=0; replay_rows=[]
    for corpus in CORPORA:
        n_miss, drm = deep_run_misses(corpus)
        sample=SCORES[corpus]
        c_counts={"SELECTED":0,"HARNESS_ESCALATED":0,"ENUMERATED_ONLY":0,"UNCHANGED_MISS":0,"FALSE_CARRY":0}
        for s in sample:
            c_counts[s["outcome"]]+=1; agg[s["outcome"]]+=1
            replay_rows.append({"corpus":corpus, **s})
        improved = c_counts["SELECTED"]>0
        if improved: arch_improved+=1
        breakdown[corpus]={"total_misses":n_miss,"deep_run_misses":len(drm),
                           "deep_run_miss_ids":[d["id"] for d in drm],"sampled":len(sample),
                           "counts":c_counts,"architecture_improved(>=1 SELECTED)":improved}
    N=sum(agg.values())
    selected=agg["SELECTED"]; harness=agg["HARNESS_ESCALATED"]; enum=agg["ENUMERATED_ONLY"]
    metrics={
      "phase":"P189","read_only":True,"blind_model":"sonnet (different from campaign Opus)",
      "architecture_count":len(CORPORA),"architectures_improved(>=1 SELECTED)":arch_improved,
      "sample_size":N,
      "selection_rate_before":"0% (denominator = misses; original pipeline selected none by construction)",
      "selection_rate_after_strict(SELECTED/N)":round(100*selected/N,1),
      "surfaced_rate(SELECTED+HARNESS/N)":round(100*(selected+harness)/N,1),
      "appeared_any(SELECTED+HARNESS+ENUMERATED/N)":round(100*(selected+harness+enum)/N,1),
      "selection_gain":round(100*selected/N,1),
      "false_carry_rate":round(100*agg["FALSE_CARRY"]/N,1),
      "aggregate_counts":agg,
      "quantamm_control":"P184/P186 = 7/9 selected (reused, not re-run); excluded from headline per spec",
      "decision":"PROMOTE_CONFIDENCE",
      "decision_basis":("Selection improvement (>=1 SELECTED) appears in 3 of 4 measured architectures "
        "(zaros, revert-lend, panoptic) spanning perps/lending/options — architecturally distinct from "
        "quantamm's Balancer hooks; false_carry=0. Gains are NOT concentrated in quantamm-like systems. "
        "Caveats: modest absolute selection rate; a meaningful fraction is HARNESS_BOUND (2/13 NEEDS_HARNESS); "
        "2 zaros items were sibling-traced (locus-routing limitation, not adjudication); blind outputs carry "
        "high mechanism volume (precision watch, though 0 clearly-unsupported carries)."),
      "dominant_remaining_failure_mode":("Two-layered: (1) UPSTREAM coverage/locus-routing — at corpus level only "
        "~40-60% of misses were ever deep-run (rest never traced = discovery gap), and within the sample 2 items "
        "traced the wrong sibling of a multi-function locus; (2) specific-mechanism miss — on correctly-traced "
        "functions the deep-trace enumerates plausible mechanisms but not the exact subtle awarded one "
        "(panoptic H-03 zero-premium skip, M-03 wrong destructure order, ark non-receiver revert). "
        "Adjudication is no longer the sole bottleneck; coverage + specific-mechanism recall now dominate."),
      "selection_rule":SELECTION_RULE,
    }
    (PD/"replay_results.json").write_text(json.dumps(
        {"phase":"P189","selection_rule":SELECTION_RULE,"rows":replay_rows},indent=2)+"\n")
    (PD/"corpus_breakdown.json").write_text(json.dumps(breakdown,indent=2)+"\n")
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps({"breakdown":breakdown,"metrics":{k:metrics[k] for k in
        ("architectures_improved(>=1 SELECTED)","selection_rate_after_strict(SELECTED/N)",
         "surfaced_rate(SELECTED+HARNESS/N)","false_carry_rate","aggregate_counts","decision")}},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
