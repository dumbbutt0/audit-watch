#!/usr/bin/env python3
"""calibration_worklist.py — turn the calibration gap into an actionable human worklist (READ-ONLY).

The Self-Calibration Principle says a system that can't measure its own FP/recall can't be tuned. Today
`compute_metrics.py` reports FP/recall as "unmeasured (no ground truth)" because no REAL-WORLD finding has a
recorded outcome yet. AI must NOT fabricate outcomes — ground truth is human-only. So the most this tool can
honestly do is make closing the loop a fill-in-the-verdict task: it enumerates every real-world,
pipeline-ACCEPTED finding that has NO ground_truth entry, and emits a ready `record_outcome.py` command stub
per finding (finding_id + claimed_severity + current decision pre-filled; the human supplies outcome +
provenance). It writes documentation/metrics/outcome_worklist.{md,json}. It NEVER writes ground truth.

Usage:  python scripts/calibration_worklist.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compute_metrics as cm  # reuse the SAME real-world audit set + decision logic the metrics use
from audit_context import _AUDITS_DIR, _PROJECT_ROOT, load_jsonl


def _merged_index(root: Path) -> dict[str, dict]:
    p = root / "output" / "merged_findings.json"
    try:
        d = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return {f.get("id"): f for f in d.get("findings", []) if f.get("id")}


def _recorded_ids(root: Path) -> set[str]:
    gt = load_jsonl(root / "data" / "evaluation" / "ground_truth.jsonl")
    return {r.get("finding_id") for r in gt if r.get("finding_id")}


def pending() -> list[dict]:
    """Real-world pipeline-ACCEPTED findings with no recorded outcome. Pure read — writes nothing."""
    out: list[dict] = []
    for aid in cm._audit_ids():                      # real-world audits only (eval corpora excluded)
        root = _AUDITS_DIR / aid
        decisions = cm._pipeline_decision(root)
        recorded = _recorded_ids(root)
        merged = _merged_index(root)
        for fid, decision in sorted(decisions.items()):
            if decision != "accepted" or fid in recorded:
                continue
            f = merged.get(fid, {})
            sev = (f.get("severity") or "").lower()
            out.append({
                "audit_id": aid, "finding_id": fid,
                "title": f.get("title", ""), "claimed_severity": sev,
                "vuln_type": f.get("vuln_type", ""), "decision": decision,
                "source_file_hint": f"audits/{aid}/data/runtime_poc/results.jsonl",
            })
    return out


def pending_count() -> int:
    """Write-free count for the session-start status hook."""
    return len(pending())


def build() -> dict:
    pending_list = pending()

    by_audit: dict[str, int] = {}
    for p in pending_list:
        by_audit[p["audit_id"]] = by_audit.get(p["audit_id"], 0) + 1

    doc = {
        "schema": "outcome_worklist/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Pipeline-ACCEPTED real-world findings with NO recorded outcome. Recording any of them moves "
                "FP/recall off 'unmeasured'. Human-only: AI must NOT fill the verdict. READ-ONLY artifact.",
        "pending_total": len(pending_list), "by_audit": by_audit, "pending": pending_list,
    }

    out_dir = _PROJECT_ROOT / "documentation" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "outcome_worklist.json").write_text(json.dumps(doc, indent=2) + "\n")

    lines = ["# Calibration outcome worklist (human-only)", "",
             f"_generated {doc['generated_at']} · {len(pending_list)} accepted finding(s) awaiting an outcome_", "",
             "Recording any of these moves FP/recall off **unmeasured**. AI must not fill the verdict — you "
             "supply `--outcome`, `--severity`, and provenance (`--evidence-class/--source-file/--evidence`). "
             "A record without provenance is routed to `needs_human_review.jsonl`, never ground truth.", ""]
    if not pending_list:
        lines += ["_No accepted real-world findings are awaiting an outcome._", ""]
    for aid, n in sorted(by_audit.items()):
        lines += [f"## {aid} — {n} pending", ""]
        for p in [x for x in pending_list if x["audit_id"] == aid]:
            lines += [f"- **{p['finding_id']}** ({p['claimed_severity'] or '?'}) — {p['title'] or '(no title)'}",
                      "  ```bash",
                      f"  python scripts/audit_manager.py switch {aid}",
                      f"  python scripts/record_outcome.py --finding-id {p['finding_id']} \\",
                      f"      --outcome <accepted|invalid|duplicate|downgraded|paid> \\",
                      f"      --severity <critical|high|medium|low|invalid> "
                      + (f"--claimed-severity {p['claimed_severity']} \\" if p['claimed_severity'] else "\\"),
                      f"      --evidence-class <fork_confirmed|report_response|...> \\",
                      f"      --source-file {p['source_file_hint']} \\",
                      f"      --evidence \"<one-line evidence>\"",
                      "  ```"]
        lines += [""]
    (out_dir / "outcome_worklist.md").write_text("\n".join(lines) + "\n")
    return doc


def main() -> int:
    d = build()
    print(f"[calibration_worklist] {d['pending_total']} accepted finding(s) awaiting an outcome "
          f"across {len(d['by_audit'])} real-world audit(s) -> documentation/metrics/outcome_worklist.md")
    for aid, n in sorted(d["by_audit"].items()):
        print(f"   {aid}: {n}")
    if d["pending_total"]:
        print("   Record any via scripts/record_outcome.py (human-only) to move FP/recall off 'unmeasured'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
