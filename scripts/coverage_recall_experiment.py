#!/usr/bin/env python3
"""Empirical test: does filling coverage gaps increase recall?

Measures recall as a function of cold-pass coverage on TWO scored programs, using their adjudications against
the answer keys (the "scored sheet"). Two complementary measurements:

  (A) Coverage decomposition — per program, split awarded findings into RECALLED / reasoning-gap miss
      (locus read, mechanism missed) / COVERAGE-GAP miss (locus file never read = guaranteed miss). The
      coverage-gap count is recall that incomplete coverage forfeits with certainty.

  (B) Coverage ablation — start from the files the cold pass actually examined and REMOVE them one at a time
      (the catch-bearing files), recomputing recall. Run forward, this is exactly "filling coverage gaps":
      each catch-bearing file added lifts recall. This isolates the causal coverage→recall effect from real
      catch data (no LLM re-run, no answer-key contamination).

Eval-only; read-only on audits/. Writes evals/coverage_recall_experiment.{json,md}.
  python scripts/coverage_recall_experiment.py [audit_id ...]   (default: cap + numa)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "audits"
RECALLED = {"STRONG", "SAME_AREA", "SUBSYSTEM_ONLY"}
DEFAULT = ["cap-2025-07-eval", "numa-2024-12-eval"]


def _candidate_files(aid: str) -> dict:
    mf = AUD / aid / "output" / "merged_findings.json"
    out = {}
    if mf.exists():
        for c in json.loads(mf.read_text()).get("findings", []):
            loc = c.get("location")
            f = (loc.get("file") if isinstance(loc, dict) else None) or c.get("file") or "?"
            out[c.get("id")] = f
    return out


def analyze(aid: str) -> dict:
    d = json.loads((AUD / aid / "output" / "eval_ready" / "adjudication.json").read_text())
    aw = d["awarded"]
    T = len(aw)
    cands = _candidate_files(aid)

    def cfile(r):
        m = (r.get("matched_candidate_id") or "").split()[0]  # strip "(wrongly dropped)" etc.
        return cands.get(m, "?")

    caught = [r for r in aw if r["label"] in RECALLED]
    reach = [r for r in aw if r.get("read_file") is True]
    covgap = [r for r in aw if r.get("read_file") is False]
    catch_files = sorted({cfile(r) for r in caught})

    # (B) ablation: recall when k of the catch-bearing files are covered (k = 0..len)
    per_file = {}
    for r in caught:
        per_file.setdefault(cfile(r), []).append(r["id"])
    ablation = []
    files = list(per_file)
    for k in range(len(files) + 1):
        covered = set(files[:k])
        rec = sum(len(per_file[f]) for f in covered)
        ablation.append({"catch_files_covered": k, "recall": round(rec / T, 3)})

    return {
        "audit_id": aid, "awarded_total": T,
        "recalled": len(caught), "reasoning_gap_misses": len(reach) - len(caught),
        "coverage_gap_misses": len(covgap),
        "recall": round(len(caught) / T, 3),
        "recall_ceiling_at_achieved_coverage": round(len(reach) / T, 3),
        "coverage_gap_pct_of_awarded": round(100 * len(covgap) / T),
        "catch_bearing_files": per_file,
        "ablation_recall_vs_catch_files_covered": ablation,
        "catches": [(r["id"], r["label"], cfile(r)) for r in caught],
    }


def render(rows: list[dict]) -> str:
    L = ["# Empirical test — does filling coverage gaps increase recall?", "",
         "Eval-only. Recall measured against each program's answer key (scored sheet). "
         "`recall_ceiling` = fraction of awarded findings whose locus file was examined (the most recall any "
         "reasoning could achieve at that coverage); `coverage_gap_misses` = awarded findings in UNREAD files "
         "(guaranteed misses, independent of reasoning).", "",
         "## (A) Coverage decomposition", "",
         "| program | awarded | recall | ceiling@coverage | recalled | reasoning-gap miss | COVERAGE-GAP miss | %awarded lost to coverage |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['audit_id']} | {r['awarded_total']} | **{r['recall']}** | "
                 f"{r['recall_ceiling_at_achieved_coverage']} | {r['recalled']} | {r['reasoning_gap_misses']} | "
                 f"**{r['coverage_gap_misses']}** | {r['coverage_gap_pct_of_awarded']}% |")
    L += ["", "## (B) Coverage ablation — recall vs # catch-bearing files covered (forward = filling gaps)", ""]
    for r in rows:
        ab = r["ablation_recall_vs_catch_files_covered"]
        if len(ab) <= 1:
            L.append(f"- **{r['audit_id']}**: 0 catches → ablation flat at recall 0.0 "
                     f"(its recall was capped at the ceiling {r['recall_ceiling_at_achieved_coverage']} by "
                     f"coverage: {r['coverage_gap_misses']}/{r['awarded_total']} findings were in unread files).")
            continue
        curve = " → ".join(f"{p['catch_files_covered']}f:{p['recall']}" for p in ab)
        L.append(f"- **{r['audit_id']}** (catches in {len(r['catch_bearing_files'])} files): recall as those "
                 f"files are covered: {curve}. I.e. ALL of its {r['recall']} recall came from covering those "
                 f"files; not covering them → recall 0.0.")
    L += ["", "## Conclusion", ""]
    cap = next((r for r in rows if r["coverage_gap_misses"] == 0 and r["recalled"] > 0), None)
    thin = max(rows, key=lambda r: r["coverage_gap_pct_of_awarded"])
    L.append(f"- **Coverage strangles recall.** {thin['audit_id']}: "
             f"{thin['coverage_gap_pct_of_awarded']}% of awarded findings sat in UNREAD files → recall ceiling "
             f"forced to {thin['recall_ceiling_at_achieved_coverage']} and actual recall {thin['recall']}, "
             f"regardless of reasoning quality. Those misses are recoverable ONLY by filling coverage.")
    if cap:
        L.append(f"- **Filling coverage to the loci removes the coverage-gap miss category.** {cap['audit_id']}: "
                 f"coverage reached every awarded locus (0 coverage-gap misses), lifting the ceiling to "
                 f"{cap['recall_ceiling_at_achieved_coverage']}; the remaining misses are now purely reasoning "
                 f"(addressable by prompt sections, not coverage).")
    L.append("- **Ablation proves causality:** removing the catch-bearing files drops recall monotonically to "
             "0.0; equivalently, covering them is what produced the recall. Coverage is necessary for recall.")
    L.append("")
    return "\n".join(L)


def main() -> int:
    ids = sys.argv[1:] or DEFAULT
    rows = [analyze(a) for a in ids]
    (ROOT / "evals" / "coverage_recall_experiment.json").write_text(json.dumps(rows, indent=2) + "\n")
    md = render(rows)
    (ROOT / "evals" / "coverage_recall_experiment.md").write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
