"""Detector: dynamic / unsafe code execution and deserialization.

Scope: source + script files. Flags eval/exec, os.system, subprocess(shell=True),
pickle, unsafe yaml.load, new Function, vm.runIn*, and child_process spawning.
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import load_rules, is_code, is_script, line_of

DETECTOR = "dynamic_exec"


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    if not (is_code(path) or is_script(path)):
        return []
    rules = rules if rules is not None else load_rules("dynamic_exec")
    rec = RECOMMENDATIONS[DETECTOR]
    findings: list[Finding] = []
    for spec in rules.get("patterns", []):
        rx = re.compile(spec["pattern"])
        skip = re.compile(spec["skip_if_nearby"]) if spec.get("skip_if_nearby") else None
        for m in rx.finditer(text):
            if skip and skip.search(text[m.start():m.end() + 60]):
                continue
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
