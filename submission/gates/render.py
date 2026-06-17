#!/usr/bin/env python3
"""
render.py — fill the markdown templates from a gate verdict / candidate.

Kept separate from the gate logic so templates can evolve without touching the
decision code. Pure string formatting; no I/O beyond reading template files.
"""
from __future__ import annotations

from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

_STATUS_BLURB = {
    "DO_NOT_SUBMIT": "Do not submit. One or more hard gates failed.",
    "NEEDS_MORE_PROOF": "Not ready: more proof/evidence required before review.",
    "READY_FOR_HUMAN_REVIEW": "Plausible, with residual uncertainty — route to a human reviewer.",
    "READY_TO_SUBMIT_AFTER_APPROVAL": "Clean. Submit only AFTER explicit human approval.",
}


def render_readiness_report(report: dict) -> str:
    """Render the internal gate verdict report (templates/readiness_report.md)."""
    status = report.get("recommended_status", "NEEDS_MORE_PROOF")
    lines: list[str] = []
    lines.append(f"# Submission Readiness — {report.get('finding_id', '')}")
    lines.append("")
    lines.append(f"**Title:** {report.get('title', '')}")
    lines.append("")
    lines.append(f"**Status:** `{status}` — {_STATUS_BLURB.get(status, '')}")
    lines.append("")
    lines.append("**Human approval required:** YES (the layer never auto-submits)")
    author = report.get("author_recommended_status")
    if author and author != status:
        lines.append("")
        lines.append(f"> Note: author recommended `{author}`; gate computed `{status}`. "
                     "The gate verdict governs.")
    lines.append("")

    if report.get("schema_errors"):
        lines.append("## Schema errors")
        for e in report["schema_errors"]:
            lines.append(f"- {e}")
        lines.append("")

    if report.get("blockers"):
        lines.append("## Blockers (DO_NOT_SUBMIT)")
        for b in report["blockers"]:
            lines.append(f"- {b}")
        lines.append("")
    if report.get("needs_proof"):
        lines.append("## Needs more proof")
        for n in report["needs_proof"]:
            lines.append(f"- {n}")
        lines.append("")
    if report.get("warnings"):
        lines.append("## Warnings (human review)")
        for w in report["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Per-gate results")
    lines.append("")
    lines.append("| # | Gate | Verdict | Reason |")
    lines.append("|---|------|---------|--------|")
    for g in report.get("gates", []):
        reason = (g.get("reason") or "").replace("\n", " ").replace("|", "\\|")
        lines.append(f"| {g.get('gate')} | {g.get('name')} | {g.get('verdict')} | {reason} |")
    lines.append("")
    lines.append(f"_Evaluated at {report.get('evaluated_at', '')}._")
    lines.append("")
    return "\n".join(lines)
