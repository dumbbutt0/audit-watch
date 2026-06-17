#!/usr/bin/env python3
"""
check_no_bare_anthropic.py — regression guard for the no-silent-fail / zero-API contract.

Every API-backed script must acquire its Claude client through scripts/llm_runtime.py
(`require_llm()` for required stages, `optional_llm()` for default-path enhancers) so that a
missing ANTHROPIC_API_KEY produces a single actionable message (or a clean skip) instead of a
cryptic SDK `TypeError` mid-run — and never an unexpected credit charge.

This guard fails (exit 1) if any file under scripts/ or tools/ constructs `anthropic.Anthropic(`
directly, except the small allowlist below. Wire it into CI / run after editing API scripts.

Usage:
    python scripts/check_no_bare_anthropic.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files allowed to construct the client directly:
#   llm_runtime.py    — the guard itself (this is where construction is supposed to live)
#   solodit_scraper.py — one-time KB-build utility, not in the audit run path; it already
#                        key-guards its Claude calls and imports anthropic lazily inside the
#                        guarded branch, so it cannot silently fail or surprise-charge.
#   dashboard.py       — long-running HTTP server. Its /api/chat handler already returns a
#                        clean "ANTHROPIC_API_KEY is not set" JSON response when no key is
#                        present and imports anthropic lazily; it must NOT use require_llm()
#                        because a SystemExit would kill the server process.
ALLOWLIST = {"llm_runtime.py", "solodit_scraper.py", "dashboard.py", "check_no_bare_anthropic.py"}

CONSTRUCT_RE = re.compile(r"anthropic\.Anthropic\s*\(")


def main() -> int:
    offenders: list[str] = []
    for base in ("scripts", "tools"):
        for path in (ROOT / base).rglob("*.py"):
            if path.name in ALLOWLIST:
                continue
            try:
                text = path.read_text()
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if CONSTRUCT_RE.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")

    if offenders:
        print("[check_no_bare_anthropic] FAIL — direct anthropic.Anthropic() construction found.")
        print("  Route these through scripts/llm_runtime.py (require_llm / optional_llm) so a")
        print("  missing API key fails actionably (or skips) instead of crashing or charging:")
        for o in offenders:
            print(f"    {o}")
        return 1

    print("[check_no_bare_anthropic] OK — all API scripts acquire their client via llm_runtime "
          "(allowlist: " + ", ".join(sorted(ALLOWLIST)) + ").")
    return 0


if __name__ == "__main__":
    sys.exit(main())
