"""Detector: malicious / risky lifecycle & build scripts.

Scoped to config + script files (package.json, Makefile, *.sh, foundry.toml,
Dockerfile, hardhat/truffle configs). Flags auto-run install hooks, download-and-
execute (curl|bash), dynamic code execution, base64 payloads, destructive ops,
foundry `ffi = true`, dependency typosquats, and risky dependency specifiers.
"""

from __future__ import annotations

import json
import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import load_rules, is_config_or_script, basename, line_of

DETECTOR = "lifecycle_scripts"


def _line_of_sub(text: str, needle: str) -> int:
    idx = text.find(needle)
    return line_of(text, idx) if idx != -1 else 0


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    if not is_config_or_script(path):
        return []
    rules = rules if rules is not None else load_rules("lifecycle_scripts")
    rec = RECOMMENDATIONS[DETECTOR]
    findings: list[Finding] = []
    bn = basename(path)

    # 1) raw dangerous-command scan (works for any script/config; gives line numbers)
    for spec in rules.get("dangerous_commands", []):
        rx = re.compile(spec["pattern"], re.IGNORECASE)
        for m in rx.finditer(text):
            cat = spec["category"]
            findings.append(Finding(
                detector=DETECTOR, category=cat,
                severity=Severity.from_str(spec["severity"]),
                file=path, line=line_of(text, m.start()),
                message=spec["message"],
                snippet=_around(text, m.start(), m.end()),
                recommendation=(RECOMMENDATIONS["_network_in_setup"]
                                if cat == "network_in_setup" else rec),
            ))

    # 2) foundry ffi
    ffi = rules.get("foundry_ffi_pattern")
    if ffi and bn in ("foundry.toml",):
        m = re.search(ffi, text, re.IGNORECASE)
        if m:
            findings.append(Finding(
                detector=DETECTOR, category="foundry_ffi", severity=Severity.CRITICAL,
                file=path, line=line_of(text, m.start()),
                message="foundry `ffi = true`: tests can execute arbitrary shell commands during compile/test.",
                snippet=_around(text, m.start(), m.end()), recommendation=rec,
            ))

    # 3) package.json structured checks (lifecycle hooks, typosquats, risky specifiers)
    if bn == "package.json":
        findings.extend(_scan_package_json(path, text, rules, rec))

    return findings


def _scan_package_json(path: str, text: str, rules: dict, rec: str) -> list[Finding]:
    out: list[Finding] = []
    try:
        data = json.loads(text)
    except Exception:
        return out
    if not isinstance(data, dict):
        return out

    hooks = set(rules.get("npm_lifecycle_hooks", []))
    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        for name, cmd in scripts.items():
            if name in hooks:
                out.append(Finding(
                    detector=DETECTOR, category="install_hook", severity=Severity.MEDIUM,
                    file=path, line=_line_of_sub(text, f'"{name}"'),
                    message=f"npm '{name}' hook runs automatically on install: {str(cmd)[:80]}",
                    snippet=str(cmd)[:160],
                    recommendation="Install with `npm ci --ignore-scripts` and review this hook before running it.",
                ))

    typos = rules.get("typosquats", [])
    risky = [re.compile(p) for p in rules.get("risky_dep_specifiers", [])]
    for dep_field in ("dependencies", "devDependencies", "optionalDependencies"):
        deps = data.get(dep_field, {})
        if not isinstance(deps, dict):
            continue
        for name, spec in deps.items():
            for t in typos:
                # Exact package-name match only — substring matching false-positives on
                # legit scoped packages (e.g. @nomiclabs/hardhat-ethers).
                if name == t:
                    out.append(Finding(
                        detector=DETECTOR, category="typosquat", severity=Severity.HIGH,
                        file=path, line=_line_of_sub(text, f'"{name}"'),
                        message=f"Dependency '{name}' resembles a typosquat of a popular package.",
                        snippet=f"{name}: {spec}", recommendation=rec,
                    ))
            for rx in risky:
                if isinstance(spec, str) and rx.search(spec):
                    out.append(Finding(
                        detector=DETECTOR, category="risky_dep_specifier", severity=Severity.MEDIUM,
                        file=path, line=_line_of_sub(text, f'"{name}"'),
                        message=f"Dependency '{name}' uses a non-registry source ({spec}). Verify provenance.",
                        snippet=f"{name}: {spec}", recommendation=rec,
                    ))
    return out


def _around(text: str, start: int, end: int, pad: int = 30) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    return text[a:b].replace("\n", " ").strip()[:160]
