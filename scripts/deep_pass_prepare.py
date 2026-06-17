#!/usr/bin/env python3
"""
deep_pass_prepare.py — Build per-candidate value-provenance bundles for the /deep-pass skill
(deterministic, no LLM, RESEARCH-ONLY).

Phase-14 / Experiment E1. Mirrors coverage_sweep_prepare.py: a deterministic prepare half that
assembles self-contained bundles the in-session /deep-pass skill reasons over; the skill emits
decisions and deep_pass_write.py --eval validates + finalizes them. Nothing here routes or gates.

Candidate set (the surface the deep-pass reasons over) = in-scope function/initializer manifest items
that are EITHER routed by a research detector (value_flow_parity / sibling / cross_contract / registry)
at any confidence, OR high-attack-surface (score >= --min-score), OR value-tagged with score >=
--tag-min-score. This is the "verify-and-extend the lens output" surface; the rule is fixed and
non-answer-key (record it in the firewall attestation before scoring the holdout).

Ablation ladder (set the bundle's `rung` + KB inclusion):
    (no flag)        rung c2  — full bundle WITH kb_precedents (reasoning + KB)
    --no-kb          rung c1  — bundle WITHOUT kb_precedents   (reasoning, no KB)
    --package-only   rung c0  — packaging control; no kb, index instructs NO reasoning (mechanical)

Each bundle embeds the candidate function body + up to --max-callees callee bodies (reuse
_function_body) so the skill reasons from the bundle text, not by re-reading files.

Usage:
    python scripts/deep_pass_prepare.py [--manifest <path>] [--min-score 4] [--tag-min-score 2]
        [--max-items 0] [--max-callees 2] [--no-kb | --package-only] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
from sibling_function_parity_audit import _function_body  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

DETECTOR_FILES = [
    "value_flow_parity_audit.json",
    "sibling_function_parity_audit.json",
    "cross_contract_sibling_parity_audit.json",
    "registry_position_lifecycle_audit.json",
]
VALUE_TAGS = {"accounting", "token", "reward", "collateral", "debt", "balance", "oracle", "fee"}
_CALL_RE = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*\(")
_KB_KEYWORDS = ("value", "amount", "owner", "index", "key", "mapping", "accounting", "balance",
                "checkpoint", "share", "reward", "rounding", "operand")


def _load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _routed_by(out_dir: Path) -> dict[str, list[str]]:
    """manifest_id -> ['<detector_lens>:<shape>:<confidence>', ...] across research detectors."""
    routed: dict[str, list[str]] = {}
    for fn in DETECTOR_FILES:
        d = _load_json(out_dir / fn)
        lens = d.get("lens", fn.replace("_audit.json", ""))
        for c in d.get("candidates", []):
            mid = c.get("manifest_id")
            if not mid:
                continue
            tag = f"{lens}:{c.get('shape', '?')}:{c.get('confidence', '?')}"
            routed.setdefault(mid, []).append(tag)
    return routed


def _load_surface_cats() -> dict:
    """Phase-14b semantic surface taxonomy (config/semantic_surface_patterns.json)."""
    cfg = _load_json(ROOT / "config" / "semantic_surface_patterns.json")
    cats = {}
    for name, c in cfg.get("categories", {}).items():
        cats[name] = {"re": re.compile(c.get("name_regex", "$^"), re.I),
                      "tags": set(c.get("tag_hints", [])),
                      "min_score": c.get("min_score", cfg.get("default_min_score", 2)),
                      "cap": c.get("cap", 10)}
    return cats


def _categorize(name: str, tags: set[str], score: int, cats: dict) -> list[str]:
    """Which high-risk semantic surfaces this in-scope function belongs to (name-regex OR tag-hint,
    gated by the category's min_score). Generic / NOT answer-key-derived."""
    n = (name or "").lower()
    out = []
    for cat, c in cats.items():
        if score < c["min_score"]:
            continue
        if c["re"].search(n) or (tags & c["tags"]):
            out.append(cat)
    return out


def _kb_precedents(tags: set[str], routed_shapes: str) -> list[dict]:
    prims = _load_json(ROOT / "kb" / "attack_primitives.json").get("primitives", [])
    hay_tags = " ".join(tags).lower()
    hits = []
    for p in prims:
        blob = " ".join(str(p.get(k, "")) for k in
                        ("name", "category", "trigger", "canonical_location_pattern")).lower()
        if any(kw in blob for kw in _KB_KEYWORDS) or any(t and t in blob for t in tags):
            hits.append({"id": p.get("id"), "name": p.get("name"), "category": p.get("category"),
                         "trigger": p.get("trigger"),
                         "canonical_location_pattern": p.get("canonical_location_pattern")})
    # bias: keep the value/identity/index/mapping precedents most relevant to wrong-value reasoning
    return hits[:4]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="coverage_manifest.json (default: active audit output)")
    ap.add_argument("--min-score", type=int, default=4, help="include in-scope fns with score >= N")
    ap.add_argument("--tag-min-score", type=int, default=2,
                    help="include value-tagged in-scope fns with score >= N")
    ap.add_argument("--routed-only", action="store_true",
                    help="restrict to detector-routed candidates only (architecture strategy A; the "
                         "firewall-clean, high-fidelity E1 surface — no high-surface/value-tag inclusion)")
    ap.add_argument("--surface-sample", action="store_true",
                    help="E1b: queue = detector_routed UNION semantic-surface-sampled "
                         "(config/semantic_surface_patterns.json); per-category caps bound the reasoning set")
    ap.add_argument("--coverage-queue", action="store_true",
                    help="E1b: emit the FULL union queue (no per-category caps; no bundle bodies) — for the "
                         "mechanical Candidate Coverage Recall / Precision metrics only")
    ap.add_argument("--max-items", type=int, default=0, help="0 = all selected candidates")
    ap.add_argument("--max-callees", type=int, default=2)
    ap.add_argument("--no-kb", action="store_true", help="rung c1: omit kb_precedents (reasoning, no KB)")
    ap.add_argument("--package-only", action="store_true",
                    help="rung c0: packaging control; no kb, index instructs NO reasoning")
    ap.add_argument("--no-source", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out_dir = audit_path("output")
    man_path = Path(args.manifest) if args.manifest else out_dir / "coverage_manifest.json"
    items = _load_json(man_path).get("items", [])
    if not items:
        raise SystemExit(f"[deep_pass_prepare] no manifest items at {man_path}")
    use_source = not args.no_source
    rung = "c0" if args.package_only else ("c1" if args.no_kb else "c2")
    include_kb = rung == "c2"

    routed = _routed_by(out_dir)
    surface_cats = _load_surface_cats() if (args.surface_sample or args.coverage_queue) else {}
    fn_items = [it for it in items if it.get("kind") in ("function", "initializer")]
    # name -> item (for callee resolution; last write wins is fine for our purpose)
    by_name = {it.get("name"): it for it in fn_items if it.get("name")}

    # selected: list of (item, reasons[legacy], selected_by[provenance], categories)
    selected = []
    for it in fn_items:
        if not it.get("in_scope", True):
            continue
        mid = it.get("id")
        score = it.get("attack_surface_score", 0)
        tags = set(it.get("tags", []))
        reasons, selected_by, cats = [], [], []
        det_lenses = sorted({t.split(":", 1)[0] for t in routed.get(mid, [])})
        if mid in routed:
            reasons.append("detector_routed")
            selected_by += [f"detector:{l}" for l in det_lenses]
        if args.surface_sample or args.coverage_queue:
            cats = _categorize(it.get("name", ""), tags, score, surface_cats)
            selected_by += [f"semantic_surface:{c}" for c in cats]
        if not (args.routed_only or args.surface_sample or args.coverage_queue):
            # legacy E1 default mode (preserved for back-compat + tests)
            if score >= args.min_score:
                reasons.append("high_surface"); selected_by.append("high_surface")
            if score >= args.tag_min_score and (tags & VALUE_TAGS):
                reasons.append("value_tag"); selected_by.append("value_tag")

        if args.routed_only:
            include = mid in routed
        elif args.surface_sample or args.coverage_queue:
            include = (mid in routed) or bool(cats)
        else:
            include = bool(reasons)
        if include:
            selected.append((it, reasons, selected_by, cats))

    # per-category cap (bounded reasoning queue) — surface_sample only, NOT coverage_queue.
    # detector-routed items are always kept; surface items kept if within top-cap of ANY of their categories.
    if args.surface_sample and not args.coverage_queue:
        keep = set(id(t[0]) for t in selected if t[0].get("id") in routed)
        for cat, c in surface_cats.items():
            in_cat = [t for t in selected if cat in t[3]]
            in_cat.sort(key=lambda t: -t[0].get("attack_surface_score", 0))
            for t in in_cat[:c["cap"]]:
                keep.add(id(t[0]))
        selected = [t for t in selected if id(t[0]) in keep]

    # detector-routed first, then by score desc, then file for stability
    selected.sort(key=lambda t: (0 if "detector_routed" in t[1] else 1,
                                 -t[0].get("attack_surface_score", 0), t[0].get("file", "")))
    if args.max_items:
        selected = selected[:args.max_items]

    # candidate_queue.json — the deterministic queue (with provenance) the coverage/precision metrics read.
    queue = [{"manifest_id": it.get("id"), "contract": it.get("contract"), "function": it.get("name"),
              "score": it.get("attack_surface_score", 0), "categories": cats,
              "selected_by": sel_by} for (it, _r, sel_by, cats) in selected]
    queue_path = out_dir / "deep_pass" / "candidate_queue.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(json.dumps({
        "mode": ("coverage_queue" if args.coverage_queue else
                 "surface_sample" if args.surface_sample else
                 "routed_only" if args.routed_only else "legacy"),
        "queue_size": len(queue), "queue": queue}, indent=2))

    # coverage_queue mode: queue only, no bundle bodies (fast; metric needs set membership, not source).
    if args.coverage_queue:
        if not args.quiet:
            print(f"[ok] coverage queue → {queue_path}  ({len(queue)} items, no bundles)")
        return 0

    bundle_dir = out_dir / "deep_pass" / "_bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    # clear stale bundles so a rung run is self-contained
    for old in bundle_dir.glob("dp_*.json"):
        old.unlink()

    index = []
    for i, (it, reasons, sel_by, cats) in enumerate(selected):
        sp = it.get("source_span", {})
        body = _function_body(it.get("file", ""), sp.get("start_line"), use_source)
        # callee bodies: identifiers called in the body that resolve to other manifest functions
        callees = []
        seen_cal = set()
        for m in _CALL_RE.finditer(body or ""):
            nm = m.group(1)
            if nm in (it.get("name"), "require", "assert", "emit", "if", "for", "while", "return"):
                continue
            tgt = by_name.get(nm)
            if tgt and nm not in seen_cal and tgt.get("id") != it.get("id"):
                seen_cal.add(nm)
                csp = tgt.get("source_span", {})
                cbody = _function_body(tgt.get("file", ""), csp.get("start_line"), use_source)
                if cbody:
                    callees.append({"name": nm, "contract": tgt.get("contract"),
                                    "file_line": f"{tgt.get('file','')}:{csp.get('start_line','')}",
                                    "body": cbody})
            if len(callees) >= args.max_callees:
                break
        tags = set(it.get("tags", []))
        bid = f"dp_{i:04d}"
        bundle = {
            "bundle_id": bid, "rung": rung, "manifest_id": it.get("id"),
            "contract": it.get("contract"), "function": it.get("name"), "file": it.get("file"),
            "file_line_refs": f"{it.get('file','')}:{sp.get('start_line','')}",
            "signature": it.get("signature", ""), "visibility": it.get("visibility", ""),
            "tags": sorted(tags), "attack_surface_score": it.get("attack_surface_score", 0),
            "source_span": sp, "selected_because": reasons,
            "selected_by": sel_by, "categories": cats,
            "routed_by": routed.get(it.get("id"), []),
            "function_body": body, "callees": callees,
        }
        if include_kb:
            bundle["kb_precedents"] = _kb_precedents(tags, " ".join(routed.get(it.get("id"), [])))
        (bundle_dir / f"{bid}.json").write_text(json.dumps(bundle, indent=2))
        index.append({"bundle_id": bid, "manifest_id": it.get("id"),
                      "contract": it.get("contract"), "function": it.get("name"),
                      "score": it.get("attack_surface_score", 0), "selected_because": reasons,
                      "selected_by": sel_by, "categories": cats,
                      "routed_by": routed.get(it.get("id"), [])})

    if rung == "c0":
        instr = ("RUNG c0 (PACKAGING CONTROL — NO REASONING). Do NOT run the /deep-pass skill. This rung "
                 "exists only to hash the packaged surface; its recall equals the detector baseline (c-1) "
                 "by construction. No deep_pass_audit.json is produced by reasoning for c0.")
    else:
        kb_note = "WITHOUT kb_precedents (rung c1)" if rung == "c1" else "WITH kb_precedents (rung c2)"
        instr = (f"RUNG {rung}: reason over each bundle {kb_note} using prompts/deep_pass_value_provenance.md "
                 "(ROUTE→PLAN→TRACE value provenance→CRITIC→DECIDE→REPRO_HINT). Emit one decision per bundle "
                 "to output/deep_pass/_decisions.json {\"packet_id\":\"deep_pass_<rung>\",\"decisions\":[...]}, "
                 "then run: python scripts/deep_pass_write.py --eval --decisions "
                 "output/deep_pass/_decisions.json --out output/deep_pass_audit.json. RESEARCH-ONLY: this does "
                 "NOT mutate coverage_dispositions.json.")
    (bundle_dir / "index.json").write_text(json.dumps({
        "rung": rung, "total_candidates": len(selected),
        "selection_rule": {"routed_only": args.routed_only, "surface_sample": args.surface_sample,
                           "min_score": args.min_score, "tag_min_score": args.tag_min_score,
                           "value_tags": sorted(VALUE_TAGS), "max_items": args.max_items},
        "bundles": index, "instructions": instr,
    }, indent=2))

    if not args.quiet:
        print(f"[ok] deep-pass bundles (rung {rung}) → {bundle_dir}")
        print(f"     {len(selected)} candidates "
              f"(detector_routed={sum(1 for t in selected if 'detector_routed' in t[1])}, "
              f"surface={sum(1 for t in selected if t[3])})")
        if rung == "c0":
            print("     c0 packaging control — do NOT run the skill; recall == c-1 baseline.")
        else:
            print("     Next: run the /deep-pass skill, then deep_pass_write.py --eval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
