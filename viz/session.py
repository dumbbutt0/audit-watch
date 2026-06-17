"""
viz/session.py — Audit session ID management for the reasoning visualization layer.

A session ties all VizEvents in one pipeline run together. Session ID is stored
in the VIZ_SESSION_ID environment variable so all pipeline subprocesses share it.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Resolve to project root regardless of cwd
_ROOT = Path(__file__).resolve().parent.parent


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


def create_session(audit_target: str = "", audit_id: str = "") -> str:
    """
    Generate a new session ID, write a manifest, set VIZ_SESSION_ID in env.
    Returns the session_id string.
    """
    session_id = str(uuid.uuid4())[:8]  # short readable ID
    sessions_dir = _sessions_dir()
    session_dir = sessions_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "session_id": session_id,
        "audit_target": audit_target,
        "audit_id": audit_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }
    (session_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (session_dir / "events.jsonl").touch()

    os.environ["VIZ_SESSION_ID"] = session_id
    return session_id


def get_current_session() -> str | None:
    """
    Returns the active session ID from env, or the most recent session on disk.
    Returns None if no sessions exist.
    """
    session_id = os.environ.get("VIZ_SESSION_ID", "").strip()
    if session_id:
        return session_id

    sessions = list_sessions()
    if sessions:
        return sessions[0]["session_id"]
    return None


def load_session(session_id: str) -> dict:
    """Load session manifest from disk. Returns {} if not found."""
    manifest_path = _sessions_dir() / session_id / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text())
    except Exception:
        return {}


def list_sessions() -> list[dict]:
    """Return all sessions sorted by created_at descending (newest first)."""
    sessions_dir = _sessions_dir()
    if not sessions_dir.exists():
        return []

    sessions = []
    for manifest_path in sessions_dir.glob("*/manifest.json"):
        try:
            data = json.loads(manifest_path.read_text())
            events_file = manifest_path.parent / "events.jsonl"
            data["event_count"] = _count_lines(events_file)
            sessions.append(data)
        except Exception:
            continue

    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


def get_events_file(session_id: str) -> Path:
    """Return the path to the events JSONL file for a session."""
    return _sessions_dir() / session_id / "events.jsonl"


def finalize_session(session_id: str) -> None:
    """Mark a session as completed."""
    manifest_path = _sessions_dir() / session_id / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text())
        manifest["status"] = "completed"
        manifest["ended_at"] = datetime.now(timezone.utc).isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2))
    except Exception:
        pass


def _count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.open() if line.strip())
    except Exception:
        return 0
