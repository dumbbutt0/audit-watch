# P271 — VERDICT

## Verdict: A — LENDING_SCAFFOLD_READY_FOR_FRESH_RECOVERY_TEST

### Why
P271 built a reusable lending runtime scaffold + completion checklist and used it to sharpen BOTH Wise family-level
awarded-locus hits into **exact mechanisms with runtime evidence** (CALIBRATION, post-reveal):
- **H-03 (bad-debt) — Tier B, REAL production code:** a `BadDebtHarness is FeeManagerHelper` executes the real
  `_increaseTotalBadDebt`/`_setBadDebtPosition`/`_decreaseTotalBadDebt`/`_eraseBadDebtUser` and proves the exact
  **increment(global)-vs-set(position)** asymmetry: after 2 partial liquidations + payback, `totalBadDebtETH` retains
  100e15 of "fake debt" (bricks `claimFeesBeneficial`); the corrected reference clears to 0.
- **H-04 (liquidation misallocation) — Tier C, faithful reproduction:** proves the exact **branch-ordering** bug —
  the normal-share-sized `potentialPureExtraCashout` is granted before the `unCollateralized` early-return, so an
  uncollateralized liquidation over-extracts by exactly `removePct × userShares`.

A's bar is met: ≥1 Wise mechanism sharpened family→exact (both) · ≥1 runtime/strong-partial PoC supports it (H-03 is
real-production-code Tier B; H-04 is a strong Tier-C reproduction) · scaffold reusable + documented (project template
+ two PoC patterns + LENDING_COMPLETION_CHECKLIST) · no production-authority leakage · frozen modules unchanged ·
tests green (3/3).

### Honest bounds
- **CALIBRATION, not fresh recovery** — the reveal was used by design; the blind test is P272.
- **No full Tier-A runtime** — the calibration showed these two mechanisms are localized accounting asymmetries
  provable at Tier B/C; a full deposit→borrow→liquidate simulator is future work for mechanisms needing cross-contract
  state evolution. The reusable deliverable is the **patterns + checklist**, not a one-click lending simulator.
- **H-04 is Tier C** (faithful reproduction of the deployed private function), one notch below H-03's Tier B.

### Not B / C / D
- Not **B** (scaffold improves setup but exact/runtime still partial): both mechanisms reached exact + runtime.
- Not **C** (exact still unclear): both exact mechanisms are isolated and runtime-demonstrated.
- Not **D** (constraint violation): research-only, advisory; frozen P260/P262/P264/P267/P269 + 5 forbidden
  byte-identical; active audit unchanged; contest source copied read-only into `pocs/p271/` (origin `/tmp` unmutated).

### The arc
P266 RANKING → P267 fixed · P268 TRIAGE → P269 fixed · P270 routed onto awarded loci (family-level) · **P271: a
reusable lending scaffold turns family-level locus hits into exact, runtime-proven mechanisms** (the key lesson:
family→exact for these lending bugs is a STRUCTURAL question — SET-vs-INCREMENT position/global accumulators, and the
ORDER of a special-case guard vs the value math — now encoded in the checklist).

### Required next step — P272
Fresh full-path rerun with the lending scaffold + LENDING_COMPLETION_CHECKLIST available (used BLIND, pre-reveal), on
a fresh scored lending contest, scoring **exact awarded recovery**. Production authority remains **withheld**.

### Constraints honored
No frozen-module tuning: P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c` · P269 `63c88d02`
byte-identical. 5 forbidden byte-identical. Active audit `size-credit-2024-06-blind` unchanged. PoCs isolated under
`pocs/p271/`; contest source copied read-only.
