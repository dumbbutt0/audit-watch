#!/usr/bin/env python3
"""
build_final_scoring_set.py — Union merged findings + new EVAL candidates into the frozen scoring set.

Deterministic, read-only on its inputs. Produces the single finding set scored against the 81-finding
answer key: the 48 merged findings (IDs preserved) ∪ the 13 root-cause-deduped EVAL findings (EVAL-*
IDs preserved). No root-cause is duplicated (the eval layer is already deduped and links to merged IDs
via duplicate_of); eval_exclusions are NOT included. real_world_poc_later entries ARE included (they are
intentionally in eval_findings.json) but tagged so the scorer treats them conservatively in FP accounting.

Usage: python scripts/build_final_scoring_set.py
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402


def main() -> int:
    out = audit_path("output") / "eval_ready"
    merged = json.loads((audit_path("output") / "merged_findings.json").read_text())["findings"]
    evalf = json.loads((out / "eval_findings.json").read_text())["eval_findings"]

    rows = []
    for f in merged:
        rows.append({
            "id": f.get("id"), "layer": "merged", "title": f.get("title", ""),
            "severity": f.get("severity", ""), "contract": f.get("_contract", ""),
            "classification": "existing_merged_finding", "duplicate_of": None,
        })
    for e in evalf:
        rows.append({
            "id": e.get("eval_id"), "layer": "eval_candidate", "title": e.get("title", ""),
            "severity": e.get("severity_ceiling", ""),
            "contract": ", ".join(e.get("affected_contracts", []))[:80],
            "classification": e.get("classification"), "duplicate_of": e.get("duplicate_of"),
            "root_cause_id": e.get("root_cause_id"), "source_leads": e.get("source_leads", []),
            "confidence": e.get("confidence"),
        })

    ts = datetime.now(timezone.utc).isoformat()
    payload = {"generated_at": ts, "scope": "merged_48 ∪ eval_findings_13",
               "count": len(rows), "merged_count": len(merged), "eval_count": len(evalf),
               "findings": rows}
    (out / "final_scoring_set.json").write_text(json.dumps(payload, indent=2))

    from collections import Counter
    cls = Counter(r["classification"] for r in rows if r["layer"] == "eval_candidate")
    md = [f"# Final scoring set — {len(rows)} findings ({len(merged)} merged ∪ {len(evalf)} eval)\n",
          f"_Generated {ts}_\n", "## New eval-candidate layer\n", "| id | class | sev | dup_of | title |", "|---|---|---|---|---|"]
    for r in rows:
        if r["layer"] == "eval_candidate":
            md.append(f"| {r['id']} | {r['classification'].replace('_eval_finding','').replace('real_world_','rw_')} "
                      f"| {r['severity']} | {r['duplicate_of'] or ''} | {r['title'][:70]} |")
    md += ["\n## Merged layer (existing 48 — IDs preserved)\n", "| id | sev | title |", "|---|---|---|"]
    for r in rows:
        if r["layer"] == "merged":
            md.append(f"| {r['id']} | {r['severity']} | {r['title'][:70]} |")
    (out / "final_scoring_set.md").write_text("\n".join(md))

    print(f"[ok] final_scoring_set: {len(rows)} ({len(merged)} merged + {len(evalf)} eval)")
    print(f"     eval classes: {dict(cls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
