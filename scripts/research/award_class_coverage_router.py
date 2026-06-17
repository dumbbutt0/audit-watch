#!/usr/bin/env python3
"""P273 — award-class coverage router (RESEARCH-ONLY, DEFAULT-OFF, ADVISORY).

Fixes the P272 objective mismatch: impact-first triage (P269) over-weighted the lending-accounting class and
monopolized PoC slots, missing init-capital's order/access/front-run/DoS awards. This router sits BETWEEN the P267
selector and P269 triage and routes >=1 representative per DISTINCT plausible award class before filling slots within
a class, so no single class monopolizes triage. Goal is NOT "prefer access control" — it is "don't let one class
monopolize".

Deterministic classification over SOURCE-DERIVABLE signal keywords (NOT award labels). No answer key, no source-read,
no network. UN-WIRED (no run_pipeline/agent_policy/dashboard ref); does not import/modify P260/P262/P264/P267/P269/P271.

Usage:
  python scripts/research/award_class_coverage_router.py --candidates <in.json> --out <decisions.json> [--md <r.md>] [--quiet]
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config/research_award_class_coverage_router.json"
FORBIDDEN = ("severity", "reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
SELECT_LABELS = ("COVERAGE_SELECT", "COVERAGE_SELECT_HEAVY")
ALL_LABELS = SELECT_LABELS + ("COVERAGE_CONTROL", "COVERAGE_DEFER_LOW_SIGNAL", "COVERAGE_DEFER_DUPLICATE_CLASS",
                              "COVERAGE_DEFER_INFEASIBLE", "COVERAGE_UNKNOWN")
HARNESS_BLOCKERS = ("needs_beacon_fixtures", "needs_slashing_setup", "needs_snapshot_scaffolding", "needs_fork",
                    "needs_proof_fixtures")
INFEASIBLE_BLOCKERS = ("source_unavailable", "dependency_unmockable", "no_exploit_path", "no_falsifiable_assertion")


class FailClosed(Exception):
    pass


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def _locus_text(c: dict) -> str:
    """Tier 1/2 — locus/function/contract names + explicit signals + templates (pre-P277 behavior)."""
    parts = [str(c.get("locus", "")), str(c.get("function", "")), str(c.get("contract", "")),
             " ".join(c.get("signals", []) if isinstance(c.get("signals"), list) else [str(c.get("signals", ""))]),
             " ".join(c.get("templates", []))]
    return " ".join(parts).lower()


def _body_text(c: dict, cfg: dict) -> str:
    """Tier 3-6 — generated-mechanism BODY fields (allow-listed). Scans top-level allow-listed fields AND each dict in
    a `mechanisms`/`generated_mechanisms` list. Award-text fields (denylist) are NEVER read. Missing fields tolerated
    => returns '' (router then behaves exactly as pre-P277)."""
    allow = cfg.get("body_signal_fields") or []
    deny = set(cfg.get("body_field_denylist") or [])
    if not allow:
        return ""
    chunks: list[str] = []

    def _collect(d: dict):
        for k, v in d.items():
            if k in deny or k not in allow:
                continue
            if isinstance(v, str):
                chunks.append(v)
            elif isinstance(v, list):
                chunks.extend(x for x in v if isinstance(x, str))

    if isinstance(c, dict):
        _collect(c)
        for mlist_key in ("mechanisms", "generated_mechanisms"):
            for m in (c.get(mlist_key) or []):
                if isinstance(m, dict):
                    _collect(m)
    return " ".join(chunks).lower()


def _classify(c: dict, cfg: dict):
    """Return (class_name, signal_strength, detail).

    Body signals ADD weight but NEVER OVERRIDE a confident locus class (the P277 intent: 'add weight, not blindly
    override; if body strongly indicates a class the locus MISSES, the class becomes eligible'). Rule:
      - locus class = argmax of locus keyword hits (the primary classifier, unchanged from pre-P277).
      - if locus has a class (locus_hits>0): KEEP it; body only REINFORCES strength when body agrees with that same
        class (so a body-confirmed class scores higher for the recall/min_signal gate). Body never flips it.
      - if locus is blank (UNKNOWN_OTHER, locus_hits==0): body MAY assign the class (this is the recall lift — a
        class hiding in the mechanism body that the locus name missed). This is the only case body changes the class.
    Verbose body text therefore cannot swamp/reshuffle confident locus classifications."""
    locus = _locus_text(c)
    body = _body_text(c, cfg)
    weight = int(cfg.get("body_signal_weight", 1))
    body_cap = int(cfg.get("body_signal_cap_per_class", 3))  # bound a verbose body's per-class contribution
    lo_class, lo_n = "UNKNOWN_OTHER", 0
    bd_class, bd_n = "UNKNOWN_OTHER", 0
    body_classes, same_class_body = [], 0
    for cls in cfg["class_order"]:
        kws = cfg["class_signals"].get(cls, [])
        ln = sum(1 for kw in kws if kw in locus)
        bn = min(sum(1 for kw in kws if kw in body), body_cap) if body else 0
        if bn > 0:
            body_classes.append(cls)
        if ln > lo_n:
            lo_class, lo_n = cls, ln
        if bn > bd_n:
            bd_class, bd_n = cls, bn

    if lo_n > 0:
        chosen, sources, changed = lo_class, ["locus"], False
        # body reinforces strength only when it agrees with the locus class
        agree = min(sum(1 for kw in cfg["class_signals"].get(lo_class, []) if kw in body), body_cap) if body else 0
        same_class_body = agree
        strength = lo_n + weight * agree
        if agree > 0:
            sources.append("mechanism_body")
    elif bd_n > 0:
        chosen, sources, changed = bd_class, ["mechanism_body"], True  # body fills a locus gap
        strength = weight * bd_n
    else:
        chosen, sources, changed, strength = "UNKNOWN_OTHER", [], False, 0

    detail = {"class_signal_sources": sources, "body_signal_hits": same_class_body if lo_n > 0 else bd_n,
              "body_signal_classes": sorted(set(body_classes)), "final_class_score": strength,
              "body_changed_decision": changed}
    return chosen, strength, detail


def _plausible(c: dict, strength: int, cfg: dict) -> bool:
    if c.get("impact_supported") is False:
        return False
    if c.get("selector_outcome") in ("REFUTE_M1_FIRST", "REFUTE_M2_FIRST"):
        return False
    blockers = c.get("feasibility_blockers", []) or []
    if any(b in INFEASIBLE_BLOCKERS for b in blockers):
        return False
    return bool(c.get("recall_delta")) or strength >= cfg["min_signal"]


def route(candidates: list, cfg: dict) -> dict:
    caps = cfg["caps"]
    # classify + score
    enriched = []
    for i, c in enumerate(candidates):
        if not isinstance(c, dict) or "id" not in c:
            raise FailClosed(f"candidate {i} malformed (need an object with id)")
        cls, strength, detail = _classify(c, cfg)
        plaus = _plausible(c, strength, cfg)
        blockers = c.get("feasibility_blockers", []) or []
        heavy = (c.get("poc_feasibility") == "heavy") or any(b in HARNESS_BLOCKERS for b in blockers)
        score = strength + (cfg["recall_delta_bonus"] if c.get("recall_delta") else 0)
        enriched.append({"c": c, "cls": cls, "strength": strength, "plausible": plaus, "heavy": heavy,
                         "score": score, "order": i, "detail": detail})

    # group plausible by class; best-first within class
    by_class: dict = {}
    for e in enriched:
        if e["plausible"]:
            by_class.setdefault(e["cls"], []).append(e)
    for cls in by_class:
        by_class[cls].sort(key=lambda e: (-e["score"], not e["c"].get("recall_delta", False), e["order"]))

    # rank classes by their best candidate's score
    ranked_classes = sorted(by_class.keys(), key=lambda cls: (-by_class[cls][0]["score"], cfg["class_order"].index(cls)))
    ranked_classes = ranked_classes[: caps["max_classes"]]

    budget = caps["poc_budget"]
    chosen_ids = set()
    reps_per_class: dict = {}
    selected_classes = []

    # round 1: >=1 representative per distinct plausible class (round-robin, capped by budget+max_classes)
    for cls in ranked_classes:
        if len(chosen_ids) >= budget:
            break
        rep = by_class[cls][0]
        chosen_ids.add(rep["c"]["id"]); reps_per_class[cls] = 1
        selected_classes.append(cls)

    # round 2: fill remaining slots with 2nd reps of strongest classes (anti-monoculture: only after every
    # plausible monoculture-guard class has >=1 rep)
    guard_classes = set(cfg["monoculture_guard_classes"])
    unrepresented_guard = lambda: [cls for cls in by_class if cls in guard_classes and reps_per_class.get(cls, 0) == 0]
    for cls in ranked_classes:
        if len(chosen_ids) >= budget:
            break
        if unrepresented_guard():
            break  # never give a 2nd slot while a plausible guard class has 0 reps
        if reps_per_class.get(cls, 0) >= caps["max_reps_per_class"]:
            continue
        for e in by_class[cls]:
            if e["c"]["id"] not in chosen_ids:
                chosen_ids.add(e["c"]["id"]); reps_per_class[cls] += 1
                break

    # emit decisions
    decisions = []
    class_first_rep_seen: dict = {}
    for e in enriched:
        cid, cls = e["c"]["id"], e["cls"]
        blockers = e["c"].get("feasibility_blockers", []) or []
        if cid in chosen_ids:
            label = "COVERAGE_SELECT_HEAVY" if e["heavy"] else "COVERAGE_SELECT"
        elif not e["plausible"]:
            if any(b in INFEASIBLE_BLOCKERS for b in blockers):
                label = "COVERAGE_DEFER_INFEASIBLE"
            elif e["strength"] == 0 and not e["c"].get("recall_delta"):
                label = "COVERAGE_UNKNOWN" if cls == "UNKNOWN_OTHER" else "COVERAGE_DEFER_LOW_SIGNAL"
            else:
                label = "COVERAGE_DEFER_LOW_SIGNAL"
        else:
            # plausible but not chosen: class already represented (budget spent) or a control
            label = "COVERAGE_DEFER_DUPLICATE_CLASS" if reps_per_class.get(cls, 0) >= 1 else "COVERAGE_CONTROL"
        det = e.get("detail", {})
        decisions.append({
            "id": cid, "locus": e["c"].get("locus"), "award_class": cls, "signal_strength": e["strength"],
            "recall_delta": bool(e["c"].get("recall_delta")), "heavy": e["heavy"], "label": label,
            "class_signal_sources": det.get("class_signal_sources", []),
            "body_signal_hits": det.get("body_signal_hits", 0),
            "body_signal_classes": det.get("body_signal_classes", []),
            "final_class_score": det.get("final_class_score", e["strength"]),
            "body_changed_decision": det.get("body_changed_decision", False),
            "severity": None, "reportable": False, "submission_ready": False,
            "concluded": False, "emits_finding": False, "production_routing": False,
            "status": "ADVISORY_COVERAGE_DECISION",
        })

    handoff = [d["id"] for d in decisions if d["label"] in SELECT_LABELS]
    return {
        "selected_classes": selected_classes,
        "representatives_per_class": reps_per_class,
        "class_rationale": {cls: f"best signal_strength {by_class[cls][0]['strength']}"
                            f"{' (recall-delta)' if by_class[cls][0]['c'].get('recall_delta') else ''}"
                            for cls in selected_classes},
        "skipped_classes": [cls for cls in by_class if cls not in selected_classes],
        "handoff_queue_to_p269": handoff,
        "decisions": decisions,
    }


def _enforce_guards(decisions: list) -> list:
    viol = []
    for d in decisions:
        if d.get("severity") is not None:
            viol.append({"id": d.get("id"), "field": "severity", "value": d.get("severity")})
        for f in FORBIDDEN:
            if d.get(f) not in (False, None):
                viol.append({"id": d.get("id"), "field": f, "value": d.get(f)})
        if d.get("status") != "ADVISORY_COVERAGE_DECISION":
            viol.append({"id": d.get("id"), "field": "status", "value": d.get("status")})
        if d.get("label") not in ALL_LABELS:
            viol.append({"id": d.get("id"), "field": "label", "value": d.get("label")})
    return viol


def _validate_config(cfg: dict) -> dict:
    if not cfg:
        raise FailClosed("config missing/unparseable")
    if cfg.get("is_gate") is not False or cfg.get("research_only") is not True or cfg.get("emits_findings") is not False:
        raise FailClosed("config research flags not set safely")
    caps = cfg.get("caps", {})
    for k in ("max_classes", "max_reps_per_class", "poc_budget"):
        v = caps.get(k)
        if not isinstance(v, int) or v <= 0:
            raise FailClosed(f"cap {k}={v} not a positive int")
    if caps["max_classes"] > caps.get("hard_max_classes", 8):
        raise FailClosed("max_classes exceeds hard max")
    if caps["poc_budget"] > caps.get("hard_max_poc_budget", 10):
        raise FailClosed("poc_budget exceeds hard max")
    return cfg


def run(cand_path, out_path, md_path, cfg) -> int:
    data = _load(cand_path)
    if data is None:
        raise FailClosed(f"missing/unreadable candidates input: {cand_path}")
    cands = data.get("candidates") if isinstance(data, dict) else data
    if not isinstance(cands, list) or not cands:
        raise FailClosed("candidates input must be a non-empty list (or {candidates:[...]})")

    result = route(cands, cfg)
    viol = _enforce_guards(result["decisions"])
    guard = {"module": "award_class_coverage_router", "guard_violations": len(viol), "violations": viol,
             "result": "PASS" if not viol else "FAIL"}
    out_dir = Path(out_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "coverage_guard_report.json").write_text(json.dumps(guard, indent=2))
    if viol:
        raise FailClosed(f"GUARD FAILURE: {len(viol)} violation(s); no decision output emitted")

    out = {
        "module": "award_class_coverage_router", "generated_at": datetime.now(timezone.utc).isoformat(),
        "is_gate": False, "research_only": True, "routes_in_production": False, "emits_findings": False,
        "concludes_vulnerability": False, "output_type": "advisory_coverage_decisions", "guard_violations": 0,
        **result,
        "selected_count": len(result["handoff_queue_to_p269"]),
    }
    Path(out_path).write_text(json.dumps(out, indent=2))
    if md_path:
        Path(md_path).write_text(_markdown(out))
    return 0


def _markdown(out: dict) -> str:
    rows = ["# Award-class coverage router — ADVISORY decisions\n",
            "**ADVISORY ONLY. No severity / reportability / submission / routing.**\n",
            f"selected_classes: {', '.join(out['selected_classes'])}\n",
            "| id | award_class | signal | recall-Δ | heavy | label |", "|---|---|---|---|---|---|"]
    for d in out["decisions"]:
        rows.append(f"| {d['id']} | {d['award_class']} | {d['signal_strength']} | "
                    f"{'Y' if d['recall_delta'] else '-'} | {'Y' if d['heavy'] else '-'} | **{d['label']}** |")
    return "\n".join(rows) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates")
    ap.add_argument("--out")
    ap.add_argument("--md")
    ap.add_argument("--config")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        cfg = _validate_config(_load(args.config or CONFIG_PATH))
        if not (args.candidates and args.out):
            raise FailClosed("requires --candidates and --out")
        run(args.candidates, args.out, args.md, cfg)
    except FailClosed as e:
        print(f"[award_class_coverage_router] FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    if not args.quiet:
        print(f"[award_class_coverage_router] ADVISORY coverage written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
