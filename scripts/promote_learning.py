#!/usr/bin/env python3
"""
promote_learning.py — Human-gated promotion of staged learning candidates into shared rules.

derive_learning.py writes candidates to data/learning/_proposed/. Nothing affects the shared
project rules until a human runs this with --confirm. Default is a dry-run listing.

NOTE: Candidates that pass the recall-safe validation gate are now AUTO-promoted by
auto_promote_learning.py into the SEPARATE auto files (data/fp_autopsies/auto_promoted_rules.jsonl,
data/auto_promoted_duplicate_registry.jsonl). This human-gated path remains for candidates that the
gate left staged (unconfirmed provenance, recall regression, duplicate) and writes into the curated
baselines below.

    python scripts/promote_learning.py                 # list staged candidates (dry-run)
    python scripts/promote_learning.py --promote --confirm   # apply ALL staged candidates
    python scripts/promote_learning.py --promote --confirm --kind rejection

Targets:
    rejection → data/fp_autopsies/rejection_rules.jsonl   (project-level, shared)
    duplicate → data/duplicate_registry.jsonl             (project-level, shared)
    severity  → audits/<active>/data/learning/severity_rules.yaml (per-audit)
Promoted candidates are archived to _proposed/_promoted_<UTC>/ so they aren't re-applied.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, load_jsonl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHARED_REJECTION = PROJECT_ROOT / "data" / "fp_autopsies" / "rejection_rules.jsonl"
SHARED_DUPES = PROJECT_ROOT / "data" / "duplicate_registry.jsonl"

KINDS = {
    "rejection": ("rejection_rules.jsonl", SHARED_REJECTION),
    "duplicate": ("duplicate_registry.jsonl", SHARED_DUPES),
    "severity":  ("severity_rules_additions.yaml", None),  # per-audit yaml append
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _strip_internal(obj: dict) -> dict:
    return {k: v for k, v in obj.items() if not k.startswith("_")}


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote staged learning candidates (human-gated)")
    ap.add_argument("--promote", action="store_true", help="Apply candidates (else dry-run list)")
    ap.add_argument("--confirm", action="store_true", help="Required with --promote to actually write")
    ap.add_argument("--kind", choices=sorted(KINDS), default=None, help="Only this kind (default: all)")
    args = ap.parse_args()

    pdir = audit_path("data/learning", "_proposed")
    if not pdir.exists():
        print("No _proposed/ directory — nothing staged.")
        return 0

    kinds = [args.kind] if args.kind else list(KINDS)
    do_write = args.promote and args.confirm

    archive = pdir / f"_promoted_{_utc()}"
    promoted_total = 0

    for kind in kinds:
        fname, shared = KINDS[kind]
        src = pdir / fname
        if not src.exists() or src.stat().st_size == 0:
            continue

        if kind == "severity":
            text = src.read_text()
            print(f"[{kind}] {src} ({text.count(chr(10))} lines) → per-audit severity_rules.yaml")
            if do_write:
                dest = audit_path("data/learning", "severity_rules.yaml")
                with dest.open("a") as fh:
                    fh.write("\n# ── promoted " + _utc() + " ──\n" + text)
                archive.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(archive / fname))
                print(f"   applied → {dest}; archived → {archive/fname}")
            continue

        candidates = load_jsonl(src)
        print(f"[{kind}] {len(candidates)} candidate(s) in {src} → {shared}")
        for c in candidates:
            cid = c.get("rule_id") or c.get("registry_id") or "?"
            print(f"   - {cid}: {c.get('pattern_type') or c.get('vuln_type','')} "
                  f"({c.get('source_finding') or c.get('our_finding_id','')})")
        if do_write:
            shared.parent.mkdir(parents=True, exist_ok=True)
            with shared.open("a") as fh:
                for c in candidates:
                    fh.write(json.dumps(_strip_internal(c)) + "\n")
            archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(archive / fname))
            promoted_total += len(candidates)
            print(f"   applied {len(candidates)} → {shared}; archived → {archive/fname}")

    if not do_write:
        print("\nDry-run. Re-run with --promote --confirm to apply.")
    else:
        print(f"\nPromoted {promoted_total} rule/registry candidate(s). Shared rules updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
