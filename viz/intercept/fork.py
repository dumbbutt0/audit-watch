"""
viz/intercept/fork.py — Counterfactual fork (AGDebugger-style checkpoint branches).

Creates a new session that branches from an existing one at a given event index.
The fork is itself a valid session — the viz server loads it as a historical session.

Usage:
    from viz.intercept.fork import Fork
    f = Fork()
    fork_id = f.create_fork(
        source_session_id="b8953102",
        branch_from_event_index=30,
        fork_label="confidence +0.3 on XTR-003",
        modification={"target_node_id": "XTR-003",
                      "field": "payload.confidence",
                      "old_value": 0.3, "new_value": 0.6}
    )
"""

from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


def _set_field(obj: dict, field_path: str, value) -> None:
    parts = field_path.split(".")
    for part in parts[:-1]:
        if part not in obj or not isinstance(obj[part], dict):
            obj[part] = {}
        obj = obj[part]
    obj[parts[-1]] = value


class Fork:
    def create_fork(
        self,
        source_session_id: str,
        branch_from_event_index: int,
        fork_label: str,
        modification: dict,
    ) -> str:
        """
        Create data/sessions/{source}/forks/{fork_id}/ with:
          - manifest.json
          - events.jsonl (events 0..branch_from_event_index with last event modified)

        Returns fork_id (short UUID, valid as a session_id).
        """
        source_dir   = _sessions_dir() / source_session_id
        events_file  = source_dir / "events.jsonl"

        # Load source events
        source_events = self._load_events(events_file)
        slice_events  = source_events[:branch_from_event_index + 1]

        if not slice_events:
            raise ValueError(f"No events found at index {branch_from_event_index}")

        # Apply modification to the last event in the slice
        modified_events = [copy.deepcopy(e) for e in slice_events]
        last = modified_events[-1]
        field = modification.get("field", "")
        new_val = modification.get("new_value")
        if field:
            _set_field(last, field, new_val)
            last["_fork_modified"] = True
            last["_fork_modification"] = modification

        fork_id  = str(uuid.uuid4())[:8]
        fork_dir = source_dir / "forks" / fork_id
        fork_dir.mkdir(parents=True)

        # Write forked events.jsonl
        fork_events_file = fork_dir / "events.jsonl"
        with fork_events_file.open("w", encoding="utf-8") as fh:
            for e in modified_events:
                fh.write(json.dumps(e, separators=(",", ":")) + "\n")

        # Load source manifest for metadata
        source_manifest = {}
        source_manifest_path = source_dir / "manifest.json"
        if source_manifest_path.exists():
            try:
                source_manifest = json.loads(source_manifest_path.read_text())
            except Exception:
                pass

        # Write fork manifest
        manifest = {
            "session_id": fork_id,
            "fork_id": fork_id,
            "source_session_id": source_session_id,
            "branch_from_event_index": branch_from_event_index,
            "fork_label": fork_label,
            "modification": modification,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "fork",
            "audit_target": source_manifest.get("audit_target", ""),
            "audit_id": source_manifest.get("audit_id", ""),
            "event_count": len(modified_events),
        }
        (fork_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        # Also register the fork as a top-level session so the server can load it
        # by creating a symlink (or copy the manifest to sessions/{fork_id})
        top_level_dir = _sessions_dir() / fork_id
        if not top_level_dir.exists():
            # Write a thin manifest that points at the fork location
            top_level_dir.mkdir(parents=True, exist_ok=True)
            (top_level_dir / "manifest.json").write_text(
                json.dumps({**manifest, "fork_source_path": str(fork_dir)}, indent=2)
            )
            # Copy events to the top-level session dir so ReplaySession can load it
            with (top_level_dir / "events.jsonl").open("w", encoding="utf-8") as fh:
                for e in modified_events:
                    fh.write(json.dumps(e, separators=(",", ":")) + "\n")

        return fork_id

    def list_forks(self, source_session_id: str) -> list[dict]:
        """Return manifests for all forks of a session."""
        forks_dir = _sessions_dir() / source_session_id / "forks"
        if not forks_dir.exists():
            return []
        results = []
        for manifest_path in forks_dir.glob("*/manifest.json"):
            try:
                data = json.loads(manifest_path.read_text())
                # Include live event count
                events_file = manifest_path.parent / "events.jsonl"
                data["event_count"] = self._count_lines(events_file)
                results.append(data)
            except Exception:
                continue
        results.sort(key=lambda m: m.get("created_at", ""))
        return results

    def get_fork_manifest(self, fork_id: str) -> dict:
        """Return the manifest for a specific fork, searching both locations."""
        # Try top-level sessions first
        path = _sessions_dir() / fork_id / "manifest.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return {}

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_events(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        events = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return events

    def _count_lines(self, path: Path) -> int:
        if not path.exists():
            return 0
        try:
            return sum(1 for l in path.open() if l.strip())
        except Exception:
            return 0
