# P158 — Selection Memo (Option-A candidate #2 / H6)

Campaign goal: run another Option-A candidate through the existing pipeline, applying the H5 lesson in
**human selection judgment** — prefer direct user-controlled value movement, public entrypoints, **no
keeper/operator dependency**, deploy-light real-contract harness, crisp economic delta, feasible
corrected-reference/control. Goal is *less operator/scope dependency than H5*, not "another Low." Outcome
measured, not forced.

Excluded arches: noya/blackhole/centrifuge/velodrome/decent/ecg/abracadabra (used); vultisig/kelp (rejected, P150).

## Severity-ceiling pre-screen (BEFORE any harness)

| candidate | mechanism (hypothesis) | likely ceiling | what caps severity | what blocks reportability | harness cost |
|---|---|---|---|---|---|
| **pooltogether PrizeVault** (SELECTED) | ERC4626 deposit/withdraw rate mismatch: `previewDeposit`/`previewMint` are `pure` 1:1 vs debt-aware `convertToShares`/`convertToAssets` | Low–QA | impact only in a **lossy state** (`totalAssets<totalDebt`), which is environmental, not attacker-forced | a guard / debt-aware previews could neutralize it | **moderate→too-heavy** (mocks small, but real contract imports concrete `TwabController`+`PrizePool`, not vendored) |
| spectra PrincipalToken | PT/IBT rate rounding / negative-yield / claimYield accounting | Med | rounding direction / dust; needs a concrete favoring direction | upgradeable+beacon(YT)+registry+IBT+rate-oracle deploy | heavy |
| basin Well | AMM swap / removeLiquidity invariant break | Med–High | needs a real invariant break, not just shape | Aquifer clone + immutable-args + Pump + WellFunction | deploy_too_heavy |

## Why H6 = PrizeVault
- Best fit to the **H5-lesson rubric**: `deposit`/`mint`/`withdraw`/`redeem` are **public, unprivileged,
  direct-value, and have NO keeper/operator dependency** (unlike H5). This is exactly the "less operator
  dependence" direction the campaign is testing.
- Crispest, most self-contained hypothesis of the three; the smallest *mock* surface
  (`TwabController` needs only `balanceOf/totalSupply/mint/burn/transfer`).
- Spectra deferred (heavier upgradeable/beacon/registry deploy; candidate for a later phase). basin = clearly
  `deploy_too_heavy` (clone + immutable args + Pump).

## Did the H5 lesson change selection? Yes
H5 was keeper-cadence bounded. For H6 I explicitly **penalized keeper/operator-gated mechanisms** and chose a
pure user-action ERC4626 path. (The pre-screen then surfaced a *different* ceiling cap for PrizeVault — see
below — which is itself a useful campaign datapoint.)

## Integrity note
`audits/pooltogether-2024-03-holdout/_sealed_answer_key/` was **not opened** (human-only; opening it would
contaminate the holdout). Selection + hypothesis are from source reading only.
