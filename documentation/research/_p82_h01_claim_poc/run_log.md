# P82 run log (exact commands + results)

1. `git submodule update --init --recursive` → forge-std 52715a2, openzeppelin 04695ae, v3-core d8b1c63
2. `forge build` → compiled OK (solc 0.7.6)
3. (env check) edit IntegrationTestBase fork URL ankr→publicnode, drop pinned block (key-gated ankr)
4. `forge test --match-test testClaim -vv` → [PASS] (env confirmed)
5. PoC iter A (testClaim-style, 2 investors, small fees) → INVESTOR_2 claim SUCCEEDS (loss masked, fees < platform buffer)
6. PoC iter B (all 5 positions, larger fees) → all 5 claim OK (still under buffer at that volume)
7. PoC final (order-independence, _accrueFees(20000 ether, 40)):
   `forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv`
   → [FAIL] INVESTOR_2 first=15151 USDC ; INVESTOR_2 second=REVERT(0) ; lost=15151  (H-01 REPRODUCED)
8. Validation: patch collect(max)→collect(uint128(amount0),uint128(amount1)); re-run → [PASS] (order-independent); restore source
9. `forge test` (full suite) → 29 existing PASS, 1 PoC FAIL (intended). No unrelated breakage.
