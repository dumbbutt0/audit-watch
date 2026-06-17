#!/usr/bin/env python3
"""
code4rena.py — render a Code4rena / Sherlock-style human draft from a
gate-validated candidate.

Produces the BODY of the draft (the watermark is added by platform_renderer).
Formats only existing candidate fields; never fabricates evidence. Recommended
Mitigation renders a human-TODO placeholder (no `recommendation` field exists).

Pure string formatting — no I/O, no submission, no automation.
"""
from __future__ import annotations

PLATFORM = "code4rena"

_MITIGATION_TODO = "_To be completed by the human reviewer (no mitigation was supplied)._"


def _join_list(items, bullet="- ") -> str:
    items = [str(i).strip() for i in (items or []) if str(i).strip()]
    if not items:
        return "_None provided._"
    return "\n".join(f"{bullet}{i}" for i in items)


def _scalar(value, fallback: str = "_Not provided._") -> str:
    value = (value or "").strip() if isinstance(value, str) else (value or "")
    return value if value else fallback


def _links_to_affected_code(candidate: dict) -> str:
    """Affected-code links: explicit file:line evidence + named contracts.

    Only emits references that already exist on the candidate (no invented
    line numbers or URLs)."""
    refs = []
    for link in candidate.get("evidence_links") or []:
        refs.append(str(link))
    for contract in candidate.get("affected_contracts") or []:
        if contract not in refs:
            refs.append(str(contract))
    return _join_list(refs)


def render_body(candidate: dict, gate_report: dict) -> str:
    c = candidate
    just = c.get("severity_justification") or {}

    lines: list[str] = []
    lines.append(f"## Title\n{_scalar(c.get('title'))}")
    lines.append(f"## Summary\n{_scalar(c.get('triager_summary') or c.get('root_cause'))}")

    vuln = [_scalar(c.get("root_cause"))]
    vuln.append("\nAttack path:")
    vuln.append("- Entry point: " + _scalar(c.get("attacker_entrypoint")))
    vuln.append(_join_list(c.get("call_trace")))
    lines.append("## Vulnerability Details\n" + "\n".join(vuln))

    impact = [
        f"{_scalar(c.get('impact_category'))} — {_scalar(c.get('asset_delta'))}",
        f"\nWorst case: {_scalar(just.get('worst_case'))}",
        f"Realistic case: {_scalar(just.get('realistic_case'))}",
    ]
    lines.append("## Impact\n" + "\n".join(impact))

    poc = [
        f"`{_scalar(c.get('poc_path'), '(no PoC path)')}` (status: {_scalar(c.get('poc_status'))}, "
        f"type: {_scalar(c.get('proof_type'))})",
        "",
        _join_list(c.get("reproduction_steps")),
    ]
    lines.append("## Proof of Concept\n" + "\n".join(poc))

    lines.append("## Recommended Mitigation\n" + _MITIGATION_TODO)
    lines.append("## Links to Affected Code\n" + _links_to_affected_code(c))

    return "\n\n".join(lines) + "\n"
