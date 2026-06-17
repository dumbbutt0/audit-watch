#!/usr/bin/env python3
"""P302 — true-blind reach test (RESEARCH-ONLY, ADVISORY).

Measures how far the DISCOVERY pipeline reaches on a program we have NOT audited: of a contest's awarded
findings, what fraction does a COLD pipeline run even SURFACE (recall_of_surfaced = the discovery ceiling,
distinct from the recovery loop's recall_of_confirmed). No PoC/recovery — reach is a surfacing measure.

  freeze <target>          : (BEFORE discovery) hash in-scope .sol, assert no prior discovery output exists,
                             record that the sealed key is unread -> outputs/freeze_manifest.json
  extract-awarded <target> : (AFTER discovery) parse the sealed C4 report.md High/Medium headers (the deduped
                             awarded denominator) READ-ONLY -> outputs/awarded_findings.json
  score <target>           : read awarded_findings.json + merged_findings.json + an in-session adjudication
                             (outputs/adjudication.json: {id: {match_level, surfaced_id, evidence}}) ->
                             tiered recall_of_surfaced -> outputs/reach_report.json

Sealed answer key + contest source READ-ONLY. Never writes ground_truth / severity / submission. Conventional
paths: audits/<id>/contracts, audits/<id>/_sealed_answer_key/report.md, audits/<id>/output/merged_findings.json.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coverage_completeness_report as ccr  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/research/assisted_mode/p302_blind_reach_test/outputs"
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None,
          "auto_submitted": False, "reportable": False, "submission_ready": False, "routes_in_production": False}
# reuse the P287/P295 reveal-score match vocabulary
LEVELS = ("STRONG_MECHANISM_MATCH", "SAME_AREA_WRONG_MECHANISM", "SUBSYSTEM_ONLY_RECALL", "MISSED")
_RECALLED = {"STRONG_MECHANISM_MATCH", "SAME_AREA_WRONG_MECHANISM", "SUBSYSTEM_ONLY_RECALL"}


def _out(target):
    # per-target outputs dir so multiple reach tests coexist (P302 pooltogether stays at the top-level OUT)
    return OUT / target


def _audit(target):
    return ROOT / "audits" / target


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sol_files(target):
    src = _audit(target) / "contracts"
    return sorted(p for p in src.rglob("*.sol") if "lib/" not in str(p.relative_to(src)))


def freeze(target):
    od = _out(target)
    od.mkdir(parents=True, exist_ok=True)
    out_dir = _audit(target) / "output"
    prior = sorted(out_dir.glob("findings_*.json")) + sorted(out_dir.glob("merged_findings.json"))
    files = _sol_files(target)
    man = dict(_STAMP, label="P302_BLIND_REACH_FREEZE", target=target, frozen_at=_now(),
               sealed_key_read=False, prior_discovery_present=bool(prior),
               prior_discovery=[str(p.relative_to(ROOT)) for p in prior],
               source_file_count=len(files),
               source_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                              for p in files})
    (od / "freeze_manifest.json").write_text(json.dumps(man, indent=2))
    print(json.dumps({"target": target, "frozen_files": len(files), "prior_discovery_present": bool(prior),
                      "blind_ok": not prior, "frozen_at": man["frozen_at"]}, indent=2))
    return 0 if not prior else 1


def extract_awarded(target):
    """Parse the sealed C4 report.md for the deduped awarded High/Medium findings (the reach denominator)."""
    report = _audit(target) / "_sealed_answer_key" / "report.md"
    txt = report.read_text()
    # section gate so Low/QA/Gas headers are excluded
    sev = None
    awarded = []
    for line in txt.splitlines():
        h = re.match(r"^#\s+(High|Medium)\s+Risk\s+Findings", line, re.I)
        if h:
            sev = h.group(1).title()
            continue
        if re.match(r"^#\s+(Low|Gas|Non|QA|Analysis|Audit|Disclosures)", line, re.I):
            sev = None
            continue
        m = re.match(r"^##\s+\[\[([HM]-\d+)\]\s+(.*?)\]\(", line)
        if m and sev:
            awarded.append({"id": m.group(1), "severity": sev, "title": m.group(2).strip()})
    out = dict(_STAMP, label="P302_AWARDED", target=target, extracted_at=_now(),
               report_sha256=hashlib.sha256(report.read_bytes()).hexdigest()[:16],
               awarded_count=len(awarded), awarded=awarded)
    od = _out(target)
    od.mkdir(parents=True, exist_ok=True)
    (od / "awarded_findings.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"target": target, "awarded": len(awarded),
                      "high": sum(1 for a in awarded if a["severity"] == "High"),
                      "medium": sum(1 for a in awarded if a["severity"] == "Medium")}))
    return 0


def score(target):
    od = _out(target)
    awarded = json.loads((od / "awarded_findings.json").read_text())["awarded"]
    adj = json.loads((od / "adjudication.json").read_text())  # {id: {match_level, surfaced_id, evidence}}
    merged_path = _audit(target) / "output" / "merged_findings.json"
    surfaced_n = 0
    if merged_path.exists():
        md = json.loads(merged_path.read_text())
        surfaced_n = len(md.get("findings", md if isinstance(md, list) else []))
    per_locus, miss = [], []
    for a in awarded:
        a_adj = adj.get(a["id"], {})
        lvl = a_adj.get("match_level", "MISSED")
        if lvl not in LEVELS:
            raise SystemExit(f"bad match_level for {a['id']}: {lvl}")
        per_locus.append({"id": a["id"], "severity": a["severity"], "title": a["title"],
                          "match_level": lvl, "surfaced_id": a_adj.get("surfaced_id"),
                          "evidence": a_adj.get("evidence", "")})
        if lvl == "MISSED":
            miss.append(a["id"])
    n = len(awarded)
    strong = sum(1 for p in per_locus if p["match_level"] == "STRONG_MECHANISM_MATCH")
    area = sum(1 for p in per_locus if p["match_level"] == "SAME_AREA_WRONG_MECHANISM")
    sub = sum(1 for p in per_locus if p["match_level"] == "SUBSYSTEM_ONLY_RECALL")
    recalled = strong + area + sub
    rep = dict(_STAMP, label="P302_REACH_REPORT", target=target, scored_at=_now(),
               totals={"awarded": n, "surfaced_findings_total": surfaced_n,
                       "strong": strong, "same_area": area, "subsystem": sub, "missed": len(miss)},
               recall_of_surfaced=round(recalled / n, 3) if n else 0.0,
               recall_strong_only=round(strong / n, 3) if n else 0.0,
               recall_strong_or_area=round((strong + area) / n, 3) if n else 0.0,
               missed_ids=miss, per_locus=per_locus)
    # P309: coverage-awareness — a reach number is only a true ceiling at 100% coverage; otherwise it is PARTIAL
    # and the unexamined files are surfaced so "missed because not read" can never be reported silently.
    try:
        cov = ccr.coverage_report(target)
        rep["coverage"] = {"in_scope": cov["in_scope"], "resolved": cov["resolved"],
                           "unexamined": cov["unexamined"], "coverage_percent": cov["coverage_percent"],
                           "complete": cov["complete"], "unexamined_file_count": cov["unexamined_file_count"],
                           "unexamined_files": [{"file": u["file"], "unexamined": u["unexamined"],
                                                 "max_score": u["max_score"]} for u in cov["unexamined_files"][:30]]}
        rep["result_status"] = "complete" if cov["complete"] else "partial"
    except (OSError, json.JSONDecodeError, KeyError):
        rep["coverage"] = {"error": "no coverage_manifest/dispositions for target"}
        rep["result_status"] = "unknown_coverage"
    (od / "reach_report.json").write_text(json.dumps(rep, indent=2))
    out = {k: rep[k] for k in ("recall_of_surfaced", "recall_strong_or_area", "recall_strong_only", "totals")}
    out["result_status"] = rep["result_status"]
    if rep.get("coverage", {}).get("complete") is False:
        c = rep["coverage"]
        out["coverage_warning"] = (f"PARTIAL — coverage {c['coverage_percent']}%; {c['unexamined']} in-scope items "
                                   f"unexamined across {c['unexamined_file_count']} files; NOT a true ceiling")
    print(json.dumps(out, indent=2))
    return 0


def coverage(target):
    rep = ccr.coverage_report(target)
    od = _out(target)
    od.mkdir(parents=True, exist_ok=True)
    (od / "coverage_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps({k: rep[k] for k in ("target", "coverage_percent", "in_scope", "resolved",
                      "unexamined", "complete", "unexamined_file_count")}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["freeze", "extract-awarded", "score", "coverage"])
    ap.add_argument("target")
    a = ap.parse_args()
    return {"freeze": freeze, "extract-awarded": extract_awarded, "score": score,
            "coverage": coverage}[a.cmd](a.target)


if __name__ == "__main__":
    raise SystemExit(main())
