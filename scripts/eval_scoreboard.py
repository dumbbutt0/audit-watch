#!/usr/bin/env python3
"""Recall Lab — the scoreboard.

Aggregates per-project adjudication.json across the corpus (evals/corpus.json) into the honest recall view:
  - TRAINING recall  (regression set; contamination acknowledged — guards regressions, NOT genuine recall)
  - HOLDOUT recall   (the HEADLINE honest number — genuinely post-cutoff blind targets)
  - per-MECHANISM-CLASS recall (which expert-bug families the system systematically misses, across projects)
  - coverage-gap vs reasoning-gap split of MISSES (read_file=false vs true) — where to invest

Writes evals/scoreboard.json + evals/scoreboard.md. Read-only on the audits/ tree. Does NOT touch the
real-world dashboard (documentation/real_world_results.json / compute_metrics default) — eval numbers live
only under evals/.

  python scripts/eval_scoreboard.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from recall_lab_loop import coverage_fraction  # full-coverage stats per audit (honest-score gate)
except Exception:  # pragma: no cover
    def coverage_fraction(aid):  # type: ignore
        return None
CORPUS = ROOT / "evals" / "corpus.json"
MECH = ROOT / "config" / "mechanism_classes.json"
OUT_JSON = ROOT / "evals" / "scoreboard.json"
OUT_MD = ROOT / "evals" / "scoreboard.md"
RECALLED = {"STRONG", "SAME_AREA", "SUBSYSTEM_ONLY"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _adj(audit_id: str) -> dict | None:
    p = ROOT / "audits" / audit_id / "output" / "eval_ready" / "adjudication.json"
    return json.loads(p.read_text()) if p.exists() else None


def _agg(rows: list[dict]) -> dict:
    """Aggregate a flat list of awarded-finding rows into recall stats (pending excluded from rates)."""
    adjudicated = [r for r in rows if r["label"] != "UNADJUDICATED"]
    n = len(adjudicated)
    recalled = sum(1 for r in adjudicated if r["label"] in RECALLED)
    strong = sum(1 for r in adjudicated if r["label"] == "STRONG")
    missed = [r for r in adjudicated if r["label"] == "MISSED"]
    cov_gap = sum(1 for r in missed if r.get("read_file") is False)
    reason_gap = sum(1 for r in missed if r.get("read_file") is True)
    return {
        "awarded_adjudicated": n,
        "pending": sum(1 for r in rows if r["label"] == "UNADJUDICATED"),
        "recall_of_surfaced": round(recalled / n, 3) if n else None,
        "strong_only": round(strong / n, 3) if n else None,
        "missed": len(missed),
        "missed_coverage_gap": cov_gap,
        "missed_reasoning_gap": reason_gap,
    }


def build() -> dict:
    corpus = json.loads(CORPUS.read_text())
    mech = json.loads(MECH.read_text())["classes"]
    sets_out = {}
    per_project = {}
    class_rows: dict[str, list[dict]] = {}

    full_cov_flat: dict[str, list[dict]] = {"training": [], "holdout": []}
    for set_name in ("training", "holdout"):
        flat: list[dict] = []
        projects = []
        for entry in corpus["sets"].get(set_name, []):
            aid = entry["id"]
            merged = ROOT / "audits" / aid / "output" / "merged_findings.json"
            doc = _adj(aid)
            # Cross-language separation: rust/Solana, move/Sui AND ton/FunC adjudications NEVER mix into the
            # Solidity scoreboard — they are tracked in their own per-language scoreboards. Skip them here (keyed
            # on the adjudication's `language` field set by the rust/move/ton recall-lab).
            _alang = str(doc.get("language", "")).lower() if doc else ""
            if _alang in ("rust", "move", "ton"):
                _sb = f"evals/{_alang}_scoreboard.md"
                projects.append({"id": aid, "status": f"{_alang} (see {_sb})"})
                continue
            no_cold = not merged.exists()
            # A scoreable holdout with no cold pass yet is "awaiting blind pass", not 0 recall.
            if no_cold or not doc or not entry.get("scoreable"):
                status = ("unscoreable" if not entry.get("scoreable")
                          else "awaiting-blind-pass" if no_cold else "no-adjudication")
                projects.append({"id": aid, "scoreable": entry.get("scoreable", False),
                                 "note": entry.get("note"), "status": status})
                continue
            rows = doc["awarded"]
            # CONFIRMED (human/seed) rows drive the headline recall; auto-heuristic rows are advisory and
            # surfaced separately so they never inflate the confirmed number.
            confirmed = [r for r in rows if r.get("source") != "auto-heuristic"]
            flat += confirmed
            # FULL-COVERAGE honesty gate: a recall number is only honest if the cold pass examined every
            # substantive in-scope file. Compute coverage and only fold full-coverage projects into the
            # full-coverage headline (thin passes inflate recall_of_surfaced by hiding coverage-gap misses).
            cov = coverage_fraction(aid)
            is_full = bool(cov and cov["full"])
            if is_full:
                full_cov_flat[set_name] += confirmed
            per_project[aid] = doc["summary"]
            projects.append({"id": aid, "auto": bool(doc["summary"].get("auto_adjudicated")),
                             "coverage_pct": (cov["pct"] if cov else None), "full_coverage": is_full,
                             **doc["summary"]})
            for r in confirmed:
                mc = r.get("mechanism_class")
                if mc:
                    class_rows.setdefault(mc, []).append(r)
        sets_out[set_name] = {"projects": projects, "aggregate": _agg(flat),
                              "full_coverage_aggregate": _agg(full_cov_flat[set_name])}

    # per-mechanism-class recall (across all projects/sets)
    by_class = {}
    for mc, rows in sorted(class_rows.items()):
        a = _agg(rows)
        meta = mech.get(mc, {})
        by_class[mc] = {
            "recall_of_surfaced": a["recall_of_surfaced"],
            "strong_only": a["strong_only"],
            "n": a["awarded_adjudicated"],
            "missed": a["missed"],
            "status": meta.get("status", "untagged"),
            "prompt_section": meta.get("prompt_section"),
        }
    # mechanism classes in the taxonomy that have NO awarded example yet (blind spots we can't measure)
    untested = [mc for mc in mech if mc not in by_class]

    # auto-detected-misses rollup: scan EVERY audit dir with an auto-heuristic adjudication (incl. already-
    # evaluated contests not in the corpus sets). This is the "detect the misses in already-evaluated contests"
    # surface — advisory (heuristic), not part of the confirmed headline.
    import glob as _glob
    auto_projects = []
    for p in sorted(_glob.glob(str(ROOT / "audits" / "*" / "output" / "eval_ready" / "adjudication.json"))):
        try:
            ad = json.loads(open(p).read())
        except Exception:
            continue
        if not ad.get("auto_heuristic"):
            continue
        s = ad.get("summary", {})
        auto_projects.append({"id": ad.get("audit_id"), "awarded": s.get("awarded_total"),
                              "misses_detected": s.get("misses_detected"),
                              "heuristic_recall": s.get("recall_of_surfaced")})
    auto_projects.sort(key=lambda r: r.get("misses_detected") or 0, reverse=True)
    auto_rollup = {"projects": auto_projects,
                   "total_misses_detected": sum((r.get("misses_detected") or 0) for r in auto_projects)}

    doc = {
        "generated_at": _now(),
        "headline": {
            "holdout_recall": sets_out["holdout"]["aggregate"]["recall_of_surfaced"],
            "holdout_strong_only": sets_out["holdout"]["aggregate"]["strong_only"],
            "training_recall": sets_out["training"]["aggregate"]["recall_of_surfaced"],
            "holdout_recall_full_coverage_only": sets_out["holdout"]["full_coverage_aggregate"]["recall_of_surfaced"],
            "holdout_full_coverage_projects": sets_out["holdout"]["full_coverage_aggregate"]["awarded_adjudicated"],
            "training_recall_full_coverage_only": sets_out["training"]["full_coverage_aggregate"]["recall_of_surfaced"],
            "training_full_coverage_projects": sets_out["training"]["full_coverage_aggregate"]["awarded_adjudicated"],
            "note": ("holdout/training recall_of_surfaced = recall over surfaced findings (may include THIN passes). "
                     "*_full_coverage_only = the HONEST number, counting only projects whose cold pass examined every "
                     "substantive in-scope file. A None/0-project full-coverage headline means no scoreable project "
                     "has a full-coverage cold pass yet — run them at full coverage to populate it."),
        },
        "sets": sets_out,
        "by_mechanism_class": by_class,
        "untested_mechanism_classes": untested,
        "auto_miss_detection": auto_rollup,
    }
    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n")
    OUT_MD.write_text(render_md(doc))
    return doc


def render_md(doc: dict) -> str:
    h = doc["headline"]
    L = ["# Recall Lab — Scoreboard", "", f"_generated {doc['generated_at']}_", "",
         "Eval-only. Does not affect the real-world dashboard.", "",
         "## Headline",
         f"- **Holdout recall — FULL-COVERAGE only (the honest number):** {h['holdout_recall_full_coverage_only']}  "
         f"(over {h['holdout_full_coverage_projects']} awarded findings in full-coverage projects)",
         f"- Holdout recall — of-surfaced (may include thin passes): {h['holdout_recall']}  (strong-only {h['holdout_strong_only']})",
         f"- **Training recall — FULL-COVERAGE only:** {h['training_recall_full_coverage_only']}  "
         f"(over {h['training_full_coverage_projects']} findings); of-surfaced: {h['training_recall']} — regression set, contamination acknowledged",
         "",
         "> Honest-score policy: only cold passes that examined EVERY substantive in-scope file count toward the "
         "full-coverage headline. Thin passes inflate recall_of_surfaced by hiding coverage-gap misses, so they are "
         "shown but excluded from the honest number. Per-project coverage% is in the tables below.",
         ""]
    for set_name in ("holdout", "training"):
        s = doc["sets"][set_name]
        ag = s["aggregate"]
        L.append(f"## {set_name.capitalize()}  (recall {ag['recall_of_surfaced']}, strong {ag['strong_only']}, "
                 f"misses: {ag['missed_coverage_gap']} coverage-gap / {ag['missed_reasoning_gap']} reasoning-gap, "
                 f"pending {ag['pending']})")
        L.append("")
        L.append("| project | recall | strong | awarded | coverage | full? | note |")
        L.append("|---|---|---|---|---|---|---|")
        for p in s["projects"]:
            if "recall_of_surfaced" in p:
                note = "heuristic (auto-detected, unconfirmed)" if p.get("auto") else ""
                covpct = f"{round((p.get('coverage_pct') or 0)*100)}%" if p.get("coverage_pct") is not None else "—"
                full = "✅" if p.get("full_coverage") else ("thin" if p.get("coverage_pct") is not None else "—")
                L.append(f"| {p['id']} | {p['recall_of_surfaced']} | {p['strong_only']} | "
                         f"{p.get('awarded_total','?')} | {covpct} | {full} | {note} |")
            else:
                L.append(f"| {p['id']} | — | — | — | — | — | {p.get('status','')}{(': '+p['note']) if p.get('note') else ''} |")
        L.append("")
    ar = doc.get("auto_miss_detection", {})
    if ar.get("projects"):
        L.append(f"## Auto-detected misses (heuristic; incl. already-evaluated contests) — "
                 f"{ar['total_misses_detected']} total")
        L.append("")
        L.append("> Advisory miss-detection over every contest with a cold pass + an answer key (any format). "
                 "Heuristic + confidence-tagged; NOT part of the confirmed headline and NOT protected by the "
                 "regression gate. Use to find unexamined expert-bug families to reincorporate.")
        L.append("")
        L.append("| project | awarded | misses detected | heuristic recall |")
        L.append("|---|---|---|---|")
        for r in ar["projects"]:
            L.append(f"| {r['id']} | {r.get('awarded')} | {r.get('misses_detected')} | {r.get('heuristic_recall')} |")
        L.append("")
    L.append("## Per-mechanism-class recall  (which expert-bug families we miss)")
    L.append("")
    L.append("| mechanism class | recall | strong | n | missed | status | prompt § |")
    L.append("|---|---|---|---|---|---|---|")
    for mc, v in sorted(doc["by_mechanism_class"].items(), key=lambda kv: (kv[1]["recall_of_surfaced"] or 0)):
        L.append(f"| {mc} | {v['recall_of_surfaced']} | {v['strong_only']} | {v['n']} | {v['missed']} "
                 f"| {v['status']} | {v['prompt_section'] or '-'} |")
    L.append("")
    if doc["untested_mechanism_classes"]:
        L.append("**Untested classes (in taxonomy, no awarded example yet — unmeasured blind spots):** "
                 + ", ".join(doc["untested_mechanism_classes"]))
        L.append("")
    return "\n".join(L)


def build_language(lang: str) -> dict | None:
    """Per-language recall scoreboard for rust/move. The Solidity board (build()) routes these OUT (so they never
    inflate Solidity recall); this writes their OWN board so the honest non-Solidity number lives in a file, not
    only in adjudication.json. Keyed on each adjudication's `language` field across ALL audits with one."""
    import glob
    mech = json.loads(MECH.read_text())["classes"]
    flat: list[dict] = []
    full_flat: list[dict] = []
    projects: list[dict] = []
    class_rows: dict[str, list[dict]] = {}
    for p in sorted(glob.glob(str(ROOT / "audits" / "*" / "output" / "eval_ready" / "adjudication.json"))):
        try:
            doc = json.loads(Path(p).read_text())
        except Exception:
            continue
        if str(doc.get("language", "")).lower() != lang:
            continue
        aid = doc.get("audit_id") or Path(p).parents[2].name
        rows = doc.get("awarded", [])
        confirmed = [r for r in rows if r.get("source") != "auto-heuristic"]
        if not confirmed:
            projects.append({"id": aid, "status": "no-adjudication"})
            continue
        flat += confirmed
        cov = coverage_fraction(aid)
        is_full = bool(cov and cov["full"])
        if is_full:
            full_flat += confirmed
        summ = dict(doc.get("summary", {}))
        # compute awarded count explicitly (adjudication summary schemas vary across sessions)
        summ.setdefault("awarded_adjudicated", sum(1 for r in confirmed if r.get("label") != "UNADJUDICATED"))
        per_proj = _agg(confirmed)
        projects.append({"id": aid, "coverage_pct": (cov["pct"] if cov else None),
                         "full_coverage": is_full, "recall_of_surfaced": per_proj["recall_of_surfaced"],
                         "strong_only": per_proj["strong_only"], "awarded_adjudicated": per_proj["awarded_adjudicated"]})
        for r in confirmed:
            mc = r.get("mechanism_class")
            if mc:
                class_rows.setdefault(mc, []).append(r)
    if not projects:
        return None
    by_class = {}
    for mc, rows in sorted(class_rows.items()):
        a = _agg(rows)
        meta = mech.get(mc, {})
        by_class[mc] = {"recall_of_surfaced": a["recall_of_surfaced"], "strong_only": a["strong_only"],
                        "n": a["awarded_adjudicated"], "missed": a["missed"],
                        "status": meta.get("status", "untagged"), "prompt_section": meta.get("prompt_section")}
    # Non-blind reincorporations: classes earned from a NON-BLIND / source-level eval (auditor saw the report;
    # no blind cold-pass fixture/adjudication on disk). These are honestly NOT banked toward blind recall above —
    # surface them so the provenance isn't lost (e.g. the LayerZero-Solana Zellic reincorporation).
    adjudicated_ids = {p["id"] for p in projects if "recall_of_surfaced" in p}
    non_blind: dict[str, list[str]] = {}
    for mc, meta in mech.items():
        if str(meta.get("language", "")).lower() != lang or meta.get("status") != "reincorporated":
            continue
        for ex in meta.get("awarded_examples", []):
            eid = str(ex).split(":")[0]
            if eid and eid not in adjudicated_ids:
                non_blind.setdefault(eid, [])
                if mc not in non_blind[eid]:
                    non_blind[eid].append(mc)

    doc = {"language": lang, "generated_at": _now(), "aggregate": _agg(flat),
           "full_coverage_aggregate": _agg(full_flat), "projects": projects, "by_mechanism_class": by_class,
           "non_blind_reincorporations": {k: sorted(v) for k, v in non_blind.items()}}
    (ROOT / "evals" / f"{lang}_scoreboard.json").write_text(json.dumps(doc, indent=2) + "\n")
    (ROOT / "evals" / f"{lang}_scoreboard.md").write_text(render_language_md(lang, doc))
    return doc


def render_language_md(lang: str, doc: dict) -> str:
    ag, fc = doc["aggregate"], doc["full_coverage_aggregate"]
    L = [f"# Recall Lab — {lang.capitalize()} Scoreboard", "", f"_generated {doc['generated_at']}_", "",
         f"Eval-only, {lang}-only. NEVER counted toward Solidity recall (the Solidity board routes these out). "
         "The honest non-Solidity recall number lives here.", "",
         "## Headline",
         f"- **Recall — FULL-COVERAGE only (honest):** {fc['recall_of_surfaced']}  "
         f"(over {fc['awarded_adjudicated']} awarded findings in full-coverage cold passes)",
         f"- Recall — of-surfaced (may include thin passes): {ag['recall_of_surfaced']}  (strong-only {ag['strong_only']})",
         f"- Misses: {ag['missed_coverage_gap']} coverage-gap / {ag['missed_reasoning_gap']} reasoning-gap · pending {ag['pending']}",
         "",
         "| project | recall | strong | awarded | coverage | full? |",
         "|---|---|---|---|---|---|"]
    for p in doc["projects"]:
        if "recall_of_surfaced" in p:
            covpct = f"{round((p.get('coverage_pct') or 0)*100)}%" if p.get("coverage_pct") is not None else "—"
            full = "✅" if p.get("full_coverage") else ("thin" if p.get("coverage_pct") is not None else "—")
            L.append(f"| {p['id']} | {p['recall_of_surfaced']} | {p['strong_only']} | "
                     f"{p.get('awarded_adjudicated', p.get('awarded','?'))} | {covpct} | {full} |")
        else:
            L.append(f"| {p['id']} | — | — | — | — | {p.get('status','')} |")
    L += ["", "## Per-mechanism-class recall", "",
          "| mechanism class | recall | strong | n | missed | status | prompt § |",
          "|---|---|---|---|---|---|---|"]
    for mc, v in sorted(doc["by_mechanism_class"].items(), key=lambda kv: (kv[1]["recall_of_surfaced"] or 0)):
        L.append(f"| {mc} | {v['recall_of_surfaced']} | {v['strong_only']} | {v['n']} | {v['missed']} "
                 f"| {v['status']} | {v['prompt_section'] or '-'} |")
    L.append("")
    nb = doc.get("non_blind_reincorporations") or {}
    if nb:
        L += ["## Non-blind reincorporations — NON-BLIND, not banked as blind recall", "",
              "> These classes were reincorporated from a **NON-BLIND** / source-level eval (the auditor saw the "
              "report; there is no blind cold-pass fixture/adjudication on disk). They are honestly **not banked** "
              "toward the blind-recall headline above — provenance only.", "",
              "| eval (non-blind) | classes reincorporated |", "|---|---|"]
        for eid, mcs in sorted(nb.items()):
            L.append(f"| {eid} | {', '.join(mcs)} |")
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    d = build()
    print(f"holdout_recall={d['headline']['holdout_recall']} "
          f"training_recall={d['headline']['training_recall']} "
          f"classes={len(d['by_mechanism_class'])} -> {OUT_MD.relative_to(ROOT)}")
    for _lang in ("move", "rust", "ton"):
        ld = build_language(_lang)
        if ld:
            print(f"{_lang}_recall(full-cov)={ld['full_coverage_aggregate']['recall_of_surfaced']} "
                  f"of-surfaced={ld['aggregate']['recall_of_surfaced']} "
                  f"classes={len(ld['by_mechanism_class'])} -> evals/{_lang}_scoreboard.md")
