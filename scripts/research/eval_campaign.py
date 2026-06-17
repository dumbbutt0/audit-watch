#!/usr/bin/env python3
"""P300 — multi-target calibration campaign (RESEARCH-ONLY, ADVISORY).

Per target: recall (read-only from match_matrix) + novelty (KB chroma) + executed-PoC validity (P294 verifier over
pocs/p300/<slug>__<id>/, exploit OR logic_differential) -> per-target + aggregate scorecard. Runs the submission
filter over all validity records (confirmed-FP must be 0). Answer keys + contest source READ-ONLY.

Usage: python scripts/research/eval_campaign.py [recall_novelty|validity|all]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402
import submission_filter as sf  # noqa: E402

CFG = json.loads((ROOT / "config/research_eval_campaign.json").read_text())
OUT = ROOT / "documentation/research/assisted_mode/p300_calibration_campaign/outputs"
THRESH = float(CFG["novelty_threshold"])
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None, "reportable": False,
          "submission_ready": False, "concluded": False, "auto_submitted": False}


def _slug(t):
    return t.split("-")[0]  # silo / revert / panoptic


def _recall(spec):
    d = json.loads((ROOT / spec["match_matrix"]).read_text())
    rows = d.get("rows", []) if isinstance(d, dict) else d
    c = Counter((r.get("category") or r.get("classification") or "?") for r in rows if isinstance(r, dict))
    ak = (d.get("total_public") or d.get("answer_key_size") or len(rows)) if isinstance(d, dict) else len(rows)
    hit, part, adj = c.get("HIT", 0), c.get("PARTIAL", 0), c.get("ADJACENT", 0)
    return {"answer_key_size": ak, "tally": dict(c),
            "recall_useful": round((hit + part) / ak, 3) if ak else None,
            "recall_any_touch": round((hit + part + adj) / ak, 3) if ak else None,
            "pipeline_only_fp": len(d.get("false_positives") or d.get("pipeline_only_unmatched") or []) if isinstance(d, dict) else 0}


def _novelty(spec, model, col, space):
    mf = json.loads((ROOT / spec["merged_findings"]).read_text())
    findings = mf if isinstance(mf, list) else mf.get("findings", [])
    rows = []
    for f in findings:
        text = (f.get("title", "") + ". " + (f.get("description", "") or ""))[:2000]
        emb = model.encode([text], normalize_embeddings=True)[0].tolist()
        res = col.query(query_embeddings=[emb], n_results=1, include=["distances"])
        dists = (res.get("distances") or [[None]])[0]
        d0 = dists[0] if dists and dists[0] is not None else None
        sim = None if d0 is None else (round(1 - d0, 3) if space == "cosine" else round(1 - d0 * d0 / 2, 3))
        rows.append({"id": f.get("id"), "severity": f.get("severity"), "top_similarity": sim,
                     "novelty_class": "novel" if (sim is not None and sim < THRESH) else "known_or_duplicate"})
    nv = sum(1 for r in rows if r["novelty_class"] == "novel")
    hc_novel = [r["id"] for r in rows if r["novelty_class"] == "novel" and str(r["severity"]).lower() in ("high", "critical")]
    return {"n": len(rows), "novel": nv, "known": len(rows) - nv, "high_critical_novel_to_human": hc_novel}


def _validity(target, spec):
    slug = _slug(target)
    records, rows = [], []
    for t in spec["validity_targets"]:
        d = ROOT / "pocs/p300" / f"{slug}__{t['id']}"
        man = d / "poc_manifest.json"
        if not man.exists():
            rows.append({"id": t["id"], "build_mode": t["build_mode"], "status": "not_built",
                         "validity_confirmed": False})
            continue
        rec = epv.verify_poc(d, audit_id=target, finding_id=f"{target}-{t['id']}")
        records.append(rec)
        rows.append({"id": t["id"], "build_mode": t["build_mode"], "status": rec["status"],
                     "validity_confirmed": rec["validity_confirmed"], "attacker_verified": rec["attacker_verified"],
                     "logic_verified": rec["logic_verified"]})
    confirmed = [r for r in rows if r["validity_confirmed"]]
    return {"targets": len(spec["validity_targets"]), "confirmed": [r["id"] for r in confirmed],
            "confirmed_count": len(confirmed), "rows": rows}, records


def run(phase):
    OUT.mkdir(parents=True, exist_ok=True)
    model = col = space = None
    if phase in ("recall_novelty", "all"):
        import chromadb
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(CFG["novelty_model"])
        client = chromadb.PersistentClient(path=str(ROOT / "kb/chroma"))
        col = client.get_collection(CFG["novelty_collection"])
        space = (col.metadata or {}).get("hnsw:space", "cosine")

    per_target, all_records = {}, []
    for target, spec in CFG["targets"].items():
        entry = {"recall": _recall(spec)}
        if model is not None:
            entry["novelty"] = _novelty(spec, model, col, space)
        elif (OUT / "campaign_scorecard.json").exists():
            entry["novelty"] = json.loads((OUT / "campaign_scorecard.json").read_text())["per_target"].get(target, {}).get("novelty")
        val, recs = _validity(target, spec)
        entry["validity"] = val
        all_records += recs
        per_target[target] = entry

    # beanstalk reuse (P298 exploit + P299 logic)
    bw = CFG["beanstalk_reuse"]
    beanstalk_confirmed = bw["exploit_confirmed"] + bw["logic_confirmed"]

    filt = sf.filter_many(all_records)
    confirmed_fp = filt["filter_leaks"]  # any submit-labelled without a real executed confirmation
    targets_with_confirmation = [t for t, e in per_target.items() if e["validity"]["confirmed_count"] > 0]
    if beanstalk_confirmed:
        targets_with_confirmation = targets_with_confirmation + ["beanstalk-2024-05"]

    scorecard = dict(_STAMP, label="P300_CALIBRATION_CAMPAIGN", per_target=per_target,
                     beanstalk_reuse={"confirmed": beanstalk_confirmed, "count": len(beanstalk_confirmed)},
                     aggregate={
                         "targets_evaluated": len(per_target) + 1,
                         "targets_with_a_confirmation": len(targets_with_confirmation),
                         "targets_with_a_confirmation_list": targets_with_confirmation,
                         "total_loci_confirmed_this_campaign": sum(e["validity"]["confirmed_count"] for e in per_target.values()),
                         "cumulative_recall_of_confirmed_incl_beanstalk": sum(e["validity"]["confirmed_count"] for e in per_target.values()) + len(beanstalk_confirmed),
                         "confirmed_false_positive_count": confirmed_fp,
                         "submission_filter": {k: filt[k] for k in ("n", "submit", "needs_human", "submit_loci", "filter_leaks")}})
    (OUT / "campaign_scorecard.json").write_text(json.dumps(scorecard, indent=2))
    (OUT / "submission_filter_results.json").write_text(json.dumps(filt, indent=2))
    print(json.dumps({"per_target_recall": {t: e["recall"]["recall_useful"] for t, e in per_target.items()},
                      "per_target_confirmed": {t: e["validity"]["confirmed"] for t, e in per_target.items()},
                      "targets_with_a_confirmation": len(targets_with_confirmation),
                      "confirmed_FP": confirmed_fp,
                      "submission_filter": {k: filt[k] for k in ("submit", "needs_human", "filter_leaks")}}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", nargs="?", default="all", choices=["recall_novelty", "validity", "all"])
    return run(ap.parse_args().phase)


if __name__ == "__main__":
    raise SystemExit(main())
