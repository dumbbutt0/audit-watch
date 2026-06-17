#!/usr/bin/env python3
"""
bridge_thread_escalation_gate.py — no-silent-drop gate for BRIDGE-RELEVANT deep-analysis threads.

A promising thread whose text mentions a bridge term (see scripts/bridge_terms.py) must EITHER be
ESCALATED to a finding (its thread_id appears in some finding's thread_refs) OR carry a CONCRETE
INVALIDATION in data/threads/_bridge_thread_dispositions.json: {thread_id, exact_sink, attacker_entrypoint,
resolution{type ∈ unreachable|bounded|subsumed, reason}} with a non-vague reason. Otherwise the run is
BLOCKED and the thread is routed to the human review queue (mirrors the triage no-silent-clear rule).

Gated by config coverage_policy.bridge_thread_escalation_strict (or _strict_full_audit + AUDITWATCH_FULL_AUDIT).
Override: AUDITWATCH_BRIDGE_THREAD_OVERRIDE=1 → warn-not-block. Writes output/bridge_thread_escalation_gate.json.
Exit 0 = pass; 1 = block.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import bridge_terms as bt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_RESOLUTIONS = {"unreachable", "bounded", "subsumed"}


def _policy() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except (OSError, json.JSONDecodeError):
        return {}


def _jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _escalated_thread_ids() -> set[str]:
    """Every thread_id referenced by any finding (thread_refs) — i.e. escalated into the finding set."""
    ids: set[str] = set()
    out = audit_path("output")
    paths = list(glob.glob(str(out / "findings_*.json"))) + [str(out / "merged_findings.json")]
    for p in paths:
        try:
            d = json.loads(Path(p).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        fs = d.get("findings", d) if isinstance(d, dict) else d
        for f in (fs if isinstance(fs, list) else []):
            for t in (f.get("thread_refs") or []):
                ids.add(str(t))
    return ids


def _valid_invalidation(rec: dict) -> tuple[bool, str]:
    if not rec:
        return False, "no invalidation record"
    sink = rec.get("exact_sink", "")
    entry = rec.get("attacker_entrypoint", "")
    res = rec.get("resolution", {}) or {}
    rtype, reason = res.get("type", ""), res.get("reason", "")
    if not sink or bt.is_vague(sink):
        return False, "missing/vague exact_sink"
    if not entry or bt.is_vague(entry):
        return False, "missing/vague attacker_entrypoint"
    if rtype not in _RESOLUTIONS:
        return False, f"resolution.type must be one of {sorted(_RESOLUTIONS)}"
    if not reason or bt.is_vague(reason):
        return False, "resolution.reason missing or vague (low confidence / already covered / needs more evidence are NOT concrete)"
    return True, "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pol = _policy()
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT", "").strip().lower() in ("1", "true", "yes", "on")
    strict = pol.get("bridge_thread_escalation_strict", False) or \
        (pol.get("bridge_thread_escalation_strict_full_audit", True) and full_audit)
    override = os.environ.get("AUDITWATCH_BRIDGE_THREAD_OVERRIDE", "").strip().lower() in ("1", "true", "yes", "on")

    threads = _jsonl(audit_path("data/threads") / "promising_threads.jsonl")
    escalated = _escalated_thread_ids()
    dispositions = {d.get("thread_id"): d for d in
                    (json.loads((audit_path("data/threads") / "_bridge_thread_dispositions.json").read_text()).get("dispositions", [])
                     if (audit_path("data/threads") / "_bridge_thread_dispositions.json").exists() else [])}

    bridge_threads, blocks, warnings, ok = [], [], [], []
    for t in threads:
        if not bt.is_bridge_thread(t):
            continue
        tid = t.get("thread_id", "?")
        terms = bt.matched_bridge_terms(bt.thread_text(t))
        row = {"thread_id": tid, "verdict": t.get("verdict"), "bridge_terms": terms}
        if tid in escalated:
            row["resolution"] = "escalated_to_finding"
            ok.append(row)
        else:
            valid, why = _valid_invalidation(dispositions.get(tid, {}))
            if valid:
                row["resolution"] = "concrete_invalidation"
                ok.append(row)
            else:
                row["reason"] = (f"bridge thread {tid} (verdict={t.get('verdict')}, terms={terms}) is neither "
                                 f"escalated to a finding nor concretely invalidated: {why}")
                blocks.append(row)
        bridge_threads.append(row)

    # No-silent-drop: route blocked threads to the human review queue (mirrors triage_write).
    if blocks:
        try:
            hq_path = audit_path("data/triage") / "human_review_queue.jsonl"
            hq_path.parent.mkdir(parents=True, exist_ok=True)
            with hq_path.open("a") as fh:
                for b in blocks:
                    fh.write(json.dumps({"source": "bridge_thread_escalation_gate", **b,
                                         "reroute_reason": "bridge thread dropped without escalation or concrete invalidation"}) + "\n")
        except OSError:
            pass

    passed = (len(blocks) == 0) or override or (not strict)
    report = {
        "gate": "bridge_thread_escalation", "generated_at": datetime.now(timezone.utc).isoformat(),
        "strict_active": strict, "override_active": override, "passed": passed,
        "total_bridge_threads": len(bridge_threads), "escalated_or_invalidated": len(ok),
        "blocked": len(blocks), "blocks": blocks, "ok": ok,
    }
    (audit_path("output") / "bridge_thread_escalation_gate.json").write_text(json.dumps(report, indent=2))

    if not args.quiet:
        tag = "PASS" if passed else "BLOCK"
        extra = " (OVERRIDE)" if (blocks and override) else (" (advisory: strict off)" if (blocks and not strict) else "")
        print(f"Bridge thread escalation gate: {tag}{extra}")
        print(f"  bridge threads {len(bridge_threads)} · escalated/invalidated {len(ok)} · blocked {len(blocks)}")
        for b in blocks:
            print(f"    {b['thread_id']} ({b['verdict']}) terms={b['bridge_terms']} — {b.get('reason','')[:100]}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
