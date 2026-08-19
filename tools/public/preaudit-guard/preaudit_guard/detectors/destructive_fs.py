"""Detector: destructive / catastrophic filesystem operations.

Scope: scripts, source, and config files. Focuses on high-signal, rarely-legitimate
operations (fork bombs, dd-to-device, mkfs, rm -rf of sensitive paths, recursive
language-level deletes) so it complements rather than duplicates the generic build
`rm -rf` that lifecycle_scripts already flags at MEDIUM.
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import load_rules, is_script, is_code, is_config_or_script, line_of

DETECTOR = "destructive_fs"


def _in_scope(path: str) -> bool:
    return is_script(path) or is_code(path) or is_config_or_script(path)


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    if not _in_scope(path):
        return []
    rules = rules if rules is not None else load_rules("destructive_fs")
    rec = RECOMMENDATIONS[DETECTOR]
    findings: list[Finding] = []
    for spec in rules.get("patterns", []):
        rx = re.compile(spec["pattern"])
        for m in rx.finditer(text):
            findings.append(Finding(
                detector=DETECTOR, category=spec["category"],
                severity=Severity.from_str(spec["severity"]),
                file=path, line=line_of(text, m.start()),
                message=spec["message"],
                snippet=_around(text, m.start(), m.end()), recommendation=rec,
            ))
    return findings


def _around(text: str, start: int, end: int, pad: int = 30) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    return text[a:b].replace("\n", " ").strip()[:160]
