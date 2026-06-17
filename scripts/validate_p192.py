#!/usr/bin/env python3
"""validate_p192.py — READ-ONLY locus-resolution validation + deep-pass selection-consistency audit (P192).

Question A: run a deterministic resolution ladder (Tier 0 exact -> 1 normalized -> 2 contract-constrained fuzzy ->
3 artifact-supported alias -> 4 UNRESOLVABLE) over every unresolved awarded finding, and measure how much of
P190's "discovery" bucket resolves to a real manifest function (i.e. was measurement noise, not coverage gap).
Question B: test whether deep-pass execution follows the queue scores it computes (kind=function only), and
attribute the P191 priority-starvation cases. No model runs; every recovered match cites an artifact; unknown=UNKNOWN.
"""
from __future__ import annotations
import json, re, difflib
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
PD = ROOT / "documentation/research/assisted_mode/p192_resolution_and_selection_audit"
P190 = ROOT / "documentation/research/assisted_mode/p190_upstream_routing_analysis"
P191 = ROOT / "documentation/research/assisted_mode/p191_routing_forensics"

CDIR = {"zaros":"zaros-2025-01-part-2-eval","revert-lend":"revert-lend-2024-03-strict-eval",
        "panoptic":"panoptic-2025-12-strict-eval","ark":"ark-project-2024-07-strict-eval"}
AKP = {"zaros":"answer_key/answer_key_normalized.json",
       "revert-lend":"output/eval_ready/answer_key_normalization.json",
       "panoptic":"output/eval_ready/answer_key_normalization.json",
       "ark":"output/answer_key/answer_key.json"}

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
def contracts_of(f):
    s=set()
    for x in (f.get("affected_contracts") or []): s.add(re.sub(r"\.sol$","",str(x)).lower())
    for fld in ("affected","location"):
        v=f.get(fld)
        if isinstance(v,str):
            for m in re.findall(r"\b([A-Z][A-Za-z0-9_]{2,})\b",v): s.add(m.lower())
    return {c for c in s if c}

_SCALE=re.compile(r"(x18|x96|x32|x128|usdx?18?|wad|e18)$")
_BOILER={"get","set","the","is","of","to","for","and","fn","function","value","amount","calc","calculate"}
def norm(n):
    t=re.sub(r"[^a-z0-9]","",str(n).lower())
    t=_SCALE.sub("",t)
    return t
def norm_tokens(n):
    parts=re.findall(r"[a-z]+|[0-9]+",re.sub(r"([A-Z])",r" \1",str(n)).lower())
    return [p for p in parts if p not in _BOILER and len(p)>1]

class Corpus:
    def __init__(self,name):
        cd=CDIR[name]; self.name=name
        man=load(ROOT/"audits"/cd/"output/coverage_manifest.json")
        self.items=(man or {}).get("items",[]) if isinstance(man,dict) else (man or [])
        self.fns=[it for it in self.items if it.get("kind")=="function"]
        self.by_contract={}
        for it in self.fns: self.by_contract.setdefault(str(it.get("contract") or "").lower(),{})[it.get("name")]=it
        self.norm_by_contract={c:{norm(n):n for n in d} for c,d in self.by_contract.items()}
        q=load(ROOT/"audits"/cd/"output/deep_pass/candidate_queue.json")
        self.qit=q if isinstance(q,list) else (next((v for v in q.values() if isinstance(v,list)),[]) if isinstance(q,dict) else [])
        self.queue={it.get("manifest_id"):it for it in self.qit if isinstance(it,dict)}
        disp=load(ROOT/"audits"/cd/"output/coverage_dispositions.json")
        dl=disp.get("dispositions") if isinstance(disp,dict) else (disp or [])
        self.deep_mid={d.get("manifest_id") for d in (dl or []) if "deep" in str(d.get("assigned_pass") or "").lower()}
        ef=load(ROOT/"audits"/cd/"output/eval_ready/eval_findings.json") or {}
        efl=ef.get("eval_findings",[]) if isinstance(ef,dict) else []
        self.match_terms=set()
        for x in efl:
            for t in (x.get("match_terms") or []): self.match_terms.add(str(t))

# ---------- Question A: resolution ladder ----------
def resolve(c, f):
    cts=[ct for ct in contracts_of(f) if ct in c.by_contract]
    fns=funcset(f)
    if not cts:
        return {"tier":"TIER4_UNRESOLVABLE","confidence":"none","resolved_function":None,
                "artifact":"no awarded contract present in manifest"}
    # Tier 0 exact
    for ct in cts:
        for n in fns:
            if n in c.by_contract[ct]:
                return {"tier":"TIER0_EXACT","confidence":"exact","resolved_function":f"{ct}.{n}",
                        "artifact":f"manifest:{c.by_contract[ct][n].get('id')}"}
    # Tier 1 normalized
    for ct in cts:
        nb=c.norm_by_contract[ct]
        for n in fns:
            nn=norm(n)
            if len(nn)>=4 and nn in nb:
                return {"tier":"TIER1_NORMALIZED","confidence":"normalized","resolved_function":f"{ct}.{nb[nn]}",
                        "artifact":f"normalized('{n}')=='{nn}' -> manifest fn {nb[nn]}"}
    # Tier 2 contract-constrained fuzzy
    for ct in cts:
        names=list(c.by_contract[ct])
        for n in fns:
            if not (n[0].islower() or n.startswith("_")): continue
            mm=difflib.get_close_matches(n,names,n=1,cutoff=0.85)
            if mm:
                return {"tier":"TIER2_FUZZY","confidence":"candidate","resolved_function":f"{ct}.{mm[0]}",
                        "artifact":f"difflib('{n}','{mm[0]}')>=0.85 within {ct}"}
    # Tier 3 artifact-supported alias: a manifest fn name appears as a token in the finding's title/alt_titles,
    # or in eval_findings match_terms (artifact text), within an awarded contract.
    text=" ".join(str(f.get(k) or "") for k in ("title","root_cause"))+" "+" ".join(f.get("alt_titles") or [])
    text_tokens=set(re.findall(r"[A-Za-z_]\w{3,}",text)) | c.match_terms
    for ct in cts:
        for n in c.by_contract[ct]:
            if n in text_tokens:
                src = "answer_key.title/alt_titles" if n in re.findall(r"[A-Za-z_]\w{3,}",text) else "eval_findings.match_terms"
                return {"tier":"TIER3_ALIAS","confidence":"alias","resolved_function":f"{ct}.{n}",
                        "artifact":f"manifest fn '{n}' present in {src}"}
    return {"tier":"TIER4_UNRESOLVABLE","confidence":"none","resolved_function":None,
            "artifact":"no exact/normalized/fuzzy/alias match in resolved contract(s)"}

# ---------- Question B: selection consistency ----------
def selection_consistency(c):
    # function-level queued items with score + deep-run status
    rows=[]
    for it in c.qit:
        mid=it.get("manifest_id")
        if not str(mid).startswith("function:"): continue
        rows.append({"mid":mid,"function":it.get("function"),"score":it.get("score") or 0,
                     "selected_by":it.get("selected_by"),"deep_run":mid in c.deep_mid})
    n_deep=sum(1 for r in rows if r["deep_run"])
    if n_deep==0:
        return {"status":"UNKNOWN_no_deep_pass_executed","queued_functions":len(rows),"deep_run":0,
                "inversions":[]}
    deep_scores=[r["score"] for r in rows if r["deep_run"]]
    skip_scores=[r["score"] for r in rows if not r["deep_run"]]
    consistent = (not skip_scores) or (min(deep_scores) >= max(skip_scores))
    inversions=[]
    if not consistent:
        max_skip=max(skip_scores)
        skipped_high=[r for r in rows if not r["deep_run"] and r["score"]==max_skip]
        run_low=[r for r in rows if r["deep_run"] and r["score"]<max_skip]
        for s in skipped_high[:5]:
            for rl in run_low[:3]:
                inversions.append({"skipped_higher":{"fn":s["function"],"score":s["score"],"selected_by":s["selected_by"]},
                                   "deep_run_lower":{"fn":rl["function"],"score":rl["score"],"selected_by":rl["selected_by"]}})
    return {"status":"CONSISTENT" if consistent else "INCONSISTENT","queued_functions":len(rows),
            "deep_run":n_deep,"skipped":len(rows)-n_deep,
            "deep_score_range":[min(deep_scores),max(deep_scores)],
            "skipped_score_range":[min(skip_scores),max(skip_scores)] if skip_scores else None,
            "inversions":inversions[:8]}

def starvation_attribution(corp):
    starv=load(P191/"starvation_analysis.json")["rows"]
    out=[]
    for s in starv:
        corpus=s["corpus"]; c=corp[corpus]
        aw_score=s.get("awarded_queue_score") or 0
        # deep-run queued functions with score <= awarded (heuristic override) vs > awarded (score justified)
        deep_fns=[(it.get("function"),it.get("score") or 0,it.get("selected_by"))
                  for it in c.qit if it.get("manifest_id") in c.deep_mid and str(it.get("manifest_id")).startswith("function:")]
        lower_or_equal_deep=[d for d in deep_fns if d[1]<=aw_score]
        higher_deep=[d for d in deep_fns if d[1]>aw_score]
        if lower_or_equal_deep:
            attr="routing_heuristic_overrode_score"  # a <=-scored fn was deep-run while awarded (queued) was skipped
            ev={"awarded_score":aw_score,"example_lower_or_equal_deep_run":lower_or_equal_deep[:3]}
        elif higher_deep and not lower_or_equal_deep:
            attr="score_justified_selection"; ev={"awarded_score":aw_score,"all_deep_run_outscore_awarded":True}
        else:
            attr="unknown"; ev={"awarded_score":aw_score}
        out.append({"corpus":corpus,"id":s["id"],"awarded_rank":s.get("awarded_rank"),
                    "selection_ignores_score":s.get("selection_ignores_score(skip_within_topN)"),
                    "attribution":attr,"evidence":ev})
    return out

def main():
    PD.mkdir(parents=True,exist_ok=True)
    corp={n:Corpus(n) for n in CDIR}
    ak={n:{ (x.get("answer_key_id") or x.get("ak_id")):x for x in
            ((load(ROOT/"audits"/CDIR[n]/AKP[n]) or {}).get("findings")
             or (load(ROOT/"audits"/CDIR[n]/AKP[n]) or {}).get("families") or []) } for n in CDIR}
    funnel=load(P190/"loss_funnel.json")["rows"]
    # ---- Question A ----
    audit=[]
    for r in funnel:
        if r["corpus"] not in corp: continue
        f=ak[r["corpus"]].get(r["id"]) or {}
        res=resolve(corp[r["corpus"]], f)
        audit.append({"corpus":r["corpus"],"id":r["id"],"p190_label":r["label"],
                      "p190_stageA":r["evidence"].get("stageA"),**res})
    (PD/"locus_resolution_audit.json").write_text(json.dumps({"phase":"P192","rows":audit},indent=2)+"\n")
    # ---- Question B ----
    sel={n:selection_consistency(corp[n]) for n in CDIR}
    starv=starvation_attribution(corp)
    (PD/"selection_consistency.json").write_text(json.dumps({"phase":"P192","per_corpus":sel,
        "starvation_attribution":starv},indent=2)+"\n")
    # ---- metrics ----
    from collections import Counter
    disc=[a for a in audit if a["p190_label"]=="DISCOVERY_GAP"]
    tier_all=Counter(a["tier"] for a in audit)
    tier_disc=Counter(a["tier"] for a in disc)
    resolved_disc=sum(1 for a in disc if a["tier"]!="TIER4_UNRESOLVABLE")
    pct=lambda x,d: round(100*x/d,1) if d else 0
    incons=[n for n in CDIR if sel[n]["status"]=="INCONSISTENT"]
    cons=[n for n in CDIR if sel[n]["status"]=="CONSISTENT"]
    nodeep=[n for n in CDIR if sel[n]["status"].startswith("UNKNOWN")]
    starv_attr=Counter(s["attribution"] for s in starv)
    # decision
    discovery_noise_share=pct(resolved_disc,len(disc))
    decision=("MEASUREMENT_NOISE_PRIMARY" if discovery_noise_share>=50 else
              "ROUTING_HEURISTIC_PRIMARY" if starv_attr.get("routing_heuristic_overrode_score",0)>=len(starv)*0.6 and incons else
              "QUEUE_IMPLEMENTATION_PRIMARY" if incons and not cons else
              "MIXED_INFRASTRUCTURE_FAILURE")
    metrics={"phase":"P192","read_only":True,
      "questionA_resolution":{
        "discovery_bucket_before":len(disc),
        "discovery_resolved_to_real_function":resolved_disc,
        "discovery_bucket_after_unresolvable":len(disc)-resolved_disc,
        "resolution_recovery_rate_pct":pct(resolved_disc,len(disc)),
        "tier_histogram_discovery":dict(tier_disc),
        "tier_histogram_all_unresolved":dict(tier_all),
        "high_confidence_recovery(tier0_1)":sum(tier_disc.get(t,0) for t in ("TIER0_EXACT","TIER1_NORMALIZED")),
        "candidate_recovery(tier2_3)":sum(tier_disc.get(t,0) for t in ("TIER2_FUZZY","TIER3_ALIAS"))},
      "questionB_selection":{
        "consistent_corpora":cons,"inconsistent_corpora":incons,"no_deep_pass":nodeep,
        "rank_consistency_summary":{n:sel[n]["status"] for n in CDIR},
        "starvation_attribution":dict(starv_attr)},
      "decision":decision,
      "caveats":["Tier2 fuzzy + Tier3 alias = candidate resolutions (artifact-cited, not human-confirmed); reported apart from exact/normalized",
                 "'resolved' = awarded fn locatable in manifest -> downgrades discovery loss to measurement noise; does NOT prove the pipeline would have caught the bug",
                 "Question B genuine only for revert-lend/panoptic; zaros/ark ran no deep pass (UNKNOWN)",
                 "n small -> directional"]}
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps({"questionA":metrics["questionA_resolution"],"questionB":metrics["questionB_selection"],
                      "decision":decision},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
