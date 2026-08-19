"""Recursive, offline file walker.

Yields (relative_path, text) for every readable text file under a root, skipping
vendored/build dirs, oversized files, and binaries. Reading a file is the only
filesystem interaction — nothing is executed.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

# Directories that are dependency/build output or VCS internals — not the author's code.
SKIP_DIRS = {
    ".git", ".hg", ".svn",
    "node_modules", "bower_components",
    "out", "dist", "build", "target", "cache", "cache-foundry",
    "lib", "vendor",  # forge libs / vendored deps
    "venv", ".venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode",
}

# Read everything by default; only skip clearly-binary extensions for speed.
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".pdf", ".zip", ".gz",
    ".tar", ".tgz", ".bz2", ".7z", ".rar", ".jar", ".wasm", ".so", ".dylib",
    ".dll", ".exe", ".bin", ".class", ".o", ".a", ".pyc", ".woff", ".woff2",
    ".ttf", ".eot", ".mp4", ".mov", ".mp3", ".node",
}

MAX_BYTES = 2 * 1024 * 1024  # 2 MB per file


def _looks_binary(blob: bytes) -> bool:
    return b"\x00" in blob[:4096]


def iter_text_files(root: Path, max_bytes: int = MAX_BYTES) -> Iterator[tuple[str, str]]:
    """Walk `root`, yielding (relpath, text) for each readable text file.

    `root` may be a single file or a directory.
    """
    root = root.resolve()
    if root.is_file():
        rel = root.name
        text = _read_text(root, max_bytes)
        if text is not None:
            yield rel, text
        return

    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs in-place so os.walk does not descend into them
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in BINARY_EXT:
                continue
            text = _read_text(p, max_bytes)
            if text is None:
                continue
            yield os.path.relpath(p, root), text


def _read_text(p: Path, max_bytes: int) -> str | None:
    try:
        if p.stat().st_size > max_bytes:
            return None
        blob = p.read_bytes()
    except (OSError, ValueError):
        return None
    if _looks_binary(blob):
        return None
    return blob.decode("utf-8", errors="replace")
