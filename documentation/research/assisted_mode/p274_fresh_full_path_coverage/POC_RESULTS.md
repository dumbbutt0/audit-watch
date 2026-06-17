# P274 — POC_RESULTS (Phase 8)

Isolated foundry project `pocs/p274/gondi/` — **trimmed 19-file import closure** of the 3 target contracts (no
MultiSourceLoan / seaport, so no via-IR needed), real gondi source copied read-only + pinned solmate/openzeppelin/
forge-std. `forge test`: **5 passed, 0 failed**. Run log: `pocs/p274/gondi/run_output.txt`.

| PoC | mech / class | tier | result | proves |
|---|---|---|---|---|
| `test_permissionless_spoofed_liquidation_callback` | M1 distribute / ACCOUNTING+ACCESS | B | **PASS** | EOA calls `distribute` and reaches `loanLiquidation` on a registered LoanManager with **attacker-controlled** `loanId`/`principal` — no auth, no loan-existence check |
| `test_control_excess_split_conserves_proceeds` | M1 runner-up | B (neg. control) | **PASS** | the proceeds-split arithmetic conserves (≤ proceeds, dust < 2 wei) → the split math is *not* the bug; isolates the finding to the missing callback authentication |
| `test_burnAndWithdraw_strands_unlisted_asset` | M3 UserVault / STATE | B | **PASS** | vault burned first; unlisted NFT permanently owned by the burned vault; re-call reverts → no recovery path |
| `test_per_share_rounding_strands_funds` | M2 WithdrawalQueue / SHARE+DOS | B | **PASS** | `sum(getAvailable) < balance`; stranded = `funded % totalShares`, never claimable |
| `test_div_by_zero_before_first_mint` | M2 (liveness) | B | **PASS** | `getAvailable` reverts (÷0) while `getTotalShares == 0` |

## Reading (pre-reveal, no answer key)
- **M1 distribute** is the strongest: a clean, permissionless, real-code Tier-B proof that an unauthenticated
  caller-supplied `_loan` drives a trusted `loanLiquidation` callback into a registered Pool/LoanManager. The economic
  write-off inside a *real* Pool (`_loanTermination` accounting) is **not** executed here (partial runtime) — recorded
  as **PARTIAL on economic outcome, COMPLETE on reachability + parameter control**.
- **M3 / M2** are real but lower-severity (self-inflicted stranding footgun; dust-scale rounding loss + a pre-mint
  liveness revert).
- Each PoC names a victim and asserts before/after state (L2) and an outcome (L3). No fabricated passes; the one
  initial failure (control reverting on EOA lender) was a harness bug, fixed, and re-run.

## Pre-reveal candidate strength (no severity assigned — advisory)
| mech | class | strength | basis |
|---|---|---|---|
| M1 distribute spoofed callback | ACCOUNTING/ACCESS | **STRONG (reachability) / PARTIAL (economic)** | runtime PoC + control |
| M3 burnAndWithdraw stranding | STATE | MODERATE | runtime PoC; self-inflicted |
| M2 wq rounding/liveness | SHARE/DOS | MODERATE-LOW | runtime PoC; dust-scale |
| M4 offers | ORDER | NONE | no exact hypothesis; NEEDS_MORE_RUNTIME |

Next: Phase 9 — freeze + hash the full pre-reveal set, then Phase 10 reveal.
