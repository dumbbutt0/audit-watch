#!/usr/bin/env python3
"""
generate_scope_inventory.py — Produce output/scope_inventory.md for the active audit.

Lists every .sol (or .rs for Soroban) file in scope with its line count
and any imports that resolve outside the directory (flagged as external deps).

Run at Step 0, before sandbox_check.py.

Usage:
    python scripts/generate_scope_inventory.py --contract contracts/Vault.sol
    python scripts/generate_scope_inventory.py --contract contracts/
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, write_session

# Patterns that indicate an external (off-scope) import
EXCLUDED_DIRS = {
    "node_modules", ".git", "lib", "out", "cache",
    "artifacts", "build", "dist", ".venv", "target",
}

EXTERNAL_IMPORT_PATTERNS = [
    re.compile(r'import\s+["\'](@\w+/[^"\']+)["\']'),       # npm scoped (@openzeppelin/...)
    re.compile(r'import\s+["\']([^.][^"\']*)["\']'),         # bare name (foundry-std, etc.)
    re.compile(r'import\s+\{[^}]+\}\s+from\s+["\'](@[^"\']+)["\']'),
    re.compile(r'import\s+\{[^}]+\}\s+from\s+["\']([^./][^"\']+)["\']'),
    re.compile(r'use\s+([\w:]+)::\{'),                        # Rust extern crate-style
]


def _count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.open())
    except OSError:
        return 0


def _extract_external_imports(path: Path) -> list[str]:
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return []
    found: list[str] = []
    for pat in EXTERNAL_IMPORT_PATTERNS:
        for m in pat.finditer(text):
            dep = m.group(1)
            if dep not in found:
                found.append(dep)
    return found


def _collect_files(contract_path: Path) -> list[Path]:
    exts = {".sol", ".rs"}
    if contract_path.is_file():
        return [contract_path] if contract_path.suffix in exts else []
    result: list[Path] = []
    for p in contract_path.rglob("*"):
        if p.suffix not in exts:
            continue
        if any(part in EXCLUDED_DIRS for part in p.parts):
            continue
        result.append(p)
    return sorted(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate scope inventory for active audit")
    parser.add_argument("--contract", required=True, help="Contract file or directory")
    args = parser.parse_args()

    contract_path = Path(args.contract).resolve()
    if not contract_path.exists():
        print(f"[error] Path not found: {contract_path}")
        sys.exit(1)

    files = _collect_files(contract_path)
    if not files:
        print(f"[warn] No .sol or .rs files found under: {contract_path}")

    rows: list[tuple[str, int, str]] = []
    total_loc = 0
    for f in files:
        loc = _count_lines(f)
        total_loc += loc
        ext_deps = _extract_external_imports(f)
        dep_str = ", ".join(ext_deps) if ext_deps else ""
        try:
            rel = f.relative_to(contract_path.parent if contract_path.is_file() else contract_path)
        except ValueError:
            rel = f
        rows.append((str(rel), loc, dep_str))

    lines: list[str] = [
        "# Scope Inventory",
        "",
        f"Contract path: `{args.contract}`",
        f"Files: {len(files)}  |  Total LOC: {total_loc:,}",
        "",
        "| File | LOC | External Imports |",
        "|---|---|---|",
    ]
    for rel, loc, deps in rows:
        dep_col = f"⚠️ {deps}" if deps else "—"
        lines.append(f"| `{rel}` | {loc:,} | {dep_col} |")

    lines += [
        "",
        f"**Total LOC: {total_loc:,}**",
        "",
        "> ⚠️ = imports that resolve outside the scope directory (external dependency)",
    ]

    out_path = audit_path("output", "scope_inventory.md")
    out_path.write_text("\n".join(lines))
    write_session({"scope_files": [str(r[0]) for r in rows]})
    print(f"Scope inventory written ({len(files)} files, {total_loc:,} LOC): {out_path}")


if __name__ == "__main__":
    main()
