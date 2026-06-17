# P117 — Source trace: CuratorRewardsDistributor.distribute (phi-2024-08)

Subject: phi @ `src/reward/CuratorRewardsDistributor.sol` + `src/Cred.sol`. Read-only; cited for framing only —
runtime decides.

## distribute (the loop)
`function distribute(uint256 credId) external` — **permissionless** (no access modifier).
- `if (!credContract.isExist(credId)) revert; uint256 totalBalance = balanceOf[credId]; if (totalBalance==0) revert;`
- `address[] memory distributeAddresses = credContract.getCuratorAddresses(credId, 0, 0);`  ← fetches the curator set
- **Loop 1** over `distributeAddresses`: `totalNum += credContract.getShareNumber(credId, addr)`.
- allocates `amounts[N]`, `reasons[N]`.
- **Loop 2** over `distributeAddresses`: `getShareNumber` again + per-curator reward math.
- `_msgSender().safeTransferETH(royaltyfee + dust)` — royalty(1%, `withdrawRoyalty=100`/`RATIO_BASE=10000`) + rounding
  dust to the **caller**.
- `phiRewardsContract.depositBatch{value: actualDistributeAmount}(distributeAddresses, amounts, reasons, "...")` —
  passes the full N-length arrays.
- **No pagination**: `distribute(credId)` always processes the ENTIRE curator set; there is no partial/paged variant.

## Funding (reaching distribution state)
`function deposit(uint256 credId, uint256 amount) external payable` — **permissionless**; `balanceOf[credId] += amount`
(requires `msg.value == amount`, `isExist`). Trivially seeds reward state.

## getCuratorAddresses(credId, 0, 0) → ALL curators (the reachability determinant)
`Cred.getCuratorAddresses(credId, start, stop)` → `_getCuratorData(credId, start, stop)`:
```
if (stop_ == 0 || stop_ > shareBalance[credId_].length()) stopIndex = shareBalance[credId_].length(); // (0,0) => ALL
...
for (i = start_; i < stopIndex; ++i) { (key, shareAmount) = shareBalance[credId_].at(i); if (isShareHolder) result[index++] = ... }
```
**With `(0,0)` the function returns the FULL curator set (unbounded).** So `distribute`'s work is O(curator_count).

## Curator growth is permissionless (attacker-controllable)
`Cred.buyShareCred(uint256 credId, uint256 amount, uint256 maxPrice) public payable` → `_updateCuratorShareBalance`
→ on a new shareholder, `_addCredIdPerAddress(credId, sender)` adds the buyer to the curator set. Price via
`IBondingCurve.getBuyPriceAfterFee` (grows with supply). Any EOA can become a curator by buying ≥1 share; there is no
cap on the number of curators per cred. The existing project test `test/CuratorRewardsDistributor.t.sol` exercises
exactly this (`buyShareCred` from user1/user2 → `getCuratorAddressLength` grows) and asserts the caller receives
`depositAmount/100` — confirming the **royalty-to-caller is INTENDED** (keeper fee), so the secondary hypothesis is
not a bug and is dropped.

## Framed runtime question
`distribute` is O(N) over a permissionlessly-growable, fully-enumerated curator set with no pagination. Does its gas
exceed a practical block budget (~30M) at a reachable N, making reward distribution un-includable? → answered by the
harness (runtime), not by this trace.
