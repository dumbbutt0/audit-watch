# P125 — Decision: BootstrapPool invariants (cross-contract pivot)

## Terminal state: **KILLED_RUNTIME**

Runtime decided. The harness exercised the **real bonding-curve math** and all five economic invariants held under
executed permissionless trading — not source-only reasoning. This is the **first cross-contract pricing verdict** in
the arc (P120–P124 were thin-router KILLs that *delegated* this pricing and deferred it as NEEDS_CONTEXT).

| KILLED condition (spec) | Evidence (runtime) |
|---|---|
| no value extraction via round-trip | Probe A: `buy(C)` then immediate `sell` returns `< C` — fees make a lone round-trip strictly lossy (PASS). |
| pricing soundness (k) | Probe B: `k = reserveCurrency*reserveAgent` is non-decreasing after both a buy and a sell (PASS). |
| solvency | Probe C: a sell quoting more currency than the pool's real balance reverts; the virtual `phantom` reserve inflates the *quote* but never the *payout* (PASS). |
| permissionless `sweepFees` safe | Probe D: an arbitrary caller's `sweepFees()` leaves `getReserves()` unchanged, zeroes the fee accumulators, and routes exactly the accrued fee to `feeTo` (PASS). |
| donation-safety | Probe E: selling the same position after a currency donation never recoups the donation (`outYes < outNo + Cd`) — a donor takes a net loss (PASS). |

**Verdict:** `BootstrapPool` is an arbitrage-free, constant-product-conserving, solvent, donation-safe CPMM with a
consistent virtual (`phantom`) currency reserve. A permissionless actor cannot extract value from the pricing engine
at the per-trade invariant level → **KILLED_RUNTIME**. The pricing that `AgentRouter.buy`/`sell` delegated to — and
that P123/P124 could only defer — holds up under the real math. The cross-contract harness reached and settled the
deferred invariants, breaking the recurring NEEDS_CONTEXT ceiling for this surface.

## Out-of-scope (recorded as NEEDS_CONTEXT, not settled here)
Reserve carryover at `kill()` → `LiquidityManager.moveLiquidity` migration (mis-pricing the Fraxswap pair) — the
awarded **IQ-M-01** flow. That is a distinct cross-contract question from the per-trade pool invariants tested here and
is not promoted.

## Scope / honesty notes
- The harness uses the REAL pool/curve/fee/phantom math; only the standard ERC20 tokens are mocked (not the subject).
- HARNESS_MODERATE; no fork. iq-ai `src/` unmutated.
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).

## Hard-stop self-check
- KILLED_RUNTIME claimed only with passing runtime tests (Probes A–E all PASS, executed). ✓
- No source-only reasoning used as runtime proof — k values, round-trip deltas, revert, sweep deltas, donation
  comparison are executed assertions. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- iq-ai `src/` **unmutated** — `BootstrapPool.sol` (sha 6bd9e4bc); the harness is a test-only file under
  `/tmp/p102-iqai/test/audit/`. ✓
