# P145 — Harness Design

**harness_type: real_contract** — the real `RewardsDistributor` is deployed and both real public entrypoints
(`claim`, `claim_many`, plus `checkpoint_token`, `setAVM`) are called.

Location: `audits/blackhole-2025-05-eval/pocs/p145/` (Foundry, local to the blackhole audit — constraint 11).
- `foundry.toml` — solc 0.8.13, evm london; remaps `bh/` → real blackhole contracts + `allow_paths`;
  `lib/forge-std` (build dep; removed post-run, re-runnable via the documented clone). **No OZ** —
  `RewardsDistributor` imports only local libs/interfaces.
- `test/RewardsDistributorClaimManyRecipientParity.t.sol`.

## Contracts in the test
- **`RewardsDistributor` (REAL, `bh/RewardsDistributor.sol`)** — the subject; unmodified production source.
- **`MockVotingEscrow`** — exposes exactly the selectors the distributor calls (`token`, `user_point_epoch`,
  `user_point_history` returning real `IVotingEscrow.Point`, `balanceOfNFTAt`, `totalSupplyAtT`, `locked`
  returning real `IVotingEscrow.LockedBalance`, `ownerOf`, `deposit_for`). Value functions return constants;
  `ownerOf` is keyed per id.
- **`MockAVM`** — `tokenIdToAVMId` (nonzero for AVM ids, 0 for controls) + `getOriginalOwner` (→ user).
- **`MockERC20`** — reward token (`approve`/`balanceOf`/`transfer`).

## Why real-contract was achievable
`RewardsDistributor` has no heavyweight base (no OZ); its external dependencies are the VE / AVM / ERC20
interfaces, all mockable. The actual divergence lives in the post-`_claim` recipient branch, which executes
unmodified. The reward-accounting (`_claim`/`checkpoint_token`) is driven to a deterministic nonzero amount via
funding + a 1-WEEK warp + `checkpoint_token`, with `S < SUP` so per-claim payouts are fractional (no double-spend
across the two claims a single test performs). No production contract edited (constraint 2).

## Corrected reference / controls (constraint 14)
- **Corrected reference = the protocol's own `claim`** (it already applies the AVM correction). Tests assert the
  real `claim` pays the original owner while the real `claim_many` pays the AVM manager — the sibling divergence
  is the proof.
- **Non-AVM control** — for `tokenIdToAVMId == 0`, both paths pay `ownerOf == original owner` (no divergence),
  isolating the bug to AVM-managed tokenIds.

## Test functions (neutral names — constraint 15)
1. `test_single_claim_routes_avm_managed_to_original_owner`
2. `test_batch_claim_many_routes_avm_managed_to_nft_owner_not_original`
3. `test_corrected_behavior_matches_single_claim`
4. `test_non_avm_control_both_paths_match`
