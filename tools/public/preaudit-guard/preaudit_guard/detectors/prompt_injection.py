"""Detector: prompt-injection / AI-agent-targeting text.

Fires on PROSE surfaces only (doc files, comments, string literals) for
instruction/self-reference/base64/oversized-natspec, and on CODE files for
mixed-script (homoglyph) identifiers. This scoping keeps false positives low —
ordinary code identifiers and math-notation comments do not trip it.
"""

from __future__ import annotations

import base64
import re

from ..findings import Finding, Severity, RECOMMENDATIONS
from .base import (
    load_rules, compile_patterns, prose_segments, ext,
    CSTYLE_EXT, HASH_EXT, line_of,
)

DETECTOR = "prompt_injection"

# pattern fragments that indicate the injection tries to *steal* something
_EXFIL_HINT = re.compile(r"exfiltrat|send|leak|upload|post|environment\s+variables?|secret|private\s+key", re.I)


def detect(path: str, text: str, rules: dict | None = None) -> list[Finding]:
    rules = rules if rules is not None else load_rules("prompt_injection")
    instr_re = compile_patterns(rules.get("instruction_patterns", []))
    selfref_re = compile_patterns(rules.get("self_ref_patterns", []))
    homoglyphs: dict = rules.get("homoglyphs", {})
    natspec_max = int(rules.get("oversized_natspec_chars", 500))
    b64_min = int(rules.get("base64_min_run", 60))
    b64_ratio = float(rules.get("base64_printable_ratio", 0.8))

    findings: list[Finding] = []
    rec = RECOMMENDATIONS[DETECTOR]
    segments = prose_segments(path, text)

    for line, seg in segments:
        # instruction injection
        for rx in instr_re:
            if rx.search(seg):
                exfil = bool(_EXFIL_HINT.search(rx.pattern))
                findings.append(Finding(
                    detector=DETECTOR,
                    category="exfiltration_instruction" if exfil else "instruction_injection",
                    severity=Severity.HIGH if exfil else Severity.MEDIUM,
                    file=path, line=line,
                    message=("Text instructs an agent to exfiltrate data."
                             if exfil else
                             "Potential prompt injection: text attempts to override agent instructions. Treat as untrusted data."),
                    snippet=seg[:160],
                    recommendation=rec,
                ))
                break
        # self-reference / system-prompt probing
        for rx in selfref_re:
            if rx.search(seg):
                findings.append(Finding(
                    detector=DETECTOR, category="self_reference", severity=Severity.LOW,
                    file=path, line=line,
                    message="References an AI assistant / system prompt — possible injection scaffolding.",
                    snippet=seg[:160], recommendation=rec,
                ))
                break
        # oversized NatSpec/doc tag (payload vehicle). Strip leading comment punctuation
        # ("/// @notice ..." leaves a leading '/').
        if seg.lstrip(" /\t*").startswith("@") and len(seg) > natspec_max:
            findings.append(Finding(
                detector=DETECTOR, category="oversized_natspec", severity=Severity.LOW,
                file=path, line=line,
                message=f"Abnormally large doc/NatSpec tag ({len(seg)} chars) — possible hidden payload.",
                snippet=seg[:120] + "…", recommendation=rec,
            ))
        # embedded base64 that decodes to text
        b64 = _base64_payload(seg, b64_min, b64_ratio)
        if b64:
            findings.append(Finding(
                detector=DETECTOR, category="embedded_base64", severity=Severity.MEDIUM,
                file=path, line=line,
                message="Base64 blob in prose that decodes to readable text — possible hidden instructions/payload.",
                snippet=b64[:80] + "…", recommendation=rec,
            ))

    # homoglyphs: only in code files, only inside mixed-script identifiers
    if ext(path) in CSTYLE_EXT | HASH_EXT:
        findings.extend(_homoglyph_findings(path, text, homoglyphs, rec))

    return findings


def _base64_payload(text: str, min_run: int, ratio: float) -> str | None:
    for m in re.finditer(rf"[A-Za-z0-9+/]{{{min_run},}}={{0,2}}", text):
        blob = m.group(0)
        if len(set(blob.rstrip("="))) <= 2:          # decoration banner
            continue
        body = blob[2:] if blob[:2].lower() == "0x" else blob
        if body and all(c in "0123456789abcdefABCDEF" for c in body):  # hex literal
            continue
        try:
            decoded = base64.b64decode(blob + "==").decode("utf-8", errors="replace")
        except Exception:
            continue
        printable = sum(1 for c in decoded if c.isprintable())
        if printable / max(len(decoded), 1) > ratio:
            return blob
    return None


_WORD_RE = re.compile(r"[^\s.,;:(){}\[\]<>=+\-*/\"'`|&!?]+")


def _homoglyph_findings(path: str, text: str, homoglyphs: dict, rec: str) -> list[Finding]:
    out: list[Finding] = []
    if not homoglyphs:
        return out
    for i, line in enumerate(text.split("\n"), 1):
        for token in _WORD_RE.findall(line):
            hits = [c for c in token if c in homoglyphs]
            has_ascii = any(("a" <= c.lower() <= "z") or c.isdigit() for c in token)
            if hits and has_ascii:
                c = hits[0]
                out.append(Finding(
                    detector=DETECTOR, category="homoglyph", severity=Severity.MEDIUM,
                    file=path, line=i,
                    message=(f"Mixed-script identifier {token!r}: U+{ord(c):04X} ({c!r}) "
                             f"resembles ASCII '{homoglyphs[c]}' — possible look-alike spoofing."),
                    snippet=token[:80], recommendation=rec,
                ))
                break  # one per line is enough
    return out
