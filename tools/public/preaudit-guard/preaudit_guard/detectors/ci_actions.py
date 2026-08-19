"""Detector: GitHub Actions workflow risks.

Scope: .github/workflows/*.yml only. Flags pull_request_target, untrusted-event
script injection, curl|bash run steps (HIGH), and third-party actions not pinned to
a full commit SHA (LOW — common best-practice gap, not an exploit).
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import load_rules, is_workflow, line_of

DETECTOR = "ci_actions"

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    if not is_workflow(path):
        return []
    rules = rules if rules is not None else load_rules("ci_actions")
    rec = RECOMMENDATIONS[DETECTOR]
    findings: list[Finding] = []

    for spec in rules.get("patterns", []):
        rx = re.compile(spec["pattern"], re.IGNORECASE)
        for m in rx.finditer(text):
            findings.append(Finding(
                detector=DETECTOR, category=spec["category"],
                severity=Severity.from_str(spec["severity"]),
                file=path, line=line_of(text, m.start()),
                message=spec["message"],
                snippet=_around(text, m.start(), m.end()), recommendation=rec,
            ))

    up = rules.get("unpinned_action")
    if up:
        rx = re.compile(up["pattern"])
        sev = Severity.from_str(up["severity"])
        for m in rx.finditer(text):
            owner_repo, ref = m.group(1), m.group(2)
            if owner_repo.startswith("./") or owner_repo.startswith("docker"):
                continue  # local / docker action, not a third-party ref
            if _SHA_RE.match(ref):
                continue  # already SHA-pinned
            findings.append(Finding(
                detector=DETECTOR, category="unpinned_action", severity=sev,
                file=path, line=line_of(text, m.start()),
                message=f"{up['message']} ({owner_repo}@{ref})",
                snippet=f"uses: {owner_repo}@{ref}", recommendation=rec,
            ))
    return findings


def _around(text: str, start: int, end: int, pad: int = 30) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    return text[a:b].replace("\n", " ").strip()[:160]
