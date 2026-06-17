#!/usr/bin/env python3
"""
griefing_dos_audit.py — Field-DoS / griefing detector + creator->consumer state-growth-surface graph.

Per-item griefing tagger (read-time over the frozen manifest, snippet-aware) PLUS a light state-growth-
surface section that pairs CREATORS (functions that cheaply grow/fragment a per-account array) with CONSUMERS
(functions that loop over it on a required path) — the cost-asymmetry behind #379 (plot-spam transfer DoS),
#485 (plotIndexes duplication), #491 (transferDeposit amount==0 recipient DoS). NOT a gate; never mutates
eval3 artifacts. Writes output/griefing_dos_audit.{json,md}.

Usage: python scripts/griefing_dos_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import griefing_dos_taxonomy as grief  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATEGORY_TO_MISS = {
    "plot_spam": ["#379 attacker spams plots to victim causing transfer DoS"],
    "storage_growth": ["#379/#485 attacker-grown per-account array"],
    "array_bloat": ["#485 duplicate entries in plotIndexes via sow"],
    "pod_fragmentation": ["#485 plot/pod fragmentation"],
    "zero_amount_edge": ["#491 transferDeposit doesn't check amount==0 (recipient DoS)"],
    "deposit_fragmentation": ["#491 dust-deposit recipient list bloat"],
    "recipient_revert_dos": ["#491 recipient-controlled revert"],
    "transfer_blocking": ["#379 transfer path blocked by grown state"],
    "claim_path_dos": ["claim/harvest path DoS by grown state"],
    "lifecycle_lock": ["sunrise/settlement liveness DoS"],
}
_FILE_CACHE: dict[str, list[str]] = {}


def _snippet(file_rel, start, end, use_source):
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    return "\n".join(lines[max(0, (start or 1) - 1):min(len(lines), end or start or 1)])[:4000] if lines else ""


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[griefing_dos_audit] no manifest items at {man_path}")
    tax = grief.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    def _cov(mid):
        st = disp.get(mid, {}).get("status")
        return ("covered_by_finding" if st == "finding" else "examined_but_cleared" if st == "cleared"
                else "deferred" if st == "deferred_out_of_scope" else "uncovered")

    detected = []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = grief.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                            it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("griefing_sensitive"):
            continue
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": cls["category"], "risk_tags": cls["risk_tags"], "role": cls["role"],
            "state_growth_surface": cls["state_growth_surface"], "high_risk": grief.is_high_risk(cls, tax),
            "severity_ceiling_hint": cls.get("severity_ceiling_hint"), "matched_on": cls.get("matched_on"),
            "has_create": cls.get("_has_create"), "has_consume": cls.get("_has_consume"),
            "coverage": _cov(it["id"]), "disposition_status": disp.get(it["id"], {}).get("status"),
            "clear_reason": (disp.get(it["id"], {}).get("clear_reason") or "")[:160]
            if disp.get(it["id"], {}).get("status") == "cleared" else "",
        })

    # ── state-growth surfaces: pair creators <-> consumers per surface ──
    surfaces = defaultdict(lambda: {"creators": [], "consumers": []})
    for x in detected:
        s = x["state_growth_surface"] or "generic"
        entry = {"name": x["name"], "contract": x["contract"], "category": x["category"], "coverage": x["coverage"]}
        if x["role"] in ("creator", "both"):
            surfaces[s]["creators"].append(entry)
        if x["role"] in ("consumer", "both"):
            surfaces[s]["consumers"].append(entry)
    surface_report = []
    for s, v in sorted(surfaces.items(), key=lambda kv: -(len(kv[1]["creators"]) + len(kv[1]["consumers"]))):
        asymmetric = bool(v["creators"]) and bool(v["consumers"])  # both ends present => exploitable shape
        surface_report.append({"surface": s, "creators": v["creators"], "consumers": v["consumers"],
                               "asymmetric_pairing": asymmetric})

    by_cat = Counter(x["category"] for x in detected)
    by_surface = Counter(x["state_growth_surface"] for x in detected)
    high_risk = [x for x in detected if x["high_risk"]]
    cleared_high_risk = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    rereview = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    packets = []
    groups = defaultdict(list)
    for x in rereview:
        groups[(x["category"], x["contract"] or "?")].append(x)
    for (cat, contract), xs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({"packet_id": f"GRF-{cat}-{contract}", "label": "griefing_dos", "category": cat,
                        "contract": contract, "suggested_specialist": "dos",
                        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
                        "item_ids": sorted(x["manifest_id"] for x in xs), "files": sorted({x["file"] for x in xs}),
                        "review_prompt": (f"Re-review {len(xs)} {cat} item(s) in {contract} under the griefing/DoS "
                                          f"lens (prompts/griefing_dos_review.md). " + (meta.get("review_hint") or ""))})

    miss_classes = sorted({m for x in detected for m in CATEGORY_TO_MISS.get(x["category"], [])})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False, "source_snippets": use_source,
        "total_griefing_sensitive": len(detected), "by_category": dict(by_cat.most_common()),
        "by_state_growth_surface": dict(by_surface.most_common()), "high_risk_count": len(high_risk),
        "state_growth_surfaces": surface_report,
        "previously_cleared_high_risk": cleared_high_risk,
        "covered_by_finding": [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"],
        "examined_but_cleared": [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"],
        "uncovered": [x for x in detected if x["coverage"] == "uncovered"],
        "re_review_candidates": len(rereview), "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": miss_classes, "detected": detected,
    }
    out = audit_path("output") / "griefing_dos_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Field-DoS / griefing audit\n", f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"**{len(detected)}** griefing-sensitive · **{len(high_risk)}** high-risk · **{len(rereview)}** re-review\n",
          "## ⚖ State-growth surfaces (creator → consumer cost-asymmetry)",
          "_An exploitable shape needs BOTH a cheap creator and a later consumer that iterates the grown state._\n",
          "| surface | asymmetric? | creators | consumers |", "|---|---|---|---|"]
    for s in surface_report:
        cr = ", ".join(f"{c['name']}[{c['coverage'][:4]}]" for c in s["creators"][:5]) or "—"
        co = ", ".join(f"{c['name']}[{c['coverage'][:4]}]" for c in s["consumers"][:5]) or "—"
        md.append(f"| {s['surface']} | {'YES' if s['asymmetric_pairing'] else 'no'} | {cr} | {co} |")
    md += ["\n## ⚠ Previously cleared but high-risk griefing/DoS items\n",
           "| name | contract | category | role | clear_reason |", "|---|---|---|---|---|"]
    for x in cleared_high_risk:
        md.append(f"| {x['name']} | {x['contract']} | {x['category']} | {x['role']} | {x['clear_reason']} |")
    md += ["\n## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## By state-growth surface", "| surface | n |", "|---|---|"] + [f"| {s} | {n} |" for s, n in by_surface.most_common()]
    md += ["\n## Recommended review packets\n"] + [
        f"- **{p['packet_id']}** ({len(p['item_ids'])} items, sev≤{p['severity_ceiling_hint']}) → {p['suggested_specialist']}"
        for p in packets]
    md += ["\n## Likely eval miss classes this lens addresses\n"] + [f"- {m}" for m in miss_classes]
    (audit_path("output") / "griefing_dos_audit.md").write_text("\n".join(md))

    print(f"[ok] griefing_dos_audit → {out}")
    print(f"     detected {len(detected)} · high-risk {len(high_risk)} · re-review {len(rereview)}")
    print(f"     by_category {dict(by_cat.most_common())}")
    print(f"     by_surface {dict(by_surface.most_common())}")
    asy = [s["surface"] for s in surface_report if s["asymmetric_pairing"]]
    print(f"     asymmetric surfaces (creator+consumer): {asy}")
    print(f"     previously-cleared high-risk ({len(cleared_high_risk)}): {[(x['name'], x['category']) for x in cleared_high_risk][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
