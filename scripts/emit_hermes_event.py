#!/usr/bin/env python3
"""
emit_hermes_event.py — Fire-and-forget Hermes event emitter for pipeline scripts.

Import and call emit_hermes() from any pipeline script.  If Hermes is absent,
disabled, or raises for any reason, the call is a no-op and execution continues.
"""


def emit_hermes(event_type: str, payload: dict) -> None:
    """Write one event to ../hermes/memory/events.jsonl.  Never raises."""
    try:
        from scripts.hermes_bridge import write_memory_event
        write_memory_event(event_type, payload)
    except Exception:
        pass
