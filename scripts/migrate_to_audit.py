#!/usr/bin/env python3
"""
migrate_to_audit.py — One-time migration of flat K2 data into audits/k2-kinetic-2026-04/.

Copies:
  data/    -> audits/k2-kinetic-2026-04/data/
  output/  -> audits/k2-kinetic-2026-04/output/
  pocs/    -> audits/k2-kinetic-2026-04/pocs/
  reports/ -> audits/k2-kinetic-2026-04/reports/

Then sets k2-kinetic-2026-04 as the active audit.
Original data is preserved at the flat paths — delete manually after verifying.

Usage:
  python scripts/migrate_to_audit.py             # migrate (skips if workspace exists)
  python scripts/migrate_to_audit.py --dry-run   # print what would happen
  python scripts/migrate_to_audit.py --force     # overwrite existing workspace
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import (
    _PROJECT_ROOT, _AUDITS_DIR,
    create_audit_workspace, switch_audit, update_registry_stats,
)

AUDIT_ID = "k2-kinetic-2026-04"

K2_META = {
    "name":          "K2 Kinetic",
    "contest":       "k2-code4rena-2026-04",
    "platform":      "code4rena",
    "language":      "rust",
    "framework":     "soroban",
    "contract_path": "contracts/2026-04-k2",
    "status":        "active",
    "start_date":    "2026-04-01T00:00:00+00:00",
    "deadline":      "2026-05-27T23:59:00Z",
}

COPY_MAP = [
    ("data",    "data"),
    ("output",  "output"),
    ("pocs",    "pocs"),
    ("reports", "reports"),
]


def _count_files(path: Path) -> int:
    return sum(1 for _ in path.rglob("*") if _.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate K2 flat data to audit workspace")
    parser.add_argument("--dry-run", action="store_true", help="Print actions, make no changes")
    parser.add_argument("--force",   action="store_true", help="Overwrite existing workspace")
    args = parser.parse_args()

    dest_root = _AUDITS_DIR / AUDIT_ID

    if dest_root.exists() and not args.force:
        print(f"[skip] Workspace already exists: {dest_root}")
        print("       Switching active audit without re-copying data.")
        if not args.dry_run:
            switch_audit(AUDIT_ID)
            update_registry_stats()
            print(f"[ok]   Active audit set to {AUDIT_ID}")
        return 0

    if args.dry_run:
        print(f"[dry-run] Would create workspace: {dest_root}")
        for src_name, dst_name in COPY_MAP:
            src = _PROJECT_ROOT / src_name
            if src.exists():
                count = _count_files(src)
                print(f"[dry-run]   Copy {src_name}/ ({count} files) -> {dst_name}/")
            else:
                print(f"[dry-run]   Skip {src_name}/ (not found)")
        print(f"[dry-run] Would write meta.json and update registry")
        print(f"[dry-run] Would set active audit to {AUDIT_ID}")
        return 0

    if args.force and dest_root.exists():
        print(f"[warn] Removing existing workspace: {dest_root}")
        shutil.rmtree(dest_root)

    print(f"Creating audit workspace: {dest_root}")
    create_audit_workspace(AUDIT_ID, K2_META)

    total_copied = 0
    for src_name, dst_name in COPY_MAP:
        src = _PROJECT_ROOT / src_name
        dst = dest_root / dst_name
        if not src.exists():
            print(f"  [skip] {src_name}/ does not exist")
            continue
        # create_audit_workspace already created empty dest dirs — remove them first
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        src_count = _count_files(src)
        dst_count = _count_files(dst)
        status = "OK" if src_count == dst_count else f"MISMATCH src={src_count} dst={dst_count}"
        print(f"  Copied {src_name}/ -> {dst_name}/ ({dst_count} files) [{status}]")
        total_copied += dst_count

    switch_audit(AUDIT_ID)
    update_registry_stats()

    print(f"\n[ok] Migration complete — {total_copied} files total")
    print(f"     Active audit: {AUDIT_ID}")
    print(f"     Workspace: {dest_root}")
    print(f"\nOriginal data preserved at output/, data/, pocs/, reports/")
    print("Delete them manually once you have verified the migration.")
    print("\nVerify with: python scripts/audit_manager.py info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
