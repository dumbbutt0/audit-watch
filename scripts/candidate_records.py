#!/usr/bin/env python3
"""candidate_records.py — the READ side of the ONE canonical per-finding record.

`build_candidate_records.py` writes `output/candidates/<id>.json` with a single derived `state`
(candidate -> human_pending -> poc_required -> ready -> rejected/duplicate) and the readiness blockers.
This module is how every CONSUMER (dashboard, final_submission_pack, ...) reads READY/state so they all
agree — review task 2 (one canonical record, star-files become derived).

Graceful by design: when the canonical record is absent (old audits, or before the review gate ran),
`load_records` returns {} and `overlay`/`apply_canonical_ready` leave the caller's legacy behavior
untouched. So wiring this in changes nothing until the record exists, then forces ONE READY definition.
"""
from __future__ import annotations

import json
from pathlib import Path

READY_STATE = "ready"


def load_records(output_dir) -> dict[str, dict]:
    """Return {finding_id: record} from <output_dir>/candidates/*.json. Empty dict when absent."""
    d = Path(output_dir) / "candidates"
    out: dict[str, dict] = {}
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.json")):
        try:
            r = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        fid = r.get("id")
        if fid:
            out[fid] = r
    return out


def is_ready(rec: dict | None) -> bool:
    """The single READY predicate. A finding is READY iff its canonical state == 'ready'."""
    return bool(rec) and rec.get("state") == READY_STATE


def overlay(finding: dict, rec: dict | None) -> dict:
    """Overlay the canonical record onto a consumer's per-finding dict (mutates + returns it).

    When `rec` is present: `state`, `readiness_blockers`, and the report fields are set from it, and
    `submission_ready` is forced to the ONE definition (state == 'ready') — so a dashboard card can no
    longer disagree with the gate verdicts. When `rec` is None: `state`/blockers default empty and
    `submission_ready` is left exactly as the caller computed it (legacy fallback).
    """
    if not rec:
        finding.setdefault("state", None)
        finding.setdefault("readiness_blockers", [])
        finding.setdefault("readiness_advisories", [])
        return finding
    finding["state"] = rec.get("state")
    finding["readiness_blockers"] = rec.get("readiness_blockers", [])
    finding["readiness_advisories"] = rec.get("readiness_advisories", [])  # advisory-only (submission_risk)
    finding["submission_ready"] = is_ready(rec)
    ev = rec.get("evidence") or {}
    finding["who_loses"] = ev.get("who_loses")
    finding["who_gains"] = ev.get("who_gains")
    finding["suggested_fix"] = ev.get("suggested_fix")
    return finding


def apply_canonical_ready(rows: list[dict], records: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    """Partition submit-triage rows by the canonical READY definition.

    Returns (ready, held). A row is HELD only when a canonical record EXISTS for its id and that record
    is not `ready` — i.e. triage put it in submit but the gauntlet/confirmation/PoC blocks it. Rows with
    no record pass through unchanged (no record => no enforcement => legacy behavior). Each held row is
    annotated with `_canonical_state` and `_readiness_blockers` for the operator message.
    """
    if not records:
        return list(rows), []
    ready, held = [], []
    for r in rows:
        fid = r.get("finding_id") or r.get("id")
        rec = records.get(fid)
        if rec is not None and not is_ready(rec):
            held.append({**r, "_canonical_state": rec.get("state"),
                         "_readiness_blockers": rec.get("readiness_blockers", [])})
        else:
            ready.append(r)
    return ready, held
