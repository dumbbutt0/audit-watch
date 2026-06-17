# Real-World Hunt Results

_Generated 2026-06-11_

> Real-world bounty-hunt activity. Candidate findings are PoC-proven but UNCONFIRMED and UNSUBMITTED (flagged for human verification). No FP/recall/paid scores are shown: those require human-confirmed ground truth, which does not exist for these hunts. Eval/synthetic corpora are excluded.

## Summary

| Targets engaged | Candidate findings (PoC-proven) | Honest negatives | Skipped | Submitted | Human-confirmed | Paid |
|---|---|---|---|---|---|---|
| 13 | 3 | 8 | 2 | 0 | 0 | 0 |

## Candidate findings (UNCONFIRMED / UNSUBMITTED — pending human verification)

| Target | Severity | Title | Status | Submitted | Human-verified | PoC |
|---|---|---|---|---|---|---|
| 40acres (loan-contracts) | High/Medium | CommunityRewards.earned() is public + state-mutating → anyone permanently zeroes/bricks any depositor's reward claims | PoC-proven candidate | False | False | `forty/test/poc/CommunityRewardsEarnedGrief*.t.sol` |
| Monolith (stablecoin factory) | Medium | Bad-debt write-off deletes debt without burning Coin → last/only borrower leaves the stablecoin unbacked (no deficit accounting) | PoC-proven candidate | False | False | `monolith/test/poc/WriteOffUnbackedCoin.t.sol` |
| infiniFi | Medium | ChainlinkOracle.price() accepts non-positive answers (no answer>0 check) → protocol-wide mispricing | PoC-proven candidate (live-bounty rubric may argue Low) | False | False | `infinifi-oracle-poc/test/ChainlinkOracleAnswerValidation.t.sol` |

## All targets

| Target | Source | Verdict | Notes |
|---|---|---|---|
| infiniFi | Cantina | candidate_finding | Core + gateway + CoWSwap + Pendle honest-negative; oracle answer>0 Medium candidate; P-01 ERC4626 inflation downgraded to Informational by live-state check (siUSD already seeded); _disableAsset value-blind = Low. |
| Rheo very-liquid-vaults | Cantina | honest_negative | yearn-v3 meta-ERC4626; dead-shares + defensive rounding; _decimalsOffset never overridden = Low/QA note only. |
| Makina (makina-core) | Cantina | honest_negative |  |
| Concrete Earn V2 | Cantina | honest_negative |  |
| Midas | Cantina | honest_negative | Mature multiply-audited RWA vault; robust DataFeed oracle; decimal-consistent. |
| Mezo mUSD | Cantina | honest_negative | Liquity fork; audited the modifications (EIP-712 BorrowerOperationsSignatures + InterestRateManager settle-before-change) — sound. |
| dreUSD | Sherlock contest | honest_negative | Full read + invariant fuzz harness (7 invariants incl. oracle-band arbitrage + multi-block swing); robust. |
| Mellow flexible-vaults | Sherlock bug bounty | honest_negative | Report-driven async queue vault; invariant fuzz + manual logic read of Oracle/RedeemQueue/DepositQueue — sound. |
| Monolith | Sherlock bug bounty | candidate_finding | See candidate_findings. Invariant harness: collateral + debt-share conservation pass 128k calls; coinBacking flagged the write-off bug. |
| 40acres | Sherlock bug bounty | candidate_finding | See candidate_findings. Fork conservation harness (outstanding-capital + no-USDC-retention) passes 1,800 calls; secondary items ruled out. |
| Napier V2 | Code4rena (public repo) | honest_negative | Pendle-style PT/YT; ran their mature invariant suite + added the missing reward-token-solvency invariant — all 11 pass @80×9,600 calls. TwoCryptoZap left unread. |
| Alphix | Sherlock bug bounty | skipped | Pinned scope commit force-pushed off the public repo → unscoreable, not audited. |
| K2 (Kinetic) | Code4rena | skipped | Rust project (out of EVM-Solidity scope). |
