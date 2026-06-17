#!/usr/bin/env python3
"""
check_api_free.py — Guard: in api-free mode no pipeline stage can hard-stop.

Asserts that every stage in llm_runtime.SKILL_MAP either:
  • has a credit-free skill route (skill != None), or
  • is optional (optional == True, so it skips cleanly with no key).

A stage that is REQUIRED (optional False) and has NO skill would call require_llm()
and raise SystemExit when the key is absent — breaking the api-free guarantee. This
check fails loudly on any such stage so conversions can't silently regress.

Two tiers:
  • CRITICAL_PATH — stages on the analyze→/ite-audit→full→review_gate path. These MUST be
    safe now (skill route or optional); a required+no-skill stage here is a hard failure.
  • Deferred (everything else: Step-5 reasoning, PoC, FP autopsy) — P1/P2 conversions; an
    unconverted one is reported as a WARNING, not a failure, since the review_gate run never
    reaches it.

Exit 0 = critical path api-free safe. Exit 1 = a critical-path stage would hard-stop.

Usage:
    python scripts/check_api_free.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_runtime import SKILL_MAP, api_free_mode  # noqa: E402

# Stages reached by analyze → /ite-audit → full → review_gate (the eval-critical path).
CRITICAL_PATH = {
    "deep_analysis", "cross_agent_connector", "synthesize_compound",
    "multi_pass_confirm", "triage",
}


def _safe(info: dict) -> bool:
    return bool(info.get("skill")) or bool(info.get("optional"))


def main() -> int:
    print(f"api_free mode pinned: {api_free_mode()}")
    print(f"Stages in SKILL_MAP: {len(SKILL_MAP)}")

    converted = [s for s, i in SKILL_MAP.items() if i.get("skill")]
    optional  = [s for s, i in SKILL_MAP.items() if not i.get("skill") and i.get("optional")]
    print(f"  with skill route ({len(converted)}): {', '.join(sorted(converted)) or '—'}")
    print(f"  optional skip   ({len(optional)}): {', '.join(sorted(optional)) or '—'}")

    critical_offenders = [
        s for s, i in SKILL_MAP.items() if s in CRITICAL_PATH and not _safe(i)
    ]
    deferred_offenders = [
        s for s, i in SKILL_MAP.items() if s not in CRITICAL_PATH and not _safe(i)
    ]

    if deferred_offenders:
        print(f"\n[warn] {len(deferred_offenders)} deferred stage(s) not yet converted "
              f"(P1/P2, off the review_gate path): {', '.join(sorted(deferred_offenders))}")

    if critical_offenders:
        print(f"\n[FAIL] {len(critical_offenders)} CRITICAL-PATH stage(s) would HARD-STOP with no key: "
              f"{', '.join(sorted(critical_offenders))}")
        print("       Convert each to a /skill (prepare→skill→write) or mark optional in SKILL_MAP.")
        return 1

    print("\n[ok] critical path api-free safe: every analyze→review_gate stage routes to a "
          "skill or skips cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
