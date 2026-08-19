#!/usr/bin/env python3
"""
suppression_report.py — Recall Lab "two-budget" false-suppression instrumentation.

MEASUREMENT ONLY. This script never changes pipeline behavior. It imports the pipeline's own
precision-filter decision functions and adjudication oracle, applies them to the recall-measured
holdout candidates, and reports — for each precision filter that can remove a candidate — BOTH:

  * cut_rate          = fraction of candidates the filter removes                       (precision budget)
  * suppression_rate  = fraction of KNOWN-VALID (awarded, caught) findings it removes    (recall budget)

A filter "suppressed" an awarded finding when (a) the oracle credits that awarded finding to a
candidate the filter removes, AND (b) after removing the filter's candidates, the recall-safe oracle
(adjudicate._auto_label) no longer labels the awarded finding as recalled. This is the exact "it
killed a real one" test the recall-regression gate protects against — reused, not reinvented.

The four filters (CLAUDE.md pipeline steps):
  3.4  ICE downgrades          (run_impact_chain_escalation.py — severity_ceiling caps)
  3.6  fp_pattern_check        (fp_pattern_check.py — rejection-rule match)
  3.7  8 pre-submission gates  (pre_submission_gate.py — overall_verdict==REJECT)
  3.8  dedup screen            (pre_submission_dupe_screen.py — duplicate removal)

Measurement mode per filter is reported honestly:
  * recomputed          — the filter's decision is a pure function of the finding + shared rules,
                          so it is faithfully reproduced over the eval candidates (fp_pattern_check).
  * logged              — a per-finding disposition sidecar exists for the project; joined by id.
  * non_removing        — the filter never removes (max action is human_review): cut_rate == 0 by design.
  * unmeasured_in_eval   — evidence-gated (needs PoC/judge/defense sidecars the blind pass omits) and
                          not run in the eval/recall path: reported as null, NOT faked as 0.

  python scripts/suppression_report.py            # over the current holdout (default)
  python scripts/suppression_report.py all        # training + holdout

Outputs: evals/suppression_report.json + evals/suppression_report.md
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import adjudicate  # recall-safe oracle: load_awarded / load_candidates / _auto_label / RECALLED
import fp_pattern_check  # check_finding / compute_recommended_action (pure)

CORPUS = ROOT / "evals" / "corpus.json"
OUT_JSON = ROOT / "evals" / "suppression_report.json"
OUT_MD = ROOT / "evals" / "suppression_report.md"
RECALLED = adjudicate.RECALLED

SEV_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0, "qa": 0, "": 0}
ADVANCE_FLOOR = SEV_RANK["medium"]  # ICE 3.4 threshold: a finding must stay >= Medium to advance


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_shared_rejection_rules() -> list[dict]:
    """The additive suppressor being measured: the shared curated + auto-promoted FP rule corpus
    (the same files fp_pattern_check merges project-wide), deduped by rule_id, curated-first."""
    rules: dict[str, dict] = {}
    for p in (ROOT / "data" / "fp_autopsies" / "rejection_rules.jsonl",
              ROOT / "data" / "fp_autopsies" / "auto_promoted_rules.jsonl"):
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            rid = r.get("rule_id", "")
            if rid and rid not in rules:
                rules[rid] = r
    return list(rules.values())


def load_raw_merged(adir: Path) -> dict[str, dict]:
    """Raw merged findings keyed by id (carry description/impact/vuln_type for the fp matcher)."""
    p = adir / "output" / "merged_findings.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text())
    fs = d.get("findings", d) if isinstance(d, dict) else d
    out = {}
    for f in (fs or []):
        if isinstance(f, dict) and f.get("id"):
            out[f["id"]] = f
    return out


def load_persisted_awarded(adir: Path) -> list[dict]:
    p = adir / "output" / "eval_ready" / "adjudication.json"
    if not p.exists():
        return []
    return json.loads(p.read_text()).get("awarded", [])


# ---------------------------------------------------------------------------
# Per-filter removed-set computation. Each returns (mode, removed_ids_or_None, reasons)
# removed=None  → unmeasured (reported as null); removed=set() → measured-empty (0.0).
# ---------------------------------------------------------------------------

def removed_fp_pattern_check(raw: dict[str, dict], rules: list[dict]) -> tuple[str, set, dict, dict]:
    """3.6 — pure function of finding + rules. Faithfully recomputed over eval candidates.

    Also returns a diagnostic: the fp matcher keys on vuln_type / _source_agent / description-keyword
    overlap. Blind-pass merged_findings candidates often lack vuln_type, so the matcher can be
    STRUCTURALLY INERT on eval-shaped records (max similarity stays below the 0.6 review bar). We track
    that so a 0.0 suppression rate is not misread as 'rules proven recall-safe'."""
    removed, reasons = set(), {}
    diag = {"n": 0, "max_top_sim": 0.0, "raw_max_sim": 0.0, "n_review": 0, "n_reject": 0,
            "n_with_vuln_type": 0, "n_with_source_agent": 0}
    for fid, f in raw.items():
        diag["n"] += 1
        if f.get("vuln_type") and str(f.get("vuln_type")) != "None":
            diag["n_with_vuln_type"] += 1
        if f.get("_source_agent") and str(f.get("_source_agent")) != "None":
            diag["n_with_source_agent"] += 1
        # raw_max_sim = best rule similarity WITHOUT the 0.6 return-threshold, so a thresholded 0.0
        # doesn't hide "how close did the rules get to firing."
        if rules:
            diag["raw_max_sim"] = max(diag["raw_max_sim"],
                                      max(fp_pattern_check.compute_rule_similarity(f, r) for r in rules))
        res = fp_pattern_check.check_finding(f, rules)
        ts = res.get("top_similarity") or 0.0
        diag["max_top_sim"] = max(diag["max_top_sim"], ts)
        act = res.get("recommended_action")
        if act == "review":
            diag["n_review"] += 1
        if act == "reject":
            diag["n_reject"] += 1
            removed.add(fid)
            mr = res.get("matching_rules") or [{}]
            reasons[fid] = f"{mr[0].get('rule_id')}: {mr[0].get('rejection_reason', '')[:80]}"
    return "recomputed", removed, reasons, diag


def removed_pre_submission_gates(adir: Path) -> tuple[str, set | None, dict]:
    """3.7 — evidence-gated (needs exploit/poc/judge/defense sidecars). Join the disposition log if
    the project ran it; otherwise unmeasured in the eval path (blind pass omits those sidecars)."""
    log = adir / "data" / "triage" / "gate_results.jsonl"
    if not log.exists():
        return "unmeasured_in_eval", None, {}
    removed, reasons = set(), {}
    for line in log.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("overall_verdict") == "REJECT":
            fid = r.get("finding_id")
            removed.add(fid)
            fails = [g for g in r.get("gate_results", []) if g.get("verdict") == "FAIL"]
            reasons[fid] = "; ".join(f"gate{g.get('gate')}:{g.get('name')}" for g in fails[:2])
    return "logged", removed, reasons


def removed_dedup_screen(adir: Path) -> tuple[str, set, dict]:
    """3.8 — non-removing by design: the strongest action is routing to human_review, never a hard
    removal. cut_rate is 0 by construction; we still surface the flagged count from a log if present."""
    return "non_removing", set(), {}


def removed_ice_downgrade(adir: Path, raw: dict[str, dict]) -> tuple[str, set, dict, dict]:
    """3.4 — ICE is an ENRICHMENT pass and is NON-REMOVING. Empirically verified on real audits: a
    sub-floor `severity_ceiling` is ADVISORY only and `ice.hold` routes to poc_required (prove-first) —
    NEITHER drops a finding from submission. Confirmed keepers (cartha AC-001/DOS-002/… — all in
    submit.jsonl at rec_sev=Medium) advance despite `ceiling=Low, poc_level=0`. So ICE contributes 0 to
    the suppression budget. We still surface, as an ADVISORY diagnostic (NOT a suppression), how many
    candidates ICE capped below the Medium advance floor — a severity-guidance signal worth a human's eye."""
    p = adir / "output" / "findings_ice.json"
    if not p.exists():
        return "unmeasured_in_eval", None, {}, {}
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError:
        return "unmeasured_in_eval", None, {}, {}
    fs = d.get("findings", d) if isinstance(d, dict) else d
    capped = []
    for f in (fs or []):
        if not isinstance(f, dict):
            continue
        orig = SEV_RANK.get(str(f.get("severity", "")).lower(), 0)
        ice = f.get("ice") or {}
        ceiling = ice.get("severity_ceiling")
        if ceiling is None:
            continue
        crank = SEV_RANK.get(str(ceiling).lower(), orig)
        if orig >= ADVANCE_FLOOR and crank < ADVANCE_FLOOR:
            capped.append(f.get("id"))
    diag = {"severity_ceiling_below_floor": sorted(x for x in capped if x),
            "note": "ADVISORY severity cap only — ICE never removes a finding; keepers advance regardless. "
                    "NOT counted as suppression."}
    return "non_removing", set(), {}, diag


# ---------------------------------------------------------------------------
# Suppression test: did removing `removed` drop a known-valid awarded finding out of recall?
# ---------------------------------------------------------------------------

def _crediting_candidate(persisted_row: dict, aw_norm: dict, candidates_full: list[dict]) -> str | None:
    """The candidate that catches this awarded finding: the persisted matched id if present, else the
    recall-safe oracle's best match over the full candidate set."""
    mid = persisted_row.get("matched_candidate_id")
    if mid:
        return mid
    if aw_norm is None:
        return None
    return adjudicate._auto_label(aw_norm, candidates_full).get("matched_candidate_id")


def project_suppression(aid: str, removed: set, candidates_full: list[dict],
                        awarded_norm_by_id: dict, persisted: list[dict]) -> tuple[int, int, list]:
    """Return (n_known_valid_caught, n_suppressed, suppressed_details) for one filter on one project."""
    known_valid = [r for r in persisted if r.get("label") in RECALLED]
    n_kv = len(known_valid)
    if not removed:
        return n_kv, 0, []
    survivors = [c for c in candidates_full if c["id"] not in removed]
    suppressed = []
    for r in known_valid:
        awid = r.get("id")
        aw_norm = awarded_norm_by_id.get(awid)
        cid = _crediting_candidate(r, aw_norm, candidates_full)
        if not cid or cid not in removed:
            continue  # its catcher survives (or unknown) → not suppressed by this filter
        # Re-check with the oracle on survivors: does any surviving candidate still catch it?
        lab_after = adjudicate._auto_label(aw_norm, survivors).get("label") if aw_norm else "MISSED"
        if lab_after not in RECALLED:
            suppressed.append({
                "project": aid, "awarded_id": awid, "awarded_title": r.get("title", "")[:90],
                "awarded_severity": r.get("severity", ""), "crediting_candidate_id": cid,
            })
    return n_kv, len(suppressed), suppressed


# ---------------------------------------------------------------------------

FILTERS = [
    ("ice_downgrade", "3.4", "ICE downgrade below Medium advance floor"),
    ("fp_pattern_check", "3.6", "false-positive rejection-rule match"),
    ("pre_submission_gates", "3.7", "8 pre-submission gates (overall REJECT)"),
    ("dedup_screen", "3.8", "duplicate screen"),
]


def build(set_names: list[str]) -> dict:
    corpus = json.loads(CORPUS.read_text())
    rules = load_shared_rejection_rules()

    project_ids: list[str] = []
    for s in set_names:
        project_ids += [e["id"] for e in corpus["sets"].get(s, []) if e.get("scoreable")]

    # accumulators per filter
    agg = {k: {"n_candidates": 0, "n_removed": 0, "n_known_valid": 0, "n_suppressed": 0,
               "suppressed_finding_ids": [], "projects_measured": 0, "modes": {}}
           for k, _, _ in FILTERS}
    fp_diag = {"n": 0, "max_top_sim": 0.0, "n_review": 0, "n_reject": 0, "n_with_vuln_type": 0,
               "n_with_source_agent": 0}
    per_project = []

    for aid in project_ids:
        adir = ROOT / "audits" / aid
        candidates_full = adjudicate.load_candidates(adir / "output" / "merged_findings.json")
        persisted = load_persisted_awarded(adir)
        if not candidates_full or not persisted:
            continue
        raw = load_raw_merged(adir)
        awarded_norm, _src = adjudicate.load_awarded(adir)
        awarded_norm_by_id = {a["id"]: a for a in awarded_norm}
        n_cand = len(candidates_full)

        proj_rec = {"project": aid, "n_candidates": n_cand, "filters": {}}
        for key, step, _desc in FILTERS:
            if key == "fp_pattern_check":
                mode, removed, reasons, d = removed_fp_pattern_check(raw, rules)
                for kk in ("n", "n_review", "n_reject", "n_with_vuln_type", "n_with_source_agent"):
                    fp_diag[kk] += d[kk]
                fp_diag["max_top_sim"] = max(fp_diag["max_top_sim"], d["max_top_sim"])
            elif key == "pre_submission_gates":
                mode, removed, reasons = removed_pre_submission_gates(adir)
            elif key == "dedup_screen":
                mode, removed, reasons = removed_dedup_screen(adir)
            elif key == "ice_downgrade":
                mode, removed, reasons, _ = removed_ice_downgrade(adir, raw)
            else:
                mode, removed, reasons = "unmeasured_in_eval", None, {}

            a = agg[key]
            a["modes"][mode] = a["modes"].get(mode, 0) + 1
            if removed is None:  # unmeasured for this project
                proj_rec["filters"][key] = {"mode": mode, "cut": None, "n_removed": None,
                                            "n_known_valid": len([r for r in persisted if r.get("label") in RECALLED]),
                                            "n_suppressed": None}
                continue
            n_kv, n_supp, supp = project_suppression(aid, removed, candidates_full,
                                                     awarded_norm_by_id, persisted)
            for s in supp:
                s["filter"] = key
                s["reason"] = reasons.get(s["crediting_candidate_id"], "")
            a["n_candidates"] += n_cand
            a["n_removed"] += len(removed)
            a["n_known_valid"] += n_kv
            a["n_suppressed"] += n_supp
            a["suppressed_finding_ids"] += supp
            a["projects_measured"] += 1
            proj_rec["filters"][key] = {
                "mode": mode, "cut": round(len(removed) / n_cand, 4) if n_cand else 0.0,
                "n_removed": len(removed), "n_known_valid": n_kv, "n_suppressed": n_supp,
            }
        per_project.append(proj_rec)

    # finalize per-filter aggregates
    filters_out = {}
    for key, step, desc in FILTERS:
        a = agg[key]
        measured = a["projects_measured"] > 0
        cut_rate = round(a["n_removed"] / a["n_candidates"], 4) if a["n_candidates"] else (0.0 if measured else None)
        supp_rate = round(a["n_suppressed"] / a["n_known_valid"], 4) if a["n_known_valid"] else (0.0 if measured else None)
        # a filter that ran but removed nothing anywhere has a defined 0.0; one never measured is null
        if not measured and not a["modes"]:
            cut_rate = supp_rate = None
        filters_out[key] = {
            "step": step, "description": desc,
            "measurement_modes": a["modes"],
            "cut_rate": cut_rate,
            "suppression_rate": supp_rate,
            "n_candidates_seen": a["n_candidates"],
            "n_removed": a["n_removed"],
            "n_known_valid_caught": a["n_known_valid"],
            "n_suppressed": a["n_suppressed"],
            "suppressed_finding_ids": a["suppressed_finding_ids"],
            "projects_measured": a["projects_measured"],
            "loosen_candidate": bool(supp_rate and supp_rate > 0),
        }
        if key == "fp_pattern_check":
            inert = fp_diag["n"] > 0 and fp_diag["max_top_sim"] < 0.6
            filters_out[key]["diagnostics"] = {**fp_diag, "max_top_sim": round(fp_diag["max_top_sim"], 3)}
            if inert:
                filters_out[key]["caveat"] = (
                    "STRUCTURALLY INERT on eval candidates: the FP matcher keys on vuln_type / "
                    f"_source_agent / description-keyword overlap, but {fp_diag['n'] - fp_diag['n_with_vuln_type']}"
                    f"/{fp_diag['n']} candidates carry no vuln_type and max similarity across all candidates "
                    f"is {round(fp_diag['max_top_sim'], 3)} (below the 0.6 review bar). suppression_rate=0 here "
                    "means the filter never fired on this candidate shape — NOT that the rules are proven "
                    "recall-safe. Re-run on real-world audits (rich merged_findings) for a true FP suppression signal."
                )

    # top line: aggregate over MEASURED filters only
    tot_removed = sum(f["n_removed"] for f in filters_out.values() if f["cut_rate"] is not None)
    tot_cand = sum(f["n_candidates_seen"] for f in filters_out.values() if f["cut_rate"] is not None)
    tot_supp = sum(f["n_suppressed"] for f in filters_out.values() if f["suppression_rate"] is not None)
    tot_kv = sum(f["n_known_valid_caught"] for f in filters_out.values() if f["suppression_rate"] is not None)
    unmeasured = [k for k, f in filters_out.items() if f["cut_rate"] is None]

    doc = {
        "generated_at": _now(),
        "eval_note": "MEASUREMENT ONLY — recomputes precision-filter removals over recall-measured "
                     "candidates; changes no pipeline behavior. Reuses adjudicate._auto_label (recall-safe "
                     "oracle) for the suppression test. Does not affect the real-world dashboard.",
        "sets": set_names,
        "projects_scored": len(per_project),
        "shared_rejection_rules_loaded": len(rules),
        "top_line": {
            "combined_cut_rate": round(tot_removed / tot_cand, 4) if tot_cand else None,
            "combined_suppression_rate": round(tot_supp / tot_kv, 4) if tot_kv else None,
            "total_suppressed": tot_supp,
            "total_known_valid_caught": tot_kv,
            "unmeasured_filters": unmeasured,
            "loosen_candidates": [k for k, f in filters_out.items() if f["loosen_candidate"]],
        },
        "filters": filters_out,
        "per_project": per_project,
    }
    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n")
    OUT_MD.write_text(render_md(doc))
    return doc


def render_md(doc: dict) -> str:
    L = ["# Recall Lab — False-Suppression (Two-Budget) Report",
         f"_generated {doc['generated_at']}_",
         "",
         "Eval-only. Measurement of precision filters' recall cost; does not affect the real-world "
         "dashboard or pipeline behavior.",
         "",
         f"- Sets: `{', '.join(doc['sets'])}`  ·  projects scored: **{doc['projects_scored']}**  ·  "
         f"shared FP rules: **{doc['shared_rejection_rules_loaded']}**",
         ""]
    tl = doc["top_line"]
    L += ["## Top line",
          f"- Combined cut rate (measured filters): **{tl['combined_cut_rate']}**",
          f"- Combined false-suppression rate: **{tl['combined_suppression_rate']}**  "
          f"({tl['total_suppressed']}/{tl['total_known_valid_caught']} known-valid caught findings removed)",
          f"- Loosen / make-reversible candidates (suppression_rate > 0): "
          f"**{', '.join(tl['loosen_candidates']) or 'none'}**",
          f"- Unmeasured in eval path: {', '.join(tl['unmeasured_filters']) or 'none'}",
          ""]
    L += ["## Per-filter",
          "",
          "| Filter | Step | Mode | Cut rate | Suppression rate | n_suppressed | Loosen? |",
          "|---|---|---|---|---|---|---|"]
    for key, f in doc["filters"].items():
        modes = ",".join(f["measurement_modes"].keys()) or "—"
        cut = "—" if f["cut_rate"] is None else f"{f['cut_rate']:.3f}"
        sup = "—" if f["suppression_rate"] is None else f"{f['suppression_rate']:.3f}"
        flag = "⚠️ YES" if f["loosen_candidate"] else "no"
        L.append(f"| {key} | {f['step']} | {modes} | {cut} | {sup} | {f['n_suppressed']} | {flag} |")
    L.append("")
    for key, f in doc["filters"].items():
        if f.get("caveat"):
            L += [f"> **Caveat — `{key}`:** {f['caveat']}", ""]
    # detail on any suppression
    any_supp = False
    for key, f in doc["filters"].items():
        if f["suppressed_finding_ids"]:
            any_supp = True
            L += [f"### Suppressed by `{key}` ({f['step']})"]
            for s in f["suppressed_finding_ids"]:
                L.append(f"- `{s['project']}` {s['awarded_id']} ({s['awarded_severity']}) — "
                         f"{s['awarded_title']}  ← cand `{s['crediting_candidate_id']}`  [{s.get('reason','')}]")
            L.append("")
    if not any_supp:
        L += ["_No filter removed a known-valid (awarded, caught) finding on the measured set._", ""]
    L += ["## Measurement modes",
          "- `recomputed` — filter decision reproduced faithfully over eval candidates (pure fn of finding+rules).",
          "- `logged` — joined a per-finding disposition sidecar the project actually wrote.",
          "- `non_removing` — filter never hard-removes (max action = human_review); cut_rate 0 by design.",
          "- `unmeasured_in_eval` — evidence-gated (needs PoC/judge/defense sidecars the blind pass omits) and "
          "not run in the recall path; reported as null, not faked as 0.",
          ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Real-audit mode: oracle = the audit's OWN confirmed findings (no answer key).
# ---------------------------------------------------------------------------

def load_confirmed_oracle(adir: Path) -> tuple[set, set]:
    """Confirmed finding-ids for a real audit. Returns (submit_set, ready_set).

    submit  = data/triage/submit.jsonl finding_ids  (present on every triaged audit; the direct
              'this is a real, submittable finding' triage verdict — the primary oracle).
    ready   = output/candidates_index.json records with state=='ready' (stricter: submit + confirmation
              + PoC satisfied + no blockers). findings_confirmed.json is intentionally NOT used (absent
              on most real audits — confirmation is skipped in the API-free path)."""
    submit = set()
    sj = adir / "data" / "triage" / "submit.jsonl"
    if sj.exists():
        for line in sj.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                submit.add(json.loads(line).get("finding_id"))
            except json.JSONDecodeError:
                continue
    ready = set()
    ci = adir / "output" / "candidates_index.json"
    if ci.exists():
        try:
            for r in json.loads(ci.read_text()).get("records", []):
                if r.get("state") == "ready":
                    ready.add(r.get("id"))
        except json.JSONDecodeError:
            pass
    submit.discard(None)
    ready.discard(None)
    return submit, ready


def compute_audit(aid: str) -> dict:
    """Real-audit false-suppression doc (no file write). Oracle = the audit's OWN confirmed findings."""
    adir = ROOT / "audits" / aid
    rules = load_shared_rejection_rules()
    raw = load_raw_merged(adir)
    n_cand = len(raw)
    submit_set, ready_set = load_confirmed_oracle(adir)

    filters_out = {}
    fp_diag = None
    ice_diag = None
    for key, step, desc in FILTERS:
        if key == "fp_pattern_check":
            mode, removed, reasons, fp_diag = removed_fp_pattern_check(raw, rules)
        elif key == "pre_submission_gates":
            mode, removed, reasons = removed_pre_submission_gates(adir)
        elif key == "dedup_screen":
            mode, removed, reasons = removed_dedup_screen(adir)
        elif key == "ice_downgrade":
            mode, removed, reasons, ice_diag = removed_ice_downgrade(adir, raw)
        else:
            mode, removed, reasons = "unmeasured_in_eval", None, {}

        entry = {"step": step, "description": desc, "mode": mode}
        if removed is None:
            entry.update({"cut_rate": None, "n_removed": None, "n_candidates": n_cand,
                          "suppression_rate_submit": None, "suppression_rate_ready": None,
                          "suppressed_submit_ids": [], "suppressed_ready_ids": [], "loosen_candidate": False})
        else:
            supp_submit = sorted(removed & submit_set)
            supp_ready = sorted(removed & ready_set)
            entry.update({
                "cut_rate": round(len(removed) / n_cand, 4) if n_cand else 0.0,
                "n_removed": len(removed), "n_candidates": n_cand,
                "removed_ids": sorted(removed),
                "suppression_rate_submit": round(len(supp_submit) / len(submit_set), 4) if submit_set else None,
                "suppression_rate_ready": round(len(supp_ready) / len(ready_set), 4) if ready_set else None,
                "suppressed_submit_ids": [{"id": i, "reason": reasons.get(i, "")} for i in supp_submit],
                "suppressed_ready_ids": [{"id": i, "reason": reasons.get(i, "")} for i in supp_ready],
                "loosen_candidate": bool(supp_submit or supp_ready),
            })
        if key == "ice_downgrade" and ice_diag:
            entry["advisory"] = ice_diag
        if key == "fp_pattern_check" and fp_diag:
            inert = fp_diag["n"] > 0 and fp_diag["max_top_sim"] < 0.6
            entry["diagnostics"] = {**fp_diag, "max_top_sim": round(fp_diag["max_top_sim"], 3)}
            entry["fired"] = fp_diag["max_top_sim"] >= 0.6
            if inert:
                entry["caveat"] = (
                    f"fp matcher never cleared the 0.6 review bar on any candidate "
                    f"(raw max similarity {round(fp_diag['raw_max_sim'], 3)}, thresholded top 0.0). "
                    f"{fp_diag['n_with_vuln_type']}/{fp_diag['n']} candidates carry vuln_type, but even "
                    "matching vuln_types stay sub-threshold once keyword overlap is added. suppression=0 "
                    "here means the rule set is DORMANT on these findings — not proven recall-safe.")
        filters_out[key] = entry

    loosen = [k for k, f in filters_out.items() if f["loosen_candidate"]]
    doc = {
        "generated_at": _now(),
        "mode": "real_audit",
        "audit_id": aid,
        "eval_note": "MEASUREMENT ONLY. Oracle = this audit's OWN confirmed findings (submit.jsonl / "
                     "state==ready). suppression_rate = fraction of confirmed keepers a filter recommends "
                     "removing. >0 = a filter tried to kill a finding we confirmed = loosen/make-reversible.",
        "n_candidates": n_cand,
        "oracle": {"submit": sorted(submit_set), "ready": sorted(ready_set),
                   "n_submit": len(submit_set), "n_ready": len(ready_set)},
        "shared_rejection_rules_loaded": len(rules),
        "loosen_candidates": loosen,
        "filters": filters_out,
    }
    return doc


def build_audit(aid: str) -> dict:
    """Real-audit false-suppression, writing evals/suppression_<id>.{json,md}."""
    doc = compute_audit(aid)
    (ROOT / "evals" / f"suppression_{aid}.json").write_text(json.dumps(doc, indent=2) + "\n")
    (ROOT / "evals" / f"suppression_{aid}.md").write_text(render_md_audit(doc))
    return doc


def build_sweep() -> dict:
    """Corpus-wide false-suppression: run the real-audit measure over EVERY workspace with candidates,
    aggregate per filter. Answers inductively 'does any precision filter ever remove a confirmed keeper
    across the whole corpus?' and 'does fp_pattern_check ever fire on a real finding?'."""
    aids = sorted({p.parent.parent.name for p in ROOT.glob("audits/*/output/merged_findings.json")})
    per_audit = []
    filt = {k: {"n_candidates": 0, "n_removed": 0, "suppressed": [], "audits_with_cut": 0,
                "audits_with_suppression": 0} for k, _, _ in FILTERS}
    fp_fired_audits, fp_raw_max = [], 0.0
    n_with_confirmed = 0
    total_confirmed = 0
    for aid in aids:
        try:
            doc = compute_audit(aid)
        except Exception as e:
            per_audit.append({"audit": aid, "error": str(e)[:120]})
            continue
        n_sub = doc["oracle"]["n_submit"]
        if n_sub > 0:
            n_with_confirmed += 1
            total_confirmed += n_sub
        rec = {"audit": aid, "n_candidates": doc["n_candidates"], "n_submit": n_sub,
               "n_ready": doc["oracle"]["n_ready"], "filters": {}}
        for key, f in doc["filters"].items():
            a = filt[key]
            if f.get("cut_rate") is not None:
                a["n_candidates"] += f.get("n_candidates", 0)
                a["n_removed"] += f.get("n_removed", 0) or 0
                if (f.get("n_removed") or 0) > 0:
                    a["audits_with_cut"] += 1
            supp = f.get("suppressed_submit_ids", [])
            if supp:
                a["audits_with_suppression"] += 1
                a["suppressed"] += [{"audit": aid, "id": s["id"], "reason": s.get("reason", "")} for s in supp]
            rec["filters"][key] = {"cut_rate": f.get("cut_rate"), "n_removed": f.get("n_removed"),
                                   "n_suppressed_submit": len(supp)}
            if key == "fp_pattern_check":
                d = f.get("diagnostics", {})
                rec["filters"][key]["fp_raw_max_sim"] = d.get("raw_max_sim")
                rec["filters"][key]["fp_fired"] = f.get("fired")
                if f.get("fired"):
                    fp_fired_audits.append(aid)
                fp_raw_max = max(fp_raw_max, d.get("raw_max_sim") or 0.0)
        per_audit.append(rec)

    filters_out = {}
    for key, _, _ in FILTERS:
        a = filt[key]
        filters_out[key] = {
            "corpus_cut_rate": round(a["n_removed"] / a["n_candidates"], 4) if a["n_candidates"] else None,
            "n_removed": a["n_removed"], "audits_with_cut": a["audits_with_cut"],
            "audits_with_suppression": a["audits_with_suppression"],
            "n_keepers_suppressed": len(a["suppressed"]),
            "suppressed_keepers": a["suppressed"],
        }
    doc = {
        "generated_at": _now(), "mode": "corpus_sweep",
        "eval_note": "MEASUREMENT ONLY. Corpus-wide real-audit false-suppression. suppression counts a "
                     "filter removing a finding the audit CONFIRMED (submit.jsonl). Any keeper suppressed "
                     "anywhere = loosen/make-reversible.",
        "audits_scanned": len(aids), "audits_with_confirmed_oracle": n_with_confirmed,
        "total_confirmed_keepers": total_confirmed,
        "any_keeper_suppressed": any(filters_out[k]["n_keepers_suppressed"] for k in filters_out),
        "fp_ever_fired": bool(fp_fired_audits), "fp_fired_audits": fp_fired_audits,
        "fp_corpus_raw_max_sim": round(fp_raw_max, 3),
        "filters": filters_out, "per_audit": per_audit,
    }
    (ROOT / "evals" / "suppression_sweep.json").write_text(json.dumps(doc, indent=2) + "\n")
    (ROOT / "evals" / "suppression_sweep.md").write_text(render_md_sweep(doc))
    return doc


def render_md_sweep(doc: dict) -> str:
    L = ["# Recall Lab — Corpus-Wide False-Suppression Sweep",
         f"_generated {doc['generated_at']}_",
         "",
         "Eval-only. Runs the real-audit suppression measure over every workspace with candidates. "
         "Measurement only — no pipeline change.",
         "",
         f"- Audits scanned: **{doc['audits_scanned']}**  ·  with a confirmed oracle (submit>0): "
         f"**{doc['audits_with_confirmed_oracle']}**  ·  total confirmed keepers: **{doc['total_confirmed_keepers']}**",
         f"- **Any confirmed keeper suppressed anywhere? {'⚠️ YES' if doc['any_keeper_suppressed'] else 'NO'}**",
         f"- fp_pattern_check ever fired on a real finding? {'YES' if doc['fp_ever_fired'] else 'NO'} "
         f"(corpus raw max similarity {doc['fp_corpus_raw_max_sim']}; fires at >=0.6, rejects at >0.85)",
         "",
         "| Filter | Corpus cut rate | audits w/ cut | audits w/ suppression | keepers suppressed |",
         "|---|---|---|---|---|"]
    for key, f in doc["filters"].items():
        cr = "—" if f["corpus_cut_rate"] is None else f"{f['corpus_cut_rate']:.4f}"
        L.append(f"| {key} | {cr} | {f['audits_with_cut']} | {f['audits_with_suppression']} | "
                 f"{f['n_keepers_suppressed']} |")
    L.append("")
    for key, f in doc["filters"].items():
        if f["suppressed_keepers"]:
            L += [f"### `{key}` suppressed confirmed keepers"]
            for s in f["suppressed_keepers"]:
                L.append(f"- `{s['audit']}` {s['id']}  [{s.get('reason', '')}]")
            L.append("")
    if not doc["any_keeper_suppressed"]:
        L += ["_No precision filter removed a confirmed keeper anywhere in the corpus._", ""]
    return "\n".join(L)


def render_md_audit(doc: dict) -> str:
    o = doc["oracle"]
    L = ["# Recall Lab — Real-Audit False-Suppression Report",
         f"_generated {doc['generated_at']}_  ·  audit `{doc['audit_id']}`",
         "",
         "Eval-only. Does a precision filter recommend removing a finding this audit CONFIRMED? "
         "Oracle = the audit's own `submit.jsonl` / `state==ready` set. Measurement only — no pipeline change.",
         "",
         f"- Candidates: **{doc['n_candidates']}**  ·  confirmed oracle: **{o['n_submit']} submit** / "
         f"**{o['n_ready']} ready**  ·  shared FP rules: **{doc['shared_rejection_rules_loaded']}**",
         f"- Loosen / make-reversible candidates (removed a confirmed keeper): "
         f"**{', '.join(doc['loosen_candidates']) or 'none'}**",
         "",
         "| Filter | Step | Mode | Cut rate | Suppr (submit) | Suppr (ready) | Loosen? |",
         "|---|---|---|---|---|---|---|"]
    for key, f in doc["filters"].items():
        cut = "—" if f["cut_rate"] is None else f"{f['cut_rate']:.3f}"
        ss = "—" if f["suppression_rate_submit"] is None else f"{f['suppression_rate_submit']:.3f}"
        sr = "—" if f["suppression_rate_ready"] is None else f"{f['suppression_rate_ready']:.3f}"
        flag = "⚠️ YES" if f["loosen_candidate"] else "no"
        L.append(f"| {key} | {f['step']} | {f['mode']} | {cut} | {ss} | {sr} | {flag} |")
    L.append("")
    for key, f in doc["filters"].items():
        if f.get("caveat"):
            L += [f"> **Caveat — `{key}`:** {f['caveat']}", ""]
        adv = f.get("advisory")
        if adv and adv.get("severity_ceiling_below_floor"):
            L += [f"> **Advisory — `{key}` (NOT suppression):** ICE capped {len(adv['severity_ceiling_below_floor'])} "
                  f"candidate(s) below the Medium floor (advisory severity guidance; the finding still advances): "
                  f"{', '.join(adv['severity_ceiling_below_floor'])}", ""]
        for bucket in ("suppressed_submit_ids", "suppressed_ready_ids"):
            if f.get(bucket):
                L += [f"### `{key}` removed confirmed findings ({bucket.split('_')[1]})"]
                for s in f[bucket]:
                    L.append(f"- `{s['id']}`  [{s.get('reason', '')}]")
                L.append("")
    return "\n".join(L)


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] in ("sweep", "--sweep"):
        doc = build_sweep()
        print(f"suppression_report [corpus sweep]: {doc['audits_scanned']} audits scanned, "
              f"{doc['audits_with_confirmed_oracle']} with a confirmed oracle "
              f"({doc['total_confirmed_keepers']} keepers)")
        print(f"  ANY confirmed keeper suppressed? {'YES ⚠️' if doc['any_keeper_suppressed'] else 'NO'}")
        print(f"  fp_pattern_check ever fired? {'YES' if doc['fp_ever_fired'] else 'NO'} "
              f"(corpus raw max sim {doc['fp_corpus_raw_max_sim']})")
        for key, f in doc["filters"].items():
            cr = "—" if f["corpus_cut_rate"] is None else f"{f['corpus_cut_rate']:.4f}"
            print(f"  {key:22} cut={cr:>7} audits_cut={f['audits_with_cut']:>3} "
                  f"keepers_suppressed={f['n_keepers_suppressed']}")
        print(f"  → evals/suppression_sweep.md")
        return 0
    if argv and argv[0] in ("audit", "--audit"):
        if len(argv) < 2:
            print("usage: suppression_report.py audit <audit-id>", file=sys.stderr)
            return 2
        aid = argv[1]
        doc = build_audit(aid)
        print(f"suppression_report [real audit {aid}]: {doc['n_candidates']} candidates, "
              f"oracle {doc['oracle']['n_submit']} submit / {doc['oracle']['n_ready']} ready")
        for key, f in doc["filters"].items():
            cut = "—" if f["cut_rate"] is None else f"{f['cut_rate']:.3f}"
            ss = "—" if f["suppression_rate_submit"] is None else f"{f['suppression_rate_submit']:.3f}"
            sr = "—" if f["suppression_rate_ready"] is None else f"{f['suppression_rate_ready']:.3f}"
            flag = "  ⚠️ LOOSEN CANDIDATE" if f["loosen_candidate"] else ""
            fired = ""
            if key == "fp_pattern_check" and "fired" in f:
                fired = f"  fp_fired={f['fired']}(max_sim={f['diagnostics']['max_top_sim']})"
            print(f"  {f['step']:4} {key:22} cut={cut:>6} suppr_submit={ss:>6} suppr_ready={sr:>6} "
                  f"[{f['mode']}]{fired}{flag}")
        if doc["loosen_candidates"]:
            print(f"\n  FLAG: removed a CONFIRMED keeper → loosen/make-reversible: "
                  f"{', '.join(doc['loosen_candidates'])}")
        print(f"  → evals/suppression_{aid}.md")
        return 0

    arg = argv[0] if argv else "holdout"
    set_names = ["training", "holdout"] if arg == "all" else [arg]
    doc = build(set_names)
    tl = doc["top_line"]
    print(f"suppression_report: {doc['projects_scored']} projects  "
          f"combined_cut={tl['combined_cut_rate']} combined_suppression={tl['combined_suppression_rate']}")
    for key, f in doc["filters"].items():
        cut = "—" if f["cut_rate"] is None else f"{f['cut_rate']:.3f}"
        sup = "—" if f["suppression_rate"] is None else f"{f['suppression_rate']:.3f}"
        flag = "  ⚠️ LOOSEN CANDIDATE" if f["loosen_candidate"] else ""
        print(f"  {f['step']:4} {key:22} cut={cut:>6} suppression={sup:>6} "
              f"n_suppressed={f['n_suppressed']} [{','.join(f['measurement_modes']) or 'n/a'}]{flag}")
    if tl["loosen_candidates"]:
        print(f"\n  FLAG: suppression_rate>0 → loosen/make-reversible: {', '.join(tl['loosen_candidates'])}")
    for key, f in doc["filters"].items():
        if f.get("caveat"):
            print(f"\n  CAVEAT [{key}]: {f['caveat']}")
    print(f"  → {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
