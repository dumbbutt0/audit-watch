#!/usr/bin/env python3
"""confirm_write.py — deterministic writer for the credit-free /confirm skill.

Reads the /confirm skill's decisions (output/confirm/_decisions.json) and writes output/findings_confirmed.json
in the SAME schema multi_pass_confirm.py produces, so the rest of the pipeline + build_candidate_records.py read
one artifact regardless of whether confirmation ran via API or the in-session skill.

Decision record (one per finding) expected from the skill:
  {"id": "H-1", "passes_run": 3, "passes_yes": 2, "human_review_reason": "..."}
Score = passes_yes / passes_run; human_review_required = score < threshold (from config).
Validates against the staged bundles (passes_run must match passes_required); refuses to invent confirmations for
findings that were not staged.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _threshold() -> float:
    try:
        pol = json.loads((ROOT / "config" / "agent_policy.json").read_text())
        return float((pol.get("multi_pass") or {}).get("confirmation_threshold", 0.6))
    except Exception:
        return 0.6


def main() -> int:
    ap = argparse.ArgumentParser(description="Write findings_confirmed.json from /confirm skill decisions")
    ap.add_argument("--decisions")
    args = ap.parse_args()

    dec_path = Path(args.decisions) if args.decisions else audit_path("output", "confirm", "_decisions.json")
    if not dec_path.exists():
        print(f"[confirm_write] no decisions at {dec_path}. Run confirm_prepare.py → /confirm skill → this.",
              file=sys.stderr)
        return 1
    decisions = json.loads(dec_path.read_text())
    if isinstance(decisions, dict):
        decisions = decisions.get("decisions", decisions.get("findings", []))

    idx_path = audit_path("output", "confirm", "_bundles", "index.json")
    staged = {r["finding_id"]: r for r in json.loads(idx_path.read_text())} if idx_path.exists() else {}
    threshold = _threshold()

    out_findings, errors = [], []
    for d in decisions:
        fid = d.get("id") or d.get("finding_id")
        if not fid:
            errors.append("decision missing id")
            continue
        if staged and fid not in staged:
            errors.append(f"{fid}: not a staged High/Critical finding — refusing to confirm")
            continue
        run = int(d.get("passes_run", 0))
        yes = int(d.get("passes_yes", 0))
        if run <= 0 or yes < 0 or yes > run:
            errors.append(f"{fid}: invalid passes_run/passes_yes ({yes}/{run})")
            continue
        if staged and staged[fid].get("passes_required") and run != staged[fid]["passes_required"]:
            errors.append(f"{fid}: passes_run {run} != required {staged[fid]['passes_required']}")
            continue
        score = round(yes / run, 3)
        out_findings.append({
            "id": fid, "confirmation_passes": run, "confirmation_yes": yes,
            "confirmation_score": score,
            "human_review_required": score < threshold,
            "human_review_reason": d.get("human_review_reason", "" if score >= threshold
                                          else "AI inconsistent across passes — verify the path manually"),
        })

    if errors:
        for e in errors:
            print(f"[confirm_write] REJECTED: {e}", file=sys.stderr)
        if not out_findings:
            return 2

    out = {"agent": "multi_pass_confirm", "source": "confirm_skill",
           "generated_at": datetime.now(timezone.utc).isoformat(), "threshold": threshold,
           "findings": out_findings}
    (audit_path("output") / "findings_confirmed.json").write_text(json.dumps(out, indent=2))
    conf = sum(1 for f in out_findings if not f["human_review_required"])
    print(f"[confirm_write] wrote {len(out_findings)} confirmation(s) → output/findings_confirmed.json "
          f"({conf} confirmed, {len(out_findings)-conf} human-review)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
