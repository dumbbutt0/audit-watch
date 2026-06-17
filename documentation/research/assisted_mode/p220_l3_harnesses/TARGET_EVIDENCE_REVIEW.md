# P220 — Target evidence review

## ZETA-04 — onReceive missing whenNotPaused (== official H-13)
- **Mechanism.** `ZetaConnectorNonEth.onReceive` (`ZetaConnector.non-eth.sol:61-79`) carries `onlyTssAddress` only.
  The sibling `onRevert` (`:87-95`, `whenNotPaused onlyTssAddress`) and `send` (`:40`, `whenNotPaused`) are pause-gated.
  `pause()`/`_pause()` live in `ZetaConnector.base.sol` (OZ `Pausable`).
- **Source refs.** non-eth.sol:61 (bug), :95 (guarded sibling), base.sol:15 (`is Pausable`), :151 (`pause`).
- **Current L3.** NEEDS_HARNESS / STATIC_ONLY; empty PoC fields.
- **Card gaps.** PoC actual/expected/control/value-delta all unknown.
- **Harness must prove.** A paused connector still mints via onReceive; the guarded sibling reverts while paused.
- **Refute/downgrade if.** Pause actually blocks onReceive (it does not), or the only trigger is a fully-trusted
  admin with no security consequence (calibration handles this: TSS-gated → not auto-High).

## ZETA-10 — getEthFromZeta missing nonReentrant (cross-function reentrancy)
- **Mechanism.** `getEthFromZeta` (`ZetaTokenConsumerUniV3.strategy.sol:124-156`) does
  `destinationAddress.call{value: amountOut}("")` (`:152`) after swap+unwrap, with NO `nonReentrant`
  (only `getTokenFromZeta` has it, `:163`). Each call is self-funded: pull caller's zeta (`:132`) → swap →
  withdraw WETH → forward ETH. The consumer holds no pooled balances between calls.
- **Source refs.** UniV3.strategy.sol:124 (entry), :152 (external call), :163 (the one guarded sibling).
- **Current L3.** NEEDS_HARNESS; static note already doubts realized theft.
- **Card gaps.** PoC actual/expected/control unknown.
- **Harness must prove.** (a) reentrancy reachable (no guard); (b) whether any value is actually extracted.
- **Refute/downgrade if.** Attacker net worth unchanged and consumer retains nothing → theft refuted (expected).

## ZETA-11 — Trident getPools(...)[0] unvalidated (~ official H-10, wrong mechanism)
- **Mechanism.** `getZetaFromEth` (`ZetaTokenConsumerTrident.strategy.sol:74-97`) reads
  `poolFactory.getPools(token0,token1,0,1)` (`:82`) and uses `pairPools[0]` (`:88`) with no length/zero/legitimacy
  check; same shape in getZetaFromToken/getEthFromZeta. Empty array → `[0]` reverts (Panic 0x32, DoS).
- **Source refs.** Trident.strategy.sol:82 (getPools), :88 (`pairPools[0]`).
- **Current L3.** NEEDS_HARNESS; "fund-loss conditional on factory permissionlessness; empty → DoS".
- **Card gaps.** PoC actual/expected/control unknown.
- **Harness must prove.** Empty getPools()[0] bricks the swap path (DoS) with a control; distinguish DoS impact
  from the candidate's theft mechanism.
- **Refute/downgrade if.** The theft mechanism requires an external permissionless factory — not assertable from
  in-scope source → wrong-mechanism / DoS-only.
