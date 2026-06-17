# Evidence bundle — LendingPool.getCollateralValue (EX-ORA-01)

Internal reviewer material backing `submission_draft.md`. Every claim must be anchored to in-scope source or
an executable result. Nothing here may be derived from an answer key.

## Subject / pinned version
- Repo: TODO — repo URL
- Commit (pinned): TODO — pin the audited commit + submodules
- Submodules: TODO — pin submodule commits (`git submodule update --init --recursive`)
- Toolchain: TODO — forge/solc versions

## Exact source references (in-scope)
- `LendingPool`
- TODO — the line that reads the spot/manipulable price
- TODO — the value/mint/liquidation decision that consumes it
- TODO — the absence of a TWAP or deviation bound
- TODO — the attacker's single-transaction manipulation path

TODO — replace each prompt with the exact `file:line` at the pinned commit.

## PoC
- PoC file: TODO — path to the `LendingPoolGetCollateralValuePoC` test (place into the repo's `test/` directory to run).
- Test-harness note: TODO — record any test-fixture change (e.g. fork URL); confirm NO in-scope contract is
  modified and in-scope contracts are deployed locally in the test.

## Command run
```
forge test --match-test test_EX_ORA_01_invariant -vv
```

## Vulnerable-source result (current source — test FAILS, as intended)
```
TODO — paste the exact failing assertion/output.
```
Interpretation: TODO — one sentence tying the output to the broken invariant.

## Minimal patch validation (discriminator — proves the root cause)
- Patch: TODO
- Result after patch: TODO — expect the test to PASS; restore source afterwards.
- This patch is an *illustrative discriminator*, not a vetted production fix.

## Unrelated test-suite result (no collateral breakage)
- TODO — `forge test` full suite: expect existing tests to pass; only the PoC fails on vulnerable source.

## L3 PoC requirements for this finding type (oracle_slot0_manipulation)
- [ ] oracle_price_inflated_proven
- [ ] balance_overstatement_shown
- [ ] overstatement_magnitude_quantified
- [ ] attacker_profit_quantified

## Reproduction provenance (frozen artifacts — read-only, for integrity)
TODO — once the PoC is frozen, record the artifact paths + SHA-256 prefixes here.
