#!/usr/bin/env python3
"""
score_eval.py (QuantAMM eval, workspace-local — Zaros pattern).
Scores the FROZEN blind scoring set against the normalized CodeHawks answer key.
Deterministic given the hand-authored MATCHES table (model judgment, recorded here for audit).
Writes: normalized_answer_key.json, answer_key.md, scorecard.json/.md, match_matrix.json,
comparison_board.csv, failure_analysis.md.
"""
import json, csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from audit_context import audit_path  # noqa

OUT = audit_path("output")
EVR = OUT / "eval_ready"
AK = OUT / "answer_key"
AK.mkdir(parents=True, exist_ok=True)

# ---- Normalized answer key: distinct report root causes (report totals: 11 High / 19 Medium / 14 Low = 44) ----
# Severity is the CodeHawks report severity. Deduped from ~120 selected+validated submission rows.
ANSWER_KEY = [
 # HIGH (11)
 ("H-01","High","Users can bypass the uplift withdrawal fee by transferring the LP NFT (cost basis reset on transfer)","UpliftOnlyExample.afterUpdate/LPNFT._update"),
 ("H-02","High","Precision loss in onAfterSwap admin-fee calculation (hookFee/(1e18/take)) → wrong admin fee","UpliftOnlyExample.onAfterSwap"),
 ("H-03","High","Missing/improper fee application in swap logic","UpliftOnlyExample.onAfterSwap"),
 ("H-04","High","Missing update of lastUpdateIntervalTime → stale weight interpolation","QuantAMMWeightedPool/UpdateWeightRunner"),
 ("H-05","High","No withdrawal mechanism for accumulated swap fees (owner fees stuck / wrong recipient)","UpliftOnlyExample"),
 ("H-06","High","onAfterRemoveLiquidity admin-fee/underflow miscalculation locks user funds / DoS withdrawals","UpliftOnlyExample.onAfterRemoveLiquidity"),
 ("H-07","High","Unauthorized access / malicious deletion of users' deposited liquidity in onAfterRemoveLiquidity","UpliftOnlyExample.onAfterRemoveLiquidity"),
 ("H-08","High","Unrestricted rule setting allows unauthorized weight manipulation","UpdateWeightRunner.setRuleForPool"),
 ("H-09","High","Integer overflow in QuantAMMMathGuard weight calculations","QuantammMathGuard"),
 ("H-10","High","Weight normalization process violates epsilon guard-rail limits","QuantammMathGuard._normalizeWeightUpdates"),
 ("H-11","High","Incorrect implementation of exponentially-weighted covariance estimation","QuantammCovarianceBasedRule"),
 # MEDIUM (19)
 ("M-01","Medium","Both swap fee and uplift fee share one storage variable → fees overwritten / mis-collected","UpdateWeightRunner.setQuantAMMUpliftFeeTake"),
 ("M-02","Medium","localData.lpTokenDepositValueChange logic underflow in uplift fee calc","UpliftOnlyExample.onAfterRemoveLiquidity"),
 ("M-03","Medium","poolsFeeData[_to] length not checked in afterUpdate (transfer past 100-deposit cap)","UpliftOnlyExample.afterUpdate"),
 ("M-04","Medium","DoS in setWeights due to length-check mismatch","QuantAMMWeightedPool.setWeights"),
 ("M-05","Medium","Withdrawing and depositing allows avoiding uplift fees","UpliftOnlyExample"),
 ("M-06","Medium","Unhandled Chainlink revert locks all price-oracle access","UpdateWeightRunner._getData/ChainlinkOracle"),
 ("M-07","Medium","Precision loss in quantAMMPack32Array due to integer division","QuantAMMStorage.quantAMMPack32Array"),
 ("M-08","Medium","maxTradeSizeRatio can be bypassed due to incorrect logic","QuantAMMWeightedPool.onSwap"),
 ("M-09","Medium","After init, updateWeightRunner can bypass minWeight; setWeights lacks boundary/normalization check","QuantAMMWeightedPool.setWeights"),
 ("M-10","Medium","Attacker can permanently DoS a victim from managing LP NFTs (malicious transfer)","UpliftOnlyExample.afterUpdate"),
 ("M-11","Medium","Missing initialize function in UpliftOnlyExample hook/router","UpliftOnlyExample"),
 ("M-12","Medium","computeBalance may revert because setWeights doesn't check boundary","QuantAMMWeightedPool.computeBalance"),
 ("M-13","Medium","Insufficient initialization check in _setInitialWeights","QuantAMMWeightedPool._setInitialWeights"),
 ("M-14","Medium","Missing updateInterval check in setWeights → spam weight updates","QuantAMMWeightedPool.setWeights"),
 ("M-15","Medium","Recovery mode bypasses hooks → NFT burning not happening","UpliftOnlyExample"),
 ("M-16","Medium","feePerLP rounding lets users pay only the minimum / less withdraw fee","UpliftOnlyExample.onAfterRemoveLiquidity"),
 ("M-17","Medium","feePerLP can exceed 100%","UpliftOnlyExample.onAfterRemoveLiquidity"),
 ("M-18","Medium","Attacker can bypass the 100-deposit limit to DoS any user","UpliftOnlyExample"),
 ("M-19","Medium","Potential staleness vulnerability in QuantAMMWeightedPool","QuantAMMWeightedPool"),
 # LOW (14)
 ("L-01","Low","blockTimestampDeposit assigned block.number instead of block.timestamp / wrong type","UpliftOnlyExample.afterUpdate"),
 ("L-02","Low","Precision loss in MultiHopOracle._getData","MultiHopOracle._getData"),
 ("L-03","Low","Lack of normalized-sum validation in setWeights / setWeightsManually","UpdateWeightRunner/QuantAMMWeightedPool"),
 ("L-04","Low","Unauthorized/permissionless pool update (anyone can trigger performUpdate)","UpdateWeightRunner.performUpdate"),
 ("L-05","Low","_getData may revert for fresh data / conflicting primary-backup oracle querying","UpdateWeightRunner._getData"),
 ("L-06","Low","Negative pool weights possible in QuantAMMMathGuard","QuantammMathGuard._clampWeights"),
 ("L-07","Low","Chainlink staleness / L2 sequencer / deviation checks missing","ChainlinkOracle"),
 ("L-08","Low","Oracle config validation: no dup check / no validation / fee setter input validation","UpdateWeightRunner"),
 ("L-09","Low","Single-asset pool DoS / gradient explosion / negative variance in rule math","rules/*"),
 ("L-10","Low","nftPool[tokenId] not deleted on burn","UpliftOnlyExample"),
 ("L-11","Low","100-deposit limit off-by-one / bypass / DoS","UpliftOnlyExample.addLiquidityProportional"),
 ("L-12","Low","Zero oracle staleness threshold / updateInterval=0 / future timestamp → DoS","UpdateWeightRunner/QuantAMMWeightedPool"),
 ("L-13","Low","Pack/unpack array underflow / int128 cast precision loss in pool init","QuantAMMStorage"),
 ("L-14","Low","Hardcoded pool version / oracle staleness in ChainlinkOracle / misc input validation","QuantAMMWeightedPoolFactory/ChainlinkOracle"),
]

# ---- MATCHES: blind eval finding -> (category, answer_key_id, note). Hand-derived model judgment. ----
# Categories: HIT (same root cause+impact) | PARTIAL (same area/family, misses mechanics/severity)
#             | ADJACENT (same region, not the AK root cause) | (default MISS for AK items not matched)
MATCHES = {
 "EVAL-001": ("HIT","H-01","DT-001 = the uplift-fee bypass via LP-NFT transfer resetting lpTokenDepositValue. Exact root cause + impact; severity High matches."),
 "EVAL-003": ("HIT","M-01","DT-002 = swap/uplift fee share one storage var. Exact match (two AK submissions describe this); severity Medium matches."),
 "EVAL-002": ("HIT","L-03","AC-001 = missing normalized-sum validation on the weight-setting path (setWeightsManually). Matches AK 'Lack of Normalized Sum Validation in setWeights' (Low)."),
 "EVAL-004": ("PARTIAL","H-06","DT-003 = unsigned-index loop underflow in onAfterRemoveLiquidity → revert/lock. Same function + DoS/lock impact family as AK H-06/M-02; exact underflow site may differ (loop index vs value-change). Severity under-called (AK High)."),
 "EVAL-007": ("PARTIAL","H-02","DT-005 = onAfterSwap admin-fee division precision (hookFee/(1e18/take)). Same root cause/line as AK H-02, but I rated it Low with under-collection impact whereas AK is High overcharge — missed true impact/severity."),
 "EVAL-005": ("PARTIAL","L-05","DT-004 = stale primary oracle used when no backup. Same _getData oracle-staleness family as AK L-05/M-06; my specific single-oracle mechanic is within the family but not the exact AK item."),
 "EVAL-008": ("PARTIAL","L-04","EA-002 = permissionless performUpdate. Same root cause as AK L-04 'any user can trigger performUpdate'; I framed it as bounded MEV (Low) rather than the unauthorized-trigger framing."),
 "EVAL-006": ("ADJACENT","M-16","AR-002 = getPoolLPTokenValue double-scales price. Touches the LP-value/fee-rounding region (near AK M-16 feePerLP rounding) but is not that root cause; closest AK is the fee-rounding family. Likely pipeline-only/benign (scaling cancels in ratio)."),
}

# load frozen blind scoring set
scoring = json.loads((EVR / "final_scoring_set.json").read_text())["findings"]
blind = {r["eval_id"]: r for r in scoring}

# write normalized answer key
ak_rows = [{"answer_key_id": i, "severity": s, "title": t, "affected": a} for (i,s,t,a) in ANSWER_KEY]
(AK / "normalized_answer_key.json").write_text(json.dumps(
    {"program":"QuantAMM","report_totals":{"High":11,"Medium":19,"Low":14,"total":44},
     "distinct_findings":ak_rows,"count":len(ak_rows)}, indent=2))
md=["# QuantAMM — normalized answer key (distinct report findings)","",
    f"Report totals: 11 High / 19 Medium / 14 Low = 44 distinct. Deduped list below ({len(ak_rows)}).","",
    "| ID | Sev | Title | Affected |","|---|---|---|---|"]
for r in ak_rows: md.append(f"| {r['answer_key_id']} | {r['severity']} | {r['title']} | {r['affected']} |")
(AK / "answer_key.md").write_text("\n".join(md)+"\n")

# build match matrix (one row per AK finding)
matched_ak = {ak:(blind_id,cat,note) for blind_id,(cat,ak,note) in MATCHES.items()}
rows=[]
for (i,s,t,a) in ANSWER_KEY:
    if i in matched_ak:
        bid,cat,note = matched_ak[i]
        rows.append({"answer_key_id":i,"severity":s,"ak_title":t,"category":cat,
                     "matched_eval_id":bid,"matched_blind_title":blind.get(bid,{}).get("title",""),
                     "matched_blind_severity":blind.get(bid,{}).get("severity",""),"note":note})
    else:
        rows.append({"answer_key_id":i,"severity":s,"ak_title":t,"category":"MISS",
                     "matched_eval_id":"","matched_blind_title":"","matched_blind_severity":"","note":"no blind finding addressed this root cause"})

# blind findings with no AK match at all => FP (none expected); ADJACENT tracked separately
blind_categorized = {bid:cat for bid,(cat,ak,note) in MATCHES.items()}
fp=[bid for bid in blind if bid not in blind_categorized]

from collections import Counter
cat_counts = Counter(r["category"] for r in rows)
# ADJACENT/PARTIAL/HIT are attached to AK rows; also count from blind side
blind_cat = Counter(c for (c,_,_) in MATCHES.values())

scorecard = {
 "program":"QuantAMM 2024-12 CodeHawks",
 "mode":"fresh blind eval (recall-first, advisory-confirm-only, API-free, deep mode)",
 "answer_key_distinct": len(ANSWER_KEY),
 "answer_key_report_totals": {"High":11,"Medium":19,"Low":14},
 "final_scoring_set_size": len(scoring),
 "scorecard": {
    "HIT": blind_cat["HIT"], "PARTIAL": blind_cat["PARTIAL"], "ADJACENT": blind_cat["ADJACENT"],
    "MISS": cat_counts["MISS"], "FP": len(fp),
    "useful_detection": blind_cat["HIT"]+blind_cat["PARTIAL"],
    "any_touch": blind_cat["HIT"]+blind_cat["PARTIAL"]+blind_cat["ADJACENT"],
    "distinct_ak_touched": sum(1 for r in rows if r["category"] in ("HIT","PARTIAL","ADJACENT")),
    "useful_rate_vs_ak": round((blind_cat["HIT"]+blind_cat["PARTIAL"])/len(ANSWER_KEY),3),
    "any_touch_rate_vs_ak": round(sum(1 for r in rows if r["category"]!="MISS")/len(ANSWER_KEY),3),
    "fp_rate": round(len(fp)/max(1,len(scoring)),3),
 },
 "detection_by_severity": {},
 "false_positives": fp,
}
for sev in ("High","Medium","Low"):
    tot=sum(1 for r in rows if r["severity"]==sev)
    scorecard["detection_by_severity"][sev]={
        "total":tot,
        "HIT":sum(1 for r in rows if r["severity"]==sev and r["category"]=="HIT"),
        "PARTIAL":sum(1 for r in rows if r["severity"]==sev and r["category"]=="PARTIAL"),
        "ADJACENT":sum(1 for r in rows if r["severity"]==sev and r["category"]=="ADJACENT"),
        "MISS":sum(1 for r in rows if r["severity"]==sev and r["category"]=="MISS"),
    }

(EVR/"scorecard.json").write_text(json.dumps(scorecard,indent=2))
(EVR/"match_matrix.json").write_text(json.dumps({"rows":rows},indent=2))
with open(EVR/"comparison_board.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["answer_key_id","severity","category","matched_eval_id","matched_blind_severity","ak_title","note"])
    for r in rows: w.writerow([r["answer_key_id"],r["severity"],r["category"],r["matched_eval_id"],r["matched_blind_severity"],r["ak_title"],r["note"]])

sc=scorecard["scorecard"]
scmd=["# QuantAMM eval scorecard","",
 f"- Answer-key distinct findings: **{len(ANSWER_KEY)}** (report 11H/19M/14L)",
 f"- Blind final scoring set: **{len(scoring)}**","",
 f"| HIT | PARTIAL | ADJACENT | MISS | FP | useful | any-touch |","|---|---|---|---|---|---|---|",
 f"| {sc['HIT']} | {sc['PARTIAL']} | {sc['ADJACENT']} | {sc['MISS']} | {sc['FP']} | {sc['useful_detection']} | {sc['any_touch']} |","",
 f"- Distinct AK findings touched: **{sc['distinct_ak_touched']}/{len(ANSWER_KEY)}**",
 f"- useful-rate vs AK: {sc['useful_rate_vs_ak']} · any-touch-rate vs AK: {sc['any_touch_rate_vs_ak']} · FP-rate: {sc['fp_rate']}","",
 "## By severity (answer-key side)","| Sev | total | HIT | PARTIAL | ADJACENT | MISS |","|---|---|---|---|---|---|"]
for sev in ("High","Medium","Low"):
    d=scorecard["detection_by_severity"][sev]
    scmd.append(f"| {sev} | {d['total']} | {d['HIT']} | {d['PARTIAL']} | {d['ADJACENT']} | {d['MISS']} |")
scmd+=["","## Blind findings → category",""]
for bid,(cat,ak,note) in MATCHES.items():
    scmd.append(f"- **{bid}** ({blind.get(bid,{}).get('blind_finding_id','')}, {blind.get(bid,{}).get('severity','')}) → {cat} vs {ak}: {note}")
(EVR/"scorecard.md").write_text("\n".join(scmd)+"\n")

print(json.dumps(sc,indent=2))
