#!/usr/bin/env python3
"""
auto_promote_learning.py — Recall-safe AUTO promotion of staged learning candidates.

This is the automated, non-human-gated counterpart to promote_learning.py. It applies the SAME
validation a careful human reviewer would, so an auto-generated rule can never silently suppress a
future valid finding (the exact risk derive_learning.py:5-8 warns about):

  A staged candidate auto-promotes only if it is
    (1) CONFIRMED   — derived from a human/platform/fork-confirmed (or manual) ground-truth outcome,
    (2) RECALL-SAFE — it would NOT cause any KNOWN-VALID finding to be rejected (rejection rules only;
                      reuses fp_pattern_check's own similarity + reject logic — the pipeline's oracle), and
    (3) NON-DUPLICATE — its rule_id and structural signature are not already in the shared rules.
  Anything that fails stays in data/learning/_proposed/ for the human promote_learning.py path.

Isolation / integrity:
  - Auto-promoted rules are written to SEPARATE files, never to the integrity-pinned baselines:
        rejection → data/fp_autopsies/auto_promoted_rules.jsonl
        duplicate → data/auto_promoted_duplicate_registry.jsonl
        severity  → audits/<active>/data/learning/severity_rules.yaml  (per-audit, not pinned)
    The curated data/fp_autopsies/rejection_rules.jsonl stays byte-identical. Reversible by deleting
    the auto files.
  - Candidates explicitly flagged human-only (status == "PROPOSED_HUMAN_PROMOTE_REQUIRED" or
    _human_only: true) are skipped. Only the canonical derive_learning staging filenames are processed
    (campaign proposal files like p300_*.jsonl are never touched).
  - Eval/blind paths must call run(eval_mode=True) (or leave disable_in_eval set) so learning never
    contaminates a blind recall measurement.

Usage:
    python scripts/auto_promote_learning.py            # promote validated candidates from active audit
    python scripts/auto_promote_learning.py --dry-run  # show decisions, write nothing
    python scripts/auto_promote_learning.py --kind rejection
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, load_jsonl, list_audits
import fp_pattern_check  # reuse the pipeline's similarity + reject oracle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDITS_DIR = PROJECT_ROOT / "audits"
SHARED_REJECTION = PROJECT_ROOT / "data" / "fp_autopsies" / "rejection_rules.jsonl"   # read-only here
AUTO_REJECTION = PROJECT_ROOT / "data" / "fp_autopsies" / "auto_promoted_rules.jsonl"
AUTO_DUPES = PROJECT_ROOT / "data" / "auto_promoted_duplicate_registry.jsonl"
CONFIG_FILE = PROJECT_ROOT / "config" / "agent_policy.json"

CONFIRMED = {"human_confirmed", "platform_confirmed", "fork_confirmed", "manual_entry"}
VALID_OUTCOMES = {"accepted", "paid", "escalated"}

# canonical derive_learning staging filenames (matches promote_learning's KINDS)
KIND_FILES = {
    "rejection": "rejection_rules.jsonl",
    "duplicate": "duplicate_registry.jsonl",
    "severity": "severity_rules_additions.yaml",
}

DEFAULT_CONFIG = {
    "enabled": True,
    "require_recall_safety": True,
    "require_dedup": True,
    "kinds": ["rejection", "duplicate", "severity"],
    "disable_in_eval": True,
}


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    try:
        pol = json.loads(CONFIG_FILE.read_text())
        cfg.update(pol.get("auto_promote_learning", {}) or {})
    except (OSError, json.JSONDecodeError):
        pass
    return cfg


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _strip_internal(obj: dict) -> dict:
    return {k: v for k, v in obj.items() if not k.startswith("_")}


def _confirmed(c: dict) -> bool:
    return c.get("_evidence_class") in CONFIRMED


def _human_only(c: dict) -> bool:
    status = str(c.get("status", ""))
    return status.startswith("PROPOSED_HUMAN") or bool(c.get("_human_only"))


def _signature(rule: dict) -> str:
    """Structural identity of a rejection rule (independent of its generated rule_id)."""
    triggers = "|".join(sorted(t.strip().lower() for t in rule.get("trigger_conditions", []) if t.strip()))
    return f"{rule.get('pattern_type','')}::{rule.get('vuln_type','')}::{triggers}"


def _existing_rejection_index() -> tuple[set[str], set[str]]:
    """Return (rule_ids, signatures) already present in the curated baseline + auto file."""
    ids: set[str] = set()
    sigs: set[str] = set()
    for path in (SHARED_REJECTION, AUTO_REJECTION):
        for r in load_jsonl(path) if path.exists() else []:
            if r.get("rule_id"):
                ids.add(r["rule_id"])
            sigs.add(_signature(r))
    return ids, sigs


def _existing_dupe_ids() -> set[str]:
    ids: set[str] = set()
    for path in (PROJECT_ROOT / "data" / "duplicate_registry.jsonl", AUTO_DUPES):
        for r in load_jsonl(path) if path.exists() else []:
            sig = r.get("root_cause_signature") or r.get("registry_id") or ""
            if sig:
                ids.add(sig.strip().lower())
    return ids


def tp_corpus() -> list[dict]:
    """Known-VALID findings across all audits, as pseudo-findings for the recall-safety oracle."""
    corpus: list[dict] = []
    for audit in list_audits():
        aid = audit.get("audit_id") or audit.get("id")
        if not aid:
            continue
        gt = AUDITS_DIR / aid / "data" / "evaluation" / "ground_truth.jsonl"
        for r in load_jsonl(gt) if gt.exists() else []:
            if r.get("ground_truth_outcome") not in VALID_OUTCOMES:
                continue
            desc = " ".join(x for x in (r.get("title", ""), r.get("evidence_summary", "")) if x)
            corpus.append({
                "vuln_type": r.get("vuln_type", ""),
                "description": desc,
                "impact": "",
                "_source_agent": r.get("agent", ""),
            })
    return corpus


def is_recall_safe(rule: dict, corpus: list[dict]) -> bool:
    """A rule is recall-safe iff it would not 'reject' any known-valid finding."""
    for finding in corpus:
        matches = fp_pattern_check.check_against_rules(finding, [rule])
        if fp_pattern_check.compute_recommended_action(matches) == "reject":
            return False
    return True


def validate_candidate(c: dict, kind: str, cfg: dict, rej_ids: set[str], rej_sigs: set[str],
                       dupe_sigs: set[str], corpus: list[dict]) -> tuple[bool, str]:
    if _human_only(c):
        return False, "human_only_marked"
    if not _confirmed(c):
        return False, "unconfirmed_provenance"
    if kind == "rejection":
        if cfg.get("require_dedup", True) and (c.get("rule_id") in rej_ids or _signature(c) in rej_sigs):
            return False, "duplicate"
        if cfg.get("require_recall_safety", True) and not is_recall_safe(c, corpus):
            return False, "recall_regression"
        return True, "recall_safe"
    if kind == "duplicate":
        sig = (c.get("root_cause_signature") or "").strip().lower()
        if cfg.get("require_dedup", True) and sig and sig in dupe_sigs:
            return False, "duplicate"
        return True, "confirmed"
    return True, "confirmed"


def _append(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def run(kinds: list[str] | None = None, eval_mode: bool = False, dry_run: bool = False) -> dict:
    cfg = load_config()
    summary = {"enabled": cfg["enabled"], "promoted": 0, "left_staged": 0, "reasons": {}, "details": []}
    if not cfg.get("enabled", True):
        summary["skipped"] = "disabled"
        return summary
    if eval_mode and cfg.get("disable_in_eval", True):
        summary["skipped"] = "eval_mode"
        return summary

    kinds = kinds or cfg.get("kinds", list(KIND_FILES))
    pdir = audit_path("data/learning", "_proposed")
    if not pdir.exists():
        return summary

    rej_ids, rej_sigs = _existing_rejection_index()
    dupe_sigs = _existing_dupe_ids()
    corpus = tp_corpus() if "rejection" in kinds else []
    archive = pdir / f"_autopromoted_{_utc()}"

    for kind in kinds:
        fname = KIND_FILES.get(kind)
        if not fname:
            continue
        src = pdir / fname
        if not src.exists() or src.stat().st_size == 0:
            continue

        # severity is freeform per-audit yaml notes: append-only (confirmed/dedup not per-line parseable)
        if kind == "severity":
            text = src.read_text()
            summary["details"].append({"kind": "severity", "decision": "append", "lines": text.count("\n")})
            if not dry_run:
                dest = audit_path("data/learning", "severity_rules.yaml")
                with dest.open("a") as fh:
                    fh.write("\n# ── auto-promoted " + _utc() + " ──\n" + text)
                archive.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(archive / fname))
            continue

        candidates = load_jsonl(src)
        promote: list[dict] = []
        keep: list[dict] = []
        for c in candidates:
            ok, reason = validate_candidate(c, kind, cfg, rej_ids, rej_sigs, dupe_sigs, corpus)
            summary["reasons"][reason] = summary["reasons"].get(reason, 0) + 1
            cid = c.get("rule_id") or c.get("registry_id") or "?"
            summary["details"].append({"kind": kind, "id": cid, "ok": ok, "reason": reason})
            if ok:
                stamped = _strip_internal(c)
                stamped["promoted_by"] = "auto:recall_safe_v1"
                stamped["promoted_at"] = _utc()
                promote.append(stamped)
                # keep the in-run dedup index current so a batch can't promote two identical rules
                if kind == "rejection":
                    if stamped.get("rule_id"):
                        rej_ids.add(stamped["rule_id"])
                    rej_sigs.add(_signature(stamped))
                elif kind == "duplicate":
                    sig = (stamped.get("root_cause_signature") or "").strip().lower()
                    if sig:
                        dupe_sigs.add(sig)
            else:
                keep.append(c)

        summary["promoted"] += len(promote)
        summary["left_staged"] += len(keep)
        if dry_run or not promote:
            continue

        dest = AUTO_REJECTION if kind == "rejection" else AUTO_DUPES
        _append(dest, promote)
        # rewrite staging with only the candidates left for human review; archive the originals
        archive.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(src), str(archive / fname))
        if keep:
            src.write_text("\n".join(json.dumps(c) for c in keep) + "\n")
        else:
            src.unlink()

    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto-promote validated (recall-safe) learning candidates")
    ap.add_argument("--dry-run", action="store_true", help="Show decisions, write nothing")
    ap.add_argument("--kind", choices=sorted(KIND_FILES), default=None, help="Only this kind")
    ap.add_argument("--eval", action="store_true", help="Eval/blind context — honors disable_in_eval")
    args = ap.parse_args()

    s = run(kinds=[args.kind] if args.kind else None, eval_mode=args.eval, dry_run=args.dry_run)
    if s.get("skipped"):
        print(f"auto_promote_learning: skipped ({s['skipped']}).")
        return 0
    print(f"auto_promote_learning: promoted {s['promoted']}, left staged {s['left_staged']} "
          f"{'(dry-run) ' if args.dry_run else ''}— reasons: {s['reasons']}")
    for d in s["details"]:
        if d.get("kind") == "severity":
            continue
        mark = "✓ promote" if d["ok"] else "· stay"
        print(f"   {mark} [{d['kind']}] {d.get('id','?')} — {d['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
