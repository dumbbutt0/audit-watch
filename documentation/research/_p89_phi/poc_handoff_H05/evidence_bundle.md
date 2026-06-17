# Evidence bundle — Cred._addCredIdPerAddress (P89-H05)

Internal reviewer material backing `submission_draft.md`. Every claim must be anchored to in-scope source or
an executable result. Nothing here may be derived from an answer key.

## Subject / pinned version
- Repo: TODO — repo URL
- Commit (pinned): 2465e04364b759c721f1a0aebace69920411f8aa
- Submodules: TODO — pin submodule commits (`git submodule update --init --recursive`)
- Toolchain: TODO — forge/solc versions

## Exact source references (in-scope)
- `Cred`
- TODO — the entrypoint declaration showing the missing/insufficient modifier
- TODO — the privileged state it mutates
- TODO — the role/owner variable that should have gated it
- TODO — any sibling function that IS correctly guarded (parity evidence)

TODO — replace each prompt with the exact `file:line` at the pinned commit.

## PoC
- PoC file: TODO — path to the `CredAddCredIdPerAddressPoC` test (place into the repo's `test/` directory to run).
- Test-harness note: TODO — record any test-fixture change (e.g. fork URL); confirm NO in-scope contract is
  modified and in-scope contracts are deployed locally in the test.

## Command run
```
forge test --match-test test_P89_H05_invariant -vv
```

## Vulnerable-source result (current source — test FAILS, as intended)
```
TODO — paste the exact failing assertion/output.
```
Interpretation: TODO — one sentence tying the output to the broken invariant.

## Minimal patch validation (discriminator — proves the root cause)
- Patch: Add onlyRegistratorOrGovernor modifier. Assert that the attacker contract call reverts. Assert totalDepositsWei unchanged.
- Result after patch: TODO — expect the test to PASS; restore source afterwards.
- This patch is an *illustrative discriminator*, not a vetted production fix.

## Unrelated test-suite result (no collateral breakage)
- TODO — `forge test` full suite: expect existing tests to pass; only the PoC fails on vulnerable source.

## L3 PoC requirements for this finding type (missing_auth_accounting_drift)
- [ ] unauthorized_call_succeeds
- [ ] accounting_drift_shown
- [ ] direct_fund_loss_asserted

## Reproduction provenance (frozen artifacts — read-only, for integrity)
TODO — once the PoC is frozen, record the artifact paths + SHA-256 prefixes here.
