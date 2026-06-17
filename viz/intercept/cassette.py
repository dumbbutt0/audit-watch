"""
viz/intercept/cassette.py — VCR cassette recorder for LLM API calls.

Records every Anthropic API call to an append-only JSONL tape.
On fork replay, CassettePlayer.get_response() returns the recorded
response without making a real API call.

Usage in pipeline scripts:

    try:
        from viz.intercept.cassette import CassetteRecorder
        import os, uuid
        _rec = CassetteRecorder(os.environ.get("VIZ_SESSION_ID", ""))
        _rec.record_llm_call(
            call_id=str(uuid.uuid4()),
            agent="escalate_threads",
            model=MODEL,
            messages=messages,
            response=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
    except Exception:
        pass
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_FILE_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_LOCK = threading.Lock()


def _get_lock(path: str) -> threading.Lock:
    with _LOCKS_LOCK:
        if path not in _FILE_LOCKS:
            _FILE_LOCKS[path] = threading.Lock()
        return _FILE_LOCKS[path]


def _sessions_dir() -> Path:
    return _ROOT / "data" / "sessions"


def _cassette_path(session_id: str) -> Path:
    return _sessions_dir() / session_id / "cassette" / f"{session_id}.jsonl"


def _hash_messages(messages: list) -> str:
    """SHA-256 of the messages list for deduplication lookup."""
    try:
        canonical = json.dumps(messages, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
    except Exception:
        return str(uuid.uuid4())[:16]


class CassetteRecorder:
    """Append LLM call records to the session cassette JSONL."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

    def get_cassette_path(self) -> Path:
        return _cassette_path(self.session_id)

    def record_llm_call(
        self,
        call_id: str,
        agent: str,
        model: str,
        messages: list,
        response: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        temperature: float = 1.0,
        timestamp: str = "",
    ) -> None:
        """Appends one frame to the cassette. Never raises."""
        try:
            if not self.session_id:
                return
            path = self.get_cassette_path()
            path.parent.mkdir(parents=True, exist_ok=True)

            frame = {
                "frame_id": str(uuid.uuid4()),
                "session_id": self.session_id,
                "call_id": call_id,
                "agent": agent,
                "model": model,
                "messages_hash": _hash_messages(messages),
                "messages": messages,
                "response": response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "temperature": temperature,
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            }

            lock = _get_lock(str(path))
            with lock:
                with path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(frame, separators=(",", ":")) + "\n")
        except Exception:
            pass


class CassettePlayer:
    """Load a cassette and serve recorded responses for fork replay."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._frames: list[dict] = self._load()

    def _load(self) -> list[dict]:
        path = _cassette_path(self.session_id)
        if not path.exists():
            return []
        frames = []
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        frames.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return frames

    def get_response(self, agent: str, messages: list) -> str | None:
        """
        Return the recorded response for (agent, messages) if found.
        Match on agent name + SHA-256 of the messages list.
        Returns None if no match — caller must make a real API call.
        """
        target_hash = _hash_messages(messages)
        for frame in self._frames:
            if frame.get("agent") == agent and frame.get("messages_hash") == target_hash:
                return frame.get("response")
        return None

    def get_frame_count(self) -> int:
        return len(self._frames)

    def get_frames(self) -> list[dict]:
        return list(self._frames)

    def get_frames_summary(self) -> list[dict]:
        """Return frames without the full messages list (for API responses)."""
        return [
            {
                "frame_id": f.get("frame_id"),
                "agent": f.get("agent"),
                "model": f.get("model"),
                "input_tokens": f.get("input_tokens"),
                "output_tokens": f.get("output_tokens"),
                "timestamp": f.get("timestamp"),
                "messages_hash": f.get("messages_hash"),
            }
            for f in self._frames
        ]
