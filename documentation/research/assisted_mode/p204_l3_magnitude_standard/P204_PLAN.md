# P204 — plan (L3 PoC/harness magnitude HIGH standard on decent)

## Goal
Prototype a harness-grade realized-impact HIGH standard: HIGH_CONFIRMED only if a concrete attacker tx, under
source-valid config + honest custody, realizes **material** theft/insolvency/permanent-loss/unauthorized-priv-control.
Test whether executable impact separates true High (H-01) from the false-Highs static gates over-confirmed (M-03,
decent-06, decent-12). Reuse frozen P202/P203 artifacts; build & run Foundry harnesses; no production change.

## Method
Self-contained Foundry project under `pocs/`: real decent contracts imported via a byte-identical copy
(`realsrc/`, production untouched); only **external deps mocked** (`OFTV2`, solmate `Owned`, forge-std `IERC20`,
`@uniswap IV3SwapRouter`); forge-std-free (inline `Vm` + assert base). L3 standard + harness matrix pre-registered;
honest custody (no artificial attacker/UTB funds).

## Sequence
precheck → L3_HIGH_STANDARD (pre-spec) → HARNESS_TARGET_MATRIX → H-01 positive harness → M-03 negative harness →
decent-06/12 false-High controls → L3 scoring → failure cases → recommendation/decision → integrity + memory.

## Decision space
L3_STANDARD_PROMISING · L3_STANDARD_PARTIAL · L3_STANDARD_FAILED_FALSE_HIGH · L3_STANDARD_FAILED_FALSE_DEMOTION ·
HARNESS_INCONCLUSIVE · INVALID_RUN.

## Outcome
`L3_STANDARD_PROMISING` — H-01 HIGH (executed material mint), M-03 + decent-06 demoted (no material theft under
honest custody), decent-12 NEEDS_HARNESS (source obstacle). HIGH bucket 6→1, 0 genuine-High loss. See
`P204_RECOMMENDATION.md`. 5/5 harness tests pass (`pocs/run_log.txt`); production byte-identical.
