#!/usr/bin/env python3
"""
_build_eval.py — deterministic generator for the Beanstalk Finale eval outputs.

Joins the per-finding answer-key mapping (documentation/evals/beanstalk-finale/answer_key.json)
with the fetched official severities and a STRICT-HIT re-scoring override, then emits the board
(md/csv/json), failure analysis (md/json), scorecard (md/json), and independent_findings.json.

Read-only inputs; writes only into evals/beanstalk_finale/ and the documentation eval dir.
No pipeline execution, no API calls.
"""
from __future__ import annotations
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "evals" / "beanstalk_finale"
ANSWER_KEY = ROOT / "documentation" / "evals" / "beanstalk-finale" / "answer_key.json"
MERGED = ROOT / "audits" / "beanstalk-2024-05" / "output" / "merged_findings.json"

# ── Official per-finding severities (fetched from CodeHawks /s/<id> pages this session) ──
OFFICIAL_SEV = {
 30:"Low",37:"Medium",68:"Low",90:"High",99:"Low",128:"Medium",131:"Low",133:"Low",135:"Medium",
 139:"Low",140:"Low",142:"Low",184:"Low",186:"Low",200:"Low",204:"Low",224:"High",227:"High",
 228:"Medium",229:"Low",239:"High",241:"Medium",242:"Medium",248:"Medium",251:"High",259:"Low",
 260:"Medium",261:"Low",262:"Medium",267:"Low",272:"Medium",273:"Low",279:"High",303:"High",
 307:"Medium",309:"Low",319:"Low",320:"Low",323:"Medium",324:"Medium",325:"High",327:"High",
 328:"High",330:"Medium",332:"Low",336:"Low",348:"Low",350:"High",357:"Medium",364:"Medium",
 375:"High",377:"Medium",378:"Low",379:"Medium",384:"Medium",395:"High",396:"High",397:"High",398:"Medium",
 401:"Medium",411:"High",412:"High",419:"Low",423:"Medium",433:"Medium",444:"High",447:"High",
 451:"Medium",452:"High",454:"Medium",461:"Medium",462:"High",469:"Low",471:"Medium",476:"Medium",
 478:"Medium",485:"Low",491:"Medium",505:"Low",519:"Medium",522:"Low",
}
# Reconciles to 21 H / 31 M / 29 L per submission pages; official aggregate is 22/31/28 — a known
# one-finding submission-page-vs-tally artifact (documented). Counts below use these per-finding values.

# ── STRICT-HIT re-scoring overrides (vs the prior looser "root cause + impact" mapping) ──
# Each: sub -> (new_status, new_match_quality, reason)
STRICT_OVERRIDES = {
 419: ("PARTIAL", "PARTIAL",
       "STRICT downgrade from HIT: same root-cause constant (hardcoded mainnet C.PIPELINE) but the "
       "pipeline found it in LibPipelineConvert.executePipelineConvert, NOT in the public bug's "
       "contract/function DepotFacet. Fails strict criterion 'same contract/function'."),
}

# ── Map answer_key failure_reason text -> the eval's failure-label vocabulary ──
FAIL_LABEL = {
 "agent did not inspect correct contract":"Agent did not inspect the correct contract",
 "weak invariant extraction":"Weak invariant extraction",
 "missed lifecycle edge case":"Missed lifecycle edge case",
 "architecture mapping failure":"Architecture mapping failure",
 "missed reward accounting edge case":"Missed accounting invariant",
 "missed accounting invariant":"Missed accounting invariant",
 "missed state transition":"Missed state transition",
 "missed oracle/precision/decimal issue":"Missed oracle/precision/decimal issue",
 "missed oracle/precision issue":"Missed oracle/precision/decimal issue",
 "missed oracle/precision/heartbeat issue":"Missed oracle/precision/decimal issue",
 "missing domain knowledge":"Missing domain knowledge",
 "missed attacker-controlled input":"Missed attacker-controlled input",
 "missed cross-chain/migration edge case":"Missed cross-chain or migration edge case",
 "severity reasoning failure":"Severity reasoning failure",
 "agent found but failed to escalate":"Agent found the issue but failed to escalate it",
 "":"",
}

AGENT_BY_PREFIX = {
 "AC":"access_control","AR":"arithmetic","BSA":"behavioral_state_analysis","CC":"cross_chain",
 "DS":"dos","EA":"economic_attack","FL":"flash_loan","LG":"logic","OR":"oracle","PC":"protocol_context",
 "RE":"reentrancy","SG":"semantic_guard","SN":"snapshot","TI":"token_integration","US":"upgrade_storage",
 "SC":"supply_chain","AM":"attacker_mindset",
}

def primary_id(pid: str) -> str:
    return (pid or "").split("/")[0].strip()

def agent_of(pid: str) -> str:
    p = primary_id(pid)[:3].rstrip("-")[:2].upper() if primary_id(pid) else ""
    # use 2-letter prefix (BSA is 3) — handle BSA/US explicitly
    pp = primary_id(pid).split("-")[0].upper()
    return AGENT_BY_PREFIX.get(pp, AGENT_BY_PREFIX.get(pp[:2], "unknown")) if pp else ""

def main():
    ak = json.loads(ANSWER_KEY.read_text())
    findings = ak["findings"]
    merged = json.loads(MERGED.read_text())
    psev = {f["id"]: f.get("severity","") for f in merged.get("findings",[])}

    # apply strict overrides + attach official severity
    rows = []
    for f in findings:
        sub = f["sub"]
        status = f["pipeline_status"]
        mq = f["match_quality"]
        reason = f.get("note","")
        if sub in STRICT_OVERRIDES:
            status, mq, ov = STRICT_OVERRIDES[sub]
            reason = ov + " | prior: " + f.get("note","")
        rows.append({
            "sub": sub,
            "title": f["title"],
            "category": f["category"],
            "official_severity": OFFICIAL_SEV.get(sub,"?"),
            "pipeline_id": f["pipeline_id"],
            "classification": status,
            "match_quality": mq,
            "reason": reason,
            "evidence_missing": "" if status=="HIT" else f.get("note",""),
            "poc_existed": "No",  # no PoCs generated for beanstalk (no API that run)
            "pipeline_severity": psev.get(primary_id(f["pipeline_id"]),"(merged-pre)"),
            "agent": agent_of(f["pipeline_id"]),
            "failure_label": FAIL_LABEL.get(f.get("failure_reason",""), f.get("failure_reason","")) if status in ("MISS","PARTIAL","ADJACENT") else "",
        })

    # severity-correct flag (exact official vs pipeline severity, where pipeline sev resolvable)
    for r in rows:
        ps, os_ = r["pipeline_severity"], r["official_severity"]
        if r["classification"] in ("HIT","PARTIAL") and ps not in ("(merged-pre)",""):
            r["severity_correct"] = "yes" if ps == os_ else f"no ({ps}→{os_})"
        else:
            r["severity_correct"] = "n/a"
        r["contract_inspected"] = "yes" if r["classification"] in ("HIT","PARTIAL","ADJACENT") else "no"

    # ── counts ──
    cls = Counter(r["classification"] for r in rows)
    HIT,PART,ADJ,MISS = cls["HIT"],cls["PARTIAL"],cls["ADJACENT"],cls["MISS"]
    total = len(rows)
    meaningful = HIT+PART
    any_touch = HIT+PART+ADJ

    by_sev = defaultdict(Counter)
    for r in rows: by_sev[r["official_severity"]][r["classification"]] += 1
    by_cat = defaultdict(Counter)
    for r in rows: by_cat[r["category"]][r["classification"]] += 1

    # severity accuracy over matched (HIT+PARTIAL) with resolvable pipeline sev
    matched = [r for r in rows if r["classification"] in ("HIT","PARTIAL")]
    sev_resolvable = [r for r in matched if r["pipeline_severity"] not in ("(merged-pre)","")]
    sev_exact = sum(1 for r in sev_resolvable if r["pipeline_severity"]==r["official_severity"])

    # agent contribution (HIT+PARTIAL)
    agent_contrib = Counter(r["agent"] for r in matched if r["agent"])

    # failure labels (MISS+PARTIAL)
    fail_counts = Counter(r["failure_label"] for r in rows if r["classification"] in ("MISS","PARTIAL") and r["failure_label"])

    # ── write filled_comparison_board.csv ──
    cols = ["sub","official_severity","category","classification","match_quality","pipeline_id",
            "agent","pipeline_severity","severity_correct","contract_inspected","poc_existed","title","reason"]
    with (EVAL/"filled_comparison_board.csv").open("w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=cols,extrasaction="ignore"); w.writeheader()
        for r in rows: w.writerow(r)

    # ── match_matrix.json ──
    (EVAL/"match_matrix.json").write_text(json.dumps({
        "contest":"2024-05-beanstalk-the-finale","total":total,
        "scoring_rule":"STRICT (same contract/function + root cause + invariant + impact + plausible exploit path)",
        "counts":{"HIT":HIT,"PARTIAL":PART,"ADJACENT":ADJ,"MISS":MISS},
        "rows":rows,
    },indent=2))

    # ── filled_comparison_board.md ──
    L=["# Filled Comparison Board — Beanstalk Finale (STRICT scoring)","",
       f"Independent run = blind artifacts in `audits/beanstalk-2024-05/` (pre-answer-key). "
       f"PoC existed = No for all (no PoCs generated that run). Scoring rule = STRICT.","",
       f"**HIT {HIT} · PARTIAL {PART} · ADJACENT {ADJ} · MISS {MISS}** of {total} · "
       f"meaningful (HIT+PARTIAL) {meaningful} ({meaningful*100//total}%) · any-touch {any_touch} ({any_touch*100//total}%)","",
       "| Sub | Sev | Category | Class | Match | Pipeline ID | Agent | Pipe Sev | Sev✓ | Reason |",
       "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['sub']} | {r['official_severity'][:1]} | {r['category']} | {r['classification']} | "
                 f"{r['match_quality']} | {r['pipeline_id'] or '—'} | {r['agent'] or '—'} | "
                 f"{r['pipeline_severity']} | {r['severity_correct']} | {r['reason'][:90].replace('|','/')} |")
    (EVAL/"filled_comparison_board.md").write_text("\n".join(L)+"\n")

    # ── failure_analysis.json/md ──
    fa = {"miss_and_partial":[{"sub":r["sub"],"title":r["title"],"classification":r["classification"],
            "failure_label":r["failure_label"],"reason":r["reason"]}
            for r in rows if r["classification"] in ("MISS","PARTIAL")],
          "failure_label_counts":dict(fail_counts.most_common())}
    (EVAL/"failure_analysis.json").write_text(json.dumps(fa,indent=2))
    FL=["# Failure Analysis — Beanstalk Finale","",
        "Every MISS / PARTIAL with its most-likely pipeline failure label.","",
        "## Failure-label frequency (MISS + PARTIAL)",""]
    for lbl,n in fail_counts.most_common(): FL.append(f"- **{lbl}** — {n}")
    FL+=["","## Per-finding","","| Sub | Class | Failure label | Reason |","|---|---|---|---|"]
    for r in rows:
        if r["classification"] in ("MISS","PARTIAL"):
            FL.append(f"| {r['sub']} | {r['classification']} | {r['failure_label']} | {r['reason'][:100].replace('|','/')} |")
    FL+=["","## False positives / pipeline-only noise (causes → validation fix)","",
         "See `rejected_candidates.md` for the full list. Cause taxonomy:",
         "- **Class A — attacker-mindset hypotheses (AM-001..021, 22 items):** surface hints leaked "
         "into the findings corpus. *Why plausible:* scored 3–5 entry points. *Why invalid:* no traced "
         "exploit path. *Gate that should catch:* schema/`validate_agent_output` should reject "
         "`attacker_mindset` Speculative entries from the corpus. *Source:* agent reasoning (Step 0.25).",
         "- **Class B — supply-chain (SC-001..006, 6 items):** real but OUT OF CONTEST SCOPE (build/CI). "
         "*Gate:* route to `build_security_annex.md`, exclude from findings/precision. *Source:* supply_chain_check.",
         "- **Class C — non-exploitable (RE-001/2/3, AC-003):** real code smells, no reachable exploit. "
         "*Gate:* exploitability gate on emit (reentrancy ≤ Low without an in-scope hooked token). *Source:* agent reasoning.",
         "- **Class D — informational (AR-003, AC-004):** unreachable pattern / a clearing mislabeled as a "
         "finding. *Gate:* confidence floor; clearings belong in `resolved_flags`. *Source:* agent reasoning.",
         "- **Class E — unmatched but source-real (SG-001, EA-002):** likely genuine (SG-001 is a real "
         "High that clusters near #505). *Fix:* route to human review, do not suppress. (Not true FPs.)"]
    (EVAL/"failure_analysis.md").write_text("\n".join(FL)+"\n")

    # ── scorecard.json/md ──
    sev_order=["High","Medium","Low"]
    sc={"total":total,"scoring_rule":"STRICT",
        "overall":{"HIT":HIT,"PARTIAL":PART,"ADJACENT":ADJ,"MISS":MISS,
                   "exact_hit_rate":round(HIT/total,3),"useful_detection_rate":round(meaningful/total,3),
                   "any_touch_rate":round(any_touch/total,3)},
        "by_severity":{s:{k:by_sev[s][k] for k in ("HIT","PARTIAL","ADJACENT","MISS")} for s in sev_order},
        "by_category":{c:{k:by_cat[c][k] for k in ("HIT","PARTIAL","ADJACENT","MISS")} for c in by_cat},
        "false_positive_count": "≈36 (Class A–E; 0 hallucinations)",
        "poc_success_rate":"0/0 — no PoCs generated for this target (no API that run)",
        "severity_accuracy":{"matched":len(matched),"resolvable":len(sev_resolvable),"exact":sev_exact,
                             "note":"CodeHawks downgraded aggressively; pipeline severities often HIGHER than official"},
        "duplicate_clustering":"1 known wrongful collapse (OR-001/OR-002, distinct oracle bugs merged); "
                               "otherwise dedup linked rather than dropped. Five-axis dedup fix is staged.",
        "agent_contribution_hit_partial":dict(agent_contrib.most_common()),
        "most_common_miss_reason": fail_counts.most_common(1)[0][0] if fail_counts else "",
        }
    (EVAL/"scorecard.json").write_text(json.dumps(sc,indent=2))

    def pct(n): return f"{n*100//total}%"
    worst=min(by_cat.items(), key=lambda kv:(kv[1]["HIT"]+kv[1]["PARTIAL"])/sum(kv[1].values()))
    best =max(by_cat.items(), key=lambda kv:(kv[1]["HIT"]+kv[1]["PARTIAL"])/sum(kv[1].values()))
    SC=["# Scorecard — Beanstalk Finale (STRICT scoring)","",
        f"Total public findings: {total}",
        f"Exact HIT: {HIT}",
        f"PARTIAL HIT: {PART}",
        f"ADJACENT: {ADJ}",
        f"MISS: {MISS}",
        f"Pipeline-only FP: ≈36 (Class A–E; 0 hallucinations)",
        f"Overall exact hit rate: {HIT}/{total} = {pct(HIT)}",
        f"Overall useful detection rate (HIT + PARTIAL HIT): {meaningful}/{total} = {pct(meaningful)}",
        f"Worst category: {worst[0]} ({(worst[1]['HIT']+worst[1]['PARTIAL'])}/{sum(worst[1].values())} meaningful)",
        f"Best category: {best[0]} ({(best[1]['HIT']+best[1]['PARTIAL'])}/{sum(best[1].values())} meaningful)",
        f"Most common miss reason: {sc['most_common_miss_reason']}",
        f"Most wasteful FP source: attacker_mindset hypotheses leaked into the findings corpus (22 items)",
        "",
        "## 1–3 Hit rate overall / by severity / by category","",
        "| Severity | Total | HIT | PARTIAL | ADJ | MISS | Meaningful |",
        "|---|---|---|---|---|---|---|"]
    for s in sev_order:
        c=by_sev[s]; t=sum(c.values()); m=c["HIT"]+c["PARTIAL"]
        SC.append(f"| {s} | {t} | {c['HIT']} | {c['PARTIAL']} | {c['ADJACENT']} | {c['MISS']} | {m} ({m*100//t if t else 0}%) |")
    SC+=["",
        "| Category | Total | HIT | PARTIAL | ADJ | MISS | Meaningful |","|---|---|---|---|---|---|---|"]
    for c,cc in sorted(by_cat.items(), key=lambda kv:-(kv[1]['HIT']+kv[1]['PARTIAL'])/sum(kv[1].values())):
        t=sum(cc.values()); m=cc["HIT"]+cc["PARTIAL"]
        SC.append(f"| {c} | {t} | {cc['HIT']} | {cc['PARTIAL']} | {cc['ADJACENT']} | {cc['MISS']} | {m} ({m*100//t if t else 0}%) |")
    SC+=["","## 4–12 Other scorecards","",
        f"- Partial-hit rate: {PART}/{total} = {pct(PART)}",
        f"- Adjacent rate: {ADJ}/{total} = {pct(ADJ)}",
        f"- Miss rate: {MISS}/{total} = {pct(MISS)}",
        f"- False-positive count: ≈36 (Class A–E); **0 hallucinations** (every unmatched finding is real code)",
        f"- False-positive rate (noise / total emitted ≈ 44 corpus + 36 noise): qualitative — ~45% of the "
        f"emitted *count* was attacker-mindset hypotheses; genuinely-wrong exploitable claims ≈ 0.",
        f"- PoC success rate: 0/0 — **no PoCs were generated** for this target (validation half didn't run; no API).",
        f"- Severity accuracy: of {len(matched)} matched, pipeline severity resolvable for {len(sev_resolvable)}; "
        f"exact match {sev_exact}. Mismatches skew to pipeline rating HIGHER than CodeHawks' aggressive downgrades.",
        f"- Duplicate-clustering accuracy: {sc['duplicate_clustering']}",
        f"- Agent/stage contribution (HIT+PARTIAL by agent): " + ", ".join(f"{a}:{n}" for a,n in agent_contrib.most_common()),
        "",
        f"_Note: by-severity uses fetched per-finding severities (21H/31M/29L); official aggregate 22/31/28 "
        f"(one-finding submission-page artifact)._"]
    (EVAL/"scorecard.md").write_text("\n".join(SC)+"\n")

    # ── independent_findings.json (reshape the 44 blind findings) ──
    indep=[]
    for f in merged.get("findings",[]):
        loc=f.get("location",{}) or {}
        pid=f.get("id","")
        indep.append({
            "id":pid,"agent":AGENT_BY_PREFIX.get(pid.split("-")[0].upper(),"unknown"),
            "severity":f.get("severity",""),
            "file":loc.get("file",""),"function":loc.get("function",""),
            "root_cause":(f.get("description","") or "")[:400],
            "attacker_input":(f.get("ite",{}) or {}).get("technique",""),
            "exploit_path":(f.get("proof_of_concept","") or "")[:400],
            "impact":(f.get("impact","") or "")[:300],
            "confidence":f.get("confidence",""),
            "poc_status":"none",
            "validation_status":"raw-detection (triage/multi-pass/PoC did not run — no API that run)",
        })
    (EVAL/"independent_findings.json").write_text(json.dumps(
        {"contest":"2024-05-beanstalk-the-finale","provenance":"blind run audits/beanstalk-2024-05 (pre-answer-key)",
         "stages_run":["static","attack_surface","16 specialists","deterministic merge"],
         "stages_not_run":["cross_agent(API)","compound_synth(API)","multi_pass_confirm(API)","triage(API)","PoC"],
         "count":len(indep),"findings":indep},indent=2))

    print(f"OK — HIT {HIT} PARTIAL {PART} ADJ {ADJ} MISS {MISS} (total {total}, meaningful {meaningful})")
    print(f"by_severity: " + " | ".join(f"{s}: H{by_sev[s]['HIT']}/P{by_sev[s]['PARTIAL']}/A{by_sev[s]['ADJACENT']}/M{by_sev[s]['MISS']}" for s in sev_order))
    print(f"sev exact-match {sev_exact}/{len(sev_resolvable)} resolvable; agents: {dict(agent_contrib.most_common())}")
    print(f"most common miss reason: {sc['most_common_miss_reason']}")

if __name__=="__main__":
    main()
