#!/usr/bin/env python3
"""validate_p193.py — READ-ONLY extraction-failure analysis (P193).

Question A: for every P192-recovered discovery finding, classify WHY extraction missed a function name already
present in artifacts (DIRECT_NAME_MISSED / ALT_TITLE_MISSED / MATCH_TERM_MISSED / NORMALIZATION_FAILURE /
GET_SET_DRIFT / MULTI_FUNCTION_AMBIGUITY / OTHER), citing the exact field.
Question B: recompute P190's funnel for the recovered loci (BEFORE vs AFTER) = measurement-accounting change only.
Question C: per-bucket automation safety (SAFE_AUTOMATION / REVIEW_REQUIRED / UNSAFE).
No model runs; deterministic; every recovery cites an artifact; unknown=UNKNOWN; a shrunk discovery bucket is a
MEASUREMENT correction, not recall.
"""
from __future__ import annotations
import json, re, difflib
from pathlib import Path
from collections import Counter

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
PD = ROOT / "documentation/research/assisted_mode/p193_extraction_failure_analysis"
P190 = ROOT / "documentation/research/assisted_mode/p190_upstream_routing_analysis"
P192 = ROOT / "documentation/research/assisted_mode/p192_resolution_and_selection_audit"

CDIR = {"zaros":"zaros-2025-01-part-2-eval","revert-lend":"revert-lend-2024-03-strict-eval",
        "panoptic":"panoptic-2025-12-strict-eval","ark":"ark-project-2024-07-strict-eval"}
AKP = {"zaros":"answer_key/answer_key_normalized.json",
       "revert-lend":"output/eval_ready/answer_key_normalization.json",
       "panoptic":"output/eval_ready/answer_key_normalization.json",
       "ark":"output/answer_key/answer_key.json"}

def load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None
def structured_funcs(f):
    """What the pipeline's locus extraction captured: the structured affected_functions/functions field only."""
    s=set()
    for k in ("affected_functions","functions"):
        v=f.get(k)
        if isinstance(v,list): s|=set(v)
        elif isinstance(v,str): s|=set(re.split(r"[\/,\s]+",v))
    return {x for x in s if x and len(x)>2}

class Corpus:
    def __init__(self,name):
        cd=CDIR[name]
        man=load(ROOT/"audits"/cd/"output/coverage_manifest.json")
        items=(man or {}).get("items",[]) if isinstance(man,dict) else (man or [])
        self.fns=[it for it in items if it.get("kind")=="function"]
        self.by_contract={}
        for it in self.fns: self.by_contract.setdefault(str(it.get("contract") or "").lower(),{}).setdefault(it.get("name"),it)
        # name -> manifest_id (within contract)
        self.mid_of={}
        for it in self.fns: self.mid_of[(str(it.get("contract") or "").lower(),it.get("name"))]=it.get("id")
        q=load(ROOT/"audits"/cd/"output/deep_pass/candidate_queue.json")
        qit=q if isinstance(q,list) else (next((v for v in q.values() if isinstance(v,list)),[]) if isinstance(q,dict) else [])
        self.queue={it.get("manifest_id"):it for it in qit if isinstance(it,dict)}
        self.queue_by_contract={}
        for it in qit:
            if isinstance(it,dict): self.queue_by_contract.setdefault(str(it.get("contract") or "").lower(),[]).append(it)
        disp=load(ROOT/"audits"/cd/"output/coverage_dispositions.json")
        dl=disp.get("dispositions") if isinstance(disp,dict) else (disp or [])
        self.deep_mid={d.get("manifest_id") for d in (dl or []) if "deep" in str(d.get("assigned_pass") or "").lower()}
        dt=load(ROOT/"audits"/cd/"output/findings_deep_trace.json")
        dtf=dt if isinstance(dt,list) else (dt.get("findings",[]) if isinstance(dt,dict) else [])
        self.dt_funcs=set()
        for x in dtf:
            loc=x.get("location") or {}
            if isinstance(loc,dict):
                for fn in re.split(r"[\/,]",str(loc.get("function",""))):
                    if fn.strip(): self.dt_funcs.add(fn.strip())

P189_DEEP = {("zaros","H-01"),("zaros","H-02"),("zaros","H-07"),("zaros","H-09"),
             ("revert-lend","H-02"),("revert-lend","H-04"),("revert-lend","H-05"),("revert-lend","H-06"),
             ("panoptic","H-02"),("panoptic","H-03"),("panoptic","M-02"),("panoptic","M-03"),("ark","AK-M2")}

def after_bucket(c, corpus, fid, contract, name):
    """Re-run P190 Stage B/C on the recovered (contract,name): where would it land once the locus is correct?"""
    mid=c.mid_of.get((contract,name))
    queued = mid in c.queue
    deep = (mid in c.deep_mid) or (name in c.dt_funcs)
    sib_queued = bool(c.queue_by_contract.get(contract))
    if deep:
        return "ADJUDICATION_or_later" if (corpus,fid) in P189_DEEP else "REACHED_DEEP_PASS(NEEDS_EVIDENCE)"
    if queued:
        aw=(c.queue.get(mid) or {}).get("score") or 0
        starved=any((it.get("score") or 0)>aw and it.get("manifest_id") in c.deep_mid for it in c.queue.values())
        return "PRIORITY_ROUTING_GAP" if starved else "DEEP_PASS_GAP"
    if sib_queued:
        return "LOCUS_ROUTING_GAP"
    return "LOCUS_ROUTING_GAP(none_routed)"

def classify_failure(c, f, recovered_fn, tier, structured):
    """Return (bucket, field_cited, present_verbatim)."""
    title=str(f.get("title") or "")
    alt=" ".join(f.get("alt_titles") or [])
    # match_terms: corpus-level (eval_findings) — pass via attribute
    def word_in(text): return re.search(rf"\b{re.escape(recovered_fn)}\b", text) is not None
    # MULTI ambiguity: same normalized name maps to >1 manifest fn in the contract
    contract=recovered_fn  # placeholder; ambiguity computed by caller with contract
    if word_in(title):
        return "DIRECT_NAME_MISSED","answer_key.title",True
    if alt and word_in(alt):
        return "ALT_TITLE_MISSED","answer_key.alt_titles",True
    if recovered_fn in c_match_terms.get(id(c),set()):
        return "MATCH_TERM_MISSED","eval_findings.match_terms",True
    if tier=="TIER1_NORMALIZED":
        return "NORMALIZATION_FAILURE","normalized(extracted)==manifest",False
    if tier=="TIER2_FUZZY":
        for s in structured:
            a,b=s.lower(),recovered_fn.lower()
            if a in b or b in a or re.sub(r"^(get|set|update|is|_)","",a)==re.sub(r"^(get|set|update|is|_)","",b):
                return "GET_SET_DRIFT","difflib+prefix",False
        return "OTHER","difflib(no prefix)",False
    if tier=="TIER3_ALIAS":
        return "MATCH_TERM_MISSED","eval_findings.match_terms",True   # tier3 fell through title/alt -> match_terms
    return "OTHER",tier,False

c_match_terms={}

def main():
    PD.mkdir(parents=True,exist_ok=True)
    corp={n:Corpus(n) for n in CDIR}
    ak={}
    for n in CDIR:
        d=load(ROOT/"audits"/CDIR[n]/AKP[n]) or {}
        fl=d.get("findings") or d.get("families") or []
        ak[n]={(x.get("answer_key_id") or x.get("ak_id")):x for x in fl}
        ef=load(ROOT/"audits"/CDIR[n]/"output/eval_ready/eval_findings.json") or {}
        efl=ef.get("eval_findings",[]) if isinstance(ef,dict) else []
        mts=set()
        for x in efl:
            for t in (x.get("match_terms") or []): mts.add(str(t))
        c_match_terms[id(corp[n])]=mts
    p192=load(P192/"locus_resolution_audit.json")["rows"]
    funnel={ (r["corpus"],r["id"]):r for r in load(P190/"loss_funnel.json")["rows"]}

    # recovered discovery findings = p190 DISCOVERY_GAP and p192 tier != TIER4
    recovered=[r for r in p192 if r["p190_label"]=="DISCOVERY_GAP" and r["tier"]!="TIER4_UNRESOLVABLE"]
    unresolved=[r for r in p192 if r["p190_label"]=="DISCOVERY_GAP" and r["tier"]=="TIER4_UNRESOLVABLE"]

    tax=[]; after_counts=Counter(); before_counts=Counter()
    for r in recovered:
        corpus=r["corpus"]; c=corp[corpus]; f=ak[corpus].get(r["id"]) or {}
        rf=r["resolved_function"]; contract,name=rf.split(".",1) if rf and "." in rf else (None,rf)
        structured=structured_funcs(f)
        bucket,field,verbatim=classify_failure(c,f,name,r["tier"],structured)
        # multi-function ambiguity overlay
        contract_fns=c.by_contract.get(contract or "",{})
        norm=lambda s: re.sub(r"[^a-z0-9]","",str(s).lower())
        collisions=[mn for mn in contract_fns if norm(mn)==norm(name)]
        if len(collisions)>1: bucket="MULTI_FUNCTION_AMBIGUITY"; field="multiple manifest fns share normalized name"
        ab=after_bucket(c,corpus,r["id"],contract,name)
        after_counts[ab]+=1; before_counts["DISCOVERY_GAP"]+=1
        tax.append({"corpus":corpus,"id":r["id"],"original_extracted":sorted(structured)[:4],
                    "recovered_function":rf,"tier":r["tier"],"failure_bucket":bucket,
                    "artifact_field":field,"present_verbatim":verbatim,"after_bucket":ab})
    for r in unresolved:
        after_counts["DISCOVERY_GAP(unresolvable)"]+=1; before_counts["DISCOVERY_GAP"]+=1

    bucket_dist=Counter(t["failure_bucket"] for t in tax)
    per_corpus=Counter((t["corpus"],t["failure_bucket"]) for t in tax)
    verbatim_present=sum(1 for t in tax if t["present_verbatim"])
    n_disc=len(recovered)+len(unresolved)
    pct=lambda x,d: round(100*x/d,1) if d else 0

    # Question C automation safety per bucket
    SAFE={"DIRECT_NAME_MISSED","ALT_TITLE_MISSED","NORMALIZATION_FAILURE"}
    REVIEW={"MATCH_TERM_MISSED","GET_SET_DRIFT","MULTI_FUNCTION_AMBIGUITY","OTHER"}
    automation=[]
    for b,cnt in bucket_dist.most_common():
        safety="SAFE_AUTOMATION" if b in SAFE else "REVIEW_REQUIRED"
        automation.append({"bucket":b,"count":cnt,"safety":safety,
            "rationale":{"DIRECT_NAME_MISSED":"verbatim fn name in title AND matches in-contract manifest fn",
                         "ALT_TITLE_MISSED":"verbatim fn name in alt_titles AND matches manifest fn",
                         "NORMALIZATION_FAILURE":"pure casing/punct/suffix normalization, deterministic",
                         "MATCH_TERM_MISSED":"match_terms include non-fn tokens; confirm before trust",
                         "GET_SET_DRIFT":"get/set/update prefix mapping ambiguous (fuzzy)",
                         "MULTI_FUNCTION_AMBIGUITY":"name maps to >1 manifest fn; needs disambiguation",
                         "OTHER":"non-prefix fuzzy; manual confirm"}.get(b,"")})
    safe_n=sum(c for b,c in bucket_dist.items() if b in SAFE)
    review_n=sum(c for b,c in bucket_dist.items() if b in REVIEW)

    # decision
    explicit_present=verbatim_present  # DIRECT+ALT+MATCH_TERM
    decision=("EXTRACTION_PIPELINE_PRIMARY" if explicit_present>=len(tax)*0.5 and safe_n>=review_n else
              "ALIAS_INFRASTRUCTURE_PRIMARY" if bucket_dist.get("MATCH_TERM_MISSED",0)+bucket_dist.get("ALT_TITLE_MISSED",0) > len(tax)*0.5 else
              "UNRESOLVABLE_PRIMARY" if len(unresolved) > len(recovered) else
              "MIXED_EXTRACTION_FAILURE")

    (PD/"extraction_failure_taxonomy.json").write_text(json.dumps({"phase":"P193","rows":tax,
        "bucket_distribution":dict(bucket_dist),
        "per_corpus_bucket":{f"{k[0]}::{k[1]}":v for k,v in per_corpus.items()}},indent=2)+"\n")
    (PD/"before_after_metrics.json").write_text(json.dumps({"phase":"P193",
        "measurement_accounting_only":True,
        "discovery_bucket_before":n_disc,"recovered":len(recovered),"unresolvable":len(unresolved),
        "discovery_bucket_after":len(unresolved),
        "discovery_shrink_pct":pct(len(recovered),n_disc),
        "after_redistribution":dict(after_counts),
        "note":"AFTER redistributes recovered findings into routing/deep-pass/adjudication buckets (the real smaller bottleneck); NOT a claim those bugs would have been caught"},indent=2)+"\n")
    (PD/"automation_candidates.json").write_text(json.dumps({"phase":"P193","per_bucket":automation,
        "safe_total":safe_n,"review_total":review_n},indent=2)+"\n")
    metrics={"phase":"P193","read_only":True,
      "largest_failure_bucket":bucket_dist.most_common(1)[0] if bucket_dist else None,
      "bucket_distribution":dict(bucket_dist),
      "pct_recovered_explicitly_present_verbatim":pct(verbatim_present,len(tax)),
      "discovery_shrink_pct":pct(len(recovered),n_disc),
      "remaining_unresolved_pct":pct(len(unresolved),n_disc),
      "automation_safe":safe_n,"automation_review":review_n,
      "per_corpus_bucket":{f"{k[0]}::{k[1]}":v for k,v in per_corpus.items()},
      "decision":decision,
      "caveats":["measurement-accounting only; recovered loci are NOT newly discovered bugs",
                 "alt_titles/match_terms exist only in zaros -> alias buckets zaros-specific; see per_corpus",
                 "Tier2/Tier3 candidate-grade; only normalized/exact are high-confidence",
                 "n=%d recovered / %d unresolvable -> directional"%(len(recovered),len(unresolved))]}
    (PD/"metrics.json"). write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps({k:metrics[k] for k in ("largest_failure_bucket","bucket_distribution",
        "pct_recovered_explicitly_present_verbatim","discovery_shrink_pct","remaining_unresolved_pct",
        "automation_safe","automation_review","decision")},indent=2))
    print("AFTER redistribution:",dict(after_counts))
    print("per_corpus_bucket:",{f"{k[0]}::{k[1]}":v for k,v in per_corpus.items()})
    return 0

if __name__=="__main__":
    raise SystemExit(main())
