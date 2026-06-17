# P170 — Final cross-architecture multi-family sweep (renzo)

P169 method exactly, on **renzo-2024-04-bench** (EigenLayer LRT). 15-family hygiene-filtered (protocol_src)
sweep, reject-first, predictions logged first, **0 harnesses built** (all refuted). Last campaign run — stopped
after renzo.

## Top 3 candidates (all predicted `static_false_positive`; all matched)
| ID | Family | Fn | Bucket | Why refuted |
|---|---|---|---|---|
| **H22** | escrow/withdrawal/claim | `WithdrawQueue.withdraw`/`claim` | SOURCE_REFUTED (G3) | `claim` reads `withdrawRequests[msg.sender][index]` (own array only); `amountToRedeem` **locked at request time**; request deleted (swap-and-pop) before transfer; `nonReentrant`; `claimReserve` add==sub. Foreign-claim / double-claim / stale-rate all guarded |
| **H23** | user-controlled recipient | `XERC20Lockbox.withdraw/withdrawTo` | NO_ATTACKER_PROFIT (G3) | 1:1 lockbox; `_withdraw(msg.sender,…)` burns the caller's own XERC20; `withdrawTo`'s `_to` is just a recipient for the caller's **own** funds |
| **H24** | rounding/accounting/oracle | `RestakeManager.deposit/depositETH` | SOURCE_REFUTED (G4) | ezETH mint is **oracle-valued** (`renzoOracle.lookupTokenValue` + `calculateTVLs`), not balanceOf/reserve-based → classic first-depositor/donation inflation doesn't apply; `nonReentrant` + `maxDepositTVL` + per-token caps. Depositor gets fair value, no excess (residual fine-rounding noted, not attacker-forced) |

## Family coverage
oracle (83) / liquidation (82) signals present, but top entries are trusted-oracle / operator-role /
EigenLayer-delegated → below the top-3 score. fee (8) → fixed `feeRecipient`. Selected the 3 strongest
value-bearing permissionless paths across escrow-claim, user-recipient, and rounding/oracle families. No
top-tier convertible surfaced.

## Prediction vs outcome
H22 SFP→SFP · H23 SFP→SFP · H24 SFP→SFP — **3/3** (campaign calibration **15/15**).

## Scorecard after P170
candidates 20 · reportable 1 · runtime_confirmed 1 · harnesses_built 1 · harnesses_avoided 19 ·
source_refutations 7 · gate_refutations 12 · **reportables_per_harness 1/1** · **prediction_accuracy 15/15** ·
**fabrication_rate 0/20**. 0 reportable / 0 harness candidate in renzo → see CLOSEOUT.md.
