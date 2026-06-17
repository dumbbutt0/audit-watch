# P125 — Runtime matrix

Command: `forge test --match-contract BootstrapPoolInvariantRuntime --evm-version cancun -vvv`
Project: `/tmp/p102-iqai` (iq-ai repo; REAL `BootstrapPool`, only ERC20s mocked; `src/` unmutated; test-only file under `test/audit/`).
Pool: `initialPrice = 1e18`, `bootstrapAmount = 1e24`, `feeBps = 100` (1%) ⇒ `phantom = 1e24`, initial reserves `1e24 : 1e24`.

| Probe | Invariant | Result | Evidence |
|---|---|---|---|
| **A** | round-trip strictly lossy | **PASS** | `buy(1000e18)` → `g` agent; `sell(g)` → `cBack < 1000e18` (fees ⇒ no free extraction) |
| **B** | constant-product `k` non-decreasing | **PASS** | `k` after buy ≥ `k` before; `k` after sell ≥ `k` after buy (`k = reserveCurrency*reserveAgent`) |
| **C** | solvency (no insolvent payout) | **PASS** | after seeding currency, a 100e18-agent sell is honored; a 5,000,000e18-agent sell (quote > real currency) **reverts** — the phantom inflates the quote, not the payout |
| **D** | permissionless `sweepFees` reserve-neutral | **PASS** | arbitrary caller sweeps; `getReserves()` unchanged before/after; `currencyTokenFeeEarned`/`agentTokenFeeEarned` zeroed; `feeTo` received exactly the accrued fee (`2000e18 * 1% = 20e18`) |
| **E** | donation not profitable | **PASS** | two identical pools; `outYes` (sell after donating `Cd=1000e18`) `< outNo + Cd` — the donation is not recouped (donor net loss) |

All 5 probes pass (executed). Full log: `execution_output.txt`.

## Reading
The real bonding-curve engine is sound at the per-trade invariant level: it is arbitrage-free for a lone trader
(A), conserves/grows the constant product (B), is solvent — the virtual `phantom` reserve inflates only the *quote*,
while the post-payout `require` + `safeTransfer` prevent paying out currency the pool does not hold (C), routes fees
without disturbing reserves even under a permissionless sweep (D), and is donation-safe (E). The pricing that
`AgentRouter` (P123/P124) delegated to — and deferred as NEEDS_CONTEXT — holds up under the real math.

## Out of scope (NEEDS_CONTEXT)
Reserve carryover at `kill()` → `moveLiquidity` migration (the awarded IQ-M-01 area) — a different question than the
per-trade pool invariants tested here.
