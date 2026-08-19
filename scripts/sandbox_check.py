#!/usr/bin/env python3
"""
sandbox_check.py

Zero-Trust governance gate. Scans Solidity contract source files for prompt injection
patterns before the source is fed to any AI agent. Untrusted contract source code is the
primary injection vector — a malicious developer could embed instructions in comments or
NatSpec that attempt to alter the auditor's methodology or severity decisions.

Run BEFORE static_analysis.py and before spawning any specialist agent.

Usage:
    python scripts/sandbox_check.py contracts/
    python scripts/sandbox_check.py contracts/Vault.sol
    python scripts/sandbox_check.py contracts/ --allow-flagged   # warn but proceed

Exit codes:
    0 — clean (no flags raised)
    1 — flags raised AND --allow-flagged not set
    0 — flags raised but --allow-flagged was set (prints warning, continues)
"""

import argparse
import base64
import json
import re
import sys
import unicodedata
from pathlib import Path


# ── Instruction-injection patterns ────────────────────────────────────────────

INSTRUCTION_PATTERNS = [
    # Direct model-control phrases
    r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"forget\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"override\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"you\s+are\s+now\s+(a\s+)?",
    r"pretend\s+(you\s+are|to\s+be)",
    r"as\s+an?\s+ai\s+",
    r"your\s+(new\s+)?instructions?\s+(are|is)\s*:",
    r"system\s+prompt",
    r"from\s+now\s+on\s+(you\s+)?",
    # Severity manipulation
    r"(rate|mark|classify|label)\s+(this|all|every)\s+(finding|vulnerability|issue|bug)",
    r"severity\s*(=|:)\s*(low|info|informational|none)",
    r"(this\s+is\s+not?\s+a|no)\s+(bug|vulnerability|finding|issue)",
    # NB: require an explicit noun ("safe code/function/contract" or "safe to ignore"). The earlier
    # `(safe|harmless|benign)\s*(code|function|contract)?` matched bare "safe mode", "unsafe", and
    # "Safe cast" in ordinary NatSpec (the Panoptic false positives) — that is too broad to be a signal.
    r"\b(safe|harmless|benign)\s+(to\s+ignore|code|function|contract)\b",
    # Role reassignment
    r"you\s+are\s+a\s+(senior\s+)?developer",
    r"act\s+as\s+(a\s+)?(developer|owner|admin)",
    r"do\s+not\s+(report|flag|include|mention)",
]

INSTRUCTION_RE = [re.compile(p, re.IGNORECASE) for p in INSTRUCTION_PATTERNS]

# Self-referential strings
SELF_REF_PATTERNS = [
    r"\bclaude\b",
    r"\banthropic\b",
    r"\bassistant\b",
    r"system\s+prompt",
    r"language\s+model",
    r"\bllm\b",
    r"gpt[-\s]?\d",
]
SELF_REF_RE = [re.compile(p, re.IGNORECASE) for p in SELF_REF_PATTERNS]

# Homoglyph detection: common Cyrillic/Greek characters that look like ASCII
HOMOGLYPH_MAP = {
    "а": "a",  # Cyrillic а
    "е": "e",  # Cyrillic е
    "о": "o",  # Cyrillic о
    "р": "r",  # Cyrillic р
    "с": "c",  # Cyrillic с
    "х": "x",  # Cyrillic х
    "р": "p",  # Cyrillic р
    "α": "a",  # Greek α
    "ε": "e",  # Greek ε
    "ο": "o",  # Greek ο
    "ρ": "p",  # Greek ρ
    "₀": "0",  # Subscript 0
    "ｏ": "o",  # Fullwidth o
    "ａ": "a",  # Fullwidth a
}

BASE64_PATTERN = re.compile(r"[A-Za-z0-9+/]{60,}={0,2}")


def _extract_comments(source: str) -> list[tuple[int, str]]:
    """Extract (line_number, comment_text) pairs from Solidity source."""
    comments = []
    lines = source.split("\n")

    in_block = False
    block_start = 0
    block_buf = []

    for i, line in enumerate(lines, 1):
        if in_block:
            end = line.find("*/")
            if end != -1:
                block_buf.append(line[:end])
                comments.append((block_start, " ".join(block_buf)))
                in_block = False
                block_buf = []
                # remainder of line after */ is code, check for //
                remainder = line[end + 2:]
                sl = remainder.find("//")
                if sl != -1:
                    comments.append((i, remainder[sl + 2:].strip()))
            else:
                block_buf.append(line.strip())
        else:
            # Check for block comment start
            bs = line.find("/*")
            sl = line.find("//")
            if bs != -1 and (sl == -1 or bs < sl):
                end = line.find("*/", bs + 2)
                if end != -1:
                    comments.append((i, line[bs + 2:end]))
                else:
                    in_block = True
                    block_start = i
                    block_buf = [line[bs + 2:].strip()]
            elif sl != -1:
                comments.append((i, line[sl + 2:].strip()))

    return comments


def _extract_strings(source: str) -> list[tuple[int, str]]:
    """Extract string literals from Solidity source."""
    strings = []
    pattern = re.compile(r'"([^"\\]|\\.)*"', re.DOTALL)
    for m in pattern.finditer(source):
        line_num = source[:m.start()].count("\n") + 1
        strings.append((line_num, m.group(0)[1:-1]))
    return strings


def _strip_comments_preserve_lines(source: str) -> str:
    """Replace comment content with spaces while preserving line numbers/length. Used so homoglyph
    detection runs on CODE (and string) text only — a `log₂(x)` subscript or √ in a NatSpec formula is
    not an identifier-confusion attack, whereas a Cyrillic `а` in an identifier still is."""
    out = []
    i, n = 0, len(source)
    in_line = in_block = False
    in_str: str | None = None
    while i < n:
        c = source[i]
        two = source[i:i + 2]
        if in_line:
            out.append("\n" if c == "\n" else " ")
            if c == "\n":
                in_line = False
            i += 1; continue
        if in_block:
            if two == "*/":
                out.append("  "); i += 2; in_block = False; continue
            out.append("\n" if c == "\n" else " "); i += 1; continue
        if in_str is not None:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(source[i + 1]); i += 2; continue
            if c == in_str:
                in_str = None
            i += 1; continue
        if c in ('"', "'"):
            in_str = c; out.append(c); i += 1; continue
        if two == "//":
            in_line = True; out.append("  "); i += 2; continue
        if two == "/*":
            in_block = True; out.append("  "); i += 2; continue
        out.append(c); i += 1
    return "".join(out)


def _check_homoglyphs(source: str, file_path: str) -> list[dict]:
    flags = []
    code_only = _strip_comments_preserve_lines(source)
    for i, line in enumerate(code_only.split("\n"), 1):
        for char in line:
            if char in HOMOGLYPH_MAP and unicodedata.category(char) not in ("Ll", "Lu", "Lt"):
                flags.append({
                    "type": "homoglyph",
                    "file": file_path,
                    "line": i,
                    "in_comment": False,
                    "snippet": f"Character U+{ord(char):04X} ({char!r}) resembles ASCII '{HOMOGLYPH_MAP[char]}'",
                })
    return flags


def _check_instructions(comments: list[tuple[int, str]], file_path: str) -> list[dict]:
    flags = []
    for line_num, text in comments:
        for pattern in INSTRUCTION_RE:
            if pattern.search(text):
                flags.append({
                    "type": "instruction_comment",
                    "file": file_path,
                    "line": line_num,
                    "in_comment": True,
                    "snippet": text[:200],
                    "pattern": pattern.pattern,
                })
                break
    return flags


def _check_self_references(comments: list[tuple[int, str]], strings: list[tuple[int, str]], file_path: str) -> list[dict]:
    flags = []
    for line_num, text in comments + strings:
        for pattern in SELF_REF_RE:
            if pattern.search(text):
                flags.append({
                    "type": "self_reference",
                    "file": file_path,
                    "line": line_num,
                    "in_comment": True,
                    "snippet": text[:200],
                })
                break
    return flags


def _check_suspicious_natspec(comments: list[tuple[int, str]], file_path: str) -> list[dict]:
    flags = []
    for line_num, text in comments:
        if text.lstrip().startswith("@") and len(text) > 500:
            flags.append({
                "type": "oversized_natspec",
                "file": file_path,
                "line": line_num,
                "in_comment": True,
                "snippet": text[:200] + "…",
                "length": len(text),
            })
    return flags


def _check_base64(comments: list[tuple[int, str]], file_path: str) -> list[dict]:
    flags = []
    for line_num, text in comments:
        for m in BASE64_PATTERN.finditer(text):
            blob = m.group(0)
            # Skip decoration banners: a 60+ run that is one or two distinct chars (e.g. `//////////`,
            # `==========`, `**********`) is a comment divider, not a payload. Real base64 is high-entropy.
            if len(set(blob.rstrip("="))) <= 2:
                continue
            # Skip pure-hex literals (optionally 0x-prefixed): a 60+ hex run in a comment is a bytes/hash
            # constant, not a base64 injection payload (which would use the full a-zA-Z0-9+/ alphabet).
            hexbody = blob[2:] if blob[:2].lower() == "0x" else blob
            if hexbody and all(c in "0123456789abcdefABCDEF" for c in hexbody):
                continue
            try:
                decoded = base64.b64decode(blob + "==").decode("utf-8", errors="replace")
                # Only flag if decoded output looks like text (not binary)
                printable = sum(1 for c in decoded if c.isprintable())
                if printable / max(len(decoded), 1) > 0.8:
                    flags.append({
                        "type": "embedded_base64",
                        "file": file_path,
                        "line": line_num,
                        "in_comment": True,
                        "snippet": blob[:80] + "…",
                        "decoded_preview": decoded[:200],
                    })
            except Exception:
                pass
    return flags


def scan_file(sol_file: Path) -> list[dict]:
    """Scan one Solidity file and return a list of flags."""
    try:
        source = sol_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [{"type": "read_error", "file": str(sol_file), "error": str(e)}]

    file_path = str(sol_file)
    comments = _extract_comments(source)
    strings = _extract_strings(source)

    flags = []
    flags.extend(_check_instructions(comments, file_path))
    flags.extend(_check_self_references(comments, strings, file_path))
    flags.extend(_check_suspicious_natspec(comments, file_path))
    flags.extend(_check_base64(comments, file_path))
    flags.extend(_check_homoglyphs(source, file_path))

    return flags


def scan_path(target: Path) -> dict:
    """Scan a file or directory tree and return the aggregated result.

    Covers Solidity (.sol) and the cross-language source extensions the pipeline now supports — Rust (.rs),
    Move (.move), Vyper (.vy), and TON/FunC (.fc/.func/.tolk). The prompt-injection regexes are language-agnostic
    (they scan comments/strings/text), so the only change needed per language is recognizing its file extension.
    """
    src_exts = (".sol", ".rs", ".move", ".vy", ".fc", ".func", ".tolk")
    if target.is_file():
        sol_files = [target] if target.suffix in src_exts else []
    elif target.is_dir():
        sol_files = [p for p in target.rglob("*") if p.is_file() and p.suffix in src_exts]
    else:
        return {"error": f"Path does not exist: {target}"}

    all_flags = []
    for f in sol_files:
        all_flags.extend(scan_file(f))

    return {
        "clean": len(all_flags) == 0,
        "files_scanned": len(sol_files),
        "flags_found": len(all_flags),
        "flags": all_flags,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Zero-trust prompt injection scanner for Solidity source code"
    )
    parser.add_argument("target", help="Contract file or directory to scan")
    parser.add_argument(
        "--allow-flagged",
        action="store_true",
        help="Print warnings but exit 0 even if flags are raised",
    )
    parser.add_argument("--json", dest="json_output", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = scan_path(Path(args.target))

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        if result.get("clean"):
            print(f"✓ sandbox_check: {result['files_scanned']} file(s) scanned — CLEAN")
        else:
            print(f"⚠ sandbox_check: {result['flags_found']} flag(s) found in {result['files_scanned']} file(s)")
            for flag in result["flags"]:
                print(f"  [{flag['type'].upper()}] {flag['file']}:{flag.get('line', '?')}")
                print(f"    {flag.get('snippet', flag.get('error', ''))[:120]}")
            print()
            print("NOTE: These flags may indicate prompt injection attempts in contract source.")
            print("      Do NOT allow contract comments to alter audit methodology or severity decisions.")
            if not args.allow_flagged:
                print("      Use --allow-flagged to proceed anyway.")

    if not result.get("clean") and not args.allow_flagged:
        sys.exit(1)


if __name__ == "__main__":
    main()
