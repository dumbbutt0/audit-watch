#!/usr/bin/env python3
"""
summarize_poc_results.py — Generate a contest-ready PoC evidence report.

Usage:
    python scripts/summarize_poc_results.py --out reports/poc_evidence.md
    python scripts/summarize_poc_results.py                              # stdout
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

POC_DIR    = audit_path("data/poc_queue")
TRIAGE_DIR = audit_path("data/triage")


# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_all_results() -> list[dict]:
    results = []
    seen = set()
    for result_file in sorted(POC_DIR.glob("*_result.json")):
        r = json.loads(result_file.read_text())
        fid = r.get("finding_id")
        if fid and fid not in seen:
            seen.add(fid)
            results.append(r)
    return results


def load_plan(finding_id: str) -> dict:
    path = POC_DIR / f"{finding_id}_plan.json"
    return json.loads(path.read_text()) if path.exists() else {}


def load_original(finding_id: str) -> dict:
    merged = audit_path("output") / "merged_findings.json"
    if merged.exists():
        for f in json.loads(merged.read_text()).get("findings", []):
            if f["id"] == finding_id:
                return f
    return {}


def load_triage(finding_id: str) -> dict:
    for bucket in ["poc_required", "submit", "downgraded"]:
        path = TRIAGE_DIR / f"{bucket}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            t = json.loads(line)
            if t.get("finding_id") == finding_id:
                return t
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Markdown rendering
# ─────────────────────────────────────────────────────────────────────────────

STATUS_ICON = {
    "proved":           "✅",
    "failed":           "❌",
    "inconclusive":     "⚠️",
    "compile_error":    "🔧",
    "needs_manual_work": "👷",
}


def render_proved_section(result: dict, plan: dict, original: dict, triage: dict) -> str:
    fid      = result["finding_id"]
    title    = original.get("title", result.get("finding_id", ""))
    sev      = triage.get("recommended_severity", original.get("severity", "?")).upper()
    test_file = result.get("test_file", "?")
    run_cmd   = result.get("run_command", "?")
    evidence  = result.get("evidence_summary", "")
    stdout    = result.get("stdout_excerpt", "")

    # Extract key assertion lines from stdout
    assertion_lines = [
        line for line in stdout.splitlines()
        if any(kw in line for kw in ["BUG", "assert", "CONFIRMED", "===", "Buggy", "Correct"])
    ]
    assertion_excerpt = "\n".join(assertion_lines[:8])

    return f"""
---

## PoC Evidence: {fid}

**Severity:** {sev}
**Status:** {STATUS_ICON.get(result['status'], '?')} {result['status'].upper()}
**Repair cycles:** {result.get('repair_attempts', 0)}

### Claim proved

{original.get('impact', evidence)[:400]}

### Test

`{test_file}`

### Command

```bash
{run_cmd}
```

### Output

```
{assertion_excerpt or stdout[:500] or "(empty output — assertions passed silently)"}
```

### Security impact

{evidence[:600]}

### Next steps

{chr(10).join(f"- {s}" for s in result.get("next_steps", [])) or "- None — ready to submit"}
"""


def render_non_proved_section(result: dict, original: dict, triage: dict) -> str:
    fid    = result["finding_id"]
    status = result["status"]
    sev    = triage.get("recommended_severity", original.get("severity", "?")).upper()
    reason = result.get("evidence_summary", result.get("stderr_excerpt", "")[:300])

    return f"""
---

## {fid} — {STATUS_ICON.get(status, '?')} {status.upper()} ({sev})

**Title:** {original.get('title', fid)}

**Reason:** {reason[:300]}

**Next steps:**
{chr(10).join(f"- {s}" for s in result.get("next_steps", [][:3])) or "- Manual PoC required"}
"""


def render_report(results: list[dict]) -> str:
    proved       = [r for r in results if r["status"] == "proved"]
    not_proved   = [r for r in results if r["status"] != "proved"]

    sections = [
        "# PoC Evidence Report",
        "",
        f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
    ]

    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    for status, count in sorted(by_status.items()):
        sections.append(f"| {STATUS_ICON.get(status, '?')} {status} | {count} |")

    sections += ["", f"**{len(proved)} bugs proved** out of {len(results)} attempted.", ""]

    if proved:
        # Sort by triage severity
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        def sev_key(r):
            t = load_triage(r["finding_id"])
            return sev_order.get(t.get("recommended_severity", "low"), 9)
        proved_sorted = sorted(proved, key=sev_key)

        sections.append("## Proved Findings")
        for result in proved_sorted:
            fid      = result["finding_id"]
            plan     = load_plan(fid)
            original = load_original(fid)
            triage   = load_triage(fid)
            sections.append(render_proved_section(result, plan, original, triage))

    if not_proved:
        sections.append("\n## Unproved Findings (needs more work)")
        for result in not_proved:
            fid      = result["finding_id"]
            original = load_original(fid)
            triage   = load_triage(fid)
            sections.append(render_non_proved_section(result, original, triage))

    return "\n".join(sections)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate PoC evidence report")
    parser.add_argument("--out", default=None, help="Output markdown file")
    args = parser.parse_args()

    results = load_all_results()
    if not results:
        print("[info] No PoC results found in data/poc_queue/. Run generate_poc_test.py first.")
        return 0

    report = render_report(results)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report)
        print(f"Report written → {args.out}")
        proved = sum(1 for r in results if r["status"] == "proved")
        print(f"  {proved}/{len(results)} bugs proved")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
