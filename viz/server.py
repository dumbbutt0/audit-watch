"""
viz/server.py — Adversarial Reasoning Visualization Server.

Serves the D3.js reasoning graph frontend and streams live VizEvents via WebSocket.

Port: 8766 (8765 is taken by the existing audit dashboard)

Launch:
    python viz/server.py
    python viz/server.py --session <session_id>

Endpoints:
    GET  /                              → viz/frontend/index.html
    GET  /api/session/{id}/graph        → full graph snapshot
    GET  /api/session/{id}/graph?at=N   → graph snapshot at event index N (replay)
    GET  /api/session/{id}/metrics      → graph metrics
    GET  /api/sessions                  → list all historical sessions
    WS   /ws/live                       → real-time event stream
    POST /api/session/{id}/branch/{bid}/suppress   → human-in-loop prune
    POST /api/session/{id}/hypothesis/{hid}/annotate → add human annotation
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# ── ensure project root is on sys.path ───────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import uvicorn

from viz.graph_state import GraphState
from viz.session import (
    get_current_session,
    get_events_file,
    list_sessions,
    load_session,
)
from viz.replay import ReplaySession

# ── app setup ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def _lifespan(app: FastAPI):
    global _current_session_id, _graph
    _current_session_id = get_current_session()
    if _current_session_id:
        _graph = await _load_graph_from_disk(_current_session_id)
        asyncio.create_task(_watch_events(_current_session_id))
        asyncio.create_task(_watch_intercept(_current_session_id))
    asyncio.create_task(_heartbeat_loop())
    yield

app = FastAPI(title="Reasoning Graph Viz", docs_url=None, redoc_url=None, lifespan=_lifespan)

_FRONTEND = _ROOT / "viz" / "frontend" / "index.html"

# Live graph state — one per server instance (current session)
_graph: GraphState = GraphState()
_current_session_id: str | None = None
_ws_clients: list[WebSocket] = []
_ws_lock = asyncio.Lock()




# ── HTTP endpoints ─────────────────────────────────────────────────────────────

@app.get("/", response_model=None)
async def root(session: str | None = None):
    if not _FRONTEND.exists():
        return HTMLResponse("<h1>viz/frontend/index.html not found</h1>", status_code=404)
    if session:
        return FileResponse(str(_FRONTEND))
    # Auto-redirect to most recent active session
    sessions = list_sessions()
    active = [s for s in sessions if s.get("status") == "active"]
    if active:
        best = active[0]
        sid = best.get("session_id", "")
        if sid:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"/?session={sid}", status_code=302)
    return FileResponse(str(_FRONTEND))


@app.get("/api/sessions")
async def api_sessions() -> JSONResponse:
    return JSONResponse(list_sessions())


@app.get("/api/session/{session_id}/graph")
async def api_graph(session_id: str, at: int | None = None) -> JSONResponse:
    try:
        if at is not None:
            replay = ReplaySession(session_id)
            return JSONResponse(replay.graph_at(at))
        if session_id == _current_session_id:
            return JSONResponse(_graph.snapshot())
        # Historical session
        replay = ReplaySession(session_id)
        return JSONResponse(replay.graph_at(replay.event_count() - 1))
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/session/{session_id}/metrics")
async def api_metrics(session_id: str) -> JSONResponse:
    try:
        if session_id == _current_session_id:
            return JSONResponse(_graph.metrics())
        replay = ReplaySession(session_id)
        graph = GraphState()
        for event in replay.all_events():
            graph.apply_event(event)
        return JSONResponse(graph.metrics())
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/session/{session_id}/events")
async def api_events(session_id: str) -> JSONResponse:
    try:
        replay = ReplaySession(session_id)
        return JSONResponse({
            "session_id": session_id,
            "event_count": replay.event_count(),
            "events": replay.all_events(),
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/api/session/{session_id}/branch/{branch_id}/suppress")
async def api_suppress(session_id: str, branch_id: str) -> JSONResponse:
    if session_id != _current_session_id:
        return JSONResponse({"error": "can only suppress nodes in current session"}, status_code=400)
    ok = _graph.suppress_node(branch_id)
    if ok:
        await _broadcast({"type": "diff", "nodes": [{"id": branch_id, "status": "PRUNED"}]})
        return JSONResponse({"ok": True, "node_id": branch_id})
    return JSONResponse({"ok": False, "error": "node not found"}, status_code=404)


@app.post("/api/session/{session_id}/hypothesis/{hyp_id}/annotate")
async def api_annotate(session_id: str, hyp_id: str, request: Request) -> JSONResponse:
    if session_id != _current_session_id:
        return JSONResponse({"error": "can only annotate nodes in current session"}, status_code=400)
    try:
        body = await request.json()
    except Exception:
        body = {}
    annotation = body.get("annotation", "")
    ok = _graph.annotate_node(hyp_id, annotation)
    if ok:
        await _broadcast({"type": "diff", "nodes": [{"id": hyp_id, "annotation": annotation}]})
        return JSONResponse({"ok": True})
    return JSONResponse({"ok": False, "error": "node not found"}, status_code=404)


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/live")
async def ws_live(ws: WebSocket) -> None:
    await ws.accept()
    async with _ws_lock:
        _ws_clients.append(ws)
    try:
        # Send full graph snapshot on connect
        snapshot = _graph.snapshot()
        await ws.send_json({"type": "snapshot", **snapshot})

        # Keep alive — client sends pings, we echo
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=30.0)
                if data == "ping":
                    await ws.send_text("pong")
            except asyncio.TimeoutError:
                await ws.send_text("ping")  # server-initiated keepalive
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        async with _ws_lock:
            if ws in _ws_clients:
                _ws_clients.remove(ws)


# ── background tasks ──────────────────────────────────────────────────────────

async def _watch_events(session_id: str) -> None:
    """
    Watch the session events file for new lines and broadcast diffs to WS clients.
    Uses watchfiles for inotify/kqueue-based notification (near-instant, not polling).
    """
    events_file = get_events_file(session_id)
    if not events_file.exists():
        return

    try:
        from watchfiles import awatch
    except ImportError:
        # Fall back to async polling every 0.5s
        await _poll_events(events_file)
        return

    last_size = events_file.stat().st_size if events_file.exists() else 0

    try:
        async for _ in awatch(str(events_file), stop_event=asyncio.Event()):
            new_size = events_file.stat().st_size
            if new_size <= last_size:
                continue
            new_lines = _read_new_lines(events_file, last_size)
            last_size = new_size
            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    diff = _graph.apply_event(event)
                    await _broadcast({
                        "type": "event",
                        "event": event,
                        "diff": diff,
                        "metrics": _graph.metrics(),
                    })
                except Exception:
                    pass
    except Exception:
        pass


async def _poll_events(events_file: Path) -> None:
    """Fallback polling if watchfiles is unavailable."""
    last_size = 0
    while True:
        await asyncio.sleep(0.5)
        try:
            if not events_file.exists():
                continue
            new_size = events_file.stat().st_size
            if new_size <= last_size:
                continue
            new_lines = _read_new_lines(events_file, last_size)
            last_size = new_size
            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    diff = _graph.apply_event(event)
                    await _broadcast({
                        "type": "event",
                        "event": event,
                        "diff": diff,
                        "metrics": _graph.metrics(),
                    })
                except Exception:
                    pass
        except Exception:
            pass


async def _watch_intercept(session_id: str) -> None:
    """
    Watch breakpoints.json and pending/ directory for intercept state changes.
    On change: broadcast pending list and breakpoints to all WS clients.
    """
    from viz.session import get_events_file
    session_dir = get_events_file(session_id).parent
    bp_file     = session_dir / "breakpoints.json"
    pending_dir = session_dir / "pending"
    pending_dir.mkdir(exist_ok=True)

    watch_paths = [str(pending_dir)]
    if bp_file.exists():
        watch_paths.append(str(bp_file))
    else:
        # Also watch parent so we notice when breakpoints.json is created
        watch_paths.append(str(session_dir))

    try:
        from watchfiles import awatch
        async for changes in awatch(*watch_paths, stop_event=asyncio.Event()):
            await _broadcast_intercept_state(session_id)
    except ImportError:
        # Fallback: poll every 0.5s
        while True:
            await asyncio.sleep(0.5)
            await _broadcast_intercept_state(session_id)
    except Exception:
        pass


async def _broadcast_intercept_state(session_id: str) -> None:
    """Send current pending list and breakpoints to all WS clients."""
    try:
        from viz.intercept.breakpoints import load_breakpoints
        from viz.session import get_events_file
        bps = load_breakpoints(session_id)

        pending_dir = get_events_file(session_id).parent / "pending"
        pending = []
        if pending_dir.exists():
            import json as _json
            for p in sorted(pending_dir.glob("*.json")):
                if p.name.endswith(".modified.json"):
                    continue
                try:
                    pending.append(_json.loads(p.read_text()))
                except Exception:
                    pass

        await _broadcast({
            "type": "intercept_state",
            "breakpoints": [b.to_dict() for b in bps],
            "pending": pending,
            "pending_count": len(pending),
        })
    except Exception:
        pass


async def _heartbeat_loop() -> None:
    while True:
        await asyncio.sleep(10)
        await _broadcast({"type": "heartbeat", "metrics": _graph.metrics()})


async def _broadcast(data: dict) -> None:
    async with _ws_lock:
        dead = []
        for ws in _ws_clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _ws_clients.remove(ws)


# ── helpers ───────────────────────────────────────────────────────────────────

def _read_new_lines(path: Path, from_byte: int) -> list[str]:
    try:
        with path.open("rb") as fh:
            fh.seek(from_byte)
            new_bytes = fh.read()
        return new_bytes.decode("utf-8", errors="replace").splitlines()
    except Exception:
        return []


async def _load_graph_from_disk(session_id: str) -> GraphState:
    """Replay existing events on startup to restore graph state."""
    state = GraphState()
    events_file = get_events_file(session_id)
    if not events_file.exists():
        return state
    try:
        for line in events_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    state.apply_event(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return state


# ── intercept routes (optional — server works without viz/intercept/) ─────────
try:
    from viz.intercept.server_routes import include_intercept_routes
    include_intercept_routes(app)
except ImportError:
    pass


# ── entry point ───────────────────────────────────────────────────────────────

def _print_banner(session_id: str | None, session_meta: dict) -> None:
    target = session_meta.get("audit_target", session_meta.get("audit_id", "unknown"))
    sid = session_id or "none"
    print()
    print("━" * 44)
    print("  REASONING GRAPH LIVE")
    print("  http://localhost:8766")
    print(f"  Session: {sid}")
    print(f"  Audit target: {target}")
    print("━" * 44)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reasoning Graph Visualization Server")
    parser.add_argument("--session", help="Session ID to watch (default: current active session)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()

    if args.session:
        os.environ["VIZ_SESSION_ID"] = args.session

    resolved_session = get_current_session()
    meta = load_session(resolved_session) if resolved_session else {}
    _print_banner(resolved_session, meta)

    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="warning",
        )
    except OSError as exc:
        print(f"[viz] Could not start server on port {args.port}: {exc}")
        print("[viz] Pipeline continues normally.")
        sys.exit(0)
