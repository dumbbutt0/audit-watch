#!/usr/bin/env python3
"""
derive_learning.py — Deterministic auto-learning fan-out (NO API).

From a human-confirmed ground-truth outcome, derive a candidate learning artifact and write it to
data/learning/_proposed/ ONLY. It NEVER touches the shared project rules — a human runs
promote_learning.py to apply approved candidates. This prevents an auto-generated rule from
silently suppressing future valid findings.

Mapping:
    invalid    → _proposed/rejection_rules.jsonl        (candidate FP rule)
    duplicate  → _proposed/duplicate_registry.jsonl     (candidate dup-registry entry)
    downgraded → _proposed/severity_rules_additions.yaml(candidate severity note)
    accepted/paid/escalated → _proposed/positive_patterns.jsonl (what worked)

Usable as a library (derive_from_record) or standalone over the active audit's ground_truth.jsonl.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, load_jsonl

# Deterministic reason-keyword → pattern_type (kept local; no API, no heavy imports).
_KEYWORD_PATTERN = [
    ("compromis", "requires_compromised_key"), ("hot key", "requires_compromised_key"),
    ("private key", "requires_compromised_key"),
    ("already guard", "inherited_guard"), ("nonreentrant", "inherited_guard"),
    ("modifier", "inherited_guard"), ("inherited", "inherited_guard"),
    ("out of scope", "out_of_scope"), ("scope", "out_of_scope"),
    ("no profit", "no_profitability"), ("not profitable", "no_profitability"),
    ("no economic", "no_profitability"),
    ("impossible", "impossible_state"), ("unreachable", "impossible_state"),
    ("liquidity", "unrealistic_liquidity"), ("drain the pool", "unrealistic_liquidity"),
    ("duplicate", "duplicate_pattern"),
    ("admin", "admin_attacker"), ("owner", "admin_attacker"), ("privileged", "admin_attacker"),
    ("trusted", "admin_attacker"),
]
_TAG_MAP = {
    "inherited_guard": "already_guarded", "admin_attacker": "admin_only",
    "impossible_state": "impossible_state", "no_profitability": "no_profitability",
    "non_exploitable": "non_exploitable", "unrealistic_liquidity": "unrealistic_liquidity",
    "requires_compromised_key": "requires_compromised_key",
    "unverifiable_assumption": "unverifiable_assumption", "duplicate_pattern": "duplicate_pattern",
    "out_of_scope": "out_of_scope",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _proposed_dir() -> Path:
    d = audit_path("data/learning", "_proposed")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _infer_pattern(reason: str) -> str:
    r = (reason or "").lower()
    for kw, pat in _KEYWORD_PATTERN:
        if kw in r:
            return pat
    return "unverifiable_assumption"


def _append(path: Path, obj: dict) -> None:
    with path.open("a") as fh:
        fh.write(json.dumps(obj) + "\n")


def derive_from_record(record: dict) -> int:
    """Stage one learning candidate from a ground-truth record. Returns count staged (0/1)."""
    # Only learn from human-confirmed provenance.
    if record.get("evidence_class") not in {"human_confirmed", "platform_confirmed",
                                            "fork_confirmed", "manual_entry"}:
        return 0
    outcome = record.get("ground_truth_outcome", "")
    fid = record.get("finding_id", "")
    pdir = _proposed_dir()
    reason = record.get("rejection_reason") or record.get("evidence_summary") or ""

    if outcome == "invalid":
        pat = _infer_pattern(reason)
        _append(pdir / "rejection_rules.jsonl", {
            "rule_id": f"FP-PROP-{hex(int(time.time()))[2:]}",
            "pattern_type": pat,
            "trigger_conditions": [c.strip() for c in reason.split(";") if c.strip()] or [reason],
            "rejection_reason": reason,
            "vuln_type": record.get("vuln_type", "other"),
            "agent": record.get("agent", "any") or "any",
            "invalidation_tag": _TAG_MAP.get(pat, "unverifiable_assumption"),
            "confidence_threshold": 0.85,
            "trust_level": 5,
            "created_at": _now(),
            "source_finding": fid,
            "source_audit": record.get("source_audit", ""),
            "judge_outcome": "invalid",
            "_proposed": True,
            "_evidence_class": record.get("evidence_class"),
            "_source_file": record.get("source_file"),
        })
        return 1

    if outcome == "duplicate":
        _append(pdir / "duplicate_registry.jsonl", {
            "registry_id": f"DUP-PROP-{hex(int(time.time()))[2:]}",
            "vuln_type": record.get("vuln_type", ""),
            "title": record.get("title", ""),
            "root_cause_signature": (record.get("title", "") + " " + reason).strip(),
            "our_finding_id": fid,
            "our_audit": record.get("source_audit", ""),
            "duplicate_of_report": record.get("duplicate_of_report", ""),
            "platform": "",
            "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "_proposed": True,
            "_evidence_class": record.get("evidence_class"),
            "_source_file": record.get("source_file"),
        })
        return 1

    if outcome == "downgraded":
        note = (f"# proposed from {fid} ({record.get('source_audit','')}) "
                f"{record.get('evidence_class')}\n"
                f"{record.get('vuln_type','unknown')}:\n"
                f"  claimed: {record.get('claimed_severity','?')} → "
                f"final: {record.get('ground_truth_severity','?')}\n"
                f"  reason: {reason}\n")
        with (pdir / "severity_rules_additions.yaml").open("a") as fh:
            fh.write(note + "\n")
        return 1

    if outcome in {"accepted", "paid", "escalated"}:
        _append(pdir / "positive_patterns.jsonl", {
            "finding_id": fid,
            "source_audit": record.get("source_audit", ""),
            "vuln_type": record.get("vuln_type", ""),
            "title": record.get("title", ""),
            "outcome": outcome,
            "final_severity": record.get("ground_truth_severity", ""),
            "paid_amount": record.get("paid_amount", ""),
            "what_worked": record.get("evidence_summary", ""),
            "recorded_at": _now(),
            "_evidence_class": record.get("evidence_class"),
            "_source_file": record.get("source_file"),
        })
        return 1

    return 0


def derive_recall_sections(audit_id: str) -> int:
    """Recall Lab: stage a specialist-prompt-section proposal for each REASONING-GAP miss in a project's
    adjudication.json (label MISSED + read_file true). Coverage-gap misses (read_file false) are NOT staged
    here — they are a coverage fix, not a prompt fix. Writes the repo-level recall_sections backlog (alongside
    blind_eval_loop's recall_gap_backlog). Human authors the actual agents/<agent>.md section + test, then
    promotes. Returns count staged."""
    root = Path(__file__).resolve().parents[1]
    adj = root / "audits" / audit_id / "output" / "eval_ready" / "adjudication.json"
    if not adj.exists():
        print(f"no adjudication.json for {audit_id} — run scripts/adjudicate.py {audit_id} first", file=sys.stderr)
        return 0
    mech = {}
    mc_path = root / "config" / "mechanism_classes.json"
    if mc_path.exists():
        mech = json.loads(mc_path.read_text()).get("classes", {})
    backlog = root / "data" / "learning" / "_proposed" / "recall_sections.jsonl"
    backlog.parent.mkdir(parents=True, exist_ok=True)
    doc = json.loads(adj.read_text())
    staged = 0
    for r in doc.get("awarded", []):
        if r.get("label") != "MISSED" or r.get("read_file") is not True:
            continue
        cls = r.get("mechanism_class")
        meta = mech.get(cls, {}) if cls else {}
        if meta.get("status") == "design":
            continue  # design-opinion class — not prompt-addressable
        _append(backlog, {
            "proposal_id": f"RS-{hex(int(time.time()*1000))[2:]}",
            "kind": "recall_section",
            "source_audit": audit_id,
            "awarded_id": r["id"],
            "title": r.get("title"),
            "mechanism_class": cls,
            "suggested_agent": meta.get("agent"),
            "suggested_prompt_section": meta.get("prompt_section"),
            "gap_type": "reasoning_gap",
            "action": f"author a numbered section in agents/{meta.get('agent','<specialist>')}.md generalizing "
                      f"'{cls or 'this mechanism'}' (from {audit_id} {r['id']}) + add a tests/ regression test",
            "_proposed": True,
            "created_at": _now(),
        })
        staged += 1
    print(f"derive_learning: staged {staged} recall-section proposal(s) from {audit_id} -> {backlog}")
    return staged


def main() -> int:
    """Standalone. Default: stage learning candidates from the active audit's ground truth.
    --from-adjudication <id>: stage recall-section proposals from an eval project's reasoning-gap misses."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-adjudication", dest="from_adj", metavar="AUDIT_ID",
                    help="stage recall-section proposals from this eval project's adjudication.json")
    args = ap.parse_args()
    if args.from_adj:
        derive_recall_sections(args.from_adj)
        return 0
    gt = load_jsonl(audit_path("data/evaluation", "ground_truth.jsonl"))
    staged = sum(derive_from_record(r) for r in gt)
    print(f"derive_learning: staged {staged} candidate(s) from {len(gt)} ground-truth record(s)")
    print(f"  → {audit_path('data/learning', '_proposed')}  (human-run promote_learning.py to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
