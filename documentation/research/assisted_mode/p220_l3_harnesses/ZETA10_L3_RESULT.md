# ZETA-10 — L3 result: FAIL (theft refuted by executed harness)

**Harness.** `pocs/p220/test/ZETA10_reentrancy.t.sol` · real unmodified `ZetaTokenConsumerUniV3` ·
mocks: `MockWETH9` + `MockUniV3Router` (constant 1:1, pays output from its own pre-funded reserves) +
`AttackerReentrant` (destination re-enters `getEthFromZeta` once during the ETH callback).
**Command.** `forge test --match-contract ZETA10 -vv` → **2/2 PASS** (`pocs/p220/logs/ZETA10_run.log`).

## What was proven
- **(a) Reentrancy IS reachable.** The attacker's `receive()` re-enters `getEthFromZeta` and no `ReentrancyError`
  is thrown (`attacker.reentered() == true`) → the missing `nonReentrant` is a real code fact.
- **(b) But NO theft.** Accounting over the whole attack:
  - attacker spent exactly `2X = 200e18` zeta and received exactly `2X = 200e18` ETH (fair 1:1) → **net worth Δ = 0**;
  - consumer residual balances after the attack: `0` zeta, `0` WETH, `0` ETH.
  The consumer is a pure pass-through (pull → swap → forward); it pools no balances between calls, so cross-function
  reentrancy has nothing to drain. Every re-entrant call is self-funded by the attacker.
- **Control / expected.** Net-worth Δ == 0 and consumer residual == 0 despite a successful re-entry; the single-swap
  sanity case forwards `X=100e18` ETH and the consumer keeps 0.

## Classification & calibration
- **l3_status = FAIL** (the High THEFT claim does not materialize), `poc_tier = L3_REAL_CONTRACT_POC`,
  `impact_class = theft`, `dependency_mocks = external_only`.
- `decide()` → **calibrated_severity = invalid** (l3=FAIL with "refuted" in notes), `high_promotion_allowed = false`,
  blocker = `l3_status=FAIL`. The missing `nonReentrant` remains a real low/code-quality observation, not a High.
- **Scorecard P220 category: `L3_FAIL_DEMOTED`** (executed refutation; aligns with the prior static doubt).

## Honesty note
The mock router deliberately introduces no value (1:1, pays from its own reserves), so any attacker gain would have
had to come from the consumer. It did not. This is a clean, executed refutation — more useful than a fabricated PASS.
