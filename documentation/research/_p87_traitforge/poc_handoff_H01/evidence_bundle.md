# Evidence bundle — TraitForgeNft.mintWithBudget (P87-H01)

Internal reviewer material backing `submission_draft.md`. Every claim must be anchored to in-scope source or
an executable result. Nothing here may be derived from an answer key.

## Subject / pinned version
- Repo: TODO — repo URL
- Commit (pinned): 72077d0a2a86d16530020afa647ffbfe64fdddb1
- Submodules: TODO — pin submodule commits (`git submodule update --init --recursive`)
- Toolchain: TODO — forge/solc versions

## Exact source references (in-scope)
- `TraitForgeNft`
- TODO — the line that sets the dirty/stale flag or skips the per-user checkpoint update
- TODO — the accrual path that skips/zeroes reward when the flag is set (e.g. `continue` on dirty)
- TODO — the recovery path that returns the user to a valid state but does NOT reset the flag/checkpoint
- TODO — every write to the flag/checkpoint (prove no while-active reset exists)

TODO — replace each prompt with the exact `file:line` at the pinned commit.

## PoC
- PoC file: TODO — path to the `TraitForgeNftMintWithBudgetPoC` test (place into the repo's `test/` directory to run).
- Test-harness note: TODO — record any test-fixture change (e.g. fork URL); confirm NO in-scope contract is
  modified and in-scope contracts are deployed locally in the test.

## Command run
```
forge test --match-test test_P87_H01_invariant -vv
```

## Vulnerable-source result (current source — test FAILS, as intended)
```
TODO — paste the exact failing assertion/output.
```
Interpretation: TODO — one sentence tying the output to the broken invariant.

## Minimal patch validation (discriminator — proves the root cause)
- Patch: Reset the dirty/stale flag to false (or advance the per-user reward checkpoint / clear the reward debt) on the recovery path (e.g. inside transferToUnoccupiedPlot / on re-entry), and set lastRewardDate to block.timestamp. Assert the participant resumes accruing the recoverable baseline and can claim owed reward, with no other change.
- Result after patch: TODO — expect the test to PASS; restore source afterwards.
- This patch is an *illustrative discriminator*, not a vetted production fix.

## Unrelated test-suite result (no collateral breakage)
- TODO — `forge test` full suite: expect existing tests to pass; only the PoC fails on vulnerable source.

## L3 PoC requirements for this finding type (reward_accrual_state_lifecycle)
- [ ] reward_accrual_halted_proven
- [ ] state_flag_or_checkpoint_not_reset_proven
- [ ] permanent_or_unrecoverable_reward_loss_proven
- [ ] loss_or_blocked_path_quantified

## Reproduction provenance (frozen artifacts — read-only, for integrity)
TODO — once the PoC is frozen, record the artifact paths + SHA-256 prefixes here.
