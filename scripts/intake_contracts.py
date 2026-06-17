#!/usr/bin/env python3
"""
intake_contracts.py — Associate downloaded contract source with an audit workspace.

Copies one or more downloaded directories into the active (or named) audit workspace,
selects ONE primary contract directory for the main pipeline run, and records the
association in meta.json (primary_contract_dir). Extra sources go to contracts/_sources/.

GUARDRAIL: never overwrites. If audits/<id>/contracts/ already has content, the script
errors and requires --replace-primary, which first moves the existing contracts/ aside to
contracts/_backup_<UTC>/. No silent delete/overwrite, ever.

Usage:
    python scripts/intake_contracts.py <dir> [<dir> ...]
    python scripts/intake_contracts.py <dir> --audit-id xterio-2026-05
    python scripts/intake_contracts.py <dir> --primary <subdir-name>
    python scripts/intake_contracts.py <dir> --replace-primary
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import _AUDITS_DIR, get_active_audit, set_primary_contract_dir

SOL_EXTS = {".sol", ".rs", ".vy", ".cairo", ".clar"}
PRIMARY_MARKERS = {"foundry.toml", "hardhat.config.js", "hardhat.config.ts", "Cargo.toml", "src"}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _score_dir(d: Path) -> tuple[int, int]:
    """Rank a candidate primary dir: (#marker hits, #contract files)."""
    if not d.is_dir():
        return (0, 0)
    markers = sum(1 for m in PRIMARY_MARKERS if (d / m).exists())
    files = sum(1 for p in d.rglob("*") if p.is_file() and p.suffix in SOL_EXTS)
    return (markers, files)


def _pick_primary(sources: list[Path], override: str | None) -> Path:
    if override:
        match = [s for s in sources if s.name == override]
        if not match:
            raise SystemExit(f"[error] --primary '{override}' not among sources: "
                             f"{[s.name for s in sources]}")
        return match[0]
    # rank by (markers, contract-file count); ties broken by file count
    ranked = sorted(sources, key=lambda s: _score_dir(s), reverse=True)
    return ranked[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Associate downloaded source with an audit")
    ap.add_argument("sources", nargs="+", help="Downloaded contract dir(s) to import")
    ap.add_argument("--audit-id", default=None, help="Target audit (default: active)")
    ap.add_argument("--primary", default=None, help="Force a source dir name as primary")
    ap.add_argument("--replace-primary", action="store_true",
                    help="Allow replacing a non-empty contracts/ (backs up the old one first)")
    args = ap.parse_args()

    audit_id = args.audit_id or get_active_audit().get("audit_id")
    if not audit_id:
        raise SystemExit("[error] No active audit. Run: python scripts/audit_manager.py switch <id>")

    root = _AUDITS_DIR / audit_id
    if not (root / "meta.json").exists():
        raise SystemExit(f"[error] Workspace not found for '{audit_id}'")

    sources = [Path(s).resolve() for s in args.sources]
    for s in sources:
        if not s.is_dir():
            raise SystemExit(f"[error] Source is not a directory: {s}")

    contracts_dir = root / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    # GUARDRAIL 5: refuse to clobber existing primary content.
    existing = [p for p in contracts_dir.iterdir() if p.name != "_sources"
                and not p.name.startswith("_backup_")]
    if existing and not args.replace_primary:
        raise SystemExit(
            f"[error] {contracts_dir} already has content: {[p.name for p in existing]}\n"
            f"        Re-run with --replace-primary to back it up and replace it.")
    if existing and args.replace_primary:
        backup = contracts_dir / f"_backup_{_utc()}"
        backup.mkdir()
        for p in existing:
            shutil.move(str(p), str(backup / p.name))
        print(f"[ok] Backed up existing primary content → {backup}")

    primary = _pick_primary(sources, args.primary)
    print(f"[ok] Primary source: {primary.name}  (score={_score_dir(primary)})")

    # Copy primary directly under contracts/<name>; others under contracts/_sources/<name>.
    sources_dir = contracts_dir / "_sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    primary_dest = contracts_dir / primary.name
    shutil.copytree(primary, primary_dest, dirs_exist_ok=False)
    rel_primary = f"contracts/{primary.name}"

    for s in sources:
        if s == primary:
            continue
        dest = sources_dir / s.name
        if dest.exists():
            print(f"[skip] _sources/{s.name} already present")
            continue
        shutil.copytree(s, dest, dirs_exist_ok=False)
        print(f"[ok] Imported secondary source → contracts/_sources/{s.name}")

    set_primary_contract_dir(rel_primary)
    print(f"[ok] meta.primary_contract_dir = {rel_primary}")
    print(f"[ok] Intake complete for {audit_id}.")
    print(f"     Next: python scripts/generate_contract_context.py --audit-id {audit_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
