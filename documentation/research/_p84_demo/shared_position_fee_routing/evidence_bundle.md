# Evidence bundle — PoolVault.claim (EX-FEE-01)

Internal reviewer material backing `submission_draft.md`. Every claim must be anchored to in-scope source or
an executable result. Nothing here may be derived from an answer key.

## Subject / pinned version
- Repo: TODO — repo URL
- Commit (pinned): TODO — pin the audited commit + submodules
- Submodules: TODO — pin submodule commits (`git submodule update --init --recursive`)
- Toolchain: TODO — forge/solc versions

## Exact source references (in-scope)
- `PoolVault`
- TODO — the line that collects/settles the WHOLE pooled position (e.g. collect(max,max))
- TODO — the line that pays the caller only its share
- TODO — the line that routes the residual to a third party (or fails to credit other shares)
- TODO — where other shares' checkpoints would be advanced (and are not)

TODO — replace each prompt with the exact `file:line` at the pinned commit.

## PoC
- PoC file: TODO — path to the `PoolVaultClaimPoC` test (place into the repo's `test/` directory to run).
- Test-harness note: TODO — record any test-fixture change (e.g. fork URL); confirm NO in-scope contract is
  modified and in-scope contracts are deployed locally in the test.

## Command run
```
forge test --match-test test_EX_FEE_01_invariant -vv
```

## Vulnerable-source result (current source — test FAILS, as intended)
```
TODO — paste the exact failing assertion/output.
```
Interpretation: TODO — one sentence tying the output to the broken invariant.

## Minimal patch validation (discriminator — proves the root cause)
- Patch: Collect only the per-claim amounts the caller is owed (e.g. collect(uint128(amount0), uint128(amount1)) instead of collect(max, max)), or advance each internal share's fee checkpoint, so other users' fees stay in the position. Assert the later claim pays the same as the order-independent baseline and does not revert.
- Result after patch: TODO — expect the test to PASS; restore source afterwards.
- This patch is an *illustrative discriminator*, not a vetted production fix.

## Unrelated test-suite result (no collateral breakage)
- TODO — `forge test` full suite: expect existing tests to pass; only the PoC fails on vulnerable source.

## L3 PoC requirements for this finding type (shared_position_fee_routing)
- [ ] order_independence_invariant_broken
- [ ] fee_diversion_to_third_party_proven
- [ ] later_claim_revert_or_underpay_proven
- [ ] loss_magnitude_quantified

## Reproduction provenance (frozen artifacts — read-only, for integrity)
TODO — once the PoC is frozen, record the artifact paths + SHA-256 prefixes here.
