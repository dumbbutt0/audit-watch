#!/usr/bin/env python3
"""
generate_review_gate.py — Write output/review_gate.md and pause the pipeline.

Reads all CONFIRMED per-finding triage files from data/triage/<id>.md,
builds a formatted gate document with severity summary and ASCII call-flow
diagrams, then exits 0 after printing the pipeline pause message.

run_pipeline.sh full must treat this exit as a hard stop before Steps 5–9.

Usage:
    python scripts/generate_review_gate.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_meta, write_session

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]


def _parse_triage_md(path: Path) -> dict | None:
    """Extract key fields from a per-finding triage markdown file."""
    text = path.read_text()

    # Must be CONFIRMED
    if "CONFIRMED" not in text or "[ ] CONFIRMED" in text:
        if "CONFIRMED" not in re.sub(r"\[ \] CONFIRMED", "", text):
            return None

    finding: dict = {"id": path.stem, "raw": text}

    # Title from first heading
    m = re.search(r"^#\s+([^\n]+)", text, re.MULTILINE)
    finding["title"] = m.group(1).strip() if m else path.stem

    # ICE re-score table
    for axis, key in [("I", "severity"), ("C", "confidence"), ("E", "exploitability")]:
        m = re.search(
            rf"\|\s*{axis}\s*\|[^|]*\|[^|]*\|([^|]+)\|",
            text
        )
        if m:
            finding[key] = m.group(1).strip()
        else:
            # Fallback: look for prior score column
            m2 = re.search(
                rf"\|\s*{axis}\s*\|([^|]+)\|",
                text
            )
            finding[key] = m2.group(1).strip() if m2 else "?"

    # Entry point
    m = re.search(r"## External Entry Point\n+([^\n#][^\n]*)", text)
    finding["entry_point"] = m.group(1).strip() if m else "?"

    # Triage notes (last section)
    m = re.search(r"## Triage Notes\n+([\s\S]*?)(?:\n##|\Z)", text)
    finding["notes"] = (m.group(1).strip()[:200] if m else "")

    # Attack sequence (first 4 numbered steps)
    steps = re.findall(r"^\d+\.\s+(.+)", text, re.MULTILINE)
    finding["attack_steps"] = steps[:4]

    return finding


def _severity_from_finding(f: dict) -> str:
    raw = f.get("severity", "")
    for sev in SEVERITY_ORDER:
        if sev.lower() in raw.lower():
            return sev
    return "Medium"


def _ascii_flow(f: dict) -> list[str]:
    """Build a minimal ASCII call-flow diagram from the attack steps."""
    lines = ["```"]
    lines.append("[EOA/Attacker]")
    lines.append("    │")

    entry = f.get("entry_point", "?")
    # Extract function name and file:line if present
    fn_match = re.search(r"`?(\w+[\.\w]*\([^)]*\))`?", entry)
    fn_str = fn_match.group(1) if fn_match else entry[:60]
    file_match = re.search(r"\[([^\]]+)\]", entry)
    file_str = file_match.group(1) if file_match else ""

    lines.append(f"    ▼")
    lines.append(f"{fn_str:<40}  {('[' + file_str + ']') if file_str else ''}")

    for i, step in enumerate(f.get("attack_steps", [])[:3]):
        step = step[:80]
        lines.append(f"    │  {step}")
        if i < len(f.get("attack_steps", [])) - 1:
            lines.append("    ▼")

    lines.append("    │")
    lines.append("    ▼")
    lines.append("[Outcome: see Triage Notes]")
    lines.append("```")
    return lines


def _advisory_section() -> list[str]:
    """P136: render existing mechanism-detector advisories as a clearly-separated NOT-confirmed section.

    ADVISORY-ONLY. Reads output/mechanism_advisory_context.json (written by surface_mechanism_advisories.py).
    Robust by contract: if the file is missing, malformed, disabled (surfaced=false), or empty, return [] —
    no section, no error. These entries are NEVER added to `findings`, so the confirmed-findings count and the
    Validated Findings table are unaffected.
    """
    try:
        p = audit_path("output", "mechanism_advisory_context.json")
        if not p.exists():
            return []
        ctx = json.loads(p.read_text())
    except (OSError, ValueError):  # ValueError covers json.JSONDecodeError
        return []
    if not isinstance(ctx, dict) or not ctx.get("surfaced"):
        return []
    advis = ctx.get("advisories") or []
    recs = ctx.get("deep_pass_recommendations") or []
    if not advis and not recs:
        return []
    out = [
        "", "---", "",
        "## Advisory Context — NOT confirmed (mechanism detectors)", "",
        "> **Advisory only — NOT confirmed findings, NOT submission-ready.** Every row below is "
        "`advisory_only=true`, `submission_ready=false`, `requires_human_review=true`. These are existing "
        "mechanism-detector signals surfaced for human review only; they are **excluded from the Validated "
        "Findings table and the confirmed-findings count**. Do not submit or assign severity from this section "
        "without independent human/PoC confirmation.", "",
    ]
    if advis:
        out += ["| Detector | Status | Location | Mechanism | Confidence | Route reason |",
                "|---|---|---|---|---|---|"]
        for a in advis:
            if not isinstance(a, dict):
                continue
            loc = f"{a.get('contract', '?')}.{a.get('function', '?')}"
            rr = str(a.get("route_reason", "")).replace("|", "/")[:90]
            out.append(f"| {a.get('source_detector', '?')} | {a.get('detector_status', '?')} | `{loc}` | "
                       f"{a.get('mechanism_class', '?')} | {a.get('confidence', '?')} | {rr} |")
    if recs:
        out += ["", "### Deep-pass recommendations (review_context only)", "",
                "| Location | Recommended prompt | Reason |", "|---|---|---|"]
        for r in recs:
            if not isinstance(r, dict):
                continue
            loc = f"{r.get('contract', '?')}.{r.get('function', '?')}"
            out.append(f"| `{loc}` | {r.get('recommended_prompt', '?')} | "
                       f"{str(r.get('prompt_reason', '')).replace('|', '/')[:90]} |")
    out += [""]
    return out


def _submission_risk_section() -> list[str]:
    """Pre-READY submission-risk advisories (reachability/novelty/design). ADVISORY-ONLY.

    Reads output/submission_risk.json (written by submission_risk_audit.py). Robust: missing/malformed/empty
    -> [] (no section, no error). These are NEVER added to `findings` and never change a finding's state — they
    flag the bounty-rejection axes (reachability / duplicate-novelty / design-accepted) so effort isn't spent
    submitting a finding likely to bounce, per the real-world calibration_lessons.
    """
    try:
        p = audit_path("output", "submission_risk.json")
        if not p.exists():
            return []
        doc = json.loads(p.read_text())
    except (OSError, ValueError):
        return []
    rows = [r for r in (doc.get("findings") or []) if r.get("overall") in ("high", "review")]
    if not rows:
        return []
    out = [
        "", "---", "",
        "## Submission-risk — ADVISORY (likely bounty-rejection axes; NOT a rejection)", "",
        "> **Advisory only.** Flags axes — *deployment-reachability, duplicate/novelty, design-accepted* — that "
        "sink real, valid PoCs at triage. A flag is a **prompt to verify before submitting**, not a finding "
        "verdict: it does **not** change any finding's state and these rows are **excluded from the Validated "
        "Findings table/count**. `checklist_required` => answer via `agents/submission_risk_review.md`.", "",
        "| Finding | Overall | Advisories |", "|---|---|---|",
    ]
    for r in rows:
        adv = "<br>".join(a.replace("|", "/") for a in r.get("advisories", [])) or "—"
        out.append(f"| {r.get('finding_id', '?')} | {r.get('overall', '?')} | {adv} |")
    out += [""]
    return out


def _value_provenance_section() -> list[str]:
    """P139: render value-provenance deep-pass auto-run results as an advisory-only subsection.

    Reads output/value_provenance_advisory_results.json. Robust: missing/malformed/disabled/empty -> [] (no
    section, no error). Results are NEVER added to `findings` (confirmed count + Validated Findings unaffected).
    """
    try:
        p = audit_path("output", "value_provenance_advisory_results.json")
        if not p.exists():
            return []
        rep = json.loads(p.read_text())
    except (OSError, ValueError):
        return []
    if not isinstance(rep, dict) or not rep.get("ran"):
        return []
    results = [r for r in (rep.get("results") or []) if isinstance(r, dict)]
    if not results:
        return []
    # P140: optional hide of strong_clear (cleared) rows; read from the advisory config block.
    hide_clear = False
    try:
        pol = json.loads((Path(__file__).resolve().parent.parent / "config" / "agent_policy.json").read_text())
        hide_clear = bool(pol.get("value_provenance_auto_run", {}).get(
            "auto_run_value_provenance_hide_strong_clear", False))
    except (OSError, ValueError):
        hide_clear = False

    def _decision_label(r: dict) -> str:
        """P140: completed finding/likely_exploitable stays explicitly NOT confirmed; strong_clear -> cleared."""
        d = r.get("prompt_decision", "?")
        if d in ("finding", "likely_exploitable"):
            return f"{d} — NOT confirmed"
        if d == "strong_clear":
            return "strong_clear (cleared advisory context)"
        return d

    rows = []
    for r in results:
        if hide_clear and r.get("prompt_decision") == "strong_clear":
            continue
        loc = f"{r.get('contract', '?')}.{r.get('function', '?')}"
        mech = str(r.get("mechanism_summary", "")).replace("|", "/")[:60]
        nxt = str(r.get("recommended_next_step") or "").replace("|", "/")
        conf = r.get("prompt_confidence") or "-"
        rows.append(f"| {r.get('auto_run_status', '?')} | `{loc}` | {_decision_label(r)} | {conf} | "
                    f"{nxt or '-'} | {mech} | {Path(str(r.get('output_path', ''))).name} |")
    if not rows:
        return []
    out = [
        "", "### Value Provenance Deep-Pass Results — advisory only", "",
        "> **Advisory only — prompt-derived review evidence, NOT proof, NOT confirmed, NOT submission-ready.** "
        "Every row is `advisory_only=true`, `submission_ready=false`, `requires_human_review=true`. **Requires "
        "human review and PoC before use in any report.** Excluded from Validated Findings and the confirmed count.", "",
        "| Status | Location | Decision | Confidence | Next step | Mechanism | Job |",
        "|---|---|---|---|---|---|---|",
    ]
    out += rows
    out += [""]
    return out


def _coverage_section() -> list:
    """Necessary-file coverage summary (from output/coverage_gate.json). Surfaces coverage% + any still-
    unexamined in-scope files so under-coverage is never silent in the review-gate deliverable."""
    try:
        cg = json.loads((audit_path("output", "coverage_gate.json")).read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return []
    s = cg.get("summary", {}) or {}
    cov = s.get("coverage_percent")
    if cov is None:
        return []
    in_scope = s.get("in_scope_items", 0)
    resolved = (s.get("finding", 0) or 0) + (s.get("cleared", 0) or 0)
    unexamined = (s.get("unassigned", 0) or 0) + (s.get("assigned_only", 0) or 0) + (s.get("examined", 0) or 0)
    complete = unexamined == 0
    status = "✅ COMPLETE (100%)" if complete else f"⚠️ PARTIAL — {unexamined} in-scope item(s) NOT yet examined"
    out = [
        "## Necessary-file coverage", "",
        f"- **Coverage:** {cov}%  ({resolved}/{in_scope} in-scope items examined) — {status}",
    ]
    if cg.get("override_active"):
        out.append("- **⚠️ COVERAGE GATE OVERRIDDEN** (`AUDITWATCH_COVERAGE_OVERRIDE=1`): this review gate was "
                   "produced BELOW 100% necessary-file coverage — bugs may be missed because a file was not examined.")
    if not complete:
        blocking = cg.get("blocking_items", []) or []
        files = []
        for b in blocking:
            f = b.get("file") or b.get("manifest_id") or ""
            if f and f not in files:
                files.append(f)
        if files:
            out.append(f"- **Unexamined in-scope files ({len(files)}):** " +
                       ", ".join(f"`{f}`" for f in files[:30]) + (" …" if len(files) > 30 else ""))
        out.append("- Run `/coverage-sweep` → `python scripts/coverage_sweep_write.py` → "
                   "`./run_pipeline.sh review-gate` to drive coverage to 100%.")
    out.append("")
    return out


def main() -> None:
    meta  = get_audit_meta()
    audit_id = meta.get("audit_id", "unknown")
    triage_dir = audit_path("data", "triage")

    md_files = sorted(triage_dir.glob("*.md"))
    findings: list[dict] = []
    for p in md_files:
        f = _parse_triage_md(p)
        if f:
            f["severity_label"] = _severity_from_finding(f)
            findings.append(f)

    # Sort by severity
    findings.sort(key=lambda f: SEVERITY_ORDER.index(
        f.get("severity_label", "Medium")
        if f.get("severity_label", "Medium") in SEVERITY_ORDER else "Medium"
    ))

    # Severity counts
    counts: dict[str, int] = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity_label", "Medium")
        if sev in counts:
            counts[sev] += 1

    # Build document
    lines: list[str] = [
        f"# Audit Review Gate — {audit_id}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Target: {meta.get('name', meta.get('contract_path', '?'))}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|---|---|",
    ]
    for sev in SEVERITY_ORDER:
        lines.append(f"| {sev} | {counts[sev]} |")
    lines += ["", "---", "", "## Validated Findings", ""]
    lines += [
        "| ID | Title | Severity | Entry Point | ICE_C | ICE_E |",
        "|---|---|---|---|---|---|",
    ]
    for f in findings:
        row_id    = f["id"]
        title     = f["title"][:50]
        sev       = f.get("severity_label", "?")
        entry     = (f.get("entry_point") or "?")[:40]
        conf      = f.get("confidence", "?")
        expl      = f.get("exploitability", "?")
        lines.append(f"| {row_id} | {title} | {sev} | {entry} | {conf} | {expl} |")

    lines += ["", "---", "", "## Finding Details", ""]

    for f in findings:
        lines += [
            f"### {f['id']} — {f['title']}",
            "",
            f"**Severity:** {f.get('severity_label', '?')}",
            f"**Entry Point:** `{f.get('entry_point', '?')}`",
            f"**ICE:** I={f.get('severity','?')} / C={f.get('confidence','?')} / E={f.get('exploitability','?')}",
            "",
            "**Attack Flow:**",
        ]
        lines += _ascii_flow(f)
        if f.get("notes"):
            lines += ["", f"**Notes:** {f['notes']}"]
        lines += ["", "**Triage Verdict:** CONFIRMED", "", "---", ""]

    # P136: append the advisory (NOT-confirmed) section, if any. Never affects `findings` / the confirmed count.
    lines += _advisory_section()
    # P139: value-provenance deep-pass auto-run results (advisory-only subsection). Same isolation guarantee.
    lines += _value_provenance_section()
    # Pre-READY submission-risk advisories (reachability/novelty/design). Advisory-only; never changes state.
    lines += _submission_risk_section()
    # P315: necessary-file coverage summary — make under-coverage explicit in the deliverable (never silent).
    lines += _coverage_section()

    out_path = audit_path("output", "review_gate.md")
    out_path.write_text("\n".join(lines))
    write_session({"active_step": 4, "findings_count": len(findings)})

    print(f"\nReview gate written: {out_path}")
    print(f"  Confirmed findings: {len(findings)}")
    print()
    print("=" * 60)
    print("PIPELINE PAUSED — Step 4 complete.")
    print(f"Review: audits/{audit_id}/output/review_gate.md")
    print()
    print('Reply with the Finding IDs you want PoC\'d')
    print('  e.g., "PoC F-001, F-003, C-001"')
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
