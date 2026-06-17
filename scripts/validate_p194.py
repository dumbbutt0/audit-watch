#!/usr/bin/env python3
"""validate_p194.py — READ-ONLY before/after + residual source audit for the P194 safe extraction repair.

Applies scripts/eval_locus_resolver.py (SAFE tiers only) across the 4 corpora's P190 discovery findings, reports
the measurement-accounting BEFORE/AFTER, and classifies the genuinely-unresolved residual (the P192 TIER4 set).
No answer-key/corpus/manifest mutation. Measurement-accounting only — recovered loci are NOT newly found bugs.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from collections import Counter

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
import sys; sys.path.insert(0, str(ROOT / "scripts"))
import eval_locus_resolver as R  # noqa: E402

PD = ROOT / "documentation/research/assisted_mode/p194_extraction_repair_and_residual_audit"
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

class C:
    def __init__(self,n):
        cd=CDIR[n]
        man=load(ROOT/"audits"/cd/"output/coverage_manifest.json")
        self.items=(man or {}).get("items",[]) if isinstance(man,dict) else (man or [])
        self.idx=R.build_manifest_index(self.items)
        self.all_fn_names={it.get("name") for it in self.items if it.get("kind")=="function"}
        q=load(ROOT/"audits"/cd/"output/deep_pass/candidate_queue.json")
        qit=q if isinstance(q,list) else (next((v for v in q.values() if isinstance(v,list)),[]) if isinstance(q,dict) else [])
        self.queue={it.get("manifest_id"):it for it in qit if isinstance(it,dict)}
        self.queue_contracts={str(it.get("contract") or "").lower() for it in qit if isinstance(it,dict)}
        disp=load(ROOT/"audits"/cd/"output/coverage_dispositions.json")
        dl=disp.get("dispositions") if isinstance(disp,dict) else (disp or [])
        self.deep_mid={d.get("manifest_id") for d in (dl or []) if "deep" in str(d.get("assigned_pass") or "").lower()}
        dt=load(ROOT/"audits"/cd/"output/findings_deep_trace.json")
        dtf=dt if isinstance(dt,list) else (dt.get("findings",[]) if isinstance(dt,dict) else [])
        self.dt_funcs=set()
        for x in dtf:
            loc=x.get("location") or {}
            if isinstance(loc,dict):
                for f in re.split(r"[\/,]",str(loc.get("function",""))):
                    if f.strip(): self.dt_funcs.add(f.strip())

def after_bucket(c, mid, name):
    queued = mid in c.queue
    deep = (mid in c.deep_mid) or (name in c.dt_funcs)
    if deep: return "REACHED_DEEP_PASS"
    if queued:
        aw=(c.queue.get(mid) or {}).get("score") or 0
        starved=any((it.get("score") or 0)>aw and it.get("manifest_id") in c.deep_mid for it in c.queue.values())
        return "PRIORITY_ROUTING_GAP" if starved else "DEEP_PASS_GAP"
    return "LOCUS_ROUTING_GAP"

def main():
    PD.mkdir(parents=True,exist_ok=True)
    corp={n:C(n) for n in CDIR}
    ak={}
    for n in CDIR:
        d=load(ROOT/"audits"/CDIR[n]/AKP[n]) or {}
        fl=d.get("findings") or d.get("families") or []
        ak[n]={(x.get("answer_key_id") or x.get("ak_id")):x for x in fl}
    funnel=load(P190/"loss_funnel.json")["rows"]
    p192={ (r["corpus"],r["id"]):r for r in load(P192/"locus_resolution_audit.json")["rows"]}
    disc=[r for r in funnel if r["label"]=="DISCOVERY_GAP" and r["corpus"] in CDIR]

    rows=[]; status_ct=Counter(); after_ct=Counter(); per_corpus=Counter()
    for r in disc:
        corpus=r["corpus"]; c=corp[corpus]; f=ak[corpus].get(r["id"]) or {}
        res=R.resolve_locus(f,c.idx)   # match_terms omitted (zaros-only; conservative)
        status_ct[res["status"]]+=1; per_corpus[(corpus,res["status"])]+=1
        ab=None
        if res["status"]=="RESOLVED":
            name=res["function"].split(".",1)[1]; ab=after_bucket(c,res["manifest_id"],name); after_ct[ab]+=1
        rows.append({"corpus":corpus,"id":r["id"],"safe_status":res["status"],"tier":res["tier"],
                     "resolved_function":res["function"],"field_cited":res["field_cited"],
                     "after_bucket":ab,"evidence":res["evidence"]})
    safe_resolved=status_ct["RESOLVED"]; review=status_ct["REVIEW_GATED"]; amb=status_ct["AMBIGUOUS"]
    unresolved=status_ct["UNRESOLVED"]; n=len(disc)
    pct=lambda x: round(100*x/n,1) if n else 0

    # ---- Part D: residual source audit over the P192 TIER4 (genuinely-unresolvable) set ----
    residual_ids=[(k[0],k[1]) for k,v in p192.items() if v["p190_label"]=="DISCOVERY_GAP" and v["tier"]=="TIER4_UNRESOLVABLE"]
    GENERIC=R.GENERIC_TOKENS
    all_contract_names={str(it.get("contract") or "").lower() for n in CDIR for it in corp[n].items}
    def fn_like(t,c):
        # function naming convention: lowerCamel or _-prefixed (PascalCase = contract/event/struct/type).
        low=t.lower()
        if low in GENERIC or len(t)<5: return False
        if low in all_contract_names: return False                 # contract name, not a function
        if t[0].isupper(): return False                            # PascalCase -> contract/event/type
        if t.startswith("Log") or t.startswith("Event"): return False
        return ("_" in t) or bool(re.search(r"[a-z][A-Z]",t))
    residual=[]
    rclass=Counter()
    for corpus,fid in residual_ids:
        c=corp[corpus]; f=ak[corpus].get(fid) or {}
        cts=[x for x in R._contracts(f) if x in c.idx["by_contract"]]
        title=str(f.get("title") or ""); rc=str(f.get("root_cause") or "")
        toks=set(re.findall(r"[A-Za-z_]\w{3,}",title+" "+rc)) | set(f.get("affected_functions") or []) | (set(re.split(r"[\/,\s]+",f.get("functions") or "")) if isinstance(f.get("functions"),str) else set())
        flike=[t for t in toks if fn_like(t,c)]
        in_target=[t for t in flike for ct in cts if t in c.idx["by_contract"].get(ct,{})]
        in_other=[t for t in flike if t in c.all_fn_names and t not in in_target]
        absent_flike=[t for t in flike if t not in c.all_fn_names]
        affected_raw=str(f.get("affected") or "")
        cls=None; detail={}
        if not cts and re.search(r"/|\*|\.md|rules|spec|whitepaper|architecture",affected_raw,re.I):
            cls="OUT_OF_SCOPE_FOR_FUNCTION_MAPPING"; detail={"affected":affected_raw[:60]}
        elif not cts:
            cls="ANSWER_KEY_STILL_UNRESOLVED"; detail={"affected":affected_raw[:60],"reason":"affected contract not in manifest"}
        elif in_target:
            cls="NEEDS_HUMAN_MAPPING"; detail={"named_in_contract":sorted(set(in_target))[:3],"reason":"would resolve but P192/safe ambiguous/multiple"}
        elif in_other:
            cls="NEEDS_HUMAN_MAPPING"; detail={"name_in_other_contract":sorted(set(in_other))[:3],"reason":"inherited/cross-contract; needs human contract mapping"}
        elif absent_flike:
            # a lowerCamel/_-prefixed token absent from the whole manifest: could be a missing fn OR a
            # var/param/struct-field. NOT artifact-confirmable as a function -> human/source mapping required.
            cls="NEEDS_HUMAN_MAPPING"; detail={"function_like_token_absent":sorted(set(absent_flike))[:3],
                "contract":cts[:2],"reason":"lowerCamel token absent from manifest; may be var/param, function status UNCONFIRMABLE from artifacts -> manual source mapping",
                "true_coverage_gap":"UNKNOWN(needs source)"}
        else:
            cls="ANSWER_KEY_STILL_UNRESOLVED"; detail={"reason":"no function-like token in answer-key fields (contract/event/var/prose only)","tokens":sorted(toks)[:5]}
        rclass[cls]+=1
        residual.append({"corpus":corpus,"id":fid,"classification":cls,"affected_contracts_in_manifest":cts[:3],"detail":detail})

    # ---- recommendation ----
    true_gaps=rclass.get("TRUE_COVERAGE_GAP",0)
    decision=("EXTRACTION_FIX_SUFFICIENT" if safe_resolved>=n*0.30 and true_gaps<=len(residual_ids)*0.2 else
              "PRODUCTION_COVERAGE_GAP_CONFIRMED" if true_gaps>=len(residual_ids)*0.5 else
              "SOURCE_MAPPING_STILL_PRIMARY" if (rclass.get("NEEDS_HUMAN_MAPPING",0)+rclass.get("ANSWER_KEY_STILL_UNRESOLVED",0))>=len(residual_ids)*0.5 else
              "MIXED")

    (PD/"before_after_resolution.json").write_text(json.dumps({"phase":"P194","measurement_accounting_only":True,
        "discovery_bucket_before":n,"safe_resolved":safe_resolved,"review_gated":review,"ambiguous":amb,
        "unresolved_after_safe":unresolved,"discovery_bucket_after_safe":n-safe_resolved,
        "discovery_shrink_pct_safe":pct(safe_resolved),
        "after_redistribution_of_resolved":dict(after_ct),
        "per_corpus_status":{f"{k[0]}::{k[1]}":v for k,v in per_corpus.items()},
        "rows":rows,
        "note":"AFTER redistributes safe-resolved loci into routing/deep-pass/adjudication buckets; NOT a claim those bugs would be caught"},indent=2)+"\n")
    (PD/"automation_decisions.json").write_text(json.dumps({"phase":"P194",
        "auto_resolved_safe":safe_resolved,"review_gated":review,"ambiguous_not_autoselected":amb,
        "unresolved":unresolved,"tier_distribution":dict(Counter(r["tier"] for r in rows if r["safe_status"]=="RESOLVED")),
        "policy":"SAFE tiers auto (DIRECT/ALT_TITLE/NORMALIZATION/MATCH_TERM-verbatim); GET_SET/OTHER/fuzzy=REVIEW_GATED; multi-match=AMBIGUOUS no-autoselect"},indent=2)+"\n")
    (PD/"residual_source_audit.json").write_text(json.dumps({"phase":"P194","residual_count":len(residual_ids),
        "classification_distribution":dict(rclass),"rows":residual},indent=2)+"\n")
    metrics={"phase":"P194","read_only":True,
      "safely_recovered":safe_resolved,"discovery_before":n,"discovery_after_safe":n-safe_resolved,
      "discovery_shrink_pct_safe":pct(safe_resolved),"review_gated":review,"ambiguous":amb,
      "unresolved_after_safe":unresolved,
      "residual_classification":dict(rclass),"true_coverage_gaps":true_gaps,
      "decision":decision,
      "production_changed":False,
      "caveats":["measurement-accounting only; recovered loci NOT newly found bugs",
                 "safe module recovers FEWER than P192 full ladder (no auto-fuzzy) by design",
                 "zaros dominates recoverable set; see per_corpus",
                 "TRUE_COVERAGE_GAP internal/private/inherited status = UNKNOWN(needs source/human)"]}
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps({k:metrics[k] for k in ("safely_recovered","discovery_before","discovery_after_safe",
        "discovery_shrink_pct_safe","review_gated","ambiguous","unresolved_after_safe","residual_classification",
        "true_coverage_gaps","decision")},indent=2))
    print("per_corpus_status:",{f"{k[0]}::{k[1]}":v for k,v in per_corpus.items()})
    print("after_redistribution:",dict(after_ct))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
