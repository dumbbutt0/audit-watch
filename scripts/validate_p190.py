#!/usr/bin/env python3
"""validate_p190.py — READ-ONLY upstream coverage & locus-routing failure analysis (P190).

For every unresolved awarded finding, deterministically trace the pipeline funnel (Stage A discovery -> B queue ->
C deep-pass) from existing artifacts and assign exactly one primary loss label (first failing stage). Stages
D/E/F (enumeration/selection/report) are not in legacy artifacts; they are taken from the 13 frozen P189
re-adjudications where available, else NEEDS_EVIDENCE. Emits loss_funnel.json, sibling_routing_table.json,
corpus_breakdown.json, metrics.json. Mutates nothing.

Join key = manifest_id  "function:<Contract>:<name>#<hash>"  shared by manifest / candidate_queue / dispositions.
Deep-run signal = disposition.assigned_pass contains 'deep'  OR  awarded fn in findings_deep_trace locations.
Routing score (for PRIORITY_ROUTING_GAP starvation) = candidate_queue 'score'.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
PD = ROOT / "documentation/research/assisted_mode/p190_upstream_routing_analysis"

CORPORA = {
 "zaros": ("zaros-2025-01-part-2-eval", "answer_key/answer_key_normalized.json",
           "output/eval_ready/eval_match_matrix.json"),
 "revert-lend": ("revert-lend-2024-03-strict-eval", "output/eval_ready/answer_key_normalization.json",
                 "output/eval_ready/match_matrix.json"),
 "panoptic": ("panoptic-2025-12-strict-eval", "output/eval_ready/answer_key_normalization.json",
              "output/eval_ready/match_matrix.json"),
 "ark": ("ark-project-2024-07-strict-eval", "output/answer_key/answer_key.json",
         "output/eval_ready/match_matrix.json"),
 "quantamm": ("quantamm-2024-12-eval", "output/answer_key/normalized_answer_key.json", None),  # control, no queue
}

# P189 re-adjudication outcomes (frozen) -> post-deep proxy for D/E/F. (corpus,id) -> outcome
P189 = {
 ("zaros","H-01"):"SELECTED", ("zaros","H-02"):"ENUMERATED_ONLY", ("zaros","H-07"):"UNCHANGED_MISS",
 ("zaros","H-09"):"UNCHANGED_MISS",
 ("revert-lend","H-02"):"HARNESS_ESCALATED", ("revert-lend","H-04"):"SELECTED",
 ("revert-lend","H-05"):"HARNESS_ESCALATED", ("revert-lend","H-06"):"SELECTED",
 ("panoptic","H-02"):"ENUMERATED_ONLY", ("panoptic","H-03"):"UNCHANGED_MISS",
 ("panoptic","M-02"):"SELECTED", ("panoptic","M-03"):"UNCHANGED_MISS",
 ("ark","AK-M2"):"UNCHANGED_MISS",
}
POSTDEEP_LABEL = {"SELECTED":"ADJUDICATION_GAP","ENUMERATED_ONLY":"ADJUDICATION_GAP",
                  "HARNESS_ESCALATED":"HARNESS_GAP","UNCHANGED_MISS":"ENUMERATION_GAP"}

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
    for k in ("affected_contracts",):
        for x in (f.get(k) or []): s.add(re.sub(r"\.sol$","",str(x)).lower())
    for fld in ("affected","location"):
        v=f.get(fld)
        if isinstance(v,str):
            for m in re.findall(r"([A-Za-z_]\w+)\.sol",v): s.add(m.lower())          # X.sol
            for m in re.findall(r"([A-Za-z_]\w+)\.[A-Za-z_]\w+",v): s.add(m.lower())  # Contract.func
            # bare PascalCase identifiers (e.g. affected="V3Vault" / "RiskEngine") = contract names
            for m in re.findall(r"\b([A-Z][A-Za-z0-9_]{2,})\b",v): s.add(m.lower())
    return {c for c in s if c}

def analyze(corpus):
    cdir,akp,mmp = CORPORA[corpus]
    ak=load(ROOT/"audits"/cdir/akp)
    akf=ak.get("findings") or ak.get("families") or (ak.get("distinct_findings") if ak else None) or []
    # unresolved ids
    unresolved=set(); sev={}
    if mmp:
        mm=load(ROOT/"audits"/cdir/mmp); rows=mm["rows"] if isinstance(mm,dict) and "rows" in mm else mm
        for r in rows:
            if str(r.get("category") or r.get("verdict")).upper() in ("MISS","UNRECOVERED"):
                unresolved.add(r.get("answer_key_id") or r.get("ak_id"))
    else:
        # quantamm control: use match matrix if present else all (flagged)
        mm=load(ROOT/"audits"/cdir/"output/eval_ready/eval_match_matrix.json")
        if mm:
            rows=mm["rows"] if isinstance(mm,dict) and "rows" in mm else mm
            for r in rows:
                if str(r.get("category") or r.get("verdict")).upper() in ("MISS","UNRECOVERED"):
                    unresolved.add(r.get("answer_key_id") or r.get("ak_id"))
    # manifest
    man=load(ROOT/"audits"/cdir/"output/coverage_manifest.json")
    items=(man or {}).get("items",[]) if isinstance(man,dict) else (man or [])
    by_contract={}; mid_item={}
    for it in items:
        c=str(it.get("contract") or "").lower(); n=it.get("name"); mid=it.get("id")
        mid_item[mid]=it; by_contract.setdefault(c,{})[n]=it
    # queue
    q=load(ROOT/"audits"/cdir/"output/deep_pass/candidate_queue.json")
    qit=q if isinstance(q,list) else (next((v for v in q.values() if isinstance(v,list)),[]) if isinstance(q,dict) else [])
    queued_mid={it.get("manifest_id"):it for it in qit if isinstance(it,dict)}
    queued_by_contract={};
    for it in qit:
        if isinstance(it,dict): queued_by_contract.setdefault(str(it.get("contract") or "").lower(),[]).append(it)
    # dispositions -> deep-run set
    disp=load(ROOT/"audits"/cdir/"output/coverage_dispositions.json")
    dlist=disp.get("dispositions") if isinstance(disp,dict) else (disp or [])
    deep_mid=set()
    for d in (dlist or []):
        if "deep" in str(d.get("assigned_pass") or "").lower(): deep_mid.add(d.get("manifest_id"))
    # deep-trace executed fns
    dt=load(ROOT/"audits"/cdir/"output/findings_deep_trace.json")
    dtf=dt if isinstance(dt,list) else (dt.get("findings",[]) if isinstance(dt,dict) else [])
    dt_funcs=set()
    for x in dtf:
        loc=x.get("location") or {}
        if isinstance(loc,dict):
            for fn in re.split(r"[\/,]",str(loc.get("function",""))):
                if fn.strip(): dt_funcs.add(fn.strip())
    # any higher-scored queued item deep-run? (for starvation)
    def starved(score):
        for mid,it in queued_mid.items():
            if (it.get("score") or 0) > score and (mid in deep_mid):
                return True
        return False

    rows=[]; sib_rows=[]
    for f in akf:
        fid=f.get("answer_key_id") or f.get("ak_id")
        if fid not in unresolved: continue
        fns=funcset(f); cts=contracts_of(f)
        # ---- Stage A ----
        man_hit=None; hit_contract=None
        for c in cts:
            for n in (by_contract.get(c) or {}):
                if n in fns: man_hit=by_contract[c][n]; hit_contract=c; break
            if man_hit: break
        contract_in_manifest=any(c in by_contract for c in cts)
        if man_hit:
            stageA="DISCOVERED_FUNCTION"; in_scope=bool(man_hit.get("in_scope",True))
        elif contract_in_manifest:
            stageA="DISCOVERED_CONTRACT_ONLY"; in_scope=None
        else:
            stageA="NOT_DISCOVERED"; in_scope=None
        # ---- Stage B ----
        awarded_mid=man_hit.get("id") if man_hit else None
        sib_queued=[it for c in cts for it in queued_by_contract.get(c,[])]
        if awarded_mid and awarded_mid in queued_mid: stageB="QUEUED_CORRECT_FUNCTION"
        elif sib_queued: stageB="QUEUED_SIBLING_FUNCTION"
        elif any(c in queued_by_contract for c in cts): stageB="QUEUED_CONTRACT_ONLY"
        else: stageB="NOT_QUEUED"
        # ---- Stage C ----
        awarded_deep = (awarded_mid in deep_mid) or bool(fns & dt_funcs)
        sib_deep = any((it.get("manifest_id") in deep_mid) for it in sib_queued) or False
        if awarded_deep: stageC="DEEP_RUN_CORRECT_FUNCTION"
        elif sib_deep: stageC="DEEP_RUN_SIBLING_FUNCTION"
        else: stageC="NOT_DEEP_RUN"
        # ---- primary loss label (first failing stage) ----
        evidence={"stageA":stageA,"in_scope":in_scope,"stageB":stageB,"stageC":stageC,
                  "awarded_manifest_id":awarded_mid,"matched_contract":hit_contract}
        if stageA=="NOT_DISCOVERED" or (man_hit and in_scope is False):
            label="DISCOVERY_GAP"
        elif stageA=="DISCOVERED_CONTRACT_ONLY":
            label="DISCOVERY_GAP"; evidence["note"]="contract-level only (coarse)"
        elif stageB!="QUEUED_CORRECT_FUNCTION":
            label="LOCUS_ROUTING_GAP"
            evidence["routing_subreason"]=("sibling_routed" if stageB=="QUEUED_SIBLING_FUNCTION"
                else "contract_only_routed" if stageB=="QUEUED_CONTRACT_ONLY" else "none_routed")
        elif stageC!="DEEP_RUN_CORRECT_FUNCTION":
            aw_score=(queued_mid.get(awarded_mid) or {}).get("score") or 0
            if starved(aw_score):
                label="PRIORITY_ROUTING_GAP"
                evidence["awarded_queue_score"]=aw_score
                evidence["starved_by_higher_scored_deep_runs"]=True
            else:
                label="DEEP_PASS_GAP"; evidence["awarded_queue_score"]=aw_score
                evidence["note"]="queued but no deep-pass reached it; no higher-scored deep-run starvation"
        else:
            # deep-run correct -> D/E/F from P189 proxy else NEEDS_EVIDENCE
            out=P189.get((corpus,fid))
            if out: label=POSTDEEP_LABEL[out]; evidence["p189_outcome"]=out
            else: label="NEEDS_EVIDENCE"; evidence["note"]="deep-run-correct; original enumeration not in artifacts"
        rows.append({"corpus":corpus,"id":fid,"severity":f.get("severity"),"label":label,"evidence":evidence})
        # sibling/priority routing table rows
        if label=="LOCUS_ROUTING_GAP" and stageB in ("QUEUED_SIBLING_FUNCTION","QUEUED_CONTRACT_ONLY"):
            routed=[{"function":it.get("function"),"score":it.get("score"),
                     "deep_run":it.get("manifest_id") in deep_mid} for it in sib_queued][:6]
            sib_rows.append({"corpus":corpus,"id":fid,"gap_type":"locus","awarded_function":sorted(fns&{n for c in cts for n in (by_contract.get(c) or {})})[:3] or sorted(fns)[:3],
                             "shared_contract":bool(cts),"routed_siblings":routed})
        if label=="PRIORITY_ROUTING_GAP":
            aw_score=(queued_mid.get(awarded_mid) or {}).get("score") or 0
            higher=[{"function":it.get("function"),"score":it.get("score")} for mid,it in queued_mid.items()
                    if (it.get("score") or 0)>aw_score and mid in deep_mid][:6]
            sib_rows.append({"corpus":corpus,"id":fid,"gap_type":"priority","awarded_function":sorted(fns)[:3],
                             "awarded_queue_score":aw_score,"starved_by":higher})
    return rows, sib_rows

LABELS=["DISCOVERY_GAP","LOCUS_ROUTING_GAP","PRIORITY_ROUTING_GAP","DEEP_PASS_GAP","ENUMERATION_GAP",
        "ADJUDICATION_GAP","HARNESS_GAP","REPORT_FORMATION_GAP","NEEDS_EVIDENCE"]

def main():
    PD.mkdir(parents=True,exist_ok=True)
    all_rows=[]; all_sib=[]; breakdown={}
    for corpus in CORPORA:
        rows,sib=analyze(corpus); all_rows+=rows; all_sib+=sib
        c={l:0 for l in LABELS}
        for r in rows: c[r["label"]]=c.get(r["label"],0)+1
        breakdown[corpus]={"total_unresolved":len(rows),"counts":c}
    agg={l:0 for l in LABELS}
    for r in all_rows: agg[r["label"]]+=1
    N=len(all_rows); pct=lambda x: round(100*x/N,1) if N else 0
    before=agg["DISCOVERY_GAP"]+agg["LOCUS_ROUTING_GAP"]+agg["PRIORITY_ROUTING_GAP"]+agg["DEEP_PASS_GAP"]
    during=agg["ENUMERATION_GAP"]; after=agg["ADJUDICATION_GAP"]+agg["HARNESS_GAP"]+agg["REPORT_FORMATION_GAP"]
    conc=max(((l,agg[l]) for l in LABELS if l!="NEEDS_EVIDENCE"), key=lambda kv:kv[1])
    # DISCOVERY_GAP split: genuine (contract absent) vs contract-only (function-name unmatched; locus-noise-prone)
    disc_rows=[r for r in all_rows if r["label"]=="DISCOVERY_GAP"]
    disc_genuine=sum(1 for r in disc_rows if r["evidence"]["stageA"]=="NOT_DISCOVERED")
    disc_contract_only=sum(1 for r in disc_rows if r["evidence"]["stageA"]=="DISCOVERED_CONTRACT_ONLY")
    routing=agg["DISCOVERY_GAP"]+agg["LOCUS_ROUTING_GAP"]+agg["PRIORITY_ROUTING_GAP"]+agg["DEEP_PASS_GAP"]
    decision=("ROUTING_IS_PRIMARY_BOTTLENECK" if routing>N/2 else
              "ENUMERATION_IS_PRIMARY_BOTTLENECK" if during>N/2 else
              "ADJUDICATION_IS_PRIMARY_BOTTLENECK" if after>N/2 else "MIXED_FAILURE")
    metrics={"phase":"P190","read_only":True,"total_unresolved":N,"aggregate_counts":agg,
             "pct":{l:pct(agg[l]) for l in LABELS},
             "loss_phase_split":{"before_deep_pass_pct":pct(before),"during_deep_pass_pct":pct(during),
                                 "after_deep_pass_pct":pct(after),"needs_evidence_pct":pct(agg["NEEDS_EVIDENCE"])},
             "recall_loss_concentration":{"label":conc[0],"count":conc[1],"pct":pct(conc[1])},
             "discovery_breakdown":{"genuine_not_discovered":disc_genuine,"genuine_pct":pct(disc_genuine),
                                    "contract_only_unmatched_fn":disc_contract_only,
                                    "contract_only_pct":pct(disc_contract_only),
                                    "note":"contract-only = contract enumerated but awarded fn name unmatched; "
                                            "locus-noise-prone, upper bound on true function-level discovery gap"},
             "routing_breakdown":{"locus_routing_pct":pct(agg["LOCUS_ROUTING_GAP"]),
                                  "priority_routing_pct":pct(agg["PRIORITY_ROUTING_GAP"])},
             "decision":decision,
             "caveats":["D-F resolved only via 13 P189 re-adjudications; rest NEEDS_EVIDENCE",
                        "answer-key loci noisy; contract-level fallback labeled coarse",
                        "quantamm Stage-B = no candidate_queue (control)",
                        "zaros/ark have no 'deep' assigned_pass -> deep-run signal ~ deep-trace fns only"]}
    (PD/"loss_funnel.json").write_text(json.dumps({"phase":"P190","rows":all_rows},indent=2)+"\n")
    (PD/"sibling_routing_table.json").write_text(json.dumps({"phase":"P190","rows":all_sib},indent=2)+"\n")
    (PD/"corpus_breakdown.json").write_text(json.dumps(breakdown,indent=2)+"\n")
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    top=sorted([r for r in all_rows if r["label"] in ("LOCUS_ROUTING_GAP","PRIORITY_ROUTING_GAP")],
               key=lambda r:(0 if r["severity"]=="High" else 1, r["corpus"]))[:20]
    (PD/"top_20_routing_failures.json").write_text(json.dumps({"phase":"P190","rows":top},indent=2)+"\n")
    print(json.dumps({"breakdown":breakdown,"aggregate":agg,"loss_phase_split":metrics["loss_phase_split"],
                      "concentration":metrics["recall_loss_concentration"],
                      "routing_breakdown":metrics["routing_breakdown"],"decision":decision},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
