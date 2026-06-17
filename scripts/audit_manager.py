#!/usr/bin/env python3
"""
audit_manager.py — CLI for managing audit workspaces.

Commands:
  list                         list all registered audits
  new <audit_id>               create a new audit workspace (interactive prompts)
  switch <audit_id>            set the active audit
  info [audit_id]              show full metadata + pipeline progress
  status <value>               update status of the active audit
  archive                      shortcut: set status=archived
  delete <audit_id> --confirm  permanently delete a workspace

Usage:
  python scripts/audit_manager.py list
  python scripts/audit_manager.py new aave-v4-2026-06
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/audit_manager.py info
  python scripts/audit_manager.py status submitting
  python scripts/audit_manager.py archive
  python scripts/audit_manager.py delete test-audit --confirm
"""
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import (
    _AUDITS_DIR,
    _read_registry,
    _write_registry,
    create_audit_workspace,
    get_active_audit,
    get_audit_meta,
    list_audits,
    switch_audit,
    update_audit_status,
    update_registry_stats,
)

_STATUS_CHOICES = ["setup", "analyzing", "triaging", "poc_phase",
                   "submitting", "submitted", "complete", "archived"]


def _days_until(iso_str: str) -> int | None:
    if not iso_str:
        return None
    try:
        deadline = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = deadline - datetime.now(timezone.utc)
        return delta.days
    except (ValueError, TypeError):
        return None


def _deadline_str(iso_str: str) -> str:
    if not iso_str:
        return "—"
    days = _days_until(iso_str)
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        date_str = dt.strftime("%b %d %Y")
    except (ValueError, TypeError):
        return iso_str
    if days is None:
        return date_str
    if days < 0:
        return f"{date_str} (PAST)"
    return f"{date_str} ({days} days remaining)"


def _pipeline_progress(audit_root: Path) -> list[tuple[str, bool]]:
    checks = [
        ("Static analysis",    audit_root / "output/static.json"),
        ("Merged findings",    audit_root / "output/merged_findings.json"),
        ("Triage: submit",     audit_root / "data/triage/submit.jsonl"),
        ("Triage: poc_req",    audit_root / "data/triage/poc_required.jsonl"),
        ("PoC queue",          audit_root / "data/poc_queue"),
        ("Exploitability",     audit_root / "data/exploitability/models.jsonl"),
        ("Duplicate risk",     audit_root / "data/duplicates/risk.jsonl"),
        ("Severity",           audit_root / "data/severity/calibrated.jsonl"),
        ("Runtime PoC",        audit_root / "data/runtime_poc/results.jsonl"),
        ("Judge simulation",   audit_root / "data/judge_simulation/results.jsonl"),
        ("Submission pack",    audit_root / "output/submission_pack.md"),
    ]
    result = []
    for label, path in checks:
        if path.is_dir():
            done = any(path.iterdir())
        else:
            done = path.exists() and path.stat().st_size > 0
        result.append((label, done))
    return result


def cmd_list(args) -> int:
    audits = list_audits()
    active = get_active_audit().get("audit_id")
    if not audits:
        print("No audits registered.")
        print("Run: python scripts/audit_manager.py new <audit_id>")
        print("  OR python scripts/migrate_to_audit.py   (first time)")
        return 0
    print(f"\n  {'ID':<32} {'Status':<12} {'Submit':>7} {'PoC':>5}  Name")
    print("  " + "─" * 72)
    for a in audits:
        marker = " ◀ active" if a["audit_id"] == active else ""
        dl = _days_until(a.get("deadline", ""))
        dl_str = f"{dl}d" if dl is not None else "  "
        print(
            f"  {a['audit_id']:<32} {a.get('status','?'):<12} "
            f"{a.get('submit_count', 0):>7} {a.get('poc_count', 0):>5}  "
            f"{a.get('name', '')}{marker}"
        )
    print()
    return 0


def cmd_new(args) -> int:
    def _prompt(label: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        val = input(f"  {label}{suffix}: ").strip()
        return val or default

    print(f"\nCreating new audit: {args.audit_id}")
    meta = {
        "name":          _prompt("Display name", args.audit_id),
        "contest":       _prompt("Contest ID (e.g. k2-code4rena-2026-04)", ""),
        "platform":      _prompt("Platform (Code4rena/Sherlock/Immunefi/Private)", ""),
        "language":      _prompt("Language (Solidity/Rust/Vyper)", "Rust"),
        "framework":     _prompt("Framework (soroban/foundry/hardhat)", "soroban"),
        "contract_path": _prompt("Contract path", ""),
        "deadline":      _prompt("Deadline (YYYY-MM-DD or ISO8601)", ""),
        "start_date":    _prompt("Start date (YYYY-MM-DD)", ""),
        "status":        "active",
    }
    # Normalise deadline to ISO format
    if meta["deadline"] and len(meta["deadline"]) == 10:
        meta["deadline"] = meta["deadline"] + "T23:59:00Z"

    try:
        root = create_audit_workspace(args.audit_id, meta)
    except ValueError as e:
        print(f"\n[error] {e}")
        return 1

    print(f"\n[ok] Created: {root}")

    if not args.no_switch:
        ans = input("Switch to this audit now? [Y/n]: ").strip().lower()
        if ans not in ("n", "no"):
            switch_audit(args.audit_id)
            print(f"[ok] Active audit set to {args.audit_id}")
    return 0


def cmd_switch(args) -> int:
    try:
        switch_audit(args.audit_id)
    except ValueError as e:
        print(f"[error] {e}")
        return 1
    meta = get_audit_meta()
    dl = _deadline_str(meta.get("deadline", ""))
    print(f"Switched to: {meta.get('name', args.audit_id)} ({args.audit_id})")
    print(f"  Contract: {meta.get('contract_path', '—')}")
    print(f"  Deadline: {dl}")
    return 0


def cmd_info(args) -> int:
    target = args.audit_id if hasattr(args, "audit_id") and args.audit_id else get_active_audit().get("audit_id")
    if not target:
        print("[error] No active audit and no audit_id specified.")
        return 1

    meta_path = _AUDITS_DIR / target / "meta.json"
    if not meta_path.exists():
        print(f"[error] No workspace found for '{target}'")
        return 1

    meta = json.loads(meta_path.read_text())
    active = get_active_audit().get("audit_id")

    if target == active:
        update_registry_stats()

    reg = _read_registry()
    reg_entry = next((a for a in reg.get("audits", []) if a["audit_id"] == target), {})

    print(f"\n{'─'*60}")
    print(f"  Audit:     {target}{'  ◀ active' if target == active else ''}")
    print(f"  Name:      {meta.get('name', '—')}")
    print(f"  Contest:   {meta.get('contest', '—')}")
    print(f"  Platform:  {meta.get('platform', '—')}")
    print(f"  Language:  {meta.get('language', '—')} / {meta.get('framework', '—')}")
    print(f"  Contract:  {meta.get('contract_path', '—')}")
    print(f"  Status:    {meta.get('status', '—')}")
    print(f"  Deadline:  {_deadline_str(meta.get('deadline', ''))}")
    print(f"  Submit:    {reg_entry.get('submit_count', 0)}")
    print(f"  PoC:       {reg_entry.get('poc_count', 0)}")
    print(f"  Workspace: {_AUDITS_DIR / target}")
    print(f"\n  Pipeline progress:")
    for label, done in _pipeline_progress(_AUDITS_DIR / target):
        tick = "✓" if done else "·"
        print(f"    {tick}  {label}")
    print()
    return 0


def cmd_status(args) -> int:
    try:
        update_audit_status(args.status_value)
    except RuntimeError as e:
        print(f"[error] {e}")
        return 1
    active = get_active_audit().get("audit_id")
    print(f"Status set to '{args.status_value}' for {active}")
    return 0


def cmd_archive(args) -> int:
    try:
        update_audit_status("archived")
    except RuntimeError as e:
        print(f"[error] {e}")
        return 1
    active = get_active_audit().get("audit_id")
    print(f"Archived: {active}")
    return 0


def cmd_delete(args) -> int:
    if not args.confirm:
        print("[error] Pass --confirm to permanently delete the workspace and all its data.")
        return 1
    target = args.audit_id
    workspace = _AUDITS_DIR / target
    if not workspace.exists():
        print(f"[error] Workspace not found: {workspace}")
        return 1
    active = get_active_audit().get("audit_id")
    if target == active:
        print("[error] Cannot delete the active audit. Switch to another audit first.")
        return 1
    file_count = sum(1 for _ in workspace.rglob("*") if _.is_file())
    shutil.rmtree(workspace)
    reg = _read_registry()
    reg["audits"] = [a for a in reg.get("audits", []) if a["audit_id"] != target]
    _write_registry(reg)
    print(f"Deleted: {workspace} ({file_count} files removed)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage audit workspaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all audits")

    p_new = sub.add_parser("new", help="Create a new audit workspace")
    p_new.add_argument("audit_id", help="Unique slug, e.g. aave-v4-2026-06")
    p_new.add_argument("--no-switch", action="store_true", dest="no_switch",
                       help="Do not prompt to switch after creation")

    p_sw = sub.add_parser("switch", help="Set the active audit")
    p_sw.add_argument("audit_id")

    p_info = sub.add_parser("info", help="Show audit metadata and pipeline progress")
    p_info.add_argument("audit_id", nargs="?", default=None)

    p_st = sub.add_parser("status", help="Update status of the active audit")
    p_st.add_argument("status_value", choices=_STATUS_CHOICES)

    sub.add_parser("archive", help="Set status=archived on the active audit")

    p_del = sub.add_parser("delete", help="Permanently delete a workspace")
    p_del.add_argument("audit_id")
    p_del.add_argument("--confirm", action="store_true",
                       help="Required: confirms permanent deletion")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    dispatch = {
        "list":    cmd_list,
        "new":     cmd_new,
        "switch":  cmd_switch,
        "info":    cmd_info,
        "status":  cmd_status,
        "archive": cmd_archive,
        "delete":  cmd_delete,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
