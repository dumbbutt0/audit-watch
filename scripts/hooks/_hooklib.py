#!/usr/bin/env python3
"""
_hooklib.py — Tiny shared helpers for Audit-Watch Claude Code hooks.

Hooks follow the Claude Code hook contract:
    - read JSON tool-input from stdin (PreToolUse / PostToolUse / SessionStart / Stop)
    - exit 0  => allow
    - exit 2  => block (stderr is shown to the model)
    - other   => non-blocking error (shown to the user, tool still runs)

Every hook here is ALSO runnable manually (no stdin) so an operator can dry-run it.
Hooks resolve all state through scripts/audit_context.py and only ever write under the
active audit's data/gates/ (plus, for the status hook, documentation/metrics/).

These helpers never touch trusted state (ground_truth.jsonl, shared rejection_rules.jsonl,
duplicate_registry.jsonl, active_audit.json, metrics.json).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _HOOKS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import audit_context as ctx  # noqa: E402

ALLOW = 0
BLOCK = 2  # Claude Code: exit 2 blocks the tool and feeds stderr back to the model.

_OVERRIDE_TRUE = {"1", "true", "yes", "on"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def override_active() -> bool:
    """True when the operator has explicitly opted out of hard-blocks for this session."""
    return os.environ.get("AUDITWATCH_HOOK_OVERRIDE", "").strip().lower() in _OVERRIDE_TRUE


def read_hook_input() -> dict:
    """Parse the Claude Code hook JSON payload from stdin.

    Returns {} when run interactively (no piped stdin) so the script stays usable by hand.
    Never raises — a malformed payload degrades to {}.
    """
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def tool_command(payload: dict) -> str:
    """The Bash command string from a PreToolUse/PostToolUse payload (or '')."""
    return str((payload.get("tool_input") or {}).get("command", "") or "")


def tool_file_path(payload: dict) -> str:
    """The file_path from a Read/Edit payload (or '')."""
    return str((payload.get("tool_input") or {}).get("file_path", "") or "")


_FINDING_ID_RE = re.compile(r"--finding[-_]id[ =]+([A-Za-z][A-Za-z0-9_-]*\d{1,3}|CHAIN-[A-Za-z0-9]+)")
_BARE_ID_RE = re.compile(r"\b([A-Z]{1,6}-\d{2,3}|CHAIN-[A-Za-z0-9]+)\b")


def finding_id_from(payload: dict, cli_id: str | None = None) -> str | None:
    """Best-effort finding id: explicit CLI arg wins, else parse the hooked command."""
    if cli_id:
        return cli_id
    cmd = tool_command(payload)
    m = _FINDING_ID_RE.search(cmd)
    if m:
        return m.group(1)
    m = _BARE_ID_RE.search(cmd)
    return m.group(1) if m else None


def active_audit_id() -> str | None:
    try:
        return ctx.get_active_audit().get("audit_id")
    except Exception:
        return None


def audit_file(*parts: str) -> Path | None:
    """Resolve a path inside the active audit WITHOUT creating dirs (read-safe).

    Returns None when there is no active audit.
    """
    aid = active_audit_id()
    if not aid:
        return None
    return ctx._AUDITS_DIR / aid / Path(*parts)


def write_gate_artifact(rel_parts, obj: dict, dry_run: bool = False) -> Path | None:
    """Write a small JSON artifact under the active audit's data/gates/. No-op without an audit.

    On dry-run, returns the intended path without writing.
    """
    aid = active_audit_id()
    if not aid:
        return None
    path = ctx._AUDITS_DIR / aid / "data" / "gates" / Path(*rel_parts)
    if dry_run:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))
    return path


def load_jsonl(path: Path | None) -> list[dict]:
    if path is None:
        return []
    return ctx.load_jsonl(path)


def ids_in_jsonl(path: Path | None, key: str = "finding_id") -> set[str]:
    return {r.get(key) for r in load_jsonl(path) if r.get(key)}


def merged_findings_index() -> dict[str, dict]:
    """id -> finding dict from the active audit's output/merged_findings.json ('id' key)."""
    p = audit_file("output", "merged_findings.json")
    if p is None or not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    rows = data.get("findings", data if isinstance(data, list) else []) or []
    out = {}
    for f in rows:
        fid = f.get("id") or f.get("finding_id")
        if fid:
            out[fid] = f
    return out


def emit_block(reason: str) -> int:
    """Print a block reason to stderr and return the BLOCK exit code."""
    print(f"[audit-watch hook] BLOCK: {reason}", file=sys.stderr)
    print("  Set AUDITWATCH_HOOK_OVERRIDE=1 to bypass if this is a deliberate exception.",
          file=sys.stderr)
    return BLOCK


def emit_warn(message: str) -> int:
    """Print a non-blocking warning to stderr and return ALLOW."""
    print(f"[audit-watch hook] {message}", file=sys.stderr)
    return ALLOW
