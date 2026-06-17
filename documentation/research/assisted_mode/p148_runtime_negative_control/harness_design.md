# P148 — Harness Design

**harness_type: real_contract** — the real velodrome `RewardsDistributor` is deployed; its real
`claim`/`claim_many`/`checkpoint_token` are called.

Location: `audits/velodrome-2022-05-bench/pocs/p148/` (Foundry, local to the holdout — constraint 11).
- `foundry.toml` — solc 0.8.13, evm london; remap `velo/` → real velodrome contracts + `allow_paths`;
  `lib/forge-std` (cloned, removed post-run). **No OZ** — `RewardsDistributor` imports only local
  `Math`/`IERC20`/`IVotingEscrow`.
- `test/RewardsDistributorParityNegativeControl.t.sol`.

## Contracts in the test
- **`RewardsDistributor` (REAL, `velo/RewardsDistributor.sol`)** — subject; unmodified production source.
- **`MockVotingEscrow`** — exposes exactly the selectors the distributor calls (`token`, `user_point_epoch`,
  `user_point_history` [flat point], `epoch`, `point_history` [flat point], `checkpoint`, `deposit_for`).
  `deposit_for` **records** `(tokenId, amount)` and pulls the reward INTO the escrow (modeling the re-lock; the
  distributor approved the escrow `max` in its ctor) — there is no external-recipient transfer to model because
  the contract never makes one.
- **`MockERC20`** — reward token.
- A fake **`externalRecipient` (0xBEEF)** — the address a B5-style bug *would* pay; asserted to stay at 0.

## Driving a nonzero `_claim`
`USER_BIAS = 1e18` (one NFT) `< SUPPLY_BIAS = 1000e18` (total) with `slope 0`; fund `R = 1000e18` + warp 1 WEEK +
`checkpoint_token` → `tokens_per_week[T0] ≈ R`; `claim` auto-runs `_checkpoint_total_supply` → `ve_supply[T0] =
SUPPLY_BIAS`; per-claim payout `= USER_BIAS · R / SUPPLY_BIAS = 1e18` (fractional → no double-spend across two
claims).

## Tests (negative control)
1. `test_suspected_recipient_divergence_does_not_occur` — claim(idA) + claim_many([idB]); assert external
   recipient balance 0, `depositForCount == 2`, each tokenId credited via `deposit_for` → **suspected divergence
   refuted**.
2. `test_claim_and_claim_many_route_identically` — both credit equal amounts to their own tokenId.
3. `test_control_single_claim_credits_correct_tokenid` — `deposit_for` targets the claimed tokenId.

No production contract edited (constraint 2); all mocks/control live in the test.
