# P272 — POC_RESULTS (Phase 7) — BLIND

Isolated project `pocs/p272/init/`. init-capital `contracts/` copied read-only to `src/`; deps: forge-std v1.9.6,
OZ v4.9.6, OZ-upgradeable v4.9.6. solc 0.8.19. `cd pocs/p272/init && forge test -vv`.

| candidate | tier | test | result | observed |
|---|---|---|---|---|
| **C-incentive** (min-floor-after-max-cap) | **B (REAL code)** | `C_LiqIncentiveCapOrdering.t.sol` | **PASS (2)** | `getLiqIncentiveMultiplier_e18` returns **3.0e18 > maxCap 1.5e18** when `min[mode]=3e18 > max=1.5e18` (floor overrides cap); control (min≤max) respects the cap |
| C-health-zero | PARTIAL | — | not run | NEEDS_MORE_RUNTIME (full deposit→borrow→underwater→liquidate stack) |
| C-coll-credit | PARTIAL | — | not run | NEEDS_MORE_RUNTIME (full health-factor stack) |

## C-incentive — exact mechanism, real-code runtime (Tier B)
A clone of the real `LiqIncentiveCalculator` (MockACM no-op governor) executes the actual
`getLiqIncentiveMultiplier_e18`. With `min[mode]=3e18 > max=1.5e18` (set via the independent real governor setters,
which lack a `min≤max` invariant), the multiplier returns **3.0e18, exceeding the intended 1.5e18 protocol-wide max
cap** — the `Math.max(min(...,max), min[mode])` ordering lets the per-mode floor override the global cap →
over-incentive / over-seizure for a liquidator. The control (min≤max) respects the cap. **L1/L2/L3:** L1 governor
config; L2 `maxLiqIncentiveMultiplier_e18` vs returned multiplier asserted; L3 multiplier > cap (invariant broken).
**Reachability caveat:** requires a `min>max` config — no on-chain invariant prevents it, but it is a
governance-misconfiguration precondition (recorded honestly).

## Honest tiering
C-incentive = Tier B (real production formula). C-health-zero / C-coll-credit = NEEDS_MORE_RUNTIME (heavy full-stack).
BLIND (no answer key consulted up to here). Hash: PoC `6b4f5189e43d03bd`.
