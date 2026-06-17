# P274 — POC_INTENT (Phase 7) — claims frozen BEFORE code

Each claim fixed before any harness was written. Tiers per P271: A full runtime · B partial runtime executing real
production code · C faithful reproduction · negative control. No severity/reportable/submission language.

## PoC-1 — distribute permissionless spoofed-liquidation callback (M1, ACCOUNTING/ACCESS) — Tier B
- **Attacker model:** EOA, no privileged role.
- **Setup:** deploy real `LiquidationDistributor` with a mock `ILoanManagerRegistry` returning `isLoanManager(x)=true`;
  a mock `LoanManager` that records `loanLiquidation` args; a mock ERC20; attacker funds + approves the distributor.
- **Tx:** attacker calls `distribute(proceeds, loan)` with a `loan.tranche[0].lender = mockLoanManager` and
  attacker-chosen `loanId/principalAmount/aprBps/startTime`.
- **Expected/assert:** `loanLiquidation` is invoked on the mock with **exactly the attacker-supplied** `loanId` and
  `principalAmount` — proving an unauthenticated, caller-controlled liquidation callback reaches a registered
  LoanManager. (Economic write-off in a real Pool is out of partial-runtime scope → recorded as PARTIAL.)
- **Refutation:** if `distribute` reverts for a missing auth/loan check, or the callback never fires, the claim is
  refuted.
- **Victim/gainer:** pool LPs / attacker-forced state.

## PoC-2 — UserVault.burnAndWithdraw strands unlisted assets (M3, STATE) — Tier B
- **Attacker model:** vault owner (self-inflicted footgun; or a griefing front-end).
- **Setup:** deploy `UserVault` (with mock `AddressManager` whitelisting a mock ERC721); owner mints a vault, deposits
  **two** NFTs.
- **Tx:** owner calls `burnAndWithdraw(vaultId, [collection], [tokenId#1], [])` listing only the **first** NFT.
- **Expected/assert:** (a) vault NFT is burned (`ownerOf` reverts); (b) NFT#2 is still owned by the vault contract;
  (c) there is no path to recover NFT#2 (a second `burnAndWithdraw` reverts). Permanent stranding proven.
- **Refutation:** if NFT#2 is auto-returned, or a recovery path exists, the claim is refuted.

## PoC-3 — WithdrawalQueue per-share rounding strands funds (M2, SHARE/DOS) — Tier B
- **Attacker model:** none required — systematic accounting loss.
- **Setup:** deploy `WithdrawalQueue(asset)` from a test "pool" address; pool mints positions with shares that do not
  evenly divide the funded balance; fund the queue with asset.
- **Tx:** read `getAvailable` for each position; sum.
- **Expected/assert:** `sum(getAvailable) < asset.balanceOf(queue)` — a non-zero remainder is permanently stranded
  (rounding-down in `_getWithdrawablePerShare`). Also assert `getAvailable` reverts (div-by-zero) when `getTotalShares
  == 0`.
- **Refutation:** if the sum equals the balance (no stranding), the claim is refuted.

## Negative control — distribute proceeds conservation (M1 runner-up) — Tier B
- Assert that in the **excess** branch the sum of per-tranche payouts equals `_proceeds` (the split math conserves),
  confirming the *split arithmetic* is NOT the bug and isolating the finding to the missing callback authentication.

## Not advanced
- M4 `offers` (ORDER): no falsifiable exact hypothesis derivable blind → **NEEDS_MORE_RUNTIME**, no PoC.
