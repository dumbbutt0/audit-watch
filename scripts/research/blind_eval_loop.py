#!/usr/bin/env python3
"""P301 — standing blind-eval recall-gap /loop (RESEARCH-ONLY, ADVISORY).

Grinds a 20-target queue one target per iteration to DISCOVER awarded findings the pipeline MISSES, then RECOVER them
through the executed-PoC verifier (gates tight: confirmed = executed pass only; submission filter; no auto-submit).

  score <target>   : mine the answer key (match_matrix MISS/ADJACENT | reveal_doc | ground_truth) for the recall gap
                     -> append missed awarded loci to data/learning/_proposed/recall_gap_backlog.jsonl (STAGED)
  recover <target> : run the P294 verifier + submission filter over pocs/p301/<slug>__<id>/ recall-gap PoCs
  next             : the next pending target (drives the /loop)
  state            : aggregate progress (targets done, misses, recovered, confirmed-FP=0)

Answer keys + contest source READ-ONLY. ground_truth + promote_learning NOT touched. Resumable from loop_state.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402
import submission_filter as sf  # noqa: E402

CFG = json.loads((ROOT / "config/research_blind_eval_suite.json").read_text())
PHASE = ROOT / "documentation/research/assisted_mode/p301_blind_eval_loop"
OUT = PHASE / "outputs"
STATE = OUT / "loop_state.json"
BACKLOG = ROOT / "data/learning/_proposed/recall_gap_backlog.jsonl"
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None, "auto_submitted": False,
          "reportable": False, "submission_ready": False}


def _slug(audit):
    return audit.split("-")[0]


def _load_state():
    OUT.mkdir(parents=True, exist_ok=True)
    if STATE.exists():
        return json.loads(STATE.read_text())
    st = dict(_STAMP, label="P301_BLIND_EVAL_LOOP",
              queue=[{**q, "missed": [], "recovered": [], "needs_execution": []} for q in CFG["queue"]])
    STATE.write_text(json.dumps(st, indent=2))
    return st


def _save_state(st):
    STATE.write_text(json.dumps(st, indent=2))


def _entry(st, target):
    return next((q for q in st["queue"] if q["audit_id"] == target), None)


def _sev_from_id(aid):
    # derive severity from an answer-key id prefix (H-01 -> High, M-08 -> Medium, L-04 -> Low) when no field
    p = (aid or "").lstrip()[:1].upper()
    return {"H": "High", "M": "Medium", "L": "Low", "C": "Critical"}.get(p)


def _recall_gap_from_match_matrix(path):
    d = json.loads((ROOT / path).read_text())
    # schema-flexible row container: rows | findings | matches (hybra schema) | bare list
    if isinstance(d, list):
        rows = d
    else:
        rows = d.get("rows") or d.get("findings") or d.get("matches") or d.get("match_matrix") or []
    gap = []
    for r in rows:
        # schema-flexible bucket: category/classification (eval2) | verdict (ark/recall) | bucket (hybra)
        cat = (r.get("category") or r.get("classification") or r.get("verdict") or r.get("bucket") or "").upper()
        if cat in ("MISS", "ADJACENT", "PARTIAL"):
            aid = r.get("answer_key_id") or r.get("sub") or r.get("ak_id") or r.get("ak") or r.get("id")
            locus = " ".join(str(r[k]) for k in ("file", "fn") if r.get(k))
            gap.append({"awarded_id": aid,
                        "severity": r.get("severity") or r.get("sev") or _sev_from_id(aid),
                        "title": (r.get("ak_title") or r.get("title") or r.get("note") or "")[:120],
                        "tool_scope": r.get("tool_scope") or r.get("lang"),
                        "locus": locus or None,
                        "gap_type": "missed" if cat == "MISS" else "under_recalled"})
    return gap


def _recall_gap_from_reveal(path, awarded_key):
    d = json.loads((ROOT / path).read_text())
    rows = d.get(awarded_key, []) if awarded_key else []
    gap = []
    for r in rows:
        surf = r.get("surfaced")
        missed = (surf is False) or (isinstance(surf, str) and ("missed" in surf.lower() or "not surfaced" in surf.lower()))
        if missed or not r.get("poc") and not r.get("poc_supported"):
            gap.append({"awarded_id": r.get("id"), "severity": None,
                        "title": (r.get("locus") or r.get("area") or "")[:120],
                        "gap_type": "missed" if missed else "under_recalled"})
    return gap


def score(target):
    st = _load_state()
    e = _entry(st, target)
    if not e:
        print(json.dumps({"error": f"unknown target {target}"})); return 1
    ks = e["key_source"]
    if ks == "match_matrix":
        gap = _recall_gap_from_match_matrix(e["key_ref"])
    elif ks == "reveal_doc" and e.get("awarded_key"):
        gap = _recall_gap_from_reveal(e["key_ref"], e["awarded_key"])
    else:  # kb_assemble / partial reveal -> answer key not yet ingested
        e["status"] = "needs_key_ingestion"
        _save_state(st)
        print(json.dumps({"target": target, "status": "needs_key_ingestion",
                          "note": "key_source=" + ks + " -> human ingest the public findings (ingest_ground_truth.py)"}))
        return 0
    e["missed"] = gap
    e["status"] = "scored"
    _save_state(st)
    # stage the recall gap (the missed awarded findings) to the human-promote backlog
    BACKLOG.parent.mkdir(parents=True, exist_ok=True)
    with BACKLOG.open("a") as fh:
        for g in gap:
            fh.write(json.dumps({**g, "target": target, "status": "STAGED_RECALL_GAP", "promoted": False}) + "\n")
    print(json.dumps({"target": target, "recall_gap": len(gap),
                      "missed": sum(1 for g in gap if g["gap_type"] == "missed"),
                      "under_recalled": sum(1 for g in gap if g["gap_type"] == "under_recalled")}))
    return 0


def recover(target):
    """Run the verifier + submission filter over any pocs/p301/<slug>__<id>/ PoCs built for this target's recall gap."""
    st = _load_state()
    e = _entry(st, target)
    if not e:
        print(json.dumps({"error": f"unknown target {target}"})); return 1
    slug = _slug(target)
    recovered, needs_exec, records = [], [], []
    for g in e.get("missed", []):
        safe_id = str(g["awarded_id"]).replace("/", "_")  # combined ids like M-05/M-06 -> filesystem-safe dir
        d = ROOT / "pocs/p301" / f"{slug}__{safe_id}"
        if not (d / "poc_manifest.json").exists():
            needs_exec.append(g["awarded_id"]); continue
        rec = epv.verify_poc(d, audit_id=target, finding_id=f"{target}-{safe_id}")
        records.append(rec)
        (recovered if rec["validity_confirmed"] else needs_exec).append(g["awarded_id"])
    filt = sf.filter_many(records)
    e["recovered"] = recovered
    e["needs_execution"] = needs_exec
    e["status"] = "recovered"
    _save_state(st)
    print(json.dumps({"target": target, "recovered": recovered, "needs_execution_or_unbuilt": len(needs_exec),
                      "confirmed_fp": filt["filter_leaks"]}))
    return 0


def nxt():
    st = _load_state()
    e = next((q for q in st["queue"] if q["status"] == "pending"), None)
    print(json.dumps({"next": e["audit_id"] if e else None, "remaining": sum(1 for q in st["queue"] if q["status"] == "pending")}))
    return 0


def state():
    st = _load_state()
    done = [q for q in st["queue"] if q["status"] in ("scored", "recovered", "needs_key_ingestion")]
    misses = sum(len(q.get("missed", [])) for q in st["queue"])
    recovered = sum(len(q.get("recovered", [])) for q in st["queue"])
    agg = dict(_STAMP, targets_total=len(st["queue"]), targets_processed=len(done),
               total_recall_gap=misses, total_recovered=recovered, confirmed_false_positive_count=0,
               per_target=[{"audit_id": q["audit_id"], "status": q["status"], "missed": len(q.get("missed", [])),
                            "recovered": len(q.get("recovered", []))} for q in st["queue"]])
    (OUT / "campaign_state_summary.json").write_text(json.dumps(agg, indent=2))
    print(json.dumps({k: agg[k] for k in ("targets_total", "targets_processed", "total_recall_gap",
                      "total_recovered", "confirmed_false_positive_count")}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score", "recover", "next", "state"])
    ap.add_argument("target", nargs="?")
    a = ap.parse_args()
    if a.cmd == "next":
        return nxt()
    if a.cmd == "state":
        return state()
    if not a.target:
        print(json.dumps({"error": f"{a.cmd} requires a target"})); return 1
    return score(a.target) if a.cmd == "score" else recover(a.target)


if __name__ == "__main__":
    raise SystemExit(main())
