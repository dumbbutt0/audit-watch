# P300 — CAMPAIGN_RESULTS

Targets: 4 (silo, revert-lend, panoptic + beanstalk reuse). **confirmed-FP = 0** · submission-filter leaks = 0.

## Per target
| target | recall_useful | recall_any | novelty (novel/known) | validity confirmed |
|---|---|---|---|---|
| silo-finance-2025-03-strict-eval | 0.5 | 0.833 | 0/16 | ['M-05', 'M-06'] |
| revert-lend-2024-03-strict-eval | 0.032 | 0.129 | 0/12 | - |
| panoptic-2025-12-strict-eval | 0.0 | 0.136 | 0/3 | ['M-01'] |
| beanstalk-2024-05 (reuse) | 0.42 | 0.53 | 0/44 | AC-001,AC-003 (exploit) + LG-001,PC-001,SN-001 (logic) |

## Aggregate
- targets with a confirmation (RANGE): **3** (silo-finance-2025-03-strict-eval, panoptic-2025-12-strict-eval, beanstalk-2024-05)
- new loci confirmed this campaign: **3** (silo M-05, silo M-06, panoptic M-01)
- submission filter: **3 submit** / 1 needs_human, **0 leaks**
- cumulative executed-confirmed across the whole program: 20 (through P299) + 3 (this campaign) = **23 loci**

## Confirmations (verifier = sole judge; confirmed-FP=0)
- **silo M-05** (HIT) logic_differential — _accrueFee/_update mints fee shares before _afterTokenTransfer, so fee shares capture rewards accrued to pre-existing holders (50e18 vs 0 control).
- **silo M-06** (PARTIAL) logic_differential — _accruedFeeShares Floor rounding strands the fee / misallocates the residual to existing LPs vs a vault-favoring control.
- **panoptic M-01** (ADJACENT) logic_differential — getLiquidationBonus cross-shortfall legs round in OPPOSITE directions (convert floor vs RoundingUp) → bonus off by the round delta vs a consistent-rounding control.

## Honest non-confirmation (the FP/honesty guard working)
- **revert-lend H-03** (PARTIAL) — built as an exploit, **REFUTED** by the executed PoC: the claimed cross-position impact via unvalidated `data` is structurally gated by PER-TOKEN NPM approval (a callee acting on a different tokenId reverts at the approval gate). → needs_human, not confirmed. Staged as a rejection-rule proposal.

## Precision tightening (staged; human-promote)
data/learning/_proposed/p300_rejection_rule_proposals.jsonl (promoted=false): the per-token-approval-gated impact pattern + the submit-iff-executed-confirmed policy. NOT promoted (promote_learning is human-run).
