#!/usr/bin/env python3
"""
migrate_workspace_layout.py — Add the 2026-05 human-facing dirs to every audit workspace.

ADDITIVE ONLY. This script mkdir's the new directories and COPIES substrate artifacts into
human-facing views. It never moves, deletes, or rewrites anything under output/, data/, or
meta.json. Two-phase by design:

    python scripts/migrate_workspace_layout.py --dry-run   # writes a report, changes nothing
    python scripts/migrate_workspace_layout.py --apply     # performs the additive migration

The dry-run report is written to documentation/refinement/migration_dryrun.md. Review it and
confirm (a) meta.json preserved, (b) output/+data/ untouched, (c) output/ symlink resolves,
(d) active-audit selection works — THEN run --apply.

New dirs per workspace: contracts/, contracts/_sources/, notes/, findings/raw/,
findings/validated/, status/.

Sync (copy substrate → human-facing view):
    output/findings_*.json   -> findings/raw/
    data/triage/<id>.md      -> findings/validated/
    output/status.json       -> status/status.json
    session.json             -> status/session.json
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import (
    _AUDITS_DIR,
    _PROJECT_ROOT,
    get_active_audit,
    list_audits,
)

NEW_DIRS = [
    "contracts",
    "contracts/_sources",
    "notes",
    "findings/raw",
    "findings/validated",
    "status",
]

REPORT_PATH = _PROJECT_ROOT / "documentation" / "refinement" / "migration_dryrun.md"

# Substrate paths that must NEVER be modified by this script.
PROTECTED = ["output", "data", "meta.json"]


def _audit_ids() -> list[str]:
    ids = [a["audit_id"] for a in list_audits()]
    # also include any workspace dirs not in registry, to be safe
    if _AUDITS_DIR.exists():
        for p in sorted(_AUDITS_DIR.iterdir()):
            if p.is_dir() and p.name not in ids and (p / "meta.json").exists():
                ids.append(p.name)
    return ids


def _plan_for(audit_id: str) -> dict:
    """Compute (but do not perform) the additive actions for one workspace."""
    root = _AUDITS_DIR / audit_id
    dirs_to_create = [d for d in NEW_DIRS if not (root / d).is_dir()]

    raw_src = sorted((root / "output").glob("findings_*.json")) if (root / "output").is_dir() else []
    triage_src = sorted((root / "data" / "triage").glob("*.md")) if (root / "data" / "triage").is_dir() else []
    status_src = []
    if (root / "output" / "status.json").exists():
        status_src.append(root / "output" / "status.json")
    if (root / "session.json").exists():
        status_src.append(root / "session.json")

    return {
        "audit_id": audit_id,
        "root": root,
        "dirs_to_create": dirs_to_create,
        "raw_files": raw_src,
        "triage_files": triage_src,
        "status_files": status_src,
    }


def _copy_into(src: Path, dest_dir: Path, apply: bool) -> None:
    dest = dest_dir / src.name
    if apply:
        dest_dir.mkdir(parents=True, exist_ok=True)
        # copy2 preserves mtime on the COPY; source is only read.
        shutil.copy2(src, dest)


def run(apply: bool) -> int:
    plans = [_plan_for(aid) for aid in _audit_ids()]

    # Perform (apply) or just record (dry-run)
    lines: list[str] = []
    lines.append("# Workspace Layout Migration — Dry-Run Report")
    lines.append("")
    lines.append(f"Audits: {len(plans)}  ·  mode: {'APPLY' if apply else 'DRY-RUN'}")
    lines.append("")
    lines.append("**WILL NOT TOUCH:** `output/`, `data/`, `meta.json` in any workspace. "
                 "This migration only creates new directories and COPIES substrate files "
                 "into the new human-facing views (sources are read-only).")
    lines.append("")

    for p in plans:
        aid = p["audit_id"]
        lines.append(f"## {aid}")
        lines.append(f"- dirs to create: {', '.join(p['dirs_to_create']) or '(all present)'}")
        lines.append(f"- findings/raw ← output/findings_*.json: {len(p['raw_files'])} file(s)")
        lines.append(f"- findings/validated ← data/triage/*.md: {len(p['triage_files'])} file(s)")
        lines.append(f"- status/ ← status.json/session.json: {len(p['status_files'])} file(s)")
        lines.append("")

        if apply:
            root = p["root"]
            for d in NEW_DIRS:
                (root / d).mkdir(parents=True, exist_ok=True)
            for f in p["raw_files"]:
                _copy_into(f, root / "findings" / "raw", apply=True)
            for f in p["triage_files"]:
                _copy_into(f, root / "findings" / "validated", apply=True)
            for f in p["status_files"]:
                _copy_into(f, root / "status", apply=True)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n")

    print(f"{'APPLIED' if apply else 'DRY-RUN'} — {len(plans)} workspace(s).")
    print(f"Report: {REPORT_PATH}")
    if not apply:
        print("Review the report, then re-run with --apply.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Additive workspace-layout migration")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="Write report, change nothing")
    g.add_argument("--apply", action="store_true", help="Perform the additive migration")
    args = ap.parse_args()
    return run(apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
