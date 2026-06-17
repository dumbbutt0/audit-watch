#!/usr/bin/env python3
"""P267 — pairwise mechanism selector (RESEARCH-ONLY, DEFAULT-OFF, ADVISORY).

Fixes the P266 ranking/selection bottleneck: an awarded mechanism that is present in B/C top-2 gets dropped before
completion/PoC because a rival is easier to PoC (lower impact). This selector makes TERMINAL IMPACT the primary axis,
applies an explicit anti-easy-PoC-bias penalty, and defaults to KEEP_BOTH rather than discarding the higher-impact
mechanism. A KEEP_BOTH is a success: it carries both into completion/PoC.

Deterministic. Operates on STRUCTURED per-mechanism dimension signals (source-derivable, NOT award labels). No
answer key, no source-reading, no network. Advisory only: it never sets severity/reportability/submission/routing,
and a runtime guard fails closed (exit nonzero, no decision output) on any such leakage.

UN-WIRED: not referenced by run_pipeline / agent_policy / dashboard / routing. Does not import or modify P260/P262/
P264 modules.

Usage:
  python scripts/research/mechanism_pairwise_selector.py --pairs <input.json> --out <decisions.json> [--md <r.md>] [--quiet]
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config/research_mechanism_pairwise_selector.json"
FORBIDDEN = ("severity", "reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


class FailClosed(Exception):
    pass


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def _w(table: dict, key, default=0):
    return table.get(key, default)


def _terminal_impact(m: dict, cfg: dict) -> int:
    return (_w(cfg["impact_class_weight"], m.get("impact_class"))
            + _w(cfg["value_at_risk_weight"], m.get("value_at_risk"))
            + _w(cfg["persistence_weight"], m.get("persistence")))


def _validity(m: dict, cfg: dict) -> int:
    return (_w(cfg["attacker_control_weight"], m.get("attacker_control"))
            + _w(cfg["refutation_resistance_weight"], m.get("refutation_resistance"))
            + _w(cfg["intent_violation_weight"], m.get("intent_violation"))
            + _w(cfg["victim_gainer_clarity_weight"], m.get("victim_gainer_clarity")))


def _plausible(m: dict) -> bool:
    return m.get("refutation_resistance") != "refuted" and m.get("attacker_control") not in (None, "none")


def _feasibility_rank(m: dict, cfg: dict) -> int:
    return _w(cfg["poc_feasibility_rank"], m.get("poc_feasibility"), 2)


def decide_pair(m1: dict, m2: dict, cfg: dict) -> dict:
    """Deterministic decision for one mechanism pair. Returns an advisory decision record."""
    ti = {"M1": _terminal_impact(m1, cfg), "M2": _terminal_impact(m2, cfg)}
    val = {"M1": _validity(m1, cfg), "M2": _validity(m2, cfg)}
    plaus = {"M1": _plausible(m1), "M2": _plausible(m2)}
    feas = {"M1": _feasibility_rank(m1, cfg), "M2": _feasibility_rank(m2, cfg)}
    min_gap = cfg["min_impact_gap"]

    hi, lo = ("M1", "M2") if ti["M1"] >= ti["M2"] else ("M2", "M1")
    gap = abs(ti["M1"] - ti["M2"])
    decisive, anti_easy = [], False
    refute_first = "REFUTE_M1_FIRST" if hi == "M1" else "REFUTE_M2_FIRST"
    select_hi = "SELECT_M1" if hi == "M1" else "SELECT_M2"
    select_lo = "SELECT_M2" if hi == "M1" else "SELECT_M1"

    if gap >= min_gap:
        # higher-impact mechanism exists and is material
        if not plaus[hi]:
            # a dramatic / high-impact mechanism that is refuted or unreachable must NOT auto-win
            if m1.get("refutation_resistance") == "refuted" or m2.get("refutation_resistance") == "refuted":
                outcome, decisive = refute_first, ["terminal_impact(high) but refuted -> refute before trusting"]
            elif plaus[lo]:
                outcome, decisive = select_lo, ["high-impact mechanism not attacker-reachable; low-impact one is plausible"]
            else:
                outcome, decisive = "INSUFFICIENT_EVIDENCE", ["neither plausible"]
        else:
            # high-impact mechanism IS plausible -> protect it
            anti_easy = feas[lo] > feas[hi]  # lo is easier to PoC than hi (the P266 trap)
            if not plaus[lo]:
                outcome = select_hi
                decisive = ["terminal_impact_dominance", "rival weak/refuted"]
            else:
                outcome = "KEEP_BOTH"
                decisive = ["terminal_impact_dominance", "both plausible -> protect high-impact before PoC"]
            if anti_easy:
                decisive.append("anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact")
    else:
        # near-equal terminal impact
        if plaus["M1"] != plaus["M2"]:
            keep = "M1" if plaus["M1"] else "M2"
            outcome = "SELECT_M1" if keep == "M1" else "SELECT_M2"
            decisive = ["near-equal impact; selected the plausible one (other refuted/unreachable)"]
        elif plaus["M1"] and plaus["M2"]:
            outcome, decisive = "KEEP_BOTH", ["near-equal impact, both plausible -> keep both"]
        else:
            outcome, decisive = "INSUFFICIENT_EVIDENCE", ["near-equal impact, neither plausible"]

    decisive = decisive[: cfg["caps"]["max_decisive_dimensions"]]
    uncertainty = []
    if gap < min_gap:
        uncertainty.append("terminal-impact gap below min_gap; decision is low-confidence")
    if not plaus["M1"] or not plaus["M2"]:
        uncertainty.append("at least one mechanism is refuted/unreachable as scored")
    return {
        "pair_id": f"{m1.get('id', 'M1')}|{m2.get('id', 'M2')}",
        "M1": {"id": m1.get("id"), "label": m1.get("label"), "terminal_impact": ti["M1"], "validity": val["M1"],
               "plausible": plaus["M1"], "poc_feasibility": m1.get("poc_feasibility")},
        "M2": {"id": m2.get("id"), "label": m2.get("label"), "terminal_impact": ti["M2"], "validity": val["M2"],
               "plausible": plaus["M2"], "poc_feasibility": m2.get("poc_feasibility")},
        "impact_gap": gap,
        "anti_easy_poc_flag": anti_easy,
        "outcome": outcome,
        "decisive_dimensions": decisive,
        "uncertainty": uncertainty,
        "falsification_questions": [m1.get("falsifier"), m2.get("falsifier")],
        # advisory contract — hard-stamped
        "severity": None, "reportable": False, "submission_ready": False,
        "concluded": False, "emits_finding": False, "production_routing": False,
        "status": "ADVISORY_SELECTOR_DECISION",
    }


def _enforce_guards(decisions: list) -> list:
    viol = []
    for d in decisions:
        if d.get("severity") is not None:
            viol.append({"pair_id": d.get("pair_id"), "field": "severity", "value": d.get("severity")})
        for f in FORBIDDEN:
            if d.get(f) not in (False, None):
                viol.append({"pair_id": d.get("pair_id"), "field": f, "value": d.get(f)})
        if d.get("status") != "ADVISORY_SELECTOR_DECISION":
            viol.append({"pair_id": d.get("pair_id"), "field": "status", "value": d.get("status")})
        if d.get("outcome") not in ("SELECT_M1", "SELECT_M2", "KEEP_BOTH", "REFUTE_M1_FIRST",
                                    "REFUTE_M2_FIRST", "INSUFFICIENT_EVIDENCE"):
            viol.append({"pair_id": d.get("pair_id"), "field": "outcome", "value": d.get("outcome")})
    return viol


def _validate_config(cfg: dict) -> dict:
    if not cfg:
        raise FailClosed("config missing/unparseable")
    if cfg.get("is_gate") is not False or cfg.get("research_only") is not True or cfg.get("emits_findings") is not False:
        raise FailClosed("config research flags not set safely")
    caps = cfg.get("caps", {})
    for k in ("max_pairs", "max_decisive_dimensions"):
        v = caps.get(k)
        if not isinstance(v, int) or v <= 0:
            raise FailClosed(f"cap {k}={v} not a positive int")
    if not isinstance(cfg.get("min_impact_gap"), int):
        raise FailClosed("min_impact_gap not an int")
    return cfg


def run(pairs_path, out_path, md_path, cfg) -> int:
    data = _load(pairs_path)
    if data is None:
        raise FailClosed(f"missing/unreadable pairs input: {pairs_path}")
    pairs = data.get("pairs") if isinstance(data, dict) else data
    if not isinstance(pairs, list) or not pairs:
        raise FailClosed("pairs input must be a non-empty list (or {pairs:[...]})")
    if len(pairs) > cfg["caps"]["max_pairs"]:
        raise FailClosed(f"too many pairs ({len(pairs)} > cap {cfg['caps']['max_pairs']})")

    decisions = []
    for i, pr in enumerate(pairs):
        if not isinstance(pr, dict) or "M1" not in pr or "M2" not in pr:
            raise FailClosed(f"pair {i} malformed (need M1 and M2 objects)")
        d = decide_pair(pr["M1"], pr["M2"], cfg)
        d["case"] = pr.get("case", f"pair_{i}")
        decisions.append(d)

    viol = _enforce_guards(decisions)
    guard = {"module": "mechanism_pairwise_selector", "guard_violations": len(viol),
             "violations": viol, "result": "PASS" if not viol else "FAIL"}
    out_dir = Path(out_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "selector_guard_report.json").write_text(json.dumps(guard, indent=2))
    if viol:
        raise FailClosed(f"GUARD FAILURE: {len(viol)} violation(s); no decision output emitted")

    out = {
        "module": "mechanism_pairwise_selector", "generated_at": datetime.now(timezone.utc).isoformat(),
        "is_gate": False, "research_only": True, "routes_in_production": False, "emits_findings": False,
        "concludes_vulnerability": False, "output_type": "advisory_selector_decisions",
        "guard_violations": 0, "decision_count": len(decisions), "decisions": decisions,
    }
    Path(out_path).write_text(json.dumps(out, indent=2))
    if md_path:
        Path(md_path).write_text(_markdown(decisions))
    return 0


def _markdown(decisions: list) -> str:
    rows = ["# Pairwise mechanism selector — ADVISORY decisions\n",
            "**ADVISORY ONLY. No severity / reportability / submission / routing.**\n",
            "| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |",
            "|---|---|---|---|---|---|---|"]
    for d in decisions:
        rows.append(f"| {d['case']} | {d['M1']['label']} ({d['M1']['terminal_impact']}) | "
                    f"{d['M2']['label']} ({d['M2']['terminal_impact']}) | {d['impact_gap']} | "
                    f"{'YES' if d['anti_easy_poc_flag'] else 'no'} | **{d['outcome']}** | "
                    f"{'; '.join(d['decisive_dimensions'])} |")
    return "\n".join(rows) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs")
    ap.add_argument("--out")
    ap.add_argument("--md")
    ap.add_argument("--config")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        cfg = _validate_config(_load(args.config or CONFIG_PATH))
        if not (args.pairs and args.out):
            raise FailClosed("requires --pairs and --out")
        run(args.pairs, args.out, args.md, cfg)
    except FailClosed as e:
        print(f"[mechanism_pairwise_selector] FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    if not args.quiet:
        print(f"[mechanism_pairwise_selector] ADVISORY decisions written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
