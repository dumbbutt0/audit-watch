#!/usr/bin/env python3
"""
P175 — Cross-corpus remaining-miss family roadmap (READ-ONLY analysis).

Reads eval match matrices + the P171 quantamm coverage_matrix, normalizes the heterogeneous match-matrix
schemas, tags every answer-key finding with a root-cause family, applies the P174 recovery override to
quantamm, aggregates the REMAINING misses per family across the portfolio, and scores each family by
`remaining_misses * detectability * expected_precision` (plus a severity-weighted variant) to produce a
ranked taxonomy roadmap.

Writes ONLY family_scoring.json next to this file. Touches no production code, answer key, or match matrix.

Run:  python documentation/research/assisted_mode/p175_remaining_miss_family_roadmap/family_roadmap.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # smart-contract-auditor/
P171 = ROOT / "documentation/research/assisted_mode/p171_eval_answer_key_miss_analysis/coverage_matrix.json"
RULES = json.loads((HERE / "family_rules.json").read_text())

RECOVERED_VERDICTS = {"HIT", "PARTIAL", "ADJACENT", "FOUND_EXACT", "FOUND_PARTIAL", "FOUND_ADJACENT"}
SEV_WEIGHT = {"HIGH": 3, "MEDIUM": 2, "MED": 2, "LOW": 1, "CRITICAL": 4, "CRIT": 4}

# (corpus, file, rows_key|None for top-level list, id_key, sev_key, title_key|None, verdict_key)
CORPORA = [
    # fully scorable (carry ak_title)
    ("quantamm", "audits/quantamm-2024-12-eval/output/eval_ready/match_matrix.json",
     "rows", "answer_key_id", "severity", "ak_title", "category"),
    ("panoptic", "audits/panoptic-2025-12-strict-eval/output/eval_ready/match_matrix.json",
     "rows", "answer_key_id", "severity", "ak_title", "category"),
    ("recall", "audits/recall-2025-02-strict-eval/output/eval_ready/match_matrix.json",
     "match_matrix", "id", "sev", "title", "verdict"),
    ("revert-lend", "audits/revert-lend-2024-03-strict-eval/output/eval_ready/match_matrix.json",
     "rows", "answer_key_id", "severity", "ak_title", "category"),
    ("silo", "audits/silo-finance-2025-03-strict-eval/output/eval_ready/match_matrix.json",
     "rows", "answer_key_id", "severity", "ak_title", "category"),
    ("zaros", "audits/zaros-2025-01-part-2-eval/output/eval_ready/eval_match_matrix.json",
     "rows", "answer_key_id", "severity", "ak_title", "category"),
    # coverage-limited (NO title -> counted by severity, NOT family-scored)
    ("ark", "audits/ark-project-2024-07-strict-eval/output/eval_ready/match_matrix.json",
     None, "ak_id", "severity", None, "verdict"),
    ("hybra", "audits/hybra-finance-2025-10-strict-eval/output/eval_ready/match_matrix.json",
     "matches", "ak", None, None, "bucket"),
    ("swan-dria", "audits/swan-dria-2024-10-strict-eval/output/eval_ready/match_matrix.json",
     None, "answer_key_id", "severity", None, "verdict"),
]
# quantamm-strict = duplicate of quantamm corpus (same 44); beanstalk file = upgrades log, not findings. Excluded.


def load_rows(path, rows_key):
    d = json.loads((ROOT / path).read_text())
    if rows_key is None:
        return d if isinstance(d, list) else []
    return d.get(rows_key, [])


def p171_quantamm():
    """{finding_id: (family, miss_class, severity)} from P171 + the P174 recovery override."""
    m = json.loads(P171.read_text())
    out = {}
    for r in m["rows"]:
        if r.get("track") != "recall_quantamm":
            continue
        out[r["finding_id"]] = {"family": r["root_cause_family"], "miss_class": r["miss_class"],
                                "severity": r["severity"]}
    return out


# P174 measured recovery on quantamm (re-surfaced by shipped lenses; these flip miss -> recovered).
P174_QUANTAMM_RECOVERED = (
    {"H-04", "M-04", "M-08", "M-09", "M-12", "M-14"}        # F1 dynamic_weight_lifecycle
    | {"H-09", "H-10", "H-11", "L-06", "L-09"}              # math_estimator (M-07 residual stays a miss)
)


OVERRIDES = RULES.get("manual_overrides", {})


def classify_title(title: str, corpus: str = "", fid: str = "") -> str:
    if f"{corpus}:{fid}" in OVERRIDES:
        return OVERRIDES[f"{corpus}:{fid}"]
    t = (title or "").lower()
    for fam, kws in RULES["rules"]:
        if any(k in t for k in kws):
            return fam
    return "unclassified"


def main() -> int:
    qtags = p171_quantamm()
    # per-family aggregation of REMAINING misses
    fam_remaining = defaultdict(lambda: defaultdict(int))   # family -> corpus -> count
    fam_sevw = defaultdict(int)                             # family -> severity-weighted remaining
    fam_high = defaultdict(list)                            # family -> [high-sev miss ids]
    fam_members = defaultdict(list)                         # family -> ["corpus:id sev | title"]
    unclassified = []
    coverage_limited = {}
    totals = {}

    for corpus, path, rk, idk, sevk, titlek, vk in CORPORA:
        rows = load_rows(path, rk)
        n = len(rows)
        recovered = miss = 0
        scorable = titlek is not None
        for r in rows:
            fid = str(r.get(idk))
            verdict = str(r.get(vk, "")).upper()
            sev = str(r.get(sevk, "") if sevk else "").upper()
            is_recovered = any(verdict.startswith(v) for v in RECOVERED_VERDICTS)

            if corpus == "quantamm":
                # post-P174 override: P171 tag + recovery set is authoritative for this corpus
                tag = qtags.get(fid, {})
                fam = tag.get("family", "unclassified")
                sev = tag.get("severity", sev).upper()
                is_recovered = (fid in P174_QUANTAMM_RECOVERED) or (
                    tag.get("miss_class", "").startswith("FOUND"))
            else:
                fam = classify_title(r.get(titlek, ""), corpus, fid) if scorable else None

            if is_recovered:
                recovered += 1
                continue
            miss += 1
            if not scorable:
                continue  # coverage-limited: counted in totals, not family-scored
            if fam == "unclassified":
                unclassified.append({"corpus": corpus, "id": fid, "title": r.get(titlek, ""), "sev": sev})
            fam_remaining[fam][corpus] += 1
            fam_sevw[fam] += SEV_WEIGHT.get(sev, 1)
            ttl = (qtags.get(fid, {}).get("family") if corpus == "quantamm" else r.get(titlek, ""))
            fam_members[fam].append(f"{corpus}:{fid} {sev[:4]:4} | {str(r.get(titlek, '') if corpus!='quantamm' else fid)[:75]}")
            if sev in ("HIGH", "CRITICAL", "CRIT"):
                fam_high[fam].append(f"{corpus}:{fid}")

        totals[corpus] = {"n": n, "recovered_or_touched": recovered, "remaining_miss": miss,
                          "scorable": scorable}
        if not scorable:
            coverage_limited[corpus] = {"n": n, "remaining_miss": miss}

    # ---- score families ----
    fammeta = RULES["families"]
    scored = []
    for fam, by_corpus in fam_remaining.items():
        total = sum(by_corpus.values())
        meta = fammeta.get(fam, {"detectability": 1, "expected_precision": 1,
                                 "reportable_yield": "?", "shipped_lens": None})
        det = meta["detectability"]
        prec = meta["expected_precision"]
        scored.append({
            "family": fam,
            "total_remaining": total,
            "by_corpus": dict(sorted(by_corpus.items())),
            "sev_weighted_remaining": fam_sevw[fam],
            "high_sev_misses": sorted(fam_high[fam]),
            "detectability": det,
            "expected_precision": prec,
            "reportable_yield": meta.get("reportable_yield"),
            "shipped_lens": meta.get("shipped_lens"),
            "members": sorted(fam_members[fam]),
            "priority": total * det * prec,
            "priority_sevweighted": fam_sevw[fam] * det * prec,
        })
    scored.sort(key=lambda x: (-x["priority"], -x["priority_sevweighted"], -x["total_remaining"]))

    # ---- clustering verdict (exclude families already covered by a shipped lens) ----
    open_fams = [s for s in scored if not s["shipped_lens"] and s["family"] != "unclassified"]
    open_total = sum(s["total_remaining"] for s in open_fams)
    def topk_pct(k):
        return round(100 * sum(s["total_remaining"] for s in open_fams[:k]) / open_total, 1) if open_total else 0
    clustering = {"open_remaining_total": open_total, "top2_pct": topk_pct(2), "top3_pct": topk_pct(3),
                  "top4_pct": topk_pct(4),
                  "n_open_families": len(open_fams)}

    out = {
        "phase": "P175",
        "type": "cross_corpus_remaining_miss_family_roadmap",
        "read_only": True,
        "score_rubric": RULES["score_rubric"],
        "corpora_used": [c[0] for c in CORPORA],
        "excluded": {"quantamm-2024-12-strict-eval": "duplicate of quantamm corpus (same 44 findings)",
                     "beanstalk-2024-05-eval2": "file is upgrades_applied log, not a finding match matrix"},
        "corpus_totals": totals,
        "coverage_limited_corpora": coverage_limited,
        "quantamm_post_p174": {"recovered_or_touched": totals["quantamm"]["recovered_or_touched"],
                               "remaining_miss": totals["quantamm"]["remaining_miss"],
                               "n": totals["quantamm"]["n"]},
        "family_scoring": scored,
        "clustering_verdict": clustering,
        "unclassified": unclassified,
    }
    (HERE / "family_scoring.json").write_text(json.dumps(out, indent=2))

    # ---- reconciliation self-checks ----
    q = totals["quantamm"]
    assert q["n"] == 44, q
    assert q["recovered_or_touched"] == 19, f"quantamm recovered={q['recovered_or_touched']} expected 19"
    assert q["remaining_miss"] == 25, f"quantamm remaining={q['remaining_miss']} expected 25"
    for c, t in totals.items():
        assert t["recovered_or_touched"] + t["remaining_miss"] == t["n"], (c, t)

    # ---- print summary ----
    print("=== P175 cross-corpus remaining-miss family roadmap ===")
    print(f"corpora scored: {[c for c,t in totals.items() if t['scorable']]}")
    print(f"coverage-limited (count-only): {list(coverage_limited)}")
    print(f"\nquantamm post-P174: {q['recovered_or_touched']}/{q['n']} recovered, {q['remaining_miss']} remaining  [reconciled OK]\n")
    print(f"{'family':24} {'remain':>6} {'sevW':>5} {'det':>3} {'prec':>4} {'prio':>5} {'prioSW':>6} {'shipped':>8}")
    for s in scored:
        ship = "yes" if s["shipped_lens"] else ""
        print(f"{s['family']:24} {s['total_remaining']:>6} {s['sev_weighted_remaining']:>5} "
              f"{s['detectability']:>3} {s['expected_precision']:>4} {s['priority']:>5} "
              f"{s['priority_sevweighted']:>6} {ship:>8}")
    print(f"\nclustering (OPEN families only, n={clustering['n_open_families']}, "
          f"total open remaining={clustering['open_remaining_total']}): "
          f"top2={clustering['top2_pct']}%  top3={clustering['top3_pct']}%  top4={clustering['top4_pct']}%")
    print(f"unclassified: {len(unclassified)}")
    if unclassified:
        for u in unclassified:
            print(f"   [{u['corpus']}] {u['id']} {u['sev']:6} {u['title'][:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
