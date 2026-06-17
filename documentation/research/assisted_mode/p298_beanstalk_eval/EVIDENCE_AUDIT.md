# P298 — EVIDENCE_AUDIT

## Confirmed-by-execution (verifier = sole judge; real forge PASS + L1+L2+L3 + assertion_map)
- **AC-001 L2ContractMigrationFacet.redeemDepositsAndInternalBalances** — source-verified: external (permissionless),
  verify→additive `stalk +=`/`roots +=` credit, NO claimed/nonce mapping; the EIP-712 struct hash carries no nonce.
  PoC: redeem a valid leaf, replay it → credited balance doubles (named before/after; control with a `claimed[leaf]`
  guard reverts). Real exploit PASS. Immunefi corroborates the class (belong 57373/57800 missing-nonce replay).
- **AC-003 UnwrapAndSendETH.unwrapAndSendETH** — source-verified: unguarded external, unwraps the ENTIRE WETH balance
  and forwards address(this).balance to a caller-supplied `to`. PoC: victim parks WETH; unrelated attacker EOA calls
  unwrapAndSendETH(attacker) and receives it (named attacker ETH + junction WETH before/after; control with an owner
  guard reverts). Real exploit PASS. Immunefi corroborates (alchemix-v3 access-control theft).
Both: confirmed honestly, FP=0.

## Setup_only — logic/correctness bugs proven by a passing differential test but exploit-shaped L1 N/A
(The builders claimed confirmed; the P294 verifier — sole judge — did NOT confirm. Judge-not-builder guard working.)
- **LG-001 ReseedField.init** — VERBATIM source bug at `ReseedField.sol:49`: `for (uint j; j < accountPlots[i].plots
  .length; i++)` increments the OUTER index `i` not `j`. The PoC (passing) shows init reverts OOB → multi-plot
  migration bricked. Real bug, real passing test; setup_only only because there is no attacker EOA entry (it's a
  migration logic bug, not an exploit an attacker calls). Should be a logic-bug confirmation, not setup_only.
- **PC-001 SeasonGettersFacet.totalDeltaB** — VERBATIM: `deltaB = LibWellMinting.check(C.BEAN_ETH_WELL)` (single well)
  vs the NatSpec "all whitelisted wells". PoC (passing) shows reported != sum over 2 wells. A view-getter correctness
  bug — no attacker/state-flip, so exploit-shaped L1/L2 don't apply → setup_only. Real, proven by test.
- **SN-001 LibFlood.balanceOfPlenty** — VERBATIM: trailing branch multiplies by LIVE `s.accts[account].roots` while the
  divisor uses the `s.sys.rain.roots` snapshot (rewardSop). PoC (passing) shows 2x over-payment for an account that
  changed roots. Has a named L2 flip but no attacker L1 → setup_only. (Strengthenable with an actor prank; left honest.)

## Needs_execution (evidence-bundle; too entangled to mock faithfully — NOT confirmed)
US-001 (reseed leaves Stalk/Roots aggregates unset), BSA-001 (reseed facet ordering), BSA-003 (redeem ignores
internalBalances), EA-001 (convert-capacity sandwich), FL-001 (spot getReserves flash-manipulable), CC-002 (L1 burn /
L2 revert), DS-003 (OOG nested loops). Each carries an evidence_bundle {call_path, source_file, mechanism, invariant,
expected_assertion} in evidence_bundles.json, marked `needs_execution` — the chain is assembled, execution deferred.

## Integrity
confirmed_false_positive_count = 0; the salty Pools.deposit refutation control stays refuted. Answer key
(match_matrix + ground_truth) byte-identical (hashes recorded). Contest source read-only (PoCs copy control-flow into
pocs/p298/ mocks; never edited). Verifier + forbidden 5 byte-identical; symlink unchanged.
