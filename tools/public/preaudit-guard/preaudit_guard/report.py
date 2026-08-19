"""Renderers: terminal text, markdown, and JSON.

Every report ends with a calibrated disclaimer and a recommendations block keyed
to which detector categories fired.
"""

from __future__ import annotations

import json

from .findings import ScanResult, Severity, RECOMMENDATIONS

DISCLAIMER = (
    "PreAudit Guard reports pre-audit RISK SIGNALS only. It does not prove a repository is "
    "safe or malicious, and it never executes the scanned code. Review flagged items before "
    "installing dependencies, running tests, or feeding the code to an AI agent."
)

_ICON = {
    Severity.CRITICAL: "🟥 CRITICAL",
    Severity.HIGH: "🟧 HIGH",
    Severity.MEDIUM: "🟨 MEDIUM",
    Severity.LOW: "🟩 LOW",
}


def _recommendations(result: ScanResult) -> list[str]:
    detectors = {f.detector for f in result.findings}
    recs: list[str] = []
    for det in ("prompt_injection", "lifecycle_scripts", "secrets",
                "network_behavior", "destructive_fs", "dynamic_exec", "ci_actions"):
        if det in detectors:
            recs.append(RECOMMENDATIONS[det])
    if any(f.category == "network_in_setup" for f in result.findings):
        recs.append(RECOMMENDATIONS["_network_in_setup"])
    return recs


def render_json(result: ScanResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def render_text(result: ScanResult) -> str:
    out: list[str] = []
    overall = result.overall
    out.append("PreAudit Guard — preflight scan")
    out.append(f"  Target : {result.root}")
    out.append(f"  Files  : {result.files_scanned}")
    out.append(f"  Risk   : {_ICON[overall]}")
    c = result.counts()
    out.append(f"  Findings: {len(result.findings)}  "
               f"(CRITICAL {c['CRITICAL']} · HIGH {c['HIGH']} · MEDIUM {c['MEDIUM']} · LOW {c['LOW']})")
    out.append("")

    if not result.findings:
        out.append("  No risk signals detected. (Absence of signals is not proof of safety.)")
    else:
        for f in result.findings:
            out.append(f"  [{f.severity.label}] {f.detector}/{f.category}")
            out.append(f"      {f.file}:{f.line}" if f.line else f"      {f.file}")
            out.append(f"      {f.message}")
            if f.snippet:
                out.append(f"      ▸ {f.snippet}")
        recs = _recommendations(result)
        if recs:
            out.append("")
            out.append("  Recommended quarantine actions:")
            for r in recs:
                out.append(f"   - {r}")

    out.append("")
    out.append(f"  NOTE: {DISCLAIMER}")
    return "\n".join(out)


def render_markdown(result: ScanResult) -> str:
    overall = result.overall
    c = result.counts()
    out: list[str] = []
    out.append("# PreAudit Guard — preflight scan")
    out.append("")
    out.append(f"- **Target:** `{result.root}`")
    out.append(f"- **Files scanned:** {result.files_scanned}")
    out.append(f"- **Overall risk:** **{overall.label}**")
    out.append(f"- **Findings:** {len(result.findings)} "
               f"(CRITICAL {c['CRITICAL']} · HIGH {c['HIGH']} · MEDIUM {c['MEDIUM']} · LOW {c['LOW']})")
    out.append("")
    if not result.findings:
        out.append("> No risk signals detected. _Absence of signals is not proof of safety._")
    else:
        out.append("| Severity | Detector | Location | Signal |")
        out.append("|---|---|---|---|")
        for f in result.findings:
            loc = f"{f.file}:{f.line}" if f.line else f.file
            msg = f.message.replace("|", "\\|")
            out.append(f"| {f.severity.label} | {f.detector}/{f.category} | `{loc}` | {msg} |")
        recs = _recommendations(result)
        if recs:
            out.append("")
            out.append("## Recommended quarantine actions")
            for r in recs:
                out.append(f"- {r}")
    out.append("")
    out.append("---")
    out.append(f"_{DISCLAIMER}_")
    return "\n".join(out)


RENDERERS = {"text": render_text, "markdown": render_markdown, "json": render_json}


def render(result: ScanResult, fmt: str) -> str:
    return RENDERERS[fmt](result)
