"""Shared detector helpers: rule loading, comment/string extraction, line lookup.

The comment/string extractors are generalized (clean-room) ports of the
defensive parsing approach used in audit-style sandbox checks — they isolate the
*prose* and *string* surfaces of a source file, which is where injection text
hides, so detectors do not fire on ordinary code identifiers.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"

# Extensions whose ENTIRE content is prose (scan all of it for injection).
DOC_EXT = {".md", ".markdown", ".mdx", ".rst", ".txt", ".adoc"}

# C-style comment languages (// and /* */) and string literals.
CSTYLE_EXT = {
    ".sol", ".js", ".ts", ".jsx", ".tsx", ".c", ".h", ".cpp", ".hpp", ".cc",
    ".go", ".rs", ".java", ".kt", ".swift", ".scala", ".php", ".cs",
}
# Hash-comment languages (#).
HASH_EXT = {".py", ".rb", ".sh", ".bash", ".zsh", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".pl"}

# Config/script files that lifecycle detection cares about (by basename or suffix).
CONFIG_BASENAMES = {
    "package.json", "foundry.toml", "Makefile", "makefile", "justfile",
    "hardhat.config.js", "hardhat.config.ts", "truffle-config.js",
    "setup.py", "pyproject.toml", "Cargo.toml", "pnpm-workspace.yaml",
    ".npmrc", "Dockerfile",
}
SCRIPT_EXT = {".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"}


@lru_cache(maxsize=None)
def load_rules(name: str) -> dict:
    """Load rules/<name>.yml (cached). Returns {} if missing."""
    path = RULES_DIR / f"{name}.yml"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def compile_patterns(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def line_of(text: str, index: int) -> int:
    """1-based line number for a character offset."""
    return text.count("\n", 0, index) + 1


def ext(path: str) -> str:
    return Path(path).suffix.lower()


def basename(path: str) -> str:
    return Path(path).name


def is_doc(path: str) -> bool:
    return ext(path) in DOC_EXT


def is_config_or_script(path: str) -> bool:
    return (
        basename(path) in CONFIG_BASENAMES
        or ext(path) in SCRIPT_EXT
        or basename(path).startswith("Dockerfile")
    )


def is_script(path: str) -> bool:
    return ext(path) in SCRIPT_EXT or basename(path).startswith("Dockerfile")


def is_code(path: str) -> bool:
    return ext(path) in CSTYLE_EXT | HASH_EXT


def is_workflow(path: str) -> bool:
    """A GitHub Actions workflow file (.github/workflows/*.yml|yaml)."""
    norm = path.replace("\\", "/")
    return (".github/workflows/" in f"/{norm}".lower()) and ext(path) in (".yml", ".yaml")


def is_test_file(path: str) -> bool:
    """Heuristic: build/test paths an auditor executes (not general app source)."""
    norm = path.replace("\\", "/").lower()
    bn = basename(norm)
    parts = norm.split("/")
    if any(seg in ("test", "tests", "spec", "specs", "__tests__", "integration", "e2e") for seg in parts):
        return True
    return (
        bn.startswith("test_")
        or bn.startswith("conftest")
        or ".test." in bn
        or ".spec." in bn
        or bn.endswith("_test.go")
        or bn.endswith(".t.sol")
    )


def prose_segments(path: str, text: str) -> list[tuple[int, str]]:
    """Return (line, text) prose segments to scan for injection.

    For doc files: the whole file as line-anchored chunks. For code files:
    comments + string literals. For anything else: the whole file (cheap, and
    injection in a plain config string still matters).
    """
    e = ext(path)
    if e in DOC_EXT:
        return [(i, ln) for i, ln in enumerate(text.split("\n"), 1) if ln.strip()]
    if e in CSTYLE_EXT:
        return extract_cstyle_comments(text) + extract_string_literals(text)
    if e in HASH_EXT:
        return extract_hash_comments(text) + extract_string_literals(text)
    # Unknown/data files (.json, .lock, .map, minified, etc.) have no defined comment
    # surface; scanning them whole-file is too false-positive-prone (lockfile integrity
    # hashes look like base64 payloads). Skip — injection hides in docs/comments/strings.
    return []


def extract_cstyle_comments(source: str) -> list[tuple[int, str]]:
    """Extract (line, text) for // and /* */ comments. Line-aware block handling."""
    comments: list[tuple[int, str]] = []
    lines = source.split("\n")
    in_block = False
    block_start = 0
    buf: list[str] = []
    for i, line in enumerate(lines, 1):
        if in_block:
            end = line.find("*/")
            if end != -1:
                buf.append(line[:end])
                comments.append((block_start, " ".join(buf)))
                in_block = False
                buf = []
                remainder = line[end + 2:]
                sl = remainder.find("//")
                if sl != -1:
                    comments.append((i, remainder[sl + 2:].strip()))
            else:
                buf.append(line.strip())
        else:
            bs = line.find("/*")
            sl = line.find("//")
            if bs != -1 and (sl == -1 or bs < sl):
                end = line.find("*/", bs + 2)
                if end != -1:
                    comments.append((i, line[bs + 2:end]))
                else:
                    in_block = True
                    block_start = i
                    buf = [line[bs + 2:].strip()]
            elif sl != -1:
                comments.append((i, line[sl + 2:].strip()))
    if in_block and buf:
        comments.append((block_start, " ".join(buf)))
    return comments


def extract_hash_comments(source: str) -> list[tuple[int, str]]:
    """Extract (line, text) for # line comments (ignores shebangs)."""
    out: list[tuple[int, str]] = []
    for i, line in enumerate(source.split("\n"), 1):
        if i == 1 and line.startswith("#!"):
            continue
        h = line.find("#")
        if h != -1:
            out.append((i, line[h + 1:].strip()))
    return out


_STRING_RE = re.compile(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'', re.DOTALL)


def extract_string_literals(source: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for m in _STRING_RE.finditer(source):
        body = m.group(0)[1:-1]
        if body.strip():
            out.append((line_of(source, m.start()), body))
    return out
