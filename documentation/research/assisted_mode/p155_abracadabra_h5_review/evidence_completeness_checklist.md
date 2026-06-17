# P155 — Gate 6: Evidence Completeness

| Required evidence | Present? | Source |
|---|---|---|
| Affected contract / function names | ✓ | `LockingMultiRewards`: `balanceOf`/`totalSupply`/`earned` (boost), `processExpiredLocks` (sole de-boost, onlyOperators) |
| Root cause | ✓ | Boost on `bal.locked`/`lockedSupply` removed only by operator-gated `processExpiredLocks`, not at `unlockTime`; no user unlock (source_reachability_map.md / source_intent_table.md) |
| Attacker scenario | ✓ | `stake(amount,true)` → wait past `unlockTime` → keep boosted reward share while unprocessed (attacker_model_table.md) |
| Runtime PoC command | ✓ | `forge test -vv` in `pocs/p154/` (P154 test_commands.md / execution_output.txt) |
| Actual result | ✓ | W2 unprocessed: A 525e18 / B 175e18 (3:1) |
| Expected result | ✓ | post-expiry should be fair 1:1 |
| Corrected behavior | ✓ | prompt `processExpiredLocks` (real code) → A 350e18 / B 350e18 (1:1); over-accrual → 0 |
| Impact statement | ✓ | zero-sum reward redistribution from honest stakers; no protocol-fund loss; quantified 175e18 (severity_bound_analysis.md) |
| Assumptions & limitations | ✓ | magnitude operator-delay-dependent; no protocol-fund loss; bounded by trusted-operator liveness |
| Scope & duplicate caveats | ✓ | trusted-operator scope (operator_scope_analysis.md); duplicate_unknown + public-known cannot_assess (novelty_duplicate_check.md) |
| Recommended mitigation | ✓ | de-boost at `unlockTime` (compute boost from per-lock `unlockTime > block.timestamp`), or add a user-callable expire/unlock so honest users can self-remediate |

## Classification: **evidence_complete_for_human_review**
Every report-drafting element is present. The only open items — the final severity grade (Med↔Low) and the
public-known/duplicate determination — are the **outputs** the human review is meant to produce, not missing
inputs. Reachability, root cause, and impact are fully evidenced.
