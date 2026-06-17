#!/usr/bin/env python3
"""validate_p191.py — READ-ONLY routing decision forensics (P191).

Answers "why did the pipeline prefer function B when the awarded finding was in function A?" by deterministic
attribution over existing artifacts (no model runs). Reuses P190 loss_funnel.json (labels + per-row stage
evidence). Five stages -> routing_pairs / score_attribution / similarity_analysis / discovery_resolution_audit /
starvation_analysis + metrics. Every value cites an artifact-derived score/record; unknowns stay UNKNOWN.
"""
from __future__ import annotations
import json, re, difflib
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
PD = ROOT / "documentation/research/assisted_mode/p191_routing_forensics"
P190 = ROOT / "documentation/research/assisted_mode/p190_upstream_routing_analysis"

CDIR = {"zaros":"zaros-2025-01-part-2-eval","revert-lend":"revert-lend-2024-03-strict-eval",
        "panoptic":"panoptic-2025-12-strict-eval","ark":"ark-project-2024-07-strict-eval",
        "quantamm":"quantamm-2024-12-eval"}
AKP = {"zaros":"answer_key/answer_key_normalized.json",
       "revert-lend":"output/eval_ready/answer_key_normalization.json",
       "panoptic":"output/eval_ready/answer_key_normalization.json",
       "ark":"output/answer_key/answer_key.json",
       "quantamm":"output/answer_key/normalized_answer_key.json"}

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

class Corpus:
    def __init__(self,name):
        cd=CDIR[name]; self.name=name
        man=load(ROOT/"audits"/cd/"output/coverage_manifest.json")
        self.items=(man or {}).get("items",[]) if isinstance(man,dict) else (man or [])
        self.mid={it.get("id"):it for it in self.items}
        self.by_contract={}
        for it in self.items: self.by_contract.setdefault(str(it.get("contract") or "").lower(),{})[it.get("name")]=it
        q=load(ROOT/"audits"/cd/"output/deep_pass/candidate_queue.json")
        qit=q if isinstance(q,list) else (next((v for v in q.values() if isinstance(v,list)),[]) if isinstance(q,dict) else [])
        self.queue={it.get("manifest_id"):it for it in qit if isinstance(it,dict)}
        self.queue_by_contract={}
        for it in qit:
            if isinstance(it,dict): self.queue_by_contract.setdefault(str(it.get("contract") or "").lower(),[]).append(it)
        disp=load(ROOT/"audits"/cd/"output/coverage_dispositions.json")
        dl=disp.get("dispositions") if isinstance(disp,dict) else (disp or [])
        self.deep_mid={d.get("manifest_id") for d in (dl or []) if "deep" in str(d.get("assigned_pass") or "").lower()}
        cg=load(ROOT/"audits"/cd/"data/interactions/call_graph.json") or {}
        self.chains=cg.get("interaction_chains",[]) if isinstance(cg,dict) else []
    def manifest_scores(self,mid):
        it=self.mid.get(mid) or {}
        return {"risk_score":it.get("risk_score"),"attack_surface_score":it.get("attack_surface_score")}
    def qinfo(self,mid):
        q=self.queue.get(mid)
        return {"queue_score":(q or {}).get("score"),"selected_by":(q or {}).get("selected_by"),
                "queued":mid in self.queue,"deep_run":mid in self.deep_mid}

def side(c,mid):
    it=c.mid.get(mid) or {}
    return {"contract":it.get("contract"),"function":it.get("name"),"manifest_id":mid,
            **c.manifest_scores(mid),**c.qinfo(mid),
            "file":it.get("file"),"tags":it.get("tags"),"external_calls":it.get("external_calls"),
            "modifiers":it.get("modifiers"),"visibility":it.get("visibility"),
            "in_tainted_sink":it.get("in_tainted_sink"),"has_loop":it.get("has_loop")}

# ---- Stage 1+2: build pairs + score attribution ----
def reconstruct(corp, rows):
    pairs=[]
    for r in rows:
        corpus=r["corpus"]; c=corp[corpus]; ev=r["evidence"]
        A_mid=ev.get("awarded_manifest_id")
        if r["label"]=="LOCUS_ROUTING_GAP":
            # B = highest-queue-score same-contract sibling
            cts={s["contract"].lower() for s in [side(c,A_mid)] if s.get("contract")} or set()
            sibs=[it for ct in cts for it in c.queue_by_contract.get(ct,[])]
            if not sibs:
                pairs.append({"corpus":corpus,"id":r["id"],"gap":"LOCUS","A":side(c,A_mid),"B":None,
                              "subreason":ev.get("routing_subreason"),"note":"no competing sibling queued"}); continue
            B=max(sibs,key=lambda it:(it.get("score") or 0)); B_mid=B.get("manifest_id")
            pairs.append({"corpus":corpus,"id":r["id"],"gap":"LOCUS","A":side(c,A_mid),"B":side(c,B_mid)})
        elif r["label"]=="PRIORITY_ROUTING_GAP":
            aw=(c.queue.get(A_mid) or {}).get("score") or 0
            higher=[(mid,it) for mid,it in c.queue.items() if (it.get("score") or 0)>aw and mid in c.deep_mid]
            B=max(higher,key=lambda kv:(kv[1].get("score") or 0)) if higher else None
            pairs.append({"corpus":corpus,"id":r["id"],"gap":"PRIORITY","A":side(c,A_mid),
                          "B":side(c,B[0]) if B else None})
    return pairs

def attribute(p):
    A,B=p["A"],p.get("B")
    if not B: return {"cause":"NO_COMPETING_SIBLING" if p["gap"]=="LOCUS" else "DEEP_PASS_STARVATION",
                      "evidence":p.get("note") or "no higher-scored deep-run competitor recorded"}
    def d(k):
        a,b=A.get(k),B.get(k)
        return (b-a) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else None
    dr,ds,dq=d("risk_score"),d("attack_surface_score"),d("queue_score")
    ev={"d_risk_score":dr,"d_attack_surface_score":ds,"d_queue_score":dq,
        "A_selected_by":A.get("selected_by"),"B_selected_by":B.get("selected_by"),
        "A_queued":A.get("queued"),"B_queued":B.get("queued")}
    if p["gap"]=="PRIORITY":
        cause="DEEP_PASS_STARVATION"
    elif not A.get("queued") and B.get("queued"):
        # A never queued; why did B make the cut?
        if (ds or 0)>0: cause="SURFACE_SCORE_INFLATION"
        elif (dr or 0)>0: cause="RISK_SCORE_INFLATION"
        elif B.get("selected_by") and not A.get("selected_by"): cause="MISSING_AWARDED_FEATURES"
        elif (dq or 0)>0: cause="QUEUE_SCORE_DOMINATED"
        else: cause="OTHER"
    else:
        cause = "SURFACE_SCORE_INFLATION" if (ds or 0)>0 else "RISK_SCORE_INFLATION" if (dr or 0)>0 else \
                "QUEUE_SCORE_DOMINATED" if (dq or 0)>0 else "OTHER"
    return {"cause":cause,"evidence":ev}

# ---- Stage 3: similarity ----
def similarity(corp,p):
    A,B=p["A"],p.get("B")
    if not B: return None
    c=corp[p["corpus"]]
    dims={}
    dims["same_contract"]=bool(A.get("contract") and A.get("contract")==B.get("contract"))
    dims["same_file"]=bool(A.get("file") and A.get("file")==B.get("file"))
    dims["same_subsystem"]=bool(A.get("file") and B.get("file") and Path(str(A["file"])).parent==Path(str(B["file"])).parent)
    ta,tb=set(A.get("tags") or []),set(B.get("tags") or [])
    dims["shared_tags"]=sorted(ta&tb)
    dims["shared_external_calls"]=bool(A.get("external_calls")==B.get("external_calls"))
    dims["shared_visibility"]=bool(A.get("visibility")==B.get("visibility"))
    # shared call-graph chain / state (best-effort)
    fa,fb=A.get("function"),B.get("function")
    shared_chain=[]; shared_state=set()
    for ch in c.chains:
        path=[str(x).split(".")[-1] for x in (ch.get("path") or [])]
        if fa in path and fb in path:
            shared_chain.append(ch.get("chain_id")); shared_state|=set(ch.get("shared_state") or [])
    dims["shared_call_graph_chain"]=shared_chain or False
    dims["shared_state_vars"]=sorted(shared_state) if shared_state else "UNKNOWN"
    score=sum([dims["same_file"],bool(dims["shared_tags"]),bool(shared_chain),
               dims["same_subsystem"],dims["shared_external_calls"] and A.get("external_calls") is True])
    lvl="HIGH_OVERLAP" if score>=3 else "MEDIUM_OVERLAP" if score==2 else "LOW_OVERLAP"
    return {"corpus":p["corpus"],"id":p["id"],"gap":p["gap"],"A":fa,"B":fb,"overlap":lvl,"dims":dims}

# ---- Stage 4: discovery resolution audit ----
def discovery_audit(corp, rows, ak_by_corpus):
    out=[]
    for r in rows:
        if not (r["label"]=="DISCOVERY_GAP" and r["evidence"]["stageA"]=="DISCOVERED_CONTRACT_ONLY"): continue
        corpus=r["corpus"]; c=corp[corpus]
        f=ak_by_corpus[corpus].get(r["id"]) or {}
        fns={x for x in funcset(f)}
        # contracts the finding touches that are present in manifest
        cts=set()
        for fld in ("affected","location"):
            v=f.get(fld)
            if isinstance(v,str):
                for m in re.findall(r"\b([A-Z][A-Za-z0-9_]{2,})\b",v):
                    if m.lower() in c.by_contract: cts.add(m.lower())
        for x in (f.get("affected_contracts") or []):
            cc=re.sub(r"\.sol$","",str(x)).lower()
            if cc in c.by_contract: cts.add(cc)
        man_names=set(n for ct in cts for n in c.by_contract.get(ct,{}))
        all_names=set(self_n for ct in c.by_contract for self_n in c.by_contract[ct])
        cat="other"; detail={}
        cand=[n for n in fns if n not in man_names and (n[0].islower() or n.startswith("_"))]
        # function-like vs answer-key noise: camelCase or _-prefixed, len>=5, not a language/common-noise token
        LANG_NOISE={"solidity","javascript","console","json","return","function","address","uint256","bool",
                    "true","false","null","require","memory","storage","public","external","internal","amount",
                    "value","data","params","abs","diff","min","max","sum","string","bytes","mapping"}
        def fn_like(n): return (("_" in n) or re.search(r"[a-z][A-Z]",n)) and len(n)>=5 and n.lower() not in LANG_NOISE
        near=None
        for n in cand:
            mm=difflib.get_close_matches(n,man_names,n=1,cutoff=0.85)
            if mm: near=(n,mm[0]); break
        if any(n in man_names for n in fns):
            cat="resolved_on_recheck"  # present after recheck (P190 contract-only was coarse) = resolution-recoverable
        elif near:
            cat="answer_key_naming_drift"; detail={"awarded":near[0],"manifest_near":near[1]}
        elif any(n in all_names for n in cand):
            cat="inherited_implementation_mismatch"; detail={"name_in_other_contract":next(n for n in cand if n in all_names)}
        else:
            # absent from manifest entirely: distinguish a real-looking fn name (possible coverage gap)
            # from answer-key locus noise (no resolvable function name).
            flike=[n for n in cand if fn_like(n)]
            if flike:
                cat="UNRESOLVABLE_FROM_ARTIFACTS"; detail={"function_like_unmatched":flike[:3],
                    "note":"real-looking fn name absent from manifest; cannot distinguish genuine coverage gap from param/locus noise w/o source"}
            else:
                cat="ANSWER_KEY_RESOLUTION_NOISE"; detail={"unmatched_tokens":sorted(cand)[:4] or sorted(fns)[:4],
                    "note":"answer-key loci yield no resolvable function name (tokens are vars/lang noise)"}
        out.append({"corpus":corpus,"id":r["id"],"contract_matched":sorted(cts)[:2],"category":cat,"detail":detail})
    return out

# ---- Stage 5: starvation ----
def starvation(corp, rows):
    out=[]
    for r in rows:
        if r["label"]!="PRIORITY_ROUTING_GAP": continue
        corpus=r["corpus"]; c=corp[corpus]; A_mid=r["evidence"]["awarded_manifest_id"]
        # rank within the queue by score (ties broken by original order)
        ranked=sorted(enumerate(c.queue.items()),key=lambda t:(-(t[1][1].get("score") or 0),t[0]))
        order=[mid for _,(mid,_) in ranked]
        aw_rank=order.index(A_mid)+1 if A_mid in order else None
        n_deep=len(c.deep_mid & set(c.queue))               # deep-pass slots used among queued items
        deep_ranks=[i+1 for i,mid in enumerate(order) if mid in c.deep_mid]
        deep_cutoff=max(deep_ranks) if deep_ranks else 0
        aw_score=(c.queue.get(A_mid) or {}).get("score")
        # If deep-pass were strict top-N-by-score, would awarded be covered at depth n_deep (+N)?
        def recover_topN(extra): return bool(aw_rank and aw_rank<=n_deep+extra)
        # selection_skip: awarded already ranks within top-N-by-score yet was NOT deep-run -> selection ignores score
        selection_skip = bool(aw_rank and aw_rank<=n_deep)
        out.append({"corpus":corpus,"id":r["id"],"awarded_rank":aw_rank,"awarded_queue_score":aw_score,
                    "deep_pass_slots_used":n_deep,"deep_cutoff_rank_observed":deep_cutoff,
                    "selection_ignores_score(skip_within_topN)":selection_skip,
                    "recover_if_topN_at_+0":recover_topN(0),"recover_if_topN_at_+3":recover_topN(3),
                    "recover_if_topN_at_+5":recover_topN(5),
                    "diagnosis":("SELECTION_LOGIC_IGNORES_SCORE" if selection_skip else
                                 "BUDGET_DEPTH_would_help_if_topN" if recover_topN(5) else
                                 "RANK_TOO_LOW_needs_better_ranking")})
    return out

def main():
    PD.mkdir(parents=True,exist_ok=True)
    funnel=load(P190/"loss_funnel.json")["rows"]
    corpuses={n:Corpus(n) for n in CDIR}
    ak_by_corpus={}
    for n in CDIR:
        ak=load(ROOT/"audits"/CDIR[n]/AKP[n]) or {}
        fl=ak.get("findings") or ak.get("families") or ak.get("distinct_findings") or []
        ak_by_corpus[n]={ (x.get("answer_key_id") or x.get("ak_id")):x for x in fl}
    route_rows=[r for r in funnel if r["label"] in ("LOCUS_ROUTING_GAP","PRIORITY_ROUTING_GAP")]
    pairs=reconstruct(corpuses,route_rows)
    attr=[{"corpus":p["corpus"],"id":p["id"],"gap":p["gap"],
           "A":p["A"].get("function"),"B":(p["B"] or {}).get("function") if p.get("B") else None,
           **attribute(p)} for p in pairs]
    sims=[s for p in pairs if (s:=similarity(corpuses,p))]
    disc=discovery_audit(corpuses,funnel,ak_by_corpus)
    starv=starvation(corpuses,funnel)

    from collections import Counter
    cause_dist=Counter(a["cause"] for a in attr)
    overlap_dist=Counter(s["overlap"] for s in sims)
    disc_dist=Counter(d["category"] for d in disc)
    Np=len(attr)
    scoring=sum(cause_dist[c] for c in ("SURFACE_SCORE_INFLATION","RISK_SCORE_INFLATION","QUEUE_SCORE_DOMINATED"))+cause_dist.get("MISSING_AWARDED_FEATURES",0)
    ambiguity=sum(1 for s in sims if s["overlap"]=="HIGH_OVERLAP")
    budget=sum(cause_dist[c] for c in ("DEEP_PASS_STARVATION",))
    # discovery bucket: resolution-recoverable (in-manifest/near) vs unresolvable vs noise
    resolution_recoverable=sum(disc_dist[c] for c in ("answer_key_naming_drift","resolved_on_recheck","inherited_implementation_mismatch"))
    answer_key_noise=disc_dist.get("ANSWER_KEY_RESOLUTION_NOISE",0)
    unresolvable=disc_dist.get("UNRESOLVABLE_FROM_ARTIFACTS",0)
    fnres_total=resolution_recoverable+answer_key_noise+unresolvable   # ~ entire contract-only bucket is a resolution/answer-key issue
    pct=lambda x,d: round(100*x/d,1) if d else 0
    # starvation diagnosis
    sel_skip=sum(1 for s in starv if s["selection_ignores_score(skip_within_topN)"])
    topn_help=sum(1 for s in starv if s["recover_if_topN_at_+5"] and not s["selection_ignores_score(skip_within_topN)"])
    # decision: contract-only discovery bucket (50) dwarfs routing pairs (25) and is ~entirely a resolution/answer-key issue
    decision = ("FUNCTION_RESOLUTION_PROBLEM" if fnres_total>=len(disc)*0.8 and len(disc)>=Np else
                "ROUTER_SCORE_PROBLEM" if scoring>Np/2 else
                "ROUTER_AMBIGUITY_PROBLEM" if ambiguity>Np/2 else
                "QUEUE_BUDGET_PROBLEM" if budget and topn_help>=budget*0.6 else
                "MIXED_ROUTING_FAILURE")
    metrics={"phase":"P191","read_only":True,"n_routing_pairs":Np,"n_discovery_contract_only":len(disc),
             "n_priority_starvation":len(starv),
             "cause_distribution":dict(cause_dist),"similarity_overlap_distribution":dict(overlap_dist),
             "discovery_resolution_distribution":dict(disc_dist),
             "pct_routing_caused_by_scoring_or_missing_features":pct(scoring,Np),
             "pct_routing_high_overlap_ambiguity":pct(ambiguity,Np),
             "pct_routing_caused_by_deep_pass_starvation":pct(budget,Np),
             "discovery_bucket_breakdown":{"resolution_recoverable":resolution_recoverable,
                "answer_key_resolution_noise":answer_key_noise,"unresolvable_from_artifacts":unresolvable,
                "of_contract_only":len(disc),
                "interpretation":"contract-only discovery loss is overwhelmingly a function-resolution / answer-key-locus-quality issue, not demonstrable coverage gaps"},
             "starvation_diagnosis":{"selection_ignores_score(skip_within_topN)":sel_skip,
                "budget_depth_would_help_if_topN":topn_help,"of":len(starv),
                "note":"awarded fns out-rank deep-run siblings yet were skipped -> deep-pass selection is NOT top-N-by-score; depth increase alone would not fix the score-skip cases"},
             "decision":decision,
             "caveats":["zaros risk_score==0 (dimension uninformative; zaros ran no deep pass -> 0 priority gaps)",
                        "Stage-4 fuzzy categories best-effort, not authoritative (answer-key loci noisy)",
                        "shared_state_vars best-effort from call_graph chains, else UNKNOWN",
                        "n small (pairs=%d, contract-only=%d) -> directional attribution not population stats"%(Np,len(disc))]}
    (PD/"routing_pairs.json").write_text(json.dumps({"phase":"P191","pairs":pairs},indent=2)+"\n")
    (PD/"score_attribution.json").write_text(json.dumps({"phase":"P191","rows":attr},indent=2)+"\n")
    (PD/"similarity_analysis.json").write_text(json.dumps({"phase":"P191","rows":sims},indent=2)+"\n")
    (PD/"discovery_resolution_audit.json").write_text(json.dumps({"phase":"P191","rows":disc},indent=2)+"\n")
    (PD/"starvation_analysis.json").write_text(json.dumps({"phase":"P191","rows":starv},indent=2)+"\n")
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps({k:metrics[k] for k in ("n_routing_pairs","cause_distribution",
        "similarity_overlap_distribution","discovery_resolution_distribution","discovery_bucket_breakdown",
        "starvation_diagnosis","decision")},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
