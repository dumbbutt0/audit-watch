#!/usr/bin/env python3
"""Fetch all 7 pages of selected-for-report + validated submissions (the answer key) from the
CodeHawks backend. POST-FREEZE, user-authorized. Tries several endpoint shapes; saves raw pages."""
import urllib.request, urllib.parse, json
from pathlib import Path
OUT=Path("audits/zaros-2025-01-part-2-eval/logs/scrape"); OUT.mkdir(parents=True,exist_ok=True)
CID="cm64lp3sj0001l50fxr1bnf3w"
UA={"User-Agent":"Mozilla/5.0","Accept":"application/json"}
def t(u):
    try:
        b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read()
        return b
    except Exception as e:
        return f"ERR {getattr(e,'code','')} {type(e).__name__}".encode()

# discover working base+path by fetching page 1 and matching the 20 we already have
bases=["https://api.codehawks.cyfrin.io","https://codehawks.cyfrin.io/api"]
paths=[
 "/submissions?contestId={cid}&selectedForReport=selectedForReport&validated=validated&page={p}",
 "/contests/{cid}/submissions?selectedForReport=selectedForReport&validated=validated&page={p}",
 "/contests/{cid}/submissions?selectedForReport=true&validated=true&page={p}",
 "/submissions?contestId={cid}&selectedForReport=true&validated=true&page={p}&limit=20",
]
log=[]; working=None
for b in bases:
    for pt in paths:
        u=b+pt.format(cid=CID,p=1)
        r=t(u)
        ok = not r.startswith(b"ERR")
        try:
            j=json.loads(r); n=len(j.get("data",j)) if isinstance(j,dict) else len(j)
        except Exception:
            n=0; ok=False
        log.append(f"{'OK' if ok else 'no'} n={n} {u}")
        if ok and n>0:
            working=(b,pt); break
    if working: break

if working:
    b,pt=working
    allitems=[]
    for p in range(1,8):
        u=b+pt.format(cid=CID,p=p)
        r=t(u)
        (OUT/f"ak_api_page{p}.json").write_bytes(r)
        try:
            j=json.loads(r); items=j.get("data",j) if isinstance(j,dict) else j
            allitems+=items; log.append(f"page{p}: {len(items)} items")
        except Exception as e:
            log.append(f"page{p}: parse err {e}")
    (OUT/"ak_all_submissions.json").write_text(json.dumps(allitems,indent=1))
    log.append(f"TOTAL {len(allitems)} submissions")
else:
    log.append("NO WORKING ENDPOINT")
(OUT/"fetch_ak_log.txt").write_text("\n".join(log))
print("\n".join(log[-12:]))
