# P152 — Harness Design

**harness_type: real_contract** (real production `ERC20MultiVotes` logic inherited unmodified). Location
`audits/ecg-2023-12-holdout/pocs/p152/` (solc 0.8.13, evm london; OZ v4.9.6 + local `SafeCastLib`; `lib/` removed
post-run).

## Contracts
- **`TestMultiVotes is ERC20MultiVotes` (REAL surface)** — adds ONLY a constructor + `mint` + `setMaxDelegates`
  (the documented "parent adds permissioned public functions" pattern; `ERC20MultiVotes` is abstract). The
  delegate/transfer/`_decrementVotesUntilFree`/`getVotes` logic is the real production code, unmodified.
- **`NaiveMultiVotesRef is ERC20MultiVotes` (vulnerable reference)** — overrides `transfer` to call
  `ERC20.transfer` directly, **skipping** `_decrementVotesUntilFree` → demonstrates the bug shape (votes retained)
  the real contract avoids. Reference only, not production.
- `setMaxDelegates(2)` enables delegation; `incrementDelegation(delegatee, amount)` delegates a specific amount.

## Tests
1. `test_real_transfer_decrements_delegated_votes` — delegate X; `getVotes(delegatee)==X`; transfer X away; assert
   `getVotes(delegatee)==0` → **suspicion refuted** (real guard decrements).
2. `test_vulnerable_reference_retains_votes` — same on the unguarded reference → `getVotes(delegatee)==X` retained
   (bug shape).
3. `test_control_no_transfer_votes_stable` — delegate, no transfer → `getVotes(delegatee)==X` stable.

## Notes
- `real_contract_used`: yes (inherited abstract production logic); `production_source_changed`: no.
- `corrected_reference_used`: the protocol's own guarded transfer IS the correct behavior; the
  vulnerable-reference contrast shows the bug shape. `control_case_used`: yes (no-transfer stability).
- deploy_complexity: moderate (OZ v4.9); harness_cost: low (3 tests).
