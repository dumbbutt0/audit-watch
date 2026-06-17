#!/usr/bin/env python3
"""
annotate_ledger_answer_key.py — POST-FREEZE ONLY: fill `answer_key_matched` in the cumulative deep-pass
ledger so a later analysis can ask "did the items we skipped/waived turn out to be real findings?".

This must run only AFTER the answer key is opened (scoring phase). It reads
output/eval_ready/ledger_answer_key_matches.json ({"matched_manifest_ids": [...]}) — produced by the
scorer from the match matrix — and stamps each item in output/deep_pass_cumulative.json. It NEVER touches
the frozen snapshot and is never called from the blind pipeline (which keeps answer_key_matched = null).

Usage: python scripts/annotate_ledger_answer_key.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402


def main() -> int:
    cum_p = audit_path("output") / "deep_pass_cumulative.json"
    matches_p = audit_path("output") / "eval_ready" / "ledger_answer_key_matches.json"
    if not cum_p.exists():
        print("[annotate] no deep_pass_cumulative.json — run deep_pass_ledger.py first", file=sys.stderr)
        return 1
    matched = set()
    if matches_p.exists():
        matched = set(json.loads(matches_p.read_text()).get("matched_manifest_ids", []))
    cum = json.loads(cum_p.read_text())
    n = 0
    for it in cum.get("items", []):
        hit = it["manifest_id"] in matched
        it["answer_key_matched"] = hit
        n += int(hit)
    skipped_or_waived_hits = [it for it in cum.get("items", [])
                              if it.get("answer_key_matched") and it.get("latest_type") in ("skipped", "waived")]
    cum["answer_key_matched_total"] = n
    cum["skipped_or_waived_that_were_real"] = [it["manifest_id"] for it in skipped_or_waived_hits]
    cum_p.write_text(json.dumps(cum, indent=2))
    print(f"[annotate] stamped {n} answer-key matches; "
          f"{len(skipped_or_waived_hits)} of them were SKIPPED/WAIVED (recall leak).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
