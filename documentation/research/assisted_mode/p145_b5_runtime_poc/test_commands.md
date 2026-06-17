# P145 — Test Commands

## Run
```bash
cd audits/blackhole-2025-05-eval/pocs/p145
forge test -vv
```

## Restore build deps (if `lib/` was cleaned)
```bash
cd audits/blackhole-2025-05-eval/pocs/p145
git clone --depth 1 --branch v1.9.4 https://github.com/foundry-rs/forge-std lib/forge-std
```
(No OpenZeppelin needed — `RewardsDistributor` imports only local blackhole libs/interfaces.)

## Result
```
[PASS] test_single_claim_routes_avm_managed_to_original_owner      claim -> 0xBEEF (user), 1e18
[PASS] test_batch_claim_many_routes_avm_managed_to_nft_owner_not_original   claim_many -> 0xA814 (AVM mgr), 1e18
[PASS] test_corrected_behavior_matches_single_claim                recipients diverge (user vs AVM mgr)
[PASS] test_non_avm_control_both_paths_match                       non-AVM: both -> user; AVM mgr 0
4 passed; 0 failed; 0 skipped
```

## Notes
- `real_function_called: true` · `public_entrypoint_called: true` (real `claim` + `claim_many`) ·
  `copied_logic_used_for_subject: false` (the corrected reference is the protocol's own `claim`).
- solc 0.8.13 (matches the production pragma); WEEK=1800 from `BlackTimeLibrary`.
- First run surfaced an underflow when one test did two claims (mock gave each NFT 100% of supply); fixed by
  `totalSupplyAtT (SUP=1000e18) > balanceOfNFTAt (S=1e18)` so per-claim payout is fractional (1e18).
