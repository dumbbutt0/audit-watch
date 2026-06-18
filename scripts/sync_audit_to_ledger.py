#!/usr/bin/env python3
"""sync_audit_to_ledger.py — keep documentation/real_world_results.json (the dashboard funnel source) in sync
with a real-world audit's canonical findings, NON-DESTRUCTIVELY.

What it does, per audit:
  * PoC-PROVEN findings (poc.proved) -> candidate_findings[] CARDS (verifier.poc_status="REPRODUCED"), so they
    render on the dashboard /candidates page under the audit's display name (meta.ledger_target).
  * Confirmed NON-PoC findings -> a delimited re-audit NOTE on the targets[] entry (honest; never a fake card —
    the ledger invariant is "cards are PoC-reproduced by definition").

SAFETY (why this is not reports/sync_realworld_candidates.py, which is destructive):
  * Never fabricates or overwrites human-adjudicated fields (outcome_class / outcome_provenance / submitted /
    human_verified). New cards carry NO outcome_class; owned cards preserve any human fields added later.
  * Dedups against existing ledger entries by CONTRACT so the re-audit's re-confirmations of already-curated
    findings are skipped (only genuinely-new contracts are added). Every skip is logged.
  * Only touches entries this sync owns: candidate_id == "<audit_id>:<finding_id>". Curated/human entries are
    never modified.
  * REAL-WORLD GATE: runs only for real-world audits (meta.ledger_sync true, or meta.platform set and the
    audit_id has no 'eval'/'blind'). Eval/blind audits are a no-op — the precision ledger is never contaminated.
  * Atomic write + timestamped .bak.

Usage: python scripts/sync_audit_to_ledger.py [--audit <id>] [--dry-run] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RW = ROOT / "documentation" / "real_world_results.json"
sys.path.insert(0, str(ROOT / "scripts"))


def _active_audit_id() -> str:
    try:
        return json.loads((ROOT / "config" / "active_audit.json").read_text()).get("audit_id", "")
    except (OSError, json.JSONDecodeError):
        return ""


def _load(p: Path, default):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def _is_real_world(meta: dict, audit_id: str) -> tuple[bool, str]:
    if meta.get("ledger_sync") is True:
        return True, "meta.ledger_sync=true"
    if meta.get("ledger_sync") is False:
        return False, "meta.ledger_sync=false"
    low = audit_id.lower()
    if "eval" in low or "blind" in low:
        return False, "audit_id looks eval/blind"
    if str(meta.get("platform") or "").strip():
        return True, f"platform={meta.get('platform')}"
    return False, "no platform / not flagged real-world"


def _contract_of(s: str) -> str:
    """Contract name from a 'Contract.function' / 'path/Contract.sol:fn' / location string."""
    if not s:
        return ""
    s = s.split(":")[0].strip()
    base = s.rsplit("/", 1)[-1].replace(".sol", "")
    return base.split(".")[0].strip().lower()


def _verifier_target(cand: dict, overrides: dict | None = None) -> str:
    """Best 'Contract.function' for the card. Order: meta override (per finding id) -> manifest_refs ->
    location. A dotted result matters: funnel.py only uses verifier.target for the displayed location when it
    contains a '.', else it falls back to the PoC filename (e.g. 'PoC_X.None')."""
    fid = cand.get("id")
    if overrides and fid in overrides and overrides[fid]:
        return str(overrides[fid])
    for ref in cand.get("manifest_refs") or []:
        m = re.search(r"([A-Za-z0-9_]+)\.sol:([A-Za-z0-9_]+)", str(ref))
        if m:
            return f"{m.group(1)}.{m.group(2)}"
        m = re.search(r"([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)", str(ref))
        if m:
            return f"{m.group(1)}.{m.group(2)}"
    loc = cand.get("location") or {}
    c, fn = loc.get("contract") or "", loc.get("function") or ""
    return f"{c}.{fn}".strip(".") or c or "unknown"


def _sev(c: dict) -> str:
    return (c.get("classification") or {}).get("severity") or c.get("severity") or "Medium"


def _verifier_block(cand: dict, vtarget: str, poc: dict) -> dict:
    ev = cand.get("evidence") or {}
    return {
        "target": vtarget,
        "surface_function": vtarget,
        "suspected_mechanism": cand.get("description") or cand.get("title") or "",
        "mechanism_class": cand.get("vuln_type") or "",
        "impact": (ev.get("impact") if isinstance(ev, dict) else None) or cand.get("impact") or "",
        "severity_recommendation": _sev(cand), "claimed_severity": _sev(cand),
        "mechanism_confirmed": True, "attacker_reachable": True, "severity_bearing": True, "reportable": True,
        "real_contract_deployed": True, "production_source_modified": False,
        "poc_command": f"forge test --match-contract {poc.get('test_contract','')} -vv",
        "poc_status": "REPRODUCED",
        "harness_path": poc.get("test_file", ""),
        "vulnerable_output": poc.get("evidence", ""),
        "who_loses": (ev.get("who_loses") if isinstance(ev, dict) else "") or "",
        "who_gains": (ev.get("who_gains") if isinstance(ev, dict) else "") or "",
        "reachability_class": cand.get("reachability_tag") or "",
    }


def build(audit_id: str) -> tuple[dict, list[str]]:
    log: list[str] = []
    adir = ROOT / "audits" / audit_id
    meta = _load(adir / "meta.json", {})
    ok, why = _is_real_world(meta, audit_id)
    if not ok:
        return {"skipped": True, "reason": why}, [f"SKIP {audit_id}: {why}"]

    target = meta.get("ledger_target") or (meta.get("name") or audit_id).split("(")[0].strip().split()[0]
    cdir = adir / "output" / "candidates"
    poc_by_id = {}
    for line in (adir / "data" / "runtime_poc" / "results.jsonl").read_text().splitlines() if (adir / "data" / "runtime_poc" / "results.jsonl").exists() else []:
        line = line.strip()
        if line:
            r = json.loads(line)
            poc_by_id[r.get("finding_id")] = r

    proven, nonpoc = [], []
    for cp in sorted(cdir.glob("*.json")) if cdir.is_dir() else []:
        c = _load(cp, {})
        st = c.get("state")
        if st in ("duplicate", "rejected"):
            continue
        if (c.get("poc") or {}).get("proved"):
            proven.append(c)
        elif st in ("ready", "poc_required", "human_pending"):
            nonpoc.append(c)

    data = _load(RW, {})
    cf = data.get("candidate_findings") or []
    tg = data.get("targets") or []

    # contracts already represented for this target (curated + others), excluding our own owned entries
    owned_prefix = f"{audit_id}:"
    existing_contracts = {
        _contract_of((e.get("verifier") or {}).get("target") or "")
        for e in cf
        if str(e.get("target", "")) == target and not str(e.get("candidate_id", "")).startswith(owned_prefix)
    }
    prior_owned = {e.get("candidate_id"): e for e in cf if str(e.get("candidate_id", "")).startswith(owned_prefix)}

    vtarget_overrides = meta.get("ledger_verifier_targets") or {}
    new_cards, kept_owned_ids, added_ids, updated_ids = [], set(), [], []
    for c in proven:
        fid = c.get("id")
        vt = _verifier_target(c, vtarget_overrides)
        contract = _contract_of(vt)
        cid = f"{audit_id}:{fid}"
        if cid not in prior_owned and contract in existing_contracts:
            log.append(f"  skip {fid} (contract '{contract}' already represented in the ledger — re-confirmation)")
            continue
        poc = poc_by_id.get(fid, {})
        card = {
            "candidate_id": cid, "target": target, "source": "re-audit",
            "severity": _sev(c), "title": c.get("title", ""),
            "status": "PoC reproduced", "submitted": False, "human_verified": False,
            "evidence": poc.get("evidence", "") or (c.get("proof_of_concept") or ""),
            "poc_path": poc.get("test_file", ""),
            "writeup": meta.get("report_path", ""),
            "verifier": _verifier_block(c, vt, poc),
            "source_audit": audit_id,
        }
        # preserve any human-adjudicated fields previously attached to our owned entry
        prev = prior_owned.get(cid)
        if prev:
            for k in ("outcome_class", "outcome_provenance", "outcome_reason", "outcome_recorded_at",
                      "submitted", "human_verified"):
                if prev.get(k) is not None:
                    card[k] = prev[k]
        new_cards.append(card)
        kept_owned_ids.add(cid)
        if prev != card:
            (updated_ids if cid in prior_owned else added_ids).append(cid)

    # rebuild cf: keep everything not owned-by-us; drop stale owned entries (replaced); append fresh cards
    rebuilt_cf = [e for e in cf if not str(e.get("candidate_id", "")).startswith(owned_prefix)]
    added, updated = len(added_ids), len(updated_ids)
    rebuilt_cf.extend(new_cards)

    # target note (non-destructive: preserve curated `notes`, set/refresh a delimited reaudit_note).
    # NB: deterministic (no timestamp) so a re-run with no new findings produces identical content (no churn).
    note = (f"[re-audit {audit_id}] "
            f"{len(new_cards)} new PoC-proven card(s): " +
            "; ".join(f"{c['id']}:{c['title'][:60]}" for c in proven if f"{audit_id}:{c['id']}" in kept_owned_ids) +
            (". Confirmed non-PoC (target notes, not cards): " +
             "; ".join(f"{c['id']}:{c.get('title','')[:60]}" for c in nonpoc) if nonpoc else "") + ".")
    tgt_entry = next((t for t in tg if t.get("target") == target), None)
    note_changed = (tgt_entry or {}).get("reaudit_note") != note
    if tgt_entry is None:
        tg.append({"target": target, "source": f"re-audit {audit_id}", "verdict": "candidate_finding",
                   "reaudit_note": note})
    else:
        tgt_entry["reaudit_note"] = note  # never touches the curated `notes`

    data["candidate_findings"] = rebuilt_cf
    data["targets"] = tg
    s = data.get("summary") or {}
    s["poc_proven_candidate_findings"] = len(rebuilt_cf)
    data["summary"] = s

    dirty = bool(added or updated or note_changed)
    log.insert(0, f"{audit_id} -> ledger target '{target}': +{added} new card(s), {updated} updated-in-place, "
                  f"{len(proven)-len(new_cards)} skipped (re-confirmations), {len(nonpoc)} non-PoC -> target note"
                  f"{'' if dirty else '  (no changes)'}")
    return {"data": data, "added": added, "updated": updated, "target": target, "dirty": dirty,
            "new_card_ids": [c["candidate_id"] for c in new_cards]}, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    audit_id = args.audit or _active_audit_id()
    if not audit_id:
        print("[ledger-sync] no audit id (pass --audit or set active audit)")
        return 0

    result, log = build(audit_id)
    if not args.quiet:
        for ln in log:
            print(ln if ln.startswith(audit_id) else f"[ledger-sync] {ln}")
    if result.get("skipped"):
        return 0  # real-world gate: no-op, success

    if not result.get("dirty"):
        return 0  # nothing changed — skip write (no churn, no .bak); keeps the pre-commit hook quiet

    if args.dry_run:
        if not args.quiet:
            print(f"[ledger-sync] DRY-RUN — would write {RW} (new cards: {result['new_card_ids']})")
        return 0

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    if RW.exists():
        (RW.with_suffix(RW.suffix + f".bak.{ts}")).write_text(RW.read_text())
    tmp = RW.with_suffix(RW.suffix + ".tmp")
    tmp.write_text(json.dumps(result["data"], indent=2) + "\n")
    os.replace(tmp, RW)
    if not args.quiet:
        print(f"[ledger-sync] wrote {RW} (+{result['added']} new / {result['updated']} updated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
