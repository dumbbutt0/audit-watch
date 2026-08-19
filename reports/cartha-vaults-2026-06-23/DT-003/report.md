# DT-003 — removePool strands the GM-deployed portion of the parent's stake

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=Medium · Confidence=High · Exploitability=Privileged (ADMIN)
- **Location(s):** `src/CarthaParentVault.sol:215-249,348-365; src/CarthaVault.sol:847-873`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`, `CarthaVault.sol`

## Description

CarthaParentVault.removePool() withdraws the parent's full stake via child.withdrawToParent(parentShares*vaultTVL/totalShares), but withdrawToParent caps the payout at the child's idle USDC and burns shares only for that portion. The pool is then deleted from vaultList. The GM-deployed portion of the parent's stake is left as child shares the parent still owns but that totalAssets() no longer counts (it iterates active pools only), so parent share price drops and value is stranded until the pool is re-added.

## Impact

Parent TVL/share price drops by the stranded GM value on pool removal; ADMIN-only and recoverable by re-adding, so Medium.

## Attack path (Intent / Technique / Evasion)

- **Intent:** n/a (correctness bug; can be triggered accidentally by governance)
- **Technique:** removePool/removeChildFromParent on a child with deployed GM
- **Evasion:** n/a

## Reachability / follow-up

reachable: removePool/removeChildFromParent on a child with deployed GM. no_privileged_keys: NO (ADMIN). state_before_after: parent totalAssets drops by the stranded GM value. why_guards_fail: withdrawToParent caps at idle; no recall-before-remove. scope_match: accounting.

## Triage reasoning

removePool recovers only the child idle slice (withdrawToParent caps at idle) then drops the pool from totalAssets(), orphaning the parent's GM-deployed child shares -> parent share price drops; value stranded until the pool is re-added. ADMIN-only and recoverable, hence Medium. Swap-pop bookkeeping verified correct (not a separate bug).
