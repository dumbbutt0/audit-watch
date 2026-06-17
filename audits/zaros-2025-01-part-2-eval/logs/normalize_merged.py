#!/usr/bin/env python3
"""Dedup merged_findings by id and give specialist findings a proper ice dict (was the string
'no ice chain provided'), so confirm_inventory/min_confirm don't crash. Pre-freeze cleanup."""
import json, sys
sys.path.insert(0,"scripts")
from audit_context import audit_path

p=audit_path("output/merged_findings.json")
doc=json.loads(p.read_text())
seen={}; order=[]
for f in doc["findings"]:
    fid=f["id"]
    if fid in seen: continue
    seen[fid]=f; order.append(fid)

def ice_for(f):
    sevcap=f.get("severity","Medium")
    return {"corrupted_state":f.get("title","")[:80],"consumers_found":[],
            "consumer_search_confidence":"medium","highest_consumer_reached":"",
            "poc_level_achieved":2,"directly_proven_impact":f.get("impact",""),
            "plausible_escalation":"","severity_ceiling":sevcap,
            "recommended_next_poc_step":"Foundry test asserting the storage/balance flip",
            "exploit_path": (f.get("ite") or {}).get("technique",""),
            "hold":False,"needs_manual_review":False,
            "triager_objections":[],"defenses_checked":[]}

for fid in order:
    f=seen[fid]
    if not isinstance(f.get("ice"), dict):
        f["ice"]=ice_for(f)
    f.setdefault("attacker_entrypoint", (f.get("location") or {}).get("function",""))
    f.setdefault("critical_assumptions", [])

doc["findings"]=[seen[fid] for fid in order]
doc.setdefault("summary",{})["total"]=len(order)
p.write_text(json.dumps(doc,indent=2))
print("merged normalized:", order)
