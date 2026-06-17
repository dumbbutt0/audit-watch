# P271 — LENDING_COMPLETION_CHECKLIST (reusable, pre-PoC-intent)

Use BEFORE freezing PoC intent on any lending/CDP/vault routed candidate. Each item is a question whose answer
sharpens a family-level locus hit toward an exact mechanism. (★ = directly recovered a Wise High in P271.)

## Borrower / lender setup
- [ ] Minimal users + tokens to reach the affected function? deposit → enable collateral → borrow path identified?
- [ ] Which functions are permissionless vs role-gated (liquidator/keeper/owner)?

## Collateral accounting
- [ ] ★ **Private vs public/normal collateral split** — is each tracked separately? Does a percentage computed on
  ONE get applied to BOTH? (Wise H-04: `removePercentage` from private collateral applied to normal shares too.)
- [ ] pure/segregated collateral mappings vs share-based deposits — distinct or conflated?

## Debt accounting
- [ ] Borrow shares vs raw debt; interest index applied consistently on borrow/repay/liquidate?

## Liquidation
- [ ] Threshold/health computed from which collateral set? Does the uncollateralized/special-case branch gate the
  RIGHT quantity?
- [ ] ★ **Guard ordering** — is the special-case check (e.g. `unCollateralized`) BEFORE or AFTER the value-extraction
  math? (Wise H-04: check is after the normal-share cashout → over-extraction.)
- [ ] Liquidation recipient: who receives collateral; can the liquidator extract more than they repay?

## Position-vs-global accounting
- [ ] ★ **SET vs INCREMENT** — is a position-level accumulator OVERWRITTEN while the global is INCREMENTED (or vice
  versa)? What happens across ≥2 repeated events (partial liquidations)? (Wise H-03: position SET, global INCREMENT.)
- [ ] On payback/clear, is the deduction the CUMULATIVE position value or only the LATEST?
- [ ] Conservation invariant: after a position is fully cleared, does the global return to its pre-event value?

## Fee manager / bad-debt paths
- [ ] ★ Bad-debt: liquidation-path setter vs heartbeat/update-path setter — do they use the same SET/INCREMENT
  semantics? (Wise H-03: `checkBadDebtLiquidation` sets; `_updateUserBadDebt` tracks diff — divergent.)
- [ ] Does any downstream gate (e.g. `claimFees*` requiring `totalBadDebt == 0`) get bricked by residual fake state?

## Share / asset conversion + rounding
- [ ] convert direction (round for/against user)? first-depositor/virtual-share offset present?
- [ ] Are assets internally tracked (donation-safe) or `balanceOf`-based (donatable)?

## Oracle / threshold movement
- [ ] Can the price/health be moved (legitimately or via manipulation) to reach the liquidation zone?

## Invariant deltas to assert in the PoC
- [ ] Position-cleared → global accumulator == pre-event value.
- [ ] Liquidator receive ≤ repaid-value × allowed-percentage on the CORRECT collateral set.
- [ ] No value extractable from an ungated/special-case quantity.

## PoC tiering (from P271)
- Accounting/ordering bug in an internal/abstract helper → **Tier B** via inherit-and-expose-internal harness
  (executes real production statements; minimal ctor mocks).
- Bug in a deeply-stateful private function → **Tier C** faithful control-flow reproduction (transcribe exact
  ordering + real formula; disclose limitation) until a Tier A full-stack runtime is built.
