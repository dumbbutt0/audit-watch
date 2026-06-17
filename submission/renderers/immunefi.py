#!/usr/bin/env python3
"""
immunefi.py — render an Immunefi-style human draft from a gate-validated candidate.

This produces the BODY of the draft (the watermark/warning block is added by
platform_renderer). It only formats fields that already exist on the candidate;
it never fabricates evidence. There is no `recommendation` field on the schema,
so Recommended Mitigation renders an explicit human-TODO placeholder.

Pure string formatting — no I/O, no submission, no automation.
"""
from __future__ import annotations

PLATFORM = "immunefi"

_MITIGATION_TODO = "_To be completed by the human reviewer (no mitigation was supplied)._"


def _join_list(items, bullet="- ") -> str:
    items = [str(i).strip() for i in (items or []) if str(i).strip()]
    if not items:
        return "_None provided._"
    return "\n".join(f"{bullet}{i}" for i in items)


def _scalar(value, fallback: str = "_Not provided._") -> str:
    value = (value or "").strip() if isinstance(value, str) else (value or "")
    return value if value else fallback


def _state_transition(st: dict) -> str:
    st = st or {}
    before = (st.get("before") or "").strip()
    after = (st.get("after") or "").strip()
    slots = st.get("slots_or_balances") or []
    if not (before or after or slots):
        return "_Not provided._"
    out = []
    if before:
        out.append(f"- Before: {before}")
    if after:
        out.append(f"- After: {after}")
    if slots:
        out.append(f"- Slots/balances: {', '.join(slots)}")
    return "\n".join(out)


def _human_review_checklist(gate_report: dict) -> str:
    """A human-only checklist (stripped before submission, like the watermark).

    Surfaces the gate's residual warnings/needs-proof items plus standing
    reminders. This is intentionally internal — do NOT paste it into the
    platform submission text.
    """
    items = [
        "[ ] Confirm the target asset is in scope for the program.",
        "[ ] Confirm the impact category is accepted by the program.",
        "[ ] Re-run / re-read the PoC and confirm the asserted outcome.",
        "[ ] Confirm this is not a duplicate / known issue.",
        "[ ] Add the Recommended Mitigation (currently a placeholder).",
        "[ ] Remove this checklist and the DRAFT watermark before submitting.",
    ]
    for w in gate_report.get("warnings", []):
        items.append(f"[ ] Resolve gate warning: {w}")
    return "\n".join(items)


def render_body(candidate: dict, gate_report: dict) -> str:
    c = candidate
    mapping = c.get("bounty_program_mapping") or {}
    just = c.get("severity_justification") or {}

    program = _scalar(mapping.get("program"))
    platform = _scalar(mapping.get("platform"), "Immunefi")
    asset = _scalar(c.get("in_scope_asset"))
    contracts = _join_list(c.get("affected_contracts"))

    lines: list[str] = []
    lines.append(f"## Program\n{program} ({platform})")
    lines.append(f"## Asset / Target\n{asset}\n\nAffected contracts:\n{contracts}")
    lines.append(f"## Impact\n{_scalar(c.get('impact_category'))}")
    lines.append(f"## Severity\n{_scalar(c.get('severity_claim'))}")
    lines.append(f"## Title\n{_scalar(c.get('title'))}")
    lines.append(f"## Description\n{_scalar(c.get('triager_summary') or c.get('root_cause'))}")

    vuln = [_scalar(c.get("root_cause"))]
    vuln.append("\nAffected functions:\n" + _join_list(c.get("affected_functions")))
    vuln.append("\nEntry point: " + _scalar(c.get("attacker_entrypoint")))
    vuln.append("\nCall path:\n" + _join_list(c.get("call_trace")))
    lines.append("## Vulnerability Details\n" + "\n".join(vuln))

    impact_details = [
        f"- Impact category: {_scalar(c.get('impact_category'))}",
        f"- Quantified delta: {_scalar(c.get('asset_delta'))}",
        f"- Worst case: {_scalar(just.get('worst_case'))}",
        f"- Realistic case: {_scalar(just.get('realistic_case'))}",
        f"- Program impact-table mapping: {_scalar(just.get('program_table_mapping'))}",
        "- State transition:\n" + _state_transition(c.get("state_transition")),
    ]
    lines.append("## Impact Details\n" + "\n".join(impact_details))

    poc = [
        f"- Proof type: {_scalar(c.get('proof_type'))}",
        f"- PoC status: {_scalar(c.get('poc_status'))}",
        f"- PoC path: {_scalar(c.get('poc_path'))}",
        "- Reproduction steps:\n" + _join_list(c.get("reproduction_steps")),
    ]
    lines.append("## Proof of Concept\n" + "\n".join(poc))

    lines.append("## Recommended Mitigation\n" + _MITIGATION_TODO)
    lines.append("## Evidence\n" + _join_list(c.get("evidence_links")))

    al = (c.get("assumptions") or []) + (c.get("invalidating_conditions") or []) \
        + (c.get("false_positive_risks") or [])
    lines.append("## Assumptions / Limitations\n" + _join_list(al))

    lines.append("## Human Review Checklist\n" + _human_review_checklist(gate_report))

    return "\n\n".join(lines) + "\n"
