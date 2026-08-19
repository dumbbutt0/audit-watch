"""Detector: secret / private-key exposure.

Matched secret material is REDACTED in output (never echoed in full). High-noise
patterns (bare 32-byte hex, 12-word phrases) are gated on a nearby context
keyword to keep false positives down.
"""

from __future__ import annotations

import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import load_rules, basename, line_of

DETECTOR = "secrets"

_PLACEHOLDERS = {
    "", "x", "xxx", "xxxx", "changeme", "your-key-here", "your_api_key",
    "todo", "none", "null", "example", "placeholder", "redacted", "secret",
}

# Files that are templates by convention — values in them are placeholders, not secrets.
_TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist", ".tpl")

# Values that are code references to a secret (read at runtime), not the secret itself.
_CODE_REF_RE = re.compile(
    r"(process\.env|import\.meta\.env|os\.environ|os\.getenv|getenv|vault|\bENV\b|\.env\.)",
    re.IGNORECASE,
)


def _redact(s: str) -> str:
    s = s.strip().strip("\"'")
    if len(s) <= 8:
        return "***"
    return f"{s[:4]}…{s[-2:]} [redacted, len={len(s)}]"


def _is_placeholder(v: str) -> bool:
    v2 = v.strip().strip("\"'")
    low = v2.lower()
    if low in _PLACEHOLDERS or len(v2) < 8:
        return True
    if v2.startswith(("$", "<", "{")):           # ${VAR}, <fill>, {{ }}
        return True
    if len(set(v2)) <= 2:                          # "aaaaaaaa", "00000000"
        return True
    if _CODE_REF_RE.search(v2):                    # process.env.X, os.getenv(...), vault refs
        return True
    return False


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    rules = rules if rules is not None else load_rules("secrets")
    rec = RECOMMENDATIONS[DETECTOR]
    findings: list[Finding] = []
    bn = basename(path)
    # Template files (.env.example, config.sample, …) hold placeholders, not real secrets.
    if bn.lower().endswith(_TEMPLATE_SUFFIXES):
        return findings
    lines = text.split("\n")

    # 1) regex secret patterns (with optional same-line context gate)
    for spec in rules.get("secret_patterns", []):
        rx = re.compile(spec["pattern"])
        ctx = re.compile(spec["needs_context"], re.IGNORECASE) if spec.get("needs_context") else None
        for m in rx.finditer(text):
            ln = line_of(text, m.start())
            if ctx and not ctx.search(lines[ln - 1] if ln - 1 < len(lines) else ""):
                continue
            findings.append(Finding(
                detector=DETECTOR, category=spec["category"],
                severity=Severity.from_str(spec["severity"]),
                file=path, line=ln, message=spec["message"],
                snippet=_redact(m.group(0)), recommendation=rec,
            ))

    # 2) standalone token shapes (AWS id, GitHub PAT, Slack)
    for spec in rules.get("token_patterns", []):
        rx = re.compile(spec["pattern"])
        for m in rx.finditer(text):
            findings.append(Finding(
                detector=DETECTOR, category=spec["category"],
                severity=Severity.from_str(spec["severity"]),
                file=path, line=line_of(text, m.start()), message=spec["message"],
                snippet=_redact(m.group(0)), recommendation=rec,
            ))

    # 3) named key assignments: NAME = value / NAME: value (value must look real)
    for spec in rules.get("named_keys", []):
        name = spec["name"]
        rx = re.compile(rf'\b{re.escape(name)}\b\s*[:=]\s*(["\']?)([^\s"\',}}]+)\1')
        for m in rx.finditer(text):
            value = m.group(2)
            if _is_placeholder(value):
                continue
            findings.append(Finding(
                detector=DETECTOR, category="named_secret",
                severity=Severity.from_str(spec["severity"]),
                file=path, line=line_of(text, m.start()),
                message=f"Assigned secret '{name}' with a concrete value.",
                snippet=f"{name}={_redact(value)}", recommendation=rec,
            ))

    # 4) Solana keypair files (64-int JSON array)
    if bn in set(rules.get("solana_keypair_basenames", [])):
        arr = rules.get("solana_keypair_array")
        if arr and re.search(arr, text):
            findings.append(Finding(
                detector=DETECTOR, category="solana_keypair", severity=Severity.CRITICAL,
                file=path, line=1,
                message=f"'{bn}' contains a 64-byte keypair array — a committed Solana private key.",
                snippet="[<64-byte secret key redacted>]", recommendation=rec,
            ))

    # 5) committed env/key files
    if bn in set(rules.get("risky_filenames", [])):
        findings.append(Finding(
            detector=DETECTOR, category="committed_env_file", severity=Severity.LOW,
            file=path, line=0,
            message=f"'{bn}' is committed — env/secret files should be gitignored.",
            snippet=bn, recommendation=rec,
        ))

    return findings
