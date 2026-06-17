"""
viz/intercept/server_routes.py — FastAPI routes for the intercept layer.

Included into viz/server.py via:
    from viz.intercept.server_routes import include_intercept_routes
    include_intercept_routes(app)
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

_ROOT = Path(__file__).resolve().parent.parent.parent


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


def _session_dir(sid: str) -> Path:
    return _sessions_dir() / sid


def _pending_dir(sid: str) -> Path:
    return _session_dir(sid) / "pending"


def _load_pending_events(sid: str) -> list[dict]:
    pd = _pending_dir(sid)
    if not pd.exists():
        return []
    events = []
    for path in sorted(pd.glob("*.json")):
        if path.name.endswith(".modified.json"):
            continue
        try:
            events.append(json.loads(path.read_text()))
        except Exception:
            pass
    return events


def include_intercept_routes(app: FastAPI) -> None:

    # ── Intercept UI JS file ──────────────────────────────────────────────────

    @app.get("/intercept/ui.js", response_model=None)
    async def serve_ui_js():
        js_path = _ROOT / "viz" / "intercept" / "ui_components.js"
        if js_path.exists():
            return FileResponse(str(js_path), media_type="application/javascript")
        return JSONResponse({"error": "ui_components.js not found"}, status_code=404)

    # ── Breakpoints ───────────────────────────────────────────────────────────

    @app.get("/api/session/{session_id}/breakpoints")
    async def get_breakpoints(session_id: str) -> JSONResponse:
        try:
            from viz.intercept.breakpoints import load_breakpoints
            bps = load_breakpoints(session_id)
            return JSONResponse([b.to_dict() for b in bps])
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/session/{session_id}/breakpoints")
    async def create_breakpoint(session_id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        try:
            from viz.intercept.breakpoints import add_breakpoint
            bp = add_breakpoint(
                session_id,
                conditions=body.get("conditions", []),
                match_mode=body.get("match_mode", "any"),
                label=body.get("label", ""),
            )
            return JSONResponse({"ok": True, "breakpoint_id": bp.id, "breakpoint": bp.to_dict()})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.patch("/api/session/{session_id}/breakpoints/{bp_id}")
    async def update_breakpoint(session_id: str, bp_id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        try:
            from viz.intercept.breakpoints import update_breakpoint as _upd
            ok = _upd(session_id, bp_id, body)
            if ok:
                return JSONResponse({"ok": True})
            return JSONResponse({"ok": False, "error": "breakpoint not found"}, status_code=404)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.delete("/api/session/{session_id}/breakpoints/{bp_id}")
    async def delete_breakpoint(session_id: str, bp_id: str) -> JSONResponse:
        try:
            from viz.intercept.breakpoints import delete_breakpoint as _del
            ok = _del(session_id, bp_id)
            if ok:
                return JSONResponse({"ok": True})
            return JSONResponse({"ok": False, "error": "breakpoint not found"}, status_code=404)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── Pending events ────────────────────────────────────────────────────────

    @app.get("/api/session/{session_id}/pending")
    async def get_pending(session_id: str) -> JSONResponse:
        try:
            events = _load_pending_events(session_id)
            return JSONResponse({"pending": events, "count": len(events)})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/session/{session_id}/pending/{event_id}/release")
    async def release_pending(session_id: str, event_id: str) -> JSONResponse:
        try:
            pending_path = _pending_dir(session_id) / f"{event_id}.json"
            if not pending_path.exists():
                return JSONResponse({"ok": False, "error": "event not pending"}, status_code=404)
            pending_path.unlink()
            return JSONResponse({"ok": True, "action": "released"})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/session/{session_id}/pending/{event_id}/modify")
    async def modify_pending(session_id: str, event_id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        try:
            pending_dir  = _pending_dir(session_id)
            pending_path = pending_dir / f"{event_id}.json"
            if not pending_path.exists():
                return JSONResponse({"ok": False, "error": "event not pending"}, status_code=404)

            original = json.loads(pending_path.read_text())
            field    = body.get("field", "")
            new_val  = body.get("new_value")

            if not field:
                return JSONResponse({"ok": False, "error": "field required"}, status_code=400)

            # Build modified event
            import copy
            modified = copy.deepcopy(original)

            # Resolve dot-path field
            parts = field.split(".")
            obj = modified
            for part in parts[:-1]:
                if part not in obj or not isinstance(obj[part], dict):
                    obj[part] = {}
                obj = obj[part]
            old_val = obj.get(parts[-1])
            obj[parts[-1]] = new_val

            # Mark for gate.py bookkeeping
            modified["_intercept_field_modified"] = field
            modified["_intercept_old_value"]      = old_val
            modified["_intercept_new_value"]       = new_val

            # Write modified file, then remove pending file to unblock gate
            modified_path = pending_dir / f"{event_id}.modified.json"
            modified_path.write_text(json.dumps(modified, indent=2))
            pending_path.unlink(missing_ok=True)

            return JSONResponse({
                "ok": True,
                "action": "modified",
                "field": field,
                "old_value": old_val,
                "new_value": new_val,
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/session/{session_id}/pending/{event_id}/drop")
    async def drop_pending(session_id: str, event_id: str) -> JSONResponse:
        try:
            pending_path = _pending_dir(session_id) / f"{event_id}.json"
            if not pending_path.exists():
                return JSONResponse({"ok": False, "error": "event not pending"}, status_code=404)

            # Load original for audit trail
            try:
                original = json.loads(pending_path.read_text())
            except Exception:
                original = {"event_id": event_id}

            # Delete pending (unblocks gate — gate sees no modified file and considers it released)
            pending_path.unlink()

            # Write GATE_DROPPED to events.jsonl as audit trail
            events_file = _session_dir(session_id) / "events.jsonl"
            gate_event = {
                "event_id": str(uuid.uuid4()),
                "event_type": "GATE_DROPPED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_agent": "intercept_ui",
                "target_node_id": original.get("target_node_id"),
                "audit_session_id": session_id,
                "payload": {
                    "held_event_id": event_id,
                    "dropped_at": datetime.now(timezone.utc).isoformat(),
                    "original_event_type": original.get("event_type", ""),
                },
            }
            with events_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(gate_event, separators=(",", ":")) + "\n")

            return JSONResponse({"ok": True, "action": "dropped"})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── Cassette ──────────────────────────────────────────────────────────────

    @app.get("/api/session/{session_id}/cassette")
    async def get_cassette(session_id: str) -> JSONResponse:
        try:
            from viz.intercept.cassette import CassettePlayer
            player = CassettePlayer(session_id)
            return JSONResponse({
                "session_id": session_id,
                "count": player.get_frame_count(),
                "frames": player.get_frames_summary(),
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── Forks ─────────────────────────────────────────────────────────────────

    @app.get("/api/session/{session_id}/forks")
    async def get_forks(session_id: str) -> JSONResponse:
        try:
            from viz.intercept.fork import Fork
            forks = Fork().list_forks(session_id)
            return JSONResponse({"session_id": session_id, "forks": forks})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/session/{session_id}/fork")
    async def create_fork(session_id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        try:
            from viz.intercept.fork import Fork
            fork_id = Fork().create_fork(
                source_session_id=session_id,
                branch_from_event_index=int(body.get("branch_from_event_index", 0)),
                fork_label=body.get("fork_label", ""),
                modification=body.get("modification", {}),
            )
            return JSONResponse({
                "ok": True,
                "fork_id": fork_id,
                "fork_url": f"/?session={fork_id}&replay=1",
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    # ── Repeater ──────────────────────────────────────────────────────────────

    @app.get("/api/session/{session_id}/repeater/history")
    async def repeater_history(session_id: str) -> JSONResponse:
        # History is in-memory per server instance; for now return empty (stateless)
        return JSONResponse({"history": []})

    @app.post("/api/session/{session_id}/repeater/capture/{event_id}")
    async def repeater_capture(session_id: str, event_id: str) -> JSONResponse:
        try:
            from viz.intercept.repeater import EventRepeater
            rep = EventRepeater(session_id)
            event = rep.capture_event(event_id)
            if event:
                return JSONResponse({"ok": True, "event": event})
            return JSONResponse({"ok": False, "error": "event not found"}, status_code=404)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/session/{session_id}/repeater/replay")
    async def repeater_replay(session_id: str, request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            body = {}
        try:
            from viz.intercept.repeater import EventRepeater
            rep = EventRepeater(session_id)

            # Capture the event first
            event_id = body.get("event_id", "")
            event = rep.capture_event(event_id)
            if not event:
                return JSONResponse({"ok": False, "error": "event not found"}, status_code=404)

            result = rep.replay_event(
                event=event,
                modifications=body.get("modifications"),
                dry_run=bool(body.get("dry_run", True)),
            )
            return JSONResponse({"ok": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
