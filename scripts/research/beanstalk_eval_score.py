#!/usr/bin/env python3
"""P298 — beanstalk eval scorer (RESEARCH-ONLY, ADVISORY). Consolidates three axes into a scorecard:

  answer-key  : recall/precision of the existing 44 merged findings vs the awarded set, READ from the prior eval2
                match_matrix (read-only) + ground_truth accepted. (Discovery is pre-existing; not re-judged here.)
  novelty     : per-finding KB similarity (from novelty.json, produced by beanstalk_eval_novelty.py).
  validity    : executed-PoC verdicts for the awarded-matched loci (from the P298 validity loop_results.json) +
                evidence-bundle/needs_execution for the entangled tail. confirmed = executed PASS only (FP=0).

Answer key + ground_truth are READ-ONLY (used only to score). Emits scorecard.json + match_matrix.json.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_beanstalk_eval.json").read_text())
OUT = ROOT / "documentation/research/assisted_mode/p298_beanstalk_eval/outputs"
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None, "reportable": False,
          "submission_ready": False, "concluded": False, "production_routing": False, "auto_submitted": False}


def _read(p):
    return json.loads((ROOT / p).read_text())


def _gt_accepted():
    return [json.loads(l) for l in (ROOT / CFG["ground_truth"]).read_text().splitlines()
            if l.strip() and json.loads(l).get("ground_truth_outcome") == "accepted"]


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    mm = _read(CFG["answer_key_match_matrix"])
    tally = mm.get("tally", {})
    ak = mm.get("total_public")
    hit, part, adj, miss = tally.get("HIT", 0), tally.get("PARTIAL", 0), tally.get("ADJACENT", 0), tally.get("MISS", 0)
    pipeline_only = len(mm.get("pipeline_only_unmatched") or [])
    accepted = _gt_accepted()

    answer_key = {
        "answer_key_size": ak, "run_scored": mm.get("run"),
        "tally": {"HIT": hit, "PARTIAL": part, "ADJACENT": adj, "MISS": miss},
        "recall_useful": round((hit + part) / ak, 3) if ak else None,
        "recall_any_touch": round((hit + part + adj) / ak, 3) if ak else None,
        "platform_confirmed_accepted": len(accepted),
        "pipeline_only_unmatched": pipeline_only,
        "note": "answer-key match is the PRIOR eval2 semantic-judge result (read-only); P298 does NOT re-discover, so "
                "recall is the current setup's existing recall. P298 adds the novelty + executed-validity axes."}

    novelty = _read("documentation/research/assisted_mode/p298_beanstalk_eval/outputs/novelty.json") \
        if (OUT / "novelty.json").exists() else None
    validity = _read("documentation/research/assisted_mode/p298_beanstalk_eval/outputs/loop_results.json") \
        if (OUT / "loop_results.json").exists() else None

    # per-accepted-locus consolidated row (matched=yes by definition of accepted; + novel? + valid?)
    nov_by_id = {n["id"]: n for n in (novelty or {}).get("findings", [])} if novelty else {}
    val_by_id = {}
    if validity:
        for r in validity.get("results", []):
            val_by_id[r.get("awarded_id")] = r
    rows = []
    for a in accepted:
        fid = a["finding_id"]
        v = val_by_id.get(fid, {})
        n = nov_by_id.get(fid, {})
        tgt = next((t for t in CFG["validity_targets"] if t["id"] == fid), {})
        rows.append({"id": fid, "severity": a.get("ground_truth_severity"), "title": a.get("title", "")[:80],
                     "answer_key": "accepted/platform_confirmed",
                     "novelty": n.get("novelty_class"), "novelty_sim": n.get("top_similarity"),
                     "build_mode": tgt.get("build_mode"),
                     "validity": (v.get("verifier_verdict") or v.get("status")
                                  or ("needs_execution" if tgt.get("build_mode") == "bundle" else "pending")),
                     "attacker_verified": bool(v.get("attacker_verified"))})

    confirmed = [r for r in rows if r["attacker_verified"]]
    needs_exec = [r for r in rows if r["validity"] in ("needs_execution", "setup_only", "pending")]
    refuted = [r for r in rows if r["validity"] in ("refuted_by_execution", "no_exploit_test")]
    confirmed_fp = (validity or {}).get("confirmed_false_positive_count", 0) if validity else 0

    scorecard = dict(_STAMP, label="P298_BEANSTALK_EVAL", contest=mm.get("contest"),
                     discovery="pre-existing (44 merged findings; eval2 run); NOT a fresh blind discovery",
                     answer_key_axis=answer_key,
                     novelty_axis=(novelty or {}).get("distribution") if novelty else "pending",
                     validity_axis={"targets": len(CFG["validity_targets"]),
                                    "confirmed_by_execution": len(confirmed),
                                    "confirmed_loci": [r["id"] for r in confirmed],
                                    "refuted": [r["id"] for r in refuted],
                                    "needs_execution_or_bundle": [r["id"] for r in needs_exec],
                                    "confirmed_false_positive_count": confirmed_fp},
                     accepted_loci=rows)
    (OUT / "scorecard.json").write_text(json.dumps(scorecard, indent=2))
    (OUT / "match_matrix.json").write_text(json.dumps(dict(_STAMP, **answer_key,
        accepted=[{k: r[k] for k in ("id", "severity", "title")} for r in rows]), indent=2))
    # read-only integrity: hash the answer-key + source-root marker
    ak_hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16]
                 for p in (CFG["answer_key_match_matrix"], CFG["ground_truth"]) if (ROOT / p).exists()}
    (OUT / "answer_key_hashes.json").write_text(json.dumps(ak_hashes, indent=2))
    print(json.dumps({"answer_key": answer_key, "validity": scorecard["validity_axis"],
                      "novelty": scorecard["novelty_axis"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
