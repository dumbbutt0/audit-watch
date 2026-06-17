#!/usr/bin/env python3
"""
recall_first_shape_sweep.py — P262 RESEARCH-ONLY, DEFAULT-OFF, UN-WIRED recall-expansion wrapper.

Diagnosis (P259/P262): recall collapsed because of EARLY LOCUS PRUNING — checkpoint/prioritizer sees the right
locus, manual selection narrows to 2–5 loci, and shape discovery never runs on the skipped award-carrying surface.
This wrapper applies the one-shot fix: MOVE SHAPE DISCOVERY BEFORE NARROW MANUAL SELECTION. It forces shape
discovery over a bounded high-risk surface set (recall-first inclusion policy), adds an optional LOWER-PRIORITY T9
math/units family (Basin-style recall), and hands a BOUNDED candidate set to downstream B/C ranking + five-op
completion.

ZERO-CONCLUSION-FP GUARD (self-tripwire): advisory only. Never emits severity / concluded:true / vulnerability:true
/ reportable:true / submission_ready:true. Every candidate carries a status label in
{RECALL_CANDIDATE_ONLY, NEEDS_RANKING, NEEDS_COMPLETION, NEEDS_REFUTATION}. A recall candidate may ONLY become a
finding after a later separate stage proves mechanism+control+delta+victim+impact+B/C-survival+completion+FP-refutation.

Reuses (does not modify) the P260 prioritizer helpers. Requires NO answer key.

Usage:
  python scripts/research/recall_first_shape_sweep.py --manifest <p> --accounting <p> --state-transition <p> \
      [--base-candidates <p>] [--prioritizer <p260.json>] --out <out.json> [--md <out.md>] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
# Reuse P260 prioritizer (importable, unchanged).
import locus_shape_prioritizer as lsp  # noqa: E402

CFG_PATH = ROOT / "config" / "research_recall_first_shape_sweep.json"
T7, T8 = "T7_liquidation_solvency_boundary", "T8_shareprice_donation_inflation"


def _load(p) -> dict | list:
    try:
        return json.loads(Path(p).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t9_mechanism(contract: str, fn: str, signature: str, t9: dict, markers: list) -> dict:
    """Build a T9 (math/units) interrogative mechanism — lower priority, ranked last."""
    return {
        "template_id": t9["template_id"],
        "mechanism_summary": f"[T9] {contract}.{fn}: {t9['summary']}",
        "source_backed_trigger": f"{contract}.{fn} {signature}".strip(),
        "matched_markers": markers,
        "attacker_action": "operator-to-derive",
        "affected_state_assets_permissions": "operator-to-derive (decimals/scale/precision/convergence)",
        "expected_value_delta": "operator-to-derive",
        "victim_gainer_hypothesis": "operator-to-derive",
        "terminality_hypothesis": "operator-to-derive",
        "amplification_hypothesis": "operator-to-derive",
        "protocol_comparand_hint": "operator-to-derive (reference math / exact conversion / convergence guarantee)",
        "assumptions": "operator-to-derive",
        "falsification_question": t9["falsifier"],
        "ranking_features_for_profile_B": {"messy_not_tidy": True, "math_units_class": True},
        "ranking_features_for_profile_C": {"candidate_for_runner_up_overtake": False, "terminal_delta_class": t9["template_id"]},
        "output_type": "mechanism_hypothesis", "concluded": False, "severity": None, "confidence": None,
        "rank_last": True,
    }


def sweep(manifest: dict, acct: dict, st: dict, base, p260_cfg: dict, cfg: dict, prior_loci: list | None) -> dict:
    rf, caps, t9 = cfg["recall_first"], cfg["caps"], cfg["t9_math_units"]
    acct_hits, st_hits = lsp._checkpoint_hits(acct), lsp._checkpoint_hits(st)

    # Full prioritized list (reuse P260 scoring; do NOT use P260's truncated output).
    ranked = prior_loci if prior_loci else lsp.prioritize(manifest, acct, st, base, p260_cfg, with_source=False)
    rank_of = {f"{l['contract']}:{l['function']}": i for i, l in enumerate(ranked)}

    # --- Recall-first inclusion over ALL in-scope fn items (no P260 low-signal pre-filter = the fix) ---
    items = [it for it in (manifest.get("items", []) if isinstance(manifest, dict) else [])
             if it.get("kind") in ("function", "initializer", "constructor") and it.get("in_scope", True)]
    by_key = {f"{it.get('contract','')}:{it.get('name','')}": it for it in items}

    included: dict[str, dict] = {}  # key -> {reasons}
    def add(key, reason):
        included.setdefault(key, {"reasons": []})["reasons"].append(reason)

    # (1) top-N overall by P260 score
    for l in ranked[:rf["top_n_overall"]]:
        add(f"{l['contract']}:{l['function']}", "top_n_overall")
    # (2) all T7/T8 loci within top-K
    for l in ranked[:rf["t7t8_within_top"]]:
        if any(t in (l.get("applied_shape_templates") or []) for t in (T7, T8)):
            add(f"{l['contract']}:{l['function']}", "t7t8_within_top")
    # (3) checkpoint-hit funcs within top-K whose name matches recall keywords
    for l in ranked[:rf["checkpoint_hit_name_within_top"]]:
        key = f"{l['contract']}:{l['function']}"
        fams = acct_hits.get(key, set()) | st_hits.get(key, set())
        if fams and any(kw in l["function"].lower() for kw in rf["name_keywords"]):
            add(key, "checkpoint_hit_name_keyword")
    # (4) ANY checkpoint-hit locus with name/signature/tag evidence markers (this rescues pruned loci)
    for key, it in by_key.items():
        fams = acct_hits.get(key, set()) | st_hits.get(key, set())
        if not fams:
            continue
        blob = (it.get("name", "") + " " + (it.get("signature", "") or "") + " " +
                " ".join(it.get("tags", []) or [])).lower()
        if any(m in blob for m in rf["evidence_markers"]) or it.get("external_calls"):
            add(key, "checkpoint_hit_evidence_marker")
    # (5) T9 math/units recall: math-named loci (checkpoint-hit OR strong-math name) — bounded, ranked last.
    #     Restores Basin-style math recall (decodeWellData / calcReserveAtRatio) that T1-T8 + the pre-filter dropped.
    t9_strong = t9.get("strong_name_markers", [])
    t9_only_added = 0
    for key, it in sorted(by_key.items(), key=lambda kv: rank_of.get(kv[0], 10**6)):
        if key in included:
            continue
        name_l = it.get("name", "").lower()
        if not any(m in name_l for m in t9["markers"]):
            continue
        fams = acct_hits.get(key, set()) | st_hits.get(key, set())
        if fams or any(m in name_l for m in t9_strong):
            if t9_only_added >= t9.get("max_t9_only_loci", 8):
                break
            add(key, "t9_math_name")
            t9_only_added += 1

    # --- Build swept candidates: route templates (T1-T8 reuse) + optional trailing T9 ---
    swept = []
    total_mechs = 0
    truncated = False
    # order swept loci by P260 rank (skipped-but-included loci still keep their score order; unranked -> end)
    keys_sorted = sorted(included.keys(), key=lambda k: rank_of.get(k, 10**6))
    for key in keys_sorted:
        it = by_key.get(key)
        if not it:
            continue
        contract, fn = it.get("contract", ""), it.get("name", "")
        sig = it.get("signature", "") or ""
        name_l, sig_l = fn.lower(), sig.lower()
        templates = lsp._route_templates(name_l, sig_l, bool(it.get("external_calls")), "", p260_cfg)
        mechs = []
        per_tmpl: dict[str, int] = {}
        for t in templates:
            if per_tmpl.get(t, 0) >= caps["max_mechs_per_template_per_locus"]:
                continue
            mechs.append(lsp._mk_mechanism(t, contract, fn, sig, templates))
            per_tmpl[t] = per_tmpl.get(t, 0) + 1
        # optional T9 (lower-priority, trailing, ranked last) — only if math/units markers present
        blob = name_l + " " + sig_l + " " + " ".join(it.get("tags", []) or []).lower()
        t9_markers = [m for m in t9["markers"] if m in blob]
        if t9_markers:
            mechs.append(_t9_mechanism(contract, fn, sig, t9, t9_markers))
        if not mechs:
            continue
        # local prune to cap per locus: keep non-T9 first (subtle-accounting path), T9 last so it never dominates
        mechs.sort(key=lambda m: 1 if m.get("rank_last") else 0)
        if len(mechs) > caps["max_mechs_per_locus"]:
            mechs = mechs[:caps["max_mechs_per_locus"]]
        fams = sorted(acct_hits.get(key, set()) | st_hits.get(key, set()))
        status = "RECALL_CANDIDATE_ONLY"  # advisory; downstream decides
        swept.append({
            "locus_key": key, "contract": contract, "function": fn,
            "source_path": it.get("file"), "source_span": it.get("source_span"),
            "p260_rank": rank_of.get(key, None),
            "inclusion_reasons": included[key]["reasons"],
            "checkpoint_signal": fams,
            "applied_shape_templates": templates + ([t9["template_id"]] if t9_markers else []),
            "t9_applied": bool(t9_markers),
            "candidate_mechanisms": mechs,
            "status_label": status,
            "needs": ["NEEDS_RANKING", "NEEDS_COMPLETION", "NEEDS_REFUTATION"],
        })

    # rank swept loci: included-by-strong-reason + P260 rank; bound to caps
    swept.sort(key=lambda s: (s["p260_rank"] if s["p260_rank"] is not None else 10**6))
    if len(swept) > caps["max_swept_loci_json"]:
        swept = swept[:caps["max_swept_loci_json"]]
        truncated = True
    # cap total mechanisms handed to ranking
    for s in swept:
        for m in s["candidate_mechanisms"]:
            if total_mechs >= caps["max_total_mechs_to_ranking"]:
                m["_dropped_over_total_cap"] = True
                truncated = True
            else:
                total_mechs += 1
    for s in swept:
        s["candidate_mechanisms"] = [m for m in s["candidate_mechanisms"] if not m.get("_dropped_over_total_cap")]
    swept = [s for s in swept if s["candidate_mechanisms"]]

    return {"swept_loci": swept, "total_mechs_to_ranking": total_mechs, "truncated": truncated,
            "candidate_loci_considered": len(ranked)}


def _assert_no_conclusions(report: dict, cfg: dict):
    forbidden = cfg["forbidden_output_fields"]
    for s in report["swept_loci"]:
        for m in s["candidate_mechanisms"]:
            assert m.get("severity") is None, "FP-GUARD VIOLATION: severity emitted"
            assert m.get("concluded") is False, "FP-GUARD VIOLATION: concluded emitted"
            for f in forbidden:
                v = m.get(f)
                assert v in (None, False), f"FP-GUARD VIOLATION: forbidden field {f}={v}"
        assert s["status_label"] in cfg["status_labels"]


def _markdown(report: dict, cfg: dict, contest: str) -> str:
    rows = []
    for s in report["swept_loci"][:cfg["caps"]["max_high_priority_md"]]:
        tmpls = ",".join(t.split("_")[0] for t in s["applied_shape_templates"])
        rows.append(f"| {s['p260_rank']} | {s['contract']}.{s['function']} | {tmpls} | "
                    f"{';'.join(s['inclusion_reasons'])} | {len(s['candidate_mechanisms'])} | {s['status_label']} |")
    return (f"# P262 recall-first sweep — {contest} (ADVISORY ONLY; no severity/conclusions)\n\n"
            f"swept_loci={len(report['swept_loci'])} · total_mechs_to_ranking={report['total_mechs_to_ranking']} "
            f"· truncated={report['truncated']}\n\n"
            "| p260_rank | locus | templates | inclusion | #mechs | status |\n|---|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n\nEvery row is RECALL_CANDIDATE_ONLY → NEEDS_RANKING/COMPLETION/REFUTATION before any finding.\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--accounting", required=True)
    ap.add_argument("--state-transition", required=True)
    ap.add_argument("--base-candidates")
    ap.add_argument("--prioritizer")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cfg = _load(CFG_PATH)
    p260_cfg = _load(lsp.CONFIG_PATH)
    if not cfg or not p260_cfg:
        raise SystemExit("[recall_first_shape_sweep] missing config")
    manifest, acct, st = _load(args.manifest), _load(args.accounting), _load(args.state_transition)
    base = _load(args.base_candidates) if args.base_candidates else None
    prior = None
    if args.prioritizer:
        pj = _load(args.prioritizer)
        prior = pj.get("prioritized_loci") if isinstance(pj, dict) else None

    res = sweep(manifest, acct, st, base, p260_cfg, cfg, prior)
    report = {
        "module": "recall_first_shape_sweep",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(args.manifest),
        "is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": [],
        "emits_findings": False, "concludes_vulnerability": False,
        "output_type": "recall_candidates_advisory",
        "policy": "shape-discovery-before-narrow-selection; advisory; promotion-gated",
        "caps": cfg["caps"],
        **res,
    }
    _assert_no_conclusions(report, cfg)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    if args.md:
        Path(args.md).write_text(_markdown(report, cfg, Path(args.manifest).stem))
    if not args.quiet:
        print(f"[recall_first_shape_sweep] ADVISORY/research-only · swept {len(report['swept_loci'])} loci · "
              f"{report['total_mechs_to_ranking']} mechs→ranking · truncated={report['truncated']} · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
