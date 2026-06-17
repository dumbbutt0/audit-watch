#!/usr/bin/env python3
"""
checkpoint_liveness_audit.py — recall lens for checkpoint/queue/returndata LIVENESS: recipient can block a
checkpoint/batch (external call in a batch loop), unbounded returndata gas bomb, compaction loop that skips
pending entries, floodable confirmation state. NOT a gate; never mutates dispositions; never finding-mints.
Two-signal, FP-tight. Recovers Recall H-07/H-09 (and flags M-04 flooding). Writes
output/checkpoint_liveness_audit.{json,md}.

Usage: python scripts/checkpoint_liveness_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import checkpoint_liveness_taxonomy as cl  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
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
        raise SystemExit(f"[checkpoint_liveness_audit] no manifest items at {man_path}")
    tax = cl.load_taxonomy()
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
        cls = cl.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                          it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("liveness_sensitive"):
            continue
        high = cl.is_high_risk(cls, tax)
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": cls["category"], "high_risk": high,
            "severity_ceiling_hint": cls["severity_ceiling_hint"],
            "signals": {k: cls[k] for k in ("in_context", "has_loop", "has_external_call",
                                            "has_returndata_load", "is_compaction", "has_append", "has_bound")},
            "coverage": _cov(it["id"]),
        })

    high_risk = [x for x in detected if x["high_risk"]]
    high_risk_ids = sorted({x["manifest_id"] for x in high_risk})
    by_cat = Counter(x["category"] for x in detected)
    packets = [{"packet_id": f"CKL-{x['contract']}-{x['name']}", "label": "checkpoint_liveness",
                "suggested_specialist": "liveness_review", "manifest_id": x["manifest_id"], "category": x["category"],
                "review_prompt": (f"{x['contract']}.{x['name']} is a {x['category']} candidate: confirm one "
                                  f"malicious item/recipient cannot block the batch/checkpoint/queue, returndata "
                                  f"is size-bounded, and compaction iterates exactly the live entries.")}
               for x in high_risk if x["coverage"] != "covered_by_finding"]

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "checkpoint_liveness", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "source_snippets": use_source, "total_sensitive": len(detected), "by_category": dict(by_cat.most_common()),
        "high_risk_count": len(high_risk), "high_risk_manifest_ids": high_risk_ids,
        "recommended_review_packets": packets, "detected": detected,
    }
    out = audit_path("output") / "checkpoint_liveness_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Checkpoint / queue / returndata liveness audit\n",
          f"_Generated {ts} · manifest `{man_path}` · NOT a gate · high-risk → needs_deep_pass_\n",
          f"**{len(detected)}** liveness-sensitive · **{len(high_risk)}** high-risk\n",
          "## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## High-risk\n", "| contract.name | category | coverage |", "|---|---|---|"]
    for x in high_risk:
        md.append(f"| {x['contract']}.{x['name']} | {x['category']} | {x['coverage']} |")
    (audit_path("output") / "checkpoint_liveness_audit.md").write_text("\n".join(md) + "\n")

    print(f"[ok] checkpoint_liveness_audit → {out}")
    print(f"     sensitive {len(detected)} · high-risk {len(high_risk)} · by_category {dict(by_cat.most_common())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
