# Evidence bundle — SecondSwap_VestingManager.listVesting (ASSISTED-M11)

Internal reviewer material backing `submission_draft.md`. Every claim must be anchored to in-scope source or
an executable result. Nothing here may be derived from an answer key.

## Subject / pinned version
- Repo: TODO — repo URL
- Commit (pinned): 6693d9e4f03a37919a52626de64b1cadf632fd29
- Submodules: TODO — pin submodule commits (`git submodule update --init --recursive`)
- Toolchain: TODO — forge/solc versions

## Exact source references (in-scope)
- `SecondSwap_VestingManager`
- TODO — the validation/loop-guard line using the wrong-domain counter
- TODO — the declaration of that counter showing it is global/monotonic (never reset)
- TODO — the correct per-scope counter that should have been used (and where it is enforced elsewhere)
- TODO — the user-facing path that becomes blocked once the global value crosses the local limit

TODO — replace each prompt with the exact `file:line` at the pinned commit.

## PoC
- PoC file: TODO — path to the `SecondSwapVestingManagerListVestingPoC` test (place into the repo's `test/` directory to run).
- Test-harness note: TODO — record any test-fixture change (e.g. fork URL); confirm NO in-scope contract is
  modified and in-scope contracts are deployed locally in the test.

## Command run
```
forge test --match-test test_ASSISTED_M11_invariant -vv
```

## Vulnerable-source result (current source — test FAILS, as intended)
```
TODO — paste the exact failing assertion/output.
```
Interpretation: TODO — one sentence tying the output to the broken invariant.

## Minimal patch validation (discriminator — proves the root cause)
- Patch: Replace the wrong-domain check with the correct scope (e.g. `generationMintCounts[currentGeneration] < maxTokensPerGen` instead of `_tokenIds < maxTokensPerGen`, or the per-user/per-scope counter). Assert the user-facing path works again at and beyond the boundary, with no other change.
- Result after patch: TODO — expect the test to PASS; restore source afterwards.
- This patch is an *illustrative discriminator*, not a vetted production fix.

## Unrelated test-suite result (no collateral breakage)
- TODO — `forge test` full suite: expect existing tests to pass; only the PoC fails on vulnerable source.

## L3 PoC requirements for this finding type (validation_liveness_counter_scope)
- [ ] wrong_validation_scope_proven
- [ ] user_facing_path_blocked_proven
- [ ] permanent_or_indefinite_brick_proven
- [ ] core_phase_or_many_users_affected_proven

## Reproduction provenance (frozen artifacts — read-only, for integrity)
TODO — once the PoC is frozen, record the artifact paths + SHA-256 prefixes here.
