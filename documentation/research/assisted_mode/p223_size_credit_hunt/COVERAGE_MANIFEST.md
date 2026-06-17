# P223 — Coverage manifest (Step 3)

Built fresh in the blind workspace, **source-only**, deterministic, no LLM.

## Command
```
python scripts/sandbox_check.py audits/size-credit-2024-06-blind/contracts/2024-06-size   # CLEAN: 39 files, 0 flags
python scripts/build_coverage_manifest.py --contract audits/size-credit-2024-06-blind/contracts/2024-06-size
python scripts/init_coverage_dispositions.py
```

## Result
- **221 items** (193 in-scope) — by kind: function 198, constant 10, immutable 8, constructor 4, initializer 1.
  Matches the original eval workspace's 221/193 (denominator is deterministic from source).
- High-surface (score≥3, in-scope): **97**; cross-chain-sensitive: 4; library/internal risk-logic boosted: 28.
- Dispositions: **193 unassigned (in-scope)** + 28 `deferred_out_of_scope` (mocks/tests/Mock* by glob). Fresh
  (added 221, preserved 0) — no prior assignments leaked from the original eval.

## Note on static.json (signals omitted, denominator unaffected)
The contracts pin `pragma solidity 0.8.23` (exact); the installed solc set is {0.8.19, 0.8.20, 0.8.24, 0.8.25,
0.8.35} and slither would additionally need the OZ/dependency remappings configured. `static.json` only
supplies optional **signal tags** (tainted sinks, risk scores) — it does **not** define the denominator, which
`build_coverage_manifest.py` parses directly from source. Discovery in this hunt is via source-reading
deep_trace subagents (not static signals), so the source-only manifest is the correct, complete review
denominator. Recorded here for honesty; not a gap in coverage.
