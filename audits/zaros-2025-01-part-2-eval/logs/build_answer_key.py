#!/usr/bin/env python3
"""Stage 5: build the Zaros Part 2 answer key from the 70 report findings embedded in report.html.
Each report 'finding' = one selected-for-report family (root cause); its `severity` is the final
report severity; `issues[0]` carries the representative title + body. Writes answer_key_raw/normalized/md."""
import json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
SCR=Path("audits/zaros-2025-01-part-2-eval/logs/scrape")
AK=Path("audits/zaros-2025-01-part-2-eval/answer_key"); AK.mkdir(parents=True,exist_ok=True)
NOW=datetime.now(timezone.utc).isoformat()
SEVNAME={"high":"High","medium":"Medium","low":"Low"}
REPORT_URL="https://codehawks.cyfrin.io/c/2025-01-zaros-part-2/results?t=report"

raw_findings=json.load(open(SCR/"report_findings_raw.json"))
CRE=re.compile(r'([A-Za-z][A-Za-z0-9]*(?:Branch|Adapter|Vault|Engine|Keeper|Proxy|Configuration|Config|Distribution|Delegation|Market|Token))|([A-Za-z0-9_]+\.sol)')
def contracts_of(text):
    s=set()
    for m in CRE.finditer(text or ""):
        s.add(m.group(1) or m.group(2))
    return sorted(x for x in s if x)

findings=[]
sev_counter={"High":0,"Medium":0,"Low":0}
for rf in raw_findings:
    sev=SEVNAME.get(rf.get("severity","low"),"Low")
    issues=rf.get("issues") or []
    rep=issues[0] if issues else {}
    title=(rep.get("title") or "").strip()
    body=rep.get("content") or rep.get("body") or rep.get("description") or ""
    text=title+" \n "+body
    sev_counter[sev]+=1
    findings.append({
        "answer_key_id":None,
        "report_finding_id":rf.get("id"),
        "selected_issue_id":rf.get("selectedIssueId"),
        "severity":sev,
        "validity":"validated_selected_for_report",
        "selectedForReport":True,
        "title":title,
        "duplicate_count":len(issues),
        "alt_titles":[(i.get("title") or "") for i in issues[1:8]],
        "affected_contracts":contracts_of(text),
        "affected_functions":sorted(set(re.findall(r'`([a-zA-Z_][a-zA-Z0-9_]{2,})\(?`?', text)))[:12],
        "root_cause":title,
        "impact":"",
        "proof_summary":(body[:400] if body else ""),
        "source_url":REPORT_URL,
        "report_url":REPORT_URL,
        "tags":[],
        "duplicate_relationships":[f"{len(issues)} merged submission(s)"],
    })

order={"High":0,"Medium":1,"Low":2}
findings.sort(key=lambda f:(order[f["severity"]], -f["duplicate_count"], f["title"].lower()))
sc={"High":0,"Medium":0,"Low":0}
for f in findings:
    sc[f["severity"]]+=1
    f["answer_key_id"]=f"{f['severity'][0]}-{sc[f['severity']]:02d}"

raw={"generated_at":NOW,"program":"Zaros Part 2","contest_slug":"2025-01-zaros-part-2",
     "source":"CodeHawks final report (selected-for-report findings) embedded in results?t=report page payload",
     "source_url":REPORT_URL,"report_url":REPORT_URL,
     "access_note":"Parsed POST-FREEZE from report.html captured after pre_answer_key_snapshot/MANIFEST.json. "
                   "70 report findings = official 16 High / 35 Medium / 19 Low.",
     "counts":sev_counter,"total":len(findings),"findings":findings}
(AK/"answer_key_raw.json").write_text(json.dumps(raw,indent=2))

norm=[{"answer_key_id":f["answer_key_id"],"severity":f["severity"],"title":f["title"],
       "affected_contracts":f["affected_contracts"],"affected_functions":f["affected_functions"],
       "root_cause":f["root_cause"],"duplicate_count":f["duplicate_count"],
       "alt_titles":f["alt_titles"],"source_url":f["source_url"]} for f in findings]
(AK/"answer_key_normalized.json").write_text(json.dumps(
    {"generated_at":NOW,"program":"Zaros Part 2","counts":sev_counter,"total":len(norm),
     "dedup_method":"CodeHawks report families (already root-cause deduped by judges)","findings":norm},indent=2))

md=["# Zaros Part 2 — Answer Key (CodeHawks final report, selected-for-report + validated)",
    f"\nSource: {REPORT_URL} (parsed from page payload, post-freeze)",
    f"\nTotal: {len(findings)} findings — High {sev_counter['High']}, Medium {sev_counter['Medium']}, Low {sev_counter['Low']}.\n"]
for f in findings:
    md.append(f"## [{f['answer_key_id']}] ({f['severity']}) {f['title']}")
    if f['affected_contracts']: md.append(f"- Contracts: {', '.join(f['affected_contracts'][:6])}")
    md.append("")
(AK/"answer_key.md").write_text("\n".join(md))

(AK/"invalid_or_nonselected_findings.json").write_text(json.dumps(
    {"generated_at":NOW,"note":"Only the 70 selected-for-report findings are exposed in the public report "
     "payload. Non-selected/invalid submissions not collected for FP calibration.","findings":[]},indent=2))

print(f"ANSWER_KEY total={len(findings)} High={sev_counter['High']} Medium={sev_counter['Medium']} Low={sev_counter['Low']}")
for f in findings[:16]:
    print(f"{f['answer_key_id']} {f['severity'][:4]:4} {f['title'][:66]} | {','.join(f['affected_contracts'][:2])}")
