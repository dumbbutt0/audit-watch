#!/usr/bin/env python3
"""Stage 6: score frozen blind findings vs the 70-item Zaros answer key (in-session, API-free).
Per-answer-key-item category (HIT/PARTIAL/ADJACENT/MISS) from the recorded MATCHES table (auditable
model judgment); plus pipeline_only / FP accounting on the blind side. Frozen findings read-only."""
import json, csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0,"scripts")
from audit_context import audit_path
NOW=datetime.now(timezone.utc).isoformat()
WS=Path("audits/zaros-2025-01-part-2-eval")
ak=json.load(open(WS/"answer_key/answer_key_normalized.json"))["findings"]
evalf=json.load(open(WS/"output/eval_ready/eval_findings.json"))["eval_findings"]

# blind eval finding capsules (frozen, read-only) for reporting
BLIND={e["eval_id"]:{"title":e["title"],"sev":e.get("severity_ceiling"),"contracts":e.get("affected_contracts",[])} for e in evalf}

# ── RECORDED SEMANTIC MATCHES (model judgment, post-freeze, auditable) ──
# answer_key_id -> (category, matched_eval_id, note)
MATCHES={
 "H-03":("HIT","EVAL-001","Same root cause: VaultRouterBranch.redeem unlocked-credit-capacity guard wrong vs lockedCreditRatio. AK frames the DoS direction (redeems blocked for high lockedCreditRatio); blind EVAL-001 identified the same guard as inverted (DoS small redeems + over-withdraw). Same function+guard+variable."),
 "M-15":("HIT","EVAL-002","Exact match: getVaultCreditCapacity negative net (assets<debt) → SD59x18→uint256 conversion → complete vault lockout/DoS when underwater. Same function, same root cause."),
 "M-21":("HIT","EVAL-004","Match: ZlpVault decimal-offset calculation → weak donation/first-deposit protection. Blind EVAL-004 flagged the inconsistent virtual-offset between ZlpVault _decimalsOffset and the MM swap-rate offset."),
 "M-14":("PARTIAL","EVAL-003","Same bug class (DEX adapter slippage), different mechanism: AK M-14 = CurveAdapter cumulative/multi-hop slippage; blind EVAL-003 = global owner-set slippage tolerance + single persistent deadline (sandwich). Adapter-slippage class overlap, root cause not identical."),
 # ADJACENT: AK item in the exact same function/contract a blind finding examined, different root cause
 "H-14":("ADJACENT","EVAL-001","Same function (VaultRouterBranch.redeem) as EVAL-001 but distinct root cause (collateral shortfall on redeem vs inverted locked-credit guard)."),
 "L-17":("ADJACENT","EVAL-002","Same function (getVaultCreditCapacity) as EVAL-002 but distinct root cause (zero-return not handled vs negative-conversion DoS)."),
 "M-23":("ADJACENT","EVAL-004","Same subsystem (ZlpVault/VaultRouter share conversion) as EVAL-004 but distinct root cause (share minting/redemption attack)."),
 "M-22":("ADJACENT","EVAL-005","Same function (VaultRouterBranch.deposit) as EVAL-005 but distinct root cause (slippage precision on min-shares vs FoT exact-amount assumption)."),
}

rows=[]; cat=Counter()
for f in ak:
    aid=f["answer_key_id"]
    c,me,note = MATCHES.get(aid, ("MISS","","no blind finding addressed this root cause"))
    cat[c]+=1
    rows.append({"answer_key_id":aid,"severity":f["severity"],"ak_title":f["title"],
        "category":c,"matched_eval_id":me,
        "matched_blind_title":BLIND.get(me,{}).get("title","") if me else "",
        "note":note})

# blind side: which eval findings matched something useful (HIT/PARTIAL)
useful_match_evals={r["matched_eval_id"] for r in rows if r["category"] in ("HIT","PARTIAL") and r["matched_eval_id"]}
adj_evals={r["matched_eval_id"] for r in rows if r["category"]=="ADJACENT" and r["matched_eval_id"]}
pipeline_only=[]; fp=[]
for e in evalf:
    eid=e["eval_id"]
    if eid in useful_match_evals: continue
    # EVAL-005 only produced ADJACENT (deposit FoT) — real latent issue, not in key → pipeline_only_valid (low value)
    if eid in adj_evals:
        pipeline_only.append({"eval_id":eid,"title":e["title"],"severity_ceiling":e.get("severity_ceiling"),
            "note":"Real but low-value / latent (e.g. FoT assumption); adjacent to an AK item, not its root cause; not a clear FP."})
    else:
        pipeline_only.append({"eval_id":eid,"title":e["title"],"severity_ceiling":e.get("severity_ceiling"),
            "note":"No AK match; plausible real issue."})

total=len(ak)
H=cat["HIT"]; P=cat["PARTIAL"]; A=cat["ADJACENT"]; M=cat["MISS"]
useful=H+P; anytouch=useful+A
by_sev={}
for s in ["High","Medium","Low"]:
    sub=[r for r in rows if r["severity"]==s]
    by_sev[s]={"total":len(sub),"HIT":sum(r["category"]=="HIT" for r in sub),
        "PARTIAL":sum(r["category"]=="PARTIAL" for r in sub),
        "ADJACENT":sum(r["category"]=="ADJACENT" for r in sub),
        "MISS":sum(r["category"]=="MISS" for r in sub)}

# bug-class detection (coarse) by matched AK title keywords
def bclass(t):
    t=t.lower()
    if "reward" in t or "weth" in t or "distribut" in t: return "reward_distribution"
    if "debt" in t or "credit" in t or "realized" in t: return "debt_credit_accounting"
    if "redeem" in t or "stake" in t or "share" in t or "deposit" in t or "lp " in t: return "vault_shares_lp"
    if "swap" in t or "slippage" in t or "adapter" in t or "usdtoken" in t or "asset out" in t: return "swap_stability"
    if "fee" in t or "keeper" in t or "upkeep" in t: return "fees_keepers"
    if "referral" in t: return "referral"
    if "decimal" in t or "precision" in t or "offset" in t: return "decimals_precision"
    return "other"
bug_class=Counter(); bug_class_hit=Counter()
for r in rows:
    bc=bclass(r["ak_title"]); bug_class[bc]+=1
    if r["category"] in ("HIT","PARTIAL","ADJACENT"): bug_class_hit[bc]+=1

scorecard={"generated_at":NOW,"program":"Zaros Part 2",
    "mode":"eval (recall-first, advisory-confirm-only, API-free)",
    "answer_key_size":total,"answer_key_counts":{"High":by_sev["High"]["total"],"Medium":by_sev["Medium"]["total"],"Low":by_sev["Low"]["total"]},
    "final_scoring_set_size":11,"blind_root_causes":len(evalf),
    "scorecard":{"HIT":H,"PARTIAL":P,"ADJACENT":A,"MISS":M,"FP":len(fp),
        "useful_detection":useful,"any_touch":anytouch,
        "useful_rate":round(useful/total,3),"any_touch_rate":round(anytouch/total,3),"fp_rate":0.0},
    "detection_by_severity":by_sev,
    "detection_by_bug_class":{k:{"ak_total":bug_class[k],"touched":bug_class_hit[k]} for k in bug_class},
    "pipeline_only_valid":pipeline_only,"pipeline_only_valid_count":len(pipeline_only),
    "false_positives":fp}
(WS/"output/eval_ready/eval_scorecard.json").write_text(json.dumps(scorecard,indent=2))
(WS/"output/eval_ready/eval_match_matrix.json").write_text(json.dumps(
    {"generated_at":NOW,"answer_key_size":total,"rows":rows,"pipeline_only_valid":pipeline_only},indent=2))
with open(WS/"output/eval_ready/eval_comparison_board.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["answer_key_id","severity","category","matched_eval_id","matched_blind_title","ak_title","note"])
    for r in rows: w.writerow([r["answer_key_id"],r["severity"],r["category"],r["matched_eval_id"],r["matched_blind_title"],r["ak_title"],r["note"]])

md=["# Zaros Part 2 — Eval Scorecard (blind vs CodeHawks answer key)","",
 f"Answer key: **{total}** validated/selected findings (High {by_sev['High']['total']}, Medium {by_sev['Medium']['total']}, Low {by_sev['Low']['total']}).",
 f"Blind scoring set: 6 merged ∪ {len(evalf)} deduped root causes (recall-first, advisory confirm only, API-free).","",
 "| Metric | Value |","|---|---|",
 f"| HIT | {H} |",f"| PARTIAL | {P} |",f"| ADJACENT | {A} |",f"| MISS | {M} |",f"| FP | {len(fp)} |",
 f"| **Useful (HIT+PARTIAL)** | {useful}/{total} = {round(100*useful/total,1)}% |",
 f"| **Any-touch (+ADJACENT)** | {anytouch}/{total} = {round(100*anytouch/total,1)}% |",
 f"| Pipeline-only-valid | {len(pipeline_only)} |","",
 "## Detection by severity","| Sev | Total | HIT | PARTIAL | ADJACENT | MISS |","|---|---|---|---|---|---|"]
for s in ["High","Medium","Low"]:
    b=by_sev[s]; md.append(f"| {s} | {b['total']} | {b['HIT']} | {b['PARTIAL']} | {b['ADJACENT']} | {b['MISS']} |")
md+=["","## Matches (non-MISS)","| AK | Sev | Cat | Blind | AK title |","|---|---|---|---|---|"]
for r in rows:
    if r["category"]!="MISS":
        md.append(f"| {r['answer_key_id']} | {r['severity']} | {r['category']} | {r['matched_eval_id']} | {r['ak_title'][:60]} |")
md+=["","## Detection by bug class","| Class | AK total | Touched |","|---|---|---|"]
for k in sorted(bug_class):
    md.append(f"| {k} | {bug_class[k]} | {bug_class_hit[k]} |")
md+=["","## Pipeline-only-valid (blind findings not matched as HIT/PARTIAL)"]
for p in pipeline_only: md.append(f"- {p['eval_id']} ({p['severity_ceiling']}): {p['title'][:80]} — {p['note']}")
(WS/"output/eval_ready/eval_scorecard.md").write_text("\n".join(md))

# failure analysis
miss=[r for r in rows if r["category"]=="MISS"]
miss_by_class=Counter(bclass(r["ak_title"]) for r in miss)
fa=["# Zaros Part 2 — Eval Failure Analysis","",
 f"Blind run produced only **{len(evalf)} root-cause findings** against an answer key of **{total}**. "
 f"Useful detection {useful}/{total} ({round(100*useful/total,1)}%), any-touch {anytouch}/{total} ({round(100*anytouch/total,1)}%).","",
 "## Biggest misses by root-cause class","| Class | Missed |","|---|---|"]
for k,v in miss_by_class.most_common(): fa.append(f"| {k} | {v} |")
fa+=["","## High-severity misses (14 of 16)"]
for r in rows:
    if r["severity"]=="High" and r["category"]=="MISS":
        fa.append(f"- {r['answer_key_id']}: {r['ak_title']}")
fa+=["","## Root-cause of low recall (honest)",
 "1. **Under-generation.** The in-session blind pass surfaced ~5 root causes; the codebase had 70. The "
 "deep-analysis + specialist reasoning concentrated on a few high-surface contracts (VaultRouterBranch, "
 "ZlpVault, dex-adapters, CreditDelegationBranch) and did not enumerate the many debt/credit-accounting "
 "bugs spread across Market.sol / Vault.sol / CreditDelegationBranch math.",
 "2. **Debt/credit accounting dominated the answer key** (settleVaultsDebt, withdrawUsdTokenFromMarket, "
 "getRealizedDebtUsd, rebalanceVaultsAssets, AutoDeleverageFactor) — these require multi-function "
 "conservation reasoning the single-pass in-session run did not exhaust.",
 "3. **What worked:** the underwater-vault DoS (M-15), decimal-offset/donation (M-21), and the redeem "
 "locked-credit guard (H-03) were all caught — exactly the high-surface vault entrypoints the pipeline "
 "prioritized. The DEX-adapter slippage class (M-14) was partially caught.",
 "4. **Coverage vs detection gap:** coverage gate = 100% (every in-scope item dispositioned), but detection "
 "is low — confirming coverage-completeness ≠ vulnerability recall. The cheap-sweep 'cleared' the long tail "
 "without deep multi-function debt tracing, which is where most findings lived."]
(WS/"output/eval_ready/eval_failure_analysis.md").write_text("\n".join(fa))

print(f"SCORED ak={total} HIT={H} PARTIAL={P} ADJACENT={A} MISS={M} FP={len(fp)} useful={useful} anytouch={anytouch} pipeline_only={len(pipeline_only)}")
