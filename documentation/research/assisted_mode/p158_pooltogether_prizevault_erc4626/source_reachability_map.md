# P158 — H6 Mechanism + Source Reachability (PrizeVault)

Target: `audits/pooltogether-2024-03-holdout/contracts/src/PrizeVault.sol`

## Stage 1 — Mechanism hypothesis (one sentence)
*Because `previewDeposit`/`previewMint` are hard-coded `pure` 1:1 while `convertToShares`/`convertToAssets`
are debt-aware, an unprivileged depositor might mint shares at the wrong (1:1) rate when the vault is in a
lossy state (`totalAssets < totalDebt`), capturing value from / being diluted relative to honest holders.*

### Refutation condition (pre-registered)
Refuted if any of: (a) deposit/mint **revert** when they would mint at the wrong rate / leave a lossy state;
(b) withdraw/redeem use **debt-aware** previews so no 1:1 over-withdrawal occurs in a lossy state; (c) the
1:1 deposit preview is actually *correct* because deposits cannot occur into a lossy vault.

## Stage 2 — Production call path (read-only, no harness)
- `deposit(assets,receiver)` → `previewDeposit(assets)` (**=assets, 1:1, `pure`**, :441) → `_depositAndMint(...)`.
- `mint(shares,receiver)` → `previewMint(shares)` (**=shares, 1:1, `pure`**, :447) → `_depositAndMint(...)`.
- `_depositAndMint` (:843): pulls assets, deposits into `yieldVault`, `_mint(receiver, shares)`, **then**
  `if (totalAssets() < totalDebt()) revert LossyDeposit(...)` (:874).
- `withdraw(assets,…)` → `previewWithdraw(assets)` (**debt-aware**: `mulDiv(totalDebt,totalAssets,Up)` when
  lossy, :454-466) → `_burnAndWithdraw`.
- `redeem(shares,…)` → `previewRedeem(shares)` = `convertToAssets(shares)` (**debt-aware**, :470-472).
- `convertToShares`/`convertToAssets` (:341-372): 1:1 when `totalAssets ≥ totalDebt`, else proportional haircut.

### Caller permissions / control
`deposit`/`mint`/`withdraw`/`redeem` are **public, unprivileged**; attacker controls `assets`/`shares`/
`receiver`. **No keeper/operator dependency** on these paths. ✓ (good selection vs H5).

## Result: NOT refuted at runtime — REFUTED at source (the guard is dispositive)
- (a) holds: `_depositAndMint` ends with **`revert LossyDeposit` if the post-deposit state is lossy** — so a
  deposit cannot mint 1:1 into/while creating a lossy vault. The 1:1 deposit preview is therefore *safe*
  precisely because lossy deposits revert.
- (b) holds: `previewWithdraw` and `previewRedeem`/`convertToAssets` are **debt-aware** (proportional haircut
  with `mulDiv`), so there is no 1:1 over-withdrawal in a lossy state.
- The deposit-side 1:1 preview is consistent with deposit always being non-lossy (guarded).

→ The hypothesised rate-mismatch **does not survive source reading**: it is guarded by `LossyDeposit` +
debt-aware withdraw/redeem. This is a **static false positive** (the ERC4626 1:1-preview "smell" is defended),
not a bug.

## Runtime status: not run (deploy_too_heavy) — see harness_design.md
A faithful real-contract harness is **not deploy-light**: real `PrizeVault` imports the *concrete*
`TwabController` (via `TwabERC20`) and `PrizePool` (via `Claimable`) types, neither vendored in the audit and
`PrizePool` is heavy. Because the mechanism is already source-refuted by an explicit guard, no runtime
confirmation was built.
