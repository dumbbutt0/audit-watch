# P215 — HARNESS RESULTS

Cap = 3 harness attempts. Policy: build only when a candidate could be High, realized impact is unclear statically,
deps are manageable, and a control case is clear; never mock-manufacture the bug.

## ZETA-07 — ZRC20 zero gas fee (EXECUTED · 2/2 PASS)
- **Real source, unmodified:** `pocs/p215/realsrc/ZRC20.sol` + `Interfaces.sol` (copied byte-for-byte from the holdout
  `zevm/`). Only an `ISystem` is mocked (returns a gas-coin ZRC20 + 1 gwei gas price); the subject ZRC20 is real.
- **Test:** `pocs/p215/test/ZETA07_zeroGasFee.t.sol` — `forge test --match-contract ZETA07 -vv` (solc 0.8.7).
- **Result:** `test_zeroGasFee_whenGasLimitZero` PASS — with `GAS_LIMIT=0` & flat-fee 0, `withdrawGasFee()` returns
  `fee==0`, `withdraw()` burns the amount and the user's gas-coin balance is **unchanged** (zero fee paid).
  `test_control_nonZeroFee_whenGasLimitSet` PASS — with `GAS_LIMIT=21000`, `fee == gasPrice*21000 > 0` and the fee **is**
  charged. Control demonstrates expected success.
- **L3 verdict:** `l3_status=PASS`, but **calibrated Medium** (not High): the precondition `GAS_LIMIT=0` is set by the
  privileged FUNGIBLE_MODULE, so `attacker_model=conditional` ⇒ not a permissionless High. **Demonstrates an executed
  harness that L3 correctly does NOT promote to High.**

## ZETA-10 — AMM consumer reentrancy (ATTEMPTED · resolved at source · NOT promoted)
- The permissionless High theft claim. **No executed PoC built.** Source analysis is decisive: `getEthFromZeta` pulls
  exactly the caller's `zetaTokenAmount`, swaps, and forwards the proceeds; the consumer holds **no pooled user balances
  between calls**, so cross-function reentrancy during the ETH callback yields **no realized theft** (each re-entry uses
  the attacker's own funds). The missing `nonReentrant` is a real code-quality inconsistency, but the *theft* magnitude
  is unsubstantiated.
- **L3 verdict:** `l3_status=NEEDS_HARNESS` → `needs_harness_for_severity` → blocked from High. Honest outcome: a
  permissionless High-ceiling candidate is **blocked because no executed realized-impact proof exists**, regardless of
  the analytic argument. (A full executed refutation would require assembling the Uniswap-V3/OZ dependency web; out of
  scope for this bounded pass.)

## Not harnessed (NEEDS_HARNESS / privileged — honest recall gap)
ZETA-01 (FoT insolvency), ZETA-04 (pause asymmetry), ZETA-05 (replay), ZETA-06 (interactor bypass), ZETA-11 (Trident
pool) — none executed. ZETA-03/08 are privileged/centralization (no permissionless PoC possible).

**Harness attempts: 2 (1 executed PASS, 1 attempted/source-resolved). No production source modified; real contracts used
where executed.**
