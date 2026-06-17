# P275 — POC_INTENT (Phase 7) — claims frozen BEFORE code

Honest framing: these PoCs prove/refute the **deviations found blind**, not (yet) a confirmed awarded mechanism. Tiers
per P271. The real KatanaV3Pool/KatanaGovernance require heavy factory/beacon/governance wiring (via-IR project);
deploying them for these specific guards is disproportionate, so the access gate is proven by **Tier-C faithful
reproduction** of the exact guard logic (the precise lines copied into a harness, no contest-source edit), clearly
labeled.

## PoC-1 — `KatanaV3Pool.swap` `tx.origin`-based authorization gate (M1, ACCESS) — Tier C (faithful reproduction)
- **Exact claim:** the swap authorization is `if (tx.origin != address(0)) require(msg.sender == router, "IR")` — an
  authorization decision driven by `tx.origin`.
- **Setup:** a harness contract reproducing the exact guard (`router` immutable; `swapGuard(...)` containing the
  verbatim 2-line check) — faithful reproduction, no real deployment.
- **Tx/assert:**
  - tx.origin != 0, msg.sender != router → **reverts `IR`** (auth enforced).
  - tx.origin != 0, msg.sender == router → passes.
  - tx.origin == 0 (simulation), msg.sender != router → **passes (auth skipped)** — the deviation.
- **Refutation:** if the guard reverts for a non-router caller even when tx.origin==0, the deviation claim is refuted.
- **Honest bound:** demonstrates the *pattern/deviation*; on-chain a state-changing tx has tx.origin≠0, so this is not
  by itself a profitable on-chain exploit. Recorded PRE_REVEAL_PARTIAL_CANDIDATE.

## PoC-2 — concentrated-liquidity conservation (M3, SHARE) — Tier C (negative control)
- **Exact claim (control):** Uniswap-V3-style liquidity↔amount conversion conserves (round-trip mint then burn of the
  same liquidity does not create value), i.e. the pool math is **not** the bug.
- **Setup:** faithful reproduction of the `getAmount0Delta/getAmount1Delta`-style rounding (mint rounds up owed, burn
  rounds down returned) over a fixed tick range.
- **Assert:** amount returned on burn ≤ amount paid on mint (no value creation) — control holds.
- **Refutation:** if burn returns more than mint took, the control fails (would indicate a real math bug).

## Not advanced
- M2 `swap_callback` (ORDER): callback validation matches canonical Uniswap; no falsifiable exact hypothesis →
  NEEDS_MORE_RUNTIME, no PoC.
