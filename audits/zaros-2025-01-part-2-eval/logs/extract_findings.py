#!/usr/bin/env python3
"""Extract the embedded findings[] from the CodeHawks report.html RSC payload.
The data is JSON with backslash-escaped quotes inside a JS string. Strategy: locate the
substring starting at '"findings":[' (in escaped form), unescape progressively, and brace-match
to capture the full array, then json.loads."""
import json, re, codecs
from pathlib import Path
SCR=Path("audits/zaros-2025-01-part-2-eval/logs/scrape")
html=open(SCR/"report.html",encoding="utf-8",errors="ignore").read()

# The payload uses \" for quotes (escaped once) and \\n inside markdown. Find the findings array.
key='\\"findings\\":['
i=html.find(key)
assert i>=0, "findings key not found"
arr_start=i+len(key)-1   # position of '['
# brace/bracket match over the escaped text, treating \" as a string delimiter toggle
s=html
depth=0; in_str=False; esc=False; j=arr_start; n=len(s)
# We iterate char by char but quotes appear as the two-char sequence \" -> detect via backslash+quote
out=[]
# Simpler: take a big slice and iteratively unescape, then brace-match on clean JSON.
slice_raw=s[arr_start: arr_start+6_000_000]
# Unescape one level: \" -> ", \\ -> \ , \\n stays as \n after; do minimal: replace \\" with " and \\\\ with \\
# The HTML has sequences like \\\" (because viewed in python repr). Real bytes: backslash-quote.
# Detect actual escaping by sampling:
sample=slice_raw[:120]
# Count backslashes before quote
def unescape_js(t):
    # turn \" into ", \\ into \, \/ into /
    t=t.replace('\\/','/')
    # handle \\n \\t (literal) later; first collapse \" and \\
    res=[]; k=0; L=len(t)
    while k<L:
        c=t[k]
        if c=='\\' and k+1<L:
            nx=t[k+1]
            if nx=='"': res.append('"'); k+=2; continue
            if nx=='\\': res.append('\\'); k+=2; continue
            if nx=='n': res.append('\n'); k+=2; continue
            if nx=='t': res.append('\t'); k+=2; continue
            if nx=='r': res.append('\r'); k+=2; continue
            if nx=='u': res.append(t[k:k+6]); k+=6; continue
            res.append(nx); k+=2; continue
        res.append(c); k+=1
    return "".join(res)

clean=unescape_js(slice_raw)
# now brace-match a proper JSON array from index 0 ('[')
assert clean[0]=='[', repr(clean[:40])
depth=0; in_str=False; esc=False
for idx,ch in enumerate(clean):
    if in_str:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch=='"': in_str=False
    else:
        if ch=='"': in_str=True
        elif ch=='[' or ch=='{': depth+=1
        elif ch==']' or ch=='}':
            depth-=1
            if depth==0:
                end=idx+1; break
arr_json=clean[:end]
findings=json.loads(arr_json)
(SCR/"report_findings_raw.json").write_text(json.dumps(findings,indent=1)[:5_000_000])
print("FINDINGS", len(findings))
if findings:
    f0=findings[0]
    print("keys", list(f0.keys()))
    from collections import Counter
    print("severity", dict(Counter(f.get("severity") for f in findings)))
    print("selectedIssue.sev", dict(Counter((f.get("SelectedIssue") or {}).get("severity") for f in findings)))
    # title field?
    for cand in ["title","name","Submission","selectedIssue","SelectedIssue"]:
        print(cand, type(f0.get(cand)).__name__, str(f0.get(cand))[:80])
