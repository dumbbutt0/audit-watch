# Phase 0 — Intercept Layer Reconnaissance

## 1. emit() is purely fire-and-forget

`viz/event_emitter.py` writes the event JSON line to `events.jsonl` using a per-file
`threading.Lock`, then returns immediately. No downstream pipeline script reads
`events.jsonl` before continuing — the file is only tailed by the viz *server* process
(`viz/server.py`) via `watchfiles.awatch()`, which runs in a completely separate OS
process. The pipeline script is never blocked by viz.

## 2. WebSocket message formats

Four message types are broadcast on `/ws/live`:

```json
// On new client connect — full graph snapshot
{"type": "snapshot", "nodes": [...], "edges": [...], "metrics": {...}, "event_count": 42}

// On each new VizEvent from events.jsonl tail
{"type": "event", "event": {...}, "diff": {"changed": [...], "added": [...], "edges_added": [...]}, "metrics": {...}}

// For human-in-loop suppress/annotate (POST endpoints)
{"type": "diff", "nodes": [{"id": "XTR-003", "status": "PRUNED"}]}

// Heartbeat every 10 s
{"type": "heartbeat", "metrics": {...}}
```

The intercept layer adds four new WS message types (see §5 below).

## 3. Event stream rendering

Bottom bar rendered by `addEventRow(event)` at line 962 of `viz/frontend/index.html`:
- Each row is a `.ev-row` div **prepended** to `#event-stream` (newest on top)
- Row contains: `ev-time`, `ev-type`, `ev-target`, `ev-desc`, `ev-sev` spans
- Clicking a row calls `selectNode(target_node_id)`
- The intercept layer adds: lock icon (⊙) on PENDING rows, Release/Modify/Drop buttons
  for held events in the pending panel

## 4. Pipeline scripts importing viz

Five scripts do lazy `from viz.event_emitter import emit` inside `try/except`:
| Script | Events emitted |
|--------|---------------|
| `tools/static_analysis.py` | HYPOTHESIS_BORN |
| `tools/retriever.py` | KB_MATCH |
| `scripts/triage_findings.py` | TRIAGER_DECISION, BRANCH_INVALIDATED |
| `scripts/calibrate_severity.py` | CONFIDENCE_SHIFT |
| `scripts/escalate_threads.py` | AGENT_SPAWNED |

All emit calls are inside `try/except Exception: pass`, so adding the gate check
to `event_emitter.py` cannot break any of them.

## 5. New WS event types for intercept

```json
{"type": "gate_opened",   "event": {...pending event...}, "breakpoint_id": "..."}
{"type": "gate_released", "event_id": "...", "held_duration": 12.4}
{"type": "gate_modified", "event_id": "...", "field": "...", "old_value": ..., "new_value": ...}
{"type": "gate_dropped",  "event_id": "..."}
{"type": "breakpoints_changed", "breakpoints": [...]}
{"type": "pending_list",  "pending": [...]}
```

## 6. Async/await status in pipeline scripts

No pipeline script that calls the Anthropic API uses `async/await`. All use
synchronous `anthropic.Anthropic().messages.create(...)`. The gate's polling
loop (`time.sleep(0.2)`) is therefore safe — it will not block an asyncio event
loop. (Only `scripts/dashboard.py` is async, and it doesn't call the Anthropic API.)

## 7. File-based coordination strategy

The gate mechanism uses the filesystem as an IPC channel:

```
data/sessions/{session_id}/
  events.jsonl          ← all events (gate events also written here for audit trail)
  pending/{event_id}.json       ← event is HELD (file exists = gate closed)
  pending/{event_id}.modified.json  ← human wrote modified payload
  held/{event_id}.json          ← audit trail: original + modified + timestamps
  breakpoints.json              ← active breakpoints (watched by server)
  cassette/{session_id}.jsonl   ← LLM call recordings
  forks/{fork_id}/
    manifest.json
    events.jsonl
```

Polling interval: 0.2 s. Max hold timeout: 300 s (configurable via VIZ_GATE_TIMEOUT).
Entire intercept layer disabled when VIZ_INTERCEPT=0 or VIZ_SESSION_ID is unset.
