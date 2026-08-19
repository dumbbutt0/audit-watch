"""Detector: programmatic network access in build/test/CI paths.

Flags language-level HTTP/socket clients in the paths an auditor actually executes
(tests, scripts, CI, build config). General app-source network calls are expected
and out of scope here; shell curl/wget in install/build config is handled by the
lifecycle_scripts detector.
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import load_rules, is_test_file, is_script, is_workflow, is_config_or_script, line_of

DETECTOR = "network_behavior"


def _in_scope(path: str) -> bool:
    return is_test_file(path) or is_script(path) or is_workflow(path) or is_config_or_script(path)


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    if not _in_scope(path):
        return []
    rules = rules if rules is not None else load_rules("network_behavior")
    sev = Severity.from_str(rules.get("severity", "MEDIUM"))
    rec = RECOMMENDATIONS[DETECTOR]
    findings: list[Finding] = []
    for spec in rules.get("network_calls", []):
        rx = re.compile(spec["pattern"], re.IGNORECASE)
        m = rx.search(text)  # one finding per pattern per file is enough signal
        if m:
            findings.append(Finding(
                detector=DETECTOR, category="network_call", severity=sev,
                file=path, line=line_of(text, m.start()),
                message=f"{spec['message']} (network access in a build/test/CI path — review before running.)",
                snippet=_around(text, m.start(), m.end()), recommendation=rec,
            ))
    return findings


def _around(text: str, start: int, end: int, pad: int = 30) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    return text[a:b].replace("\n", " ").strip()[:160]
