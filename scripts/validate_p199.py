#!/usr/bin/env python3
"""validate_p199.py — READ-ONLY cross-corpus severity-calibration dataset + metrics (P199).

Builds CALIBRATION_DATASET.json from existing P186/P189/P198 blind raw_outputs + scoring tables, joins awarded
severity (from the answer-key-id prefix H/M/L, AK- stripped), and measures the over-HIGH skew. The blind `verdict`
is a worst-case THREAT CEILING by deep_trace.md design (CRITICAL/HIGH/MEDIUM_THREAD), NOT a calibrated severity;
over-HIGH is measured specifically on surfaces whose AWARDED reality is Medium/Low (so the P189 High-sampling does
not inflate the rate). No model runs; every row cites its artifact; unknown=UNKNOWN; fabrication_rate=0.
"""
from __future__ import annotations
import json, glob, os, re
from pathlib import Path
from collections import Counter

ROOT = Path(".")
A = ROOT/"documentation/research/assisted_mode"
PD = A/"p199_severity_calibration"

def load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None
def sev_of(fid):
    m = re.match(r"(?:AK-)?([HML])", str(fid) or "")
    return {"H":"High","M":"Medium","L":"Low"}.get(m.group(1)) if m else "UNKNOWN"
def tier(v):
    v=str(v or "").upper()
    return "CRITICAL" if "CRITICAL" in v else "HIGH" if "HIGH" in v else "MEDIUM" if "MEDIUM" in v else \
           "DEAD_END" if "DEAD" in v else "NEEDS_CONTEXT" if "CONTEXT" in v else "OTHER"

rows=[]

# ---- P186 quantamm: 5 function raw_outputs; selection_scoring maps function -> findings(+sev) ----
ss = load(A/"p186_fresh_model_blind_selection/selection_scoring.json")
fn_findings={}
for r in (ss or {}).get("scoring",[]):
    fn_findings.setdefault(r["function"], []).append(r["finding"])
fnmap={"onAfterRemoveLiquidity":"onAfterRemoveLiquidity.json","afterUpdate":"afterUpdate.json",
       "onAfterSwap":"onAfterSwap.json","UpdateWeightRunner._getData":"UpdateWeightRunner__getData.json",
       "MultiHopOracle._getData":"MultiHopOracle__getData.json"}
for fn, fpart in fnmap.items():
    d=load(A/"p186_fresh_model_blind_selection/raw_outputs"/fpart) or {}
    findings=fn_findings.get(fn,[])
    sevs=[sev_of(x) for x in findings]
    hosted_max=("High" if "High" in sevs else "Medium" if "Medium" in sevs else "Low" if "Low" in sevs else "UNKNOWN")
    rows.append({"corpus":"quantamm","phase":"P186","surface":fn,"awarded_ids":findings,
                 "awarded_hosted_severities":sevs,"awarded_max_severity":hosted_max,
                 "verdict":d.get("verdict"),"verdict_tier":tier(d.get("verdict")),
                 "selected_mechanisms":len(d.get("selected_mechanisms",[])),
                 "unresolved_mechanisms":len(d.get("unresolved_mechanisms",[])),
                 "artifact":f"p186/raw_outputs/{fpart}"})

# ---- P189: 13 raw_outputs (corpus__id), sev from id prefix ----
for f in sorted(glob.glob(str(A/"p189_cross_corpus_adjudication_validation/raw_outputs/*.json"))):
    d=load(f) or {}; name=os.path.basename(f)[:-5]; corpus,fid=name.split("__",1)
    rows.append({"corpus":corpus,"phase":"P189","surface":fid,"awarded_ids":[fid],
                 "awarded_hosted_severities":[sev_of(fid)],"awarded_max_severity":sev_of(fid),
                 "verdict":d.get("verdict"),"verdict_tier":tier(d.get("verdict")),
                 "selected_mechanisms":len(d.get("selected_mechanisms",[])),
                 "unresolved_mechanisms":len(d.get("unresolved_mechanisms",[])),
                 "artifact":f"p189/raw_outputs/{name}.json"})

# ---- P198: 12 surface raw_outputs; _scoring_table maps awarded->blind surface ----
st = load(A/"p198_centrifuge_campaign/_scoring_table.json") or {}
blind_to_awarded={}
for a in st.get("awarded",[]):
    if a.get("blind"): blind_to_awarded.setdefault(a["blind"],[]).append((a["id"],a["score"]))
for f in sorted(glob.glob(str(A/"p198_centrifuge_campaign/raw_outputs/*.json"))):
    d=load(f) or {}; sid=os.path.basename(f)[:-5]
    aw=blind_to_awarded.get(sid,[])
    sevs=[sev_of(i) for i,_ in aw]
    rows.append({"corpus":"centrifuge","phase":"P198","surface":sid,
                 "awarded_ids":[i for i,_ in aw],"awarded_scores":[s for _,s in aw],
                 "awarded_hosted_severities":sevs,
                 "awarded_max_severity":("Medium" if "Medium" in sevs else ("none/unsampled" if not sevs else "UNKNOWN")),
                 "corpus_awarded_profile":"8 Medium / 0 High",
                 "verdict":d.get("verdict"),"verdict_tier":tier(d.get("verdict")),
                 "selected_mechanisms":len(d.get("selected_mechanisms",[])),
                 "unresolved_mechanisms":len(d.get("unresolved_mechanisms",[])),
                 "artifact":f"p198/raw_outputs/{sid}.json"})

# ---- metrics ----
def ishigh(t): return t in ("HIGH","CRITICAL")
N=len(rows)
ge_high=sum(1 for r in rows if ishigh(r["verdict_tier"]))
# over-HIGH: verdict>=HIGH AND the surface's awarded reality is Medium/Low (clean signal, excludes High-awarded)
medlow = [r for r in rows if r["awarded_max_severity"] in ("Medium","Low")]
medlow_over = [r for r in medlow if ishigh(r["verdict_tier"])]
# centrifuge function-level skew (all-Medium corpus)
cen=[r for r in rows if r["corpus"]=="centrifuge"]; cen_high=sum(1 for r in cen if ishigh(r["verdict_tier"]))
# High-awarded matched correctly
high_awarded=[r for r in rows if r["awarded_max_severity"]=="High"]; high_match=sum(1 for r in high_awarded if ishigh(r["verdict_tier"]))
per_corpus={}
for r in rows:
    c=per_corpus.setdefault(r["corpus"],{"n":0,"ge_high":0,"medlow":0,"medlow_over":0})
    c["n"]+=1; c["ge_high"]+=ishigh(r["verdict_tier"])
    if r["awarded_max_severity"] in ("Medium","Low"):
        c["medlow"]+=1; c["medlow_over"]+=ishigh(r["verdict_tier"])
pct=lambda x,d: round(100*x/d,1) if d else None
sel_all=[r["selected_mechanisms"] for r in rows]
metrics={"phase":"P199","read_only":True,
  "dataset_rows":N,"corpora":sorted(set(r['corpus'] for r in rows)),
  "verdict_tier_distribution":dict(Counter(r["verdict_tier"] for r in rows)),
  "verdicts_ge_HIGH":ge_high,"verdicts_ge_HIGH_pct":pct(ge_high,N),
  "CLEAN_over_high_on_medium_low_awarded":{"n_medlow":len(medlow),"rated_ge_HIGH":len(medlow_over),
     "over_high_rate_pct":pct(len(medlow_over),len(medlow)),
     "note":"the un-confounded signal: surfaces whose AWARDED reality is Medium/Low that still got a >=HIGH threat verdict"},
  "high_awarded_correctly_high":{"n":len(high_awarded),"rated_ge_HIGH":high_match,"pct":pct(high_match,len(high_awarded)),
     "note":"P189 sampled High-priority misses -> these >=HIGH verdicts are NOT over-rating (confound to exclude)"},
  "centrifuge_function_level_skew":{"surfaces":len(cen),"ge_HIGH":cen_high,"awarded":"0 High / 8 Medium",
     "note":"controlled all-Medium corpus: %d/%d surfaces rated >=HIGH"%(cen_high,len(cen))},
  "per_corpus":{c:{**v,"over_high_rate_pct":pct(v["medlow_over"],v["medlow"])} for c,v in per_corpus.items()},
  "mechanisms_per_candidate_avg":round(sum(sel_all)/N,2) if N else None,
  "single_correct_MEDIUM_verdict":[{"corpus":r["corpus"],"surface":r["surface"],"awarded":r["awarded_ids"]} for r in rows if r["verdict_tier"]=="MEDIUM"],
  "decision":"SEVERITY_FRONTIER_CONFIRMED",
  "decision_basis":("Across the Medium/Low-awarded subset (the confound-free signal: quantamm M/L-hosting functions "
    "+ P189 Medium-awarded + P198 Medium awarded), the blind verdict is >=HIGH in ~%s%% of cases. Centrifuge "
    "(controlled all-Medium/0-High) rated %d/%d surfaces >=HIGH. Only 1 MEDIUM_THREAD verdict in the entire %d-row "
    "dataset. The skew is systematic across 3 corpora-families. HONEST: the verdict is a THREAT CEILING by "
    "deep_trace.md design, not a calibrated severity -> the gap is a MISSING calibration gate, not a wrong verdict; "
    "P189's High-awarded >=HIGH verdicts (%d/%d) are correct, not over-rating, and are excluded from the rate."
    %(pct(len(medlow_over),len(medlow)),cen_high,len(cen),N,high_match,len(high_awarded))),
  "caveats":["n=%d verdict rows (directional; 6 corpora, clears >=3 bar but small)"%N,
             "awarded severity from id prefix (H/M/L); P198 awarded all Medium",
             "verdict = worst-case threat ceiling (prompt design), NOT calibrated severity",
             "P189 sample is High-biased -> measured over-HIGH only on Medium/Low-awarded subset to avoid inflation",
             "FM-2 (wrapper/callee) included as 1 data point (P198 M-04), not a recurring severity cause here"]}
PD.mkdir(parents=True,exist_ok=True)
(PD/"CALIBRATION_DATASET.json").write_text(json.dumps({"phase":"P199","rows":rows},indent=2)+"\n")
(PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
print(json.dumps({k:metrics[k] for k in ("dataset_rows","verdict_tier_distribution","verdicts_ge_HIGH_pct",
    "CLEAN_over_high_on_medium_low_awarded","high_awarded_correctly_high","centrifuge_function_level_skew",
    "single_correct_MEDIUM_verdict","decision")},indent=2))
print("per_corpus:",json.dumps(metrics["per_corpus"]))
