#!/usr/bin/env python3
"""P269 — impact-first PoC triage policy (RESEARCH-ONLY, DEFAULT-OFF, ADVISORY).

Fixes the P268 triage bottleneck: a recall-surfaced, award-class-fit subsystem (karak NativeVault/slashing/snapshot)
was de-scoped at triage because its PoC looked heavier, and the easier (non-awarded) subsystem was routed instead.
This policy ranks PoC candidates by AWARD-CLASS IMPACT FIT first; PoC feasibility is a CONSTRAINT (route
HEAVY_POC_REQUIRED / PARTIAL_RUNTIME), never a reason to drop an award-class-fit subsystem. A lower-impact candidate
never displaces a higher-impact one for being easier; each high-impact subsystem gets >=1 routed representative.

Deterministic. Operates on STRUCTURED candidate signals (source-derivable, NOT award labels). No answer key, no
source-reading, no network. UN-WIRED (no run_pipeline/agent_policy/dashboard reference); does not import/modify
P260/P262/P264/P267.

Usage:
  python scripts/research/impact_first_poc_triage.py --candidates <in.json> --out <decisions.json> [--md <r.md>] [--quiet]
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config/research_impact_first_poc_triage.json"
FORBIDDEN = ("severity", "reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
SELECT_OUTCOMES = ("SELECT_FOR_FULL_POC", "SELECT_FOR_PARTIAL_RUNTIME", "SELECT_FOR_MANUAL_HARNESS_DESIGN")
ALL_OUTCOMES = SELECT_OUTCOMES + ("KEEP_AS_CONTROL", "DEFER_LOW_IMPACT", "DEFER_INFEASIBLE")


class FailClosed(Exception):
    pass


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def _w(table: dict, key, default=0):
    return table.get(key, default)


def _impact_fit(c: dict, cfg: dict) -> int:
    fit = (_w(cfg["impact_class_weight"], c.get("impact_class"))
           + _w(cfg["value_at_risk_weight"], c.get("value_at_risk"))
           + _w(cfg["terminality_weight"], c.get("terminality")))
    if c.get("recall_delta"):
        fit += cfg["recall_delta_bonus"]
    if c.get("selector_outcome") in cfg["selector_preservation_outcomes"]:
        fit += cfg["selector_preservation_bonus"]
    return fit


def _classify(c: dict, cfg: dict, fit: int):
    """Return (outcome, heavy_poc, decisive, blocker)."""
    blockers = c.get("feasibility_blockers", []) or []
    infeasible = [b for b in blockers if b in cfg["infeasible_blockers"]]
    harness = [b for b in blockers if b in cfg["harness_weight_blockers"]]
    feas = c.get("poc_feasibility", "moderate")
    high = fit >= cfg["high_impact_threshold"]

    # 1. anti-drama: unsupported high-drama impact is NOT routed on drama
    if high and c.get("impact_supported") is False:
        return "DEFER_LOW_IMPACT", False, ["high-drama impact NOT source-backed -> not routed on drama"], None
    # 2. genuine infeasibility is the only reason to defer a high-impact candidate
    if infeasible:
        return "DEFER_INFEASIBLE", False, ["genuinely infeasible"], infeasible[0]
    # 3. high impact -> route (heavy if needed)
    if high:
        heavy = (feas == "heavy") or bool(harness)
        if heavy:
            # partial runtime if plausible, else manual harness design -- both ROUTED, not dropped
            if c.get("partial_runtime_plausible", True):
                return "SELECT_FOR_PARTIAL_RUNTIME", True, ["award-class impact fit; heavy harness -> partial runtime (not de-scoped)"], None
            return "SELECT_FOR_MANUAL_HARNESS_DESIGN", True, ["award-class impact fit; heavy harness -> manual design (not de-scoped)"], None
        return "SELECT_FOR_FULL_POC", False, ["award-class impact fit; full PoC"], None
    # 4. low impact
    if feas == "easy":
        return "KEEP_AS_CONTROL", False, ["low impact, easy -> control candidate (only if budget remains)"], None
    return "DEFER_LOW_IMPACT", False, ["below high-impact threshold"], None


def triage(candidates: list, cfg: dict) -> list:
    scored = []
    for i, c in enumerate(candidates):
        if not isinstance(c, dict) or "id" not in c:
            raise FailClosed(f"candidate {i} malformed (need an object with id)")
        fit = _impact_fit(c, cfg)
        outcome, heavy, decisive, blocker = _classify(c, cfg, fit)
        scored.append({"c": c, "fit": fit, "outcome": outcome, "heavy": heavy, "decisive": decisive,
                       "blocker": blocker, "order": i})

    # impact-first order; ties -> recall_delta, then heavier-but-routed, then input order (stable)
    scored.sort(key=lambda s: (-s["fit"], not s["c"].get("recall_delta", False),
                               not s["heavy"], s["order"]))

    # subsystem clustering + budget: ensure >=1 routed representative per high-impact subsystem before a
    # KEEP_AS_CONTROL consumes budget; cap total SELECT_* at poc_budget (high-impact reps never displaced by control)
    budget = cfg["caps"]["poc_budget"]
    selected_subsystems, selects = set(), 0
    out = []
    for s in scored:
        c, outcome = s["c"], s["outcome"]
        sub = c.get("subsystem", c.get("id"))
        if outcome in SELECT_OUTCOMES:
            if selects < budget:
                selected_subsystems.add(sub)
                selects += 1
            else:
                # budget exhausted: a high-impact candidate already represented stays selected only if its
                # subsystem isn't yet represented; otherwise demote to deferred-for-budget (recorded, not dropped silently)
                if sub not in selected_subsystems:
                    selected_subsystems.add(sub); selects += 1  # always represent a NEW high-impact subsystem
                else:
                    outcome = "DEFER_LOW_IMPACT"
                    s["decisive"] = s["decisive"] + ["budget exhausted; subsystem already represented"]
        elif outcome == "KEEP_AS_CONTROL":
            # controls only consume budget after all SELECT_* are placed
            if selects >= budget:
                outcome = "DEFER_LOW_IMPACT"
                s["decisive"] = s["decisive"] + ["control deferred: budget reserved for high-impact subsystems"]
        out.append({
            "id": c["id"], "locus": c.get("locus"), "subsystem": sub,
            "impact_class": c.get("impact_class"), "impact_fit": s["fit"], "recall_delta": bool(c.get("recall_delta")),
            "poc_feasibility": c.get("poc_feasibility"), "heavy_poc": s["heavy"],
            "selector_outcome": c.get("selector_outcome"),
            "outcome": outcome, "decisive_dimensions": s["decisive"][: cfg["caps"]["max_decisive_dimensions"]],
            "feasibility_blocker": s["blocker"],
            "severity": None, "reportable": False, "submission_ready": False,
            "concluded": False, "emits_finding": False, "production_routing": False,
            "status": "ADVISORY_TRIAGE_DECISION",
        })
    return out


def _enforce_guards(decisions: list) -> list:
    viol = []
    for d in decisions:
        if d.get("severity") is not None:
            viol.append({"id": d.get("id"), "field": "severity", "value": d.get("severity")})
        for f in FORBIDDEN:
            if d.get(f) not in (False, None):
                viol.append({"id": d.get("id"), "field": f, "value": d.get(f)})
        if d.get("status") != "ADVISORY_TRIAGE_DECISION":
            viol.append({"id": d.get("id"), "field": "status", "value": d.get("status")})
        if d.get("outcome") not in ALL_OUTCOMES:
            viol.append({"id": d.get("id"), "field": "outcome", "value": d.get("outcome")})
    return viol


def _validate_config(cfg: dict) -> dict:
    if not cfg:
        raise FailClosed("config missing/unparseable")
    if cfg.get("is_gate") is not False or cfg.get("research_only") is not True or cfg.get("emits_findings") is not False:
        raise FailClosed("config research flags not set safely")
    caps = cfg.get("caps", {})
    for k in ("max_candidates", "poc_budget", "max_decisive_dimensions"):
        v = caps.get(k)
        if not isinstance(v, int) or v <= 0:
            raise FailClosed(f"cap {k}={v} not a positive int")
    if not isinstance(cfg.get("high_impact_threshold"), int):
        raise FailClosed("high_impact_threshold not an int")
    return cfg


def run(cand_path, out_path, md_path, cfg) -> int:
    data = _load(cand_path)
    if data is None:
        raise FailClosed(f"missing/unreadable candidates input: {cand_path}")
    cands = data.get("candidates") if isinstance(data, dict) else data
    if not isinstance(cands, list) or not cands:
        raise FailClosed("candidates input must be a non-empty list (or {candidates:[...]})")
    if len(cands) > cfg["caps"]["max_candidates"]:
        raise FailClosed(f"too many candidates ({len(cands)} > cap)")

    decisions = triage(cands, cfg)
    viol = _enforce_guards(decisions)
    guard = {"module": "impact_first_poc_triage", "guard_violations": len(viol),
             "violations": viol, "result": "PASS" if not viol else "FAIL"}
    out_dir = Path(out_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "triage_guard_report.json").write_text(json.dumps(guard, indent=2))
    if viol:
        raise FailClosed(f"GUARD FAILURE: {len(viol)} violation(s); no decision output emitted")

    out = {
        "module": "impact_first_poc_triage", "generated_at": datetime.now(timezone.utc).isoformat(),
        "is_gate": False, "research_only": True, "routes_in_production": False, "emits_findings": False,
        "concludes_vulnerability": False, "output_type": "advisory_triage_decisions",
        "guard_violations": 0, "poc_budget": cfg["caps"]["poc_budget"],
        "selected_count": sum(1 for d in decisions if d["outcome"] in SELECT_OUTCOMES),
        "decision_count": len(decisions), "decisions": decisions,
    }
    Path(out_path).write_text(json.dumps(out, indent=2))
    if md_path:
        Path(md_path).write_text(_markdown(decisions))
    return 0


def _markdown(decisions: list) -> str:
    rows = ["# Impact-first PoC triage — ADVISORY decisions\n",
            "**ADVISORY ONLY. No severity / reportability / submission / routing.**\n",
            "| id | subsystem | impact_class | fit | recall-Δ | feasibility | heavy | outcome |",
            "|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        rows.append(f"| {d['id']} | {d['subsystem']} | {d['impact_class']} | {d['impact_fit']} | "
                    f"{'Y' if d['recall_delta'] else '-'} | {d['poc_feasibility']} | "
                    f"{'Y' if d['heavy_poc'] else '-'} | **{d['outcome']}** |")
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
        print(f"[impact_first_poc_triage] FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    if not args.quiet:
        print(f"[impact_first_poc_triage] ADVISORY triage written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
