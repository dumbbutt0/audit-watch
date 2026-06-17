# bakerfi — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)

3 loci selected before the key was opened. All `BASE_BORN_INCOMPLETE`. ≥1 oracle/state (L4) and ≥1 accounting
(L5). Disclosed-exposed areas (create-time reentrancy; ERC4626 share-accounting) not selected.

## L4 ← B1 — `StrategyLeverage._getPosition` staleness OR-logic (oracle / state-transition)
- **Why selected (pre-reveal):** an OR where AND is expected is a high-yield staleness pattern across the whole valuation path (deposit/withdraw/harvest all call `_getPosition`).
- **Signal:** base rank #1; oracle valuation locus feeding totalAssets.
- **What base already completed:** decoded the boolean — reverts only if *both* feeds stale; one stale feed passes.
- **What remained incomplete:** whether `getSafeLatestPrice(priceMaxAge)` already reverts on stale (making the gate moot), and the concrete misvaluation/profit if it does not — not computed.

## L5 ← B2 — `StrategyLeverage.harvest` P&L-only-when-deltaDebt==0 (accounting / invariant-delta)
- **Why selected (pre-reveal):** P&L is the input to Vault's performance-fee mint; a conditional that skips P&L on debt-adjustment harvests is an accounting-integrity risk.
- **Signal:** base rank #2 + accounting A2 on harvest.
- **What base already completed:** saw `balanceChange` set only in the `deltaDebt == 0` branches; `_deployedAmount` updated regardless.
- **What remained incomplete:** who loses (fee receiver? LPs?) and whether it's amplifiable / griefable — not computed.

## L6 ← B3 — `StrategyLeverage._undeploy` stale `_pendingAmount` (state-transition)
- **Why selected (pre-reveal):** an explicitly-not-cleared cross-call state variable is a stale-read hazard.
- **Signal:** base rank #3 + accounting A2/A4 on _undeploy/_repayAndWithdraw.
- **What base already completed:** saw `_pendingAmount` read at L517 with a "not cleared to save gas" comment.
- **What remained incomplete:** a concrete path where `_pendingAmount` is read stale (set in a prior tx, not refreshed) causing wrong `_deployedAmount`/withdraw — not traced.

**FREEZE:** final, recorded before reveal.
