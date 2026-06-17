#!/usr/bin/env python3
"""advisory_lens_attribution.py — MEASUREMENT-ONLY: close the calibration loop on the advisory lenses.

The advisory-escalation gate flags/routes manifest items per lens, but nothing tracked whether a lens hit
ever became a FINDING — so lens value stayed unmeasured (review J5: "prove value or shelve"). This joins each
lens hit (output/advisory_escalation_gate.json) to the eventual findings (merged_findings.json + the ONE
canonical candidate record) and reports, per lens: how many hits became findings and, of those, how many
reached each canonical state (ready / poc_required / human_pending / rejected / duplicate).

Hard rule — this is pure attribution: it NEVER routes, gates, sets severity, or mutates a disposition. It only
READS and writes output/advisory_lens_attribution.json. `--rollup` aggregates every
audits/*/output/advisory_lens_attribution.json into a cross-audit per-lens table
(evals/advisory_lens_value.{json,md}) — the artifact a future review reads to decide keep-vs-shelve.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_context as ac  # noqa: E402
import candidate_records as cr  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Every per-lens escalation list the gate emits, plus the advisory-only promoted hits.
_ESCALATION_KEYS = (
    "escalations", "abi_getter_mismatch_escalations", "arithmetic_conservation_escalations",
    "connector_position_accounting_escalations", "liquidation_health_accounting_escalations",
)


def _load_json(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _lens_hits(report: dict) -> list[dict]:
    """Flatten every lens hit to {lens, manifest_id, file, function} regardless of which list it came from."""
    hits: list[dict] = []
    for key in _ESCALATION_KEYS:
        for e in report.get(key, []) or []:
            hits.append({"lens": e.get("lens"), "manifest_id": e.get("manifest_id"),
                         "file": e.get("file"), "function": e.get("name"),
                         "routed": e.get("routed_to") == "needs_deep_pass"})
    for h in report.get("promoted_advisory_lens_hits", []) or []:
        hits.append({"lens": h.get("lens"), "manifest_id": h.get("manifest_id"),
                     "file": h.get("file"), "function": h.get("name"), "routed": False})
    return [h for h in hits if h.get("lens")]


def _finding_matchers(merged: dict, records: dict[str, dict]):
    """Return (by_manifest, by_loc) maps from a manifest_id / (file,function) to a finding's id+state."""
    findings = merged.get("findings", []) if isinstance(merged, dict) else (merged or [])
    by_manifest: dict[str, dict] = {}
    by_loc: dict[tuple, dict] = {}
    for f in findings:
        fid = f.get("id")
        if not fid:
            continue
        state = (records.get(fid) or {}).get("state")  # None when the canonical record hasn't been built
        info = {"finding_id": fid, "state": state}
        for mref in f.get("manifest_refs", []) or []:
            by_manifest.setdefault(mref, info)
        loc = f.get("location") or {}
        if loc.get("file") and loc.get("function"):
            by_loc.setdefault((loc["file"], loc["function"]), info)
    return by_manifest, by_loc


def _match(hit: dict, by_manifest: dict, by_loc: dict) -> dict | None:
    if hit.get("manifest_id") and hit["manifest_id"] in by_manifest:
        return by_manifest[hit["manifest_id"]]
    key = (hit.get("file"), hit.get("function"))
    if key[0] and key[1] and key in by_loc:
        return by_loc[key]
    return None


def attribute(audit_root: Path | None = None) -> dict:
    adir = audit_root or ac.get_audit_root()
    out_dir = adir / "output"
    report = _load_json(out_dir / "advisory_escalation_gate.json", {})
    merged = _load_json(out_dir / "merged_findings.json", {})
    records = cr.load_records(out_dir)

    by_manifest, by_loc = _finding_matchers(merged, records)
    hits = _lens_hits(report)

    per_lens: dict[str, dict] = defaultdict(
        lambda: {"hits": 0, "routed_to_deep_pass": 0, "became_finding": 0,
                 "by_state": defaultdict(int), "finding_ids": [], "distinct_items": set()})
    for h in hits:
        L = per_lens[h["lens"]]
        L["hits"] += 1
        if h.get("routed"):
            L["routed_to_deep_pass"] += 1
        L["distinct_items"].add(h.get("manifest_id") or (h.get("file"), h.get("function")))
        m = _match(h, by_manifest, by_loc)
        if m:
            L["became_finding"] += 1
            L["by_state"][m["state"] or "unknown"] += 1
            if m["finding_id"] not in L["finding_ids"]:
                L["finding_ids"].append(m["finding_id"])

    lenses = {}
    for lens, L in sorted(per_lens.items()):
        lenses[lens] = {"hits": L["hits"], "distinct_items": len(L["distinct_items"]),
                        "routed_to_deep_pass": L["routed_to_deep_pass"],
                        "became_finding": L["became_finding"], "by_state": dict(L["by_state"]),
                        "became_ready": L["by_state"].get("ready", 0),
                        "finding_ids": L["finding_ids"]}

    doc = {
        "schema": "advisory_lens_attribution/v1",
        "audit_id": ac.get_active_audit().get("audit_id") if audit_root is None else adir.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "MEASUREMENT-ONLY. Joins advisory-lens hits to findings + canonical state. Never routes/gates.",
        "total_hits": len(hits), "lenses": lenses,
    }
    (out_dir / "advisory_lens_attribution.json").write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def rollup() -> dict:
    """Aggregate every audit's attribution file into a cross-audit per-lens value table."""
    agg: dict[str, dict] = defaultdict(
        lambda: {"hits": 0, "became_finding": 0, "became_ready": 0, "audits_fired": 0,
                 "by_state": defaultdict(int), "finding_ids": []})
    audits_dir = ROOT / "audits"
    n_audits = 0
    for p in sorted(audits_dir.glob("*/output/advisory_lens_attribution.json")):
        doc = _load_json(p, {})
        if not doc.get("lenses"):
            continue
        n_audits += 1
        aid = doc.get("audit_id", p.parent.parent.name)
        for lens, L in doc["lenses"].items():
            A = agg[lens]
            A["hits"] += L.get("hits", 0)
            A["became_finding"] += L.get("became_finding", 0)
            A["became_ready"] += L.get("became_ready", 0)
            if L.get("hits"):
                A["audits_fired"] += 1
            for s, n in (L.get("by_state") or {}).items():
                A["by_state"][s] += n
            for fid in L.get("finding_ids", []):
                A["finding_ids"].append(f"{aid}:{fid}")

    table = {lens: {**{k: v for k, v in A.items() if k != "by_state"},
                    "by_state": dict(A["by_state"])} for lens, A in sorted(agg.items())}
    doc = {"schema": "advisory_lens_value/v1", "generated_at": datetime.now(timezone.utc).isoformat(),
           "audits_with_attribution": n_audits, "lenses": table,
           "note": "Cross-audit advisory-lens value. became_finding/became_ready==0 across many audits = a "
                   "shelve candidate (review J5). MEASUREMENT-ONLY; shelving is a separate human decision."}
    (ROOT / "evals").mkdir(exist_ok=True)
    (ROOT / "evals" / "advisory_lens_value.json").write_text(json.dumps(doc, indent=2) + "\n")

    lines = ["# Advisory-lens value (cross-audit, measurement-only)", "",
             f"_generated {doc['generated_at']} · {n_audits} audit(s) with attribution_", "",
             "became_finding / became_ready == 0 across many audits = shelve candidate (J5). "
             "Provenance (earned-from-eval) is tracked separately; this measures LIVE effect.", "",
             "| lens | audits_fired | hits | became_finding | became_ready |",
             "|---|---|---|---|---|"]
    for lens, A in table.items():
        lines.append(f"| {lens} | {A['audits_fired']} | {A['hits']} | {A['became_finding']} | {A['became_ready']} |")
    (ROOT / "evals" / "advisory_lens_value.md").write_text("\n".join(lines) + "\n")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollup", action="store_true", help="aggregate all audits into evals/advisory_lens_value.*")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.rollup:
        d = rollup()
        if not args.quiet:
            print(f"[advisory_lens_attribution] rollup over {d['audits_with_attribution']} audit(s) "
                  f"-> evals/advisory_lens_value.md ({len(d['lenses'])} lenses)")
        return 0
    d = attribute()
    if not args.quiet:
        fired = {k: v for k, v in d["lenses"].items() if v["hits"]}
        print(f"[advisory_lens_attribution] {d['total_hits']} hit(s) across {len(fired)} lens(es) "
              f"-> output/advisory_lens_attribution.json")
        for lens, L in fired.items():
            print(f"   {lens}: hits={L['hits']} became_finding={L['became_finding']} "
                  f"ready={L['became_ready']} states={L['by_state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
