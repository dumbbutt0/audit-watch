# P138 — Corpus Design & Labels (post-hoc only; NOT given to blind subagents)

10 items, 3 architectures (noya / size-credit / blackhole), balanced 5 buggy / 5 clean. Each blind packet =
function body + direct callees + a NEUTRAL one-line intended-semantics (no sibling, no role/bug hints — the
P137-T3 "aided" lesson). Labels below are used only to grade post-hoc.

## Buggy (5) — known awarded value-provenance-family bugs
| id | arch | contract.function | mechanism (answer key) |
|---|---|---|---|
| B1 | noya | NoyaValueOracle._getValue (4-arg) | H-03 stale loop var: in-loop hop uses static `asset` not updated `quotingToken` |
| B2 | noya | MorphoBlueConnector._getPositionTVL | H-19 aggregation sign: debt `borrowAmount` ADDED instead of subtracted |
| B3 | noya | BalancerConnector._getPositionTVL | H-13 weighted-pool operand: divides already-weight-adjusted balance by weight again |
| B4 | size | SellCreditMarket.validateSellCreditMarket | M-02 wrong-value: cash `params.amount` checked vs CREDIT-named `minimumCreditBorrowAToken` (should check derived credit) |
| B5 | blackhole | RewardsDistributor.claim_many | M-04 missing recipient resolution: omits `avm.getOriginalOwner` for AVM-managed tokenIds (sibling `claim` resolves it) |

## Clean (5) — with clean_label_confidence
| id | arch | contract.function | clean_label_confidence | basis |
|---|---|---|---|---|
| C1 | blackhole | RewardsDistributor.claim | HIGH | the correct M-04 sibling that DOES resolve `getOriginalOwner` (explicitly non-buggy in answer-key context) |
| C2 | noya | MorphoBlueConnector.convertCToL | MEDIUM | simple correct conversion; no known issue; not externally proven clean |
| C3 | blackhole | RewardsDistributor.claimable | MEDIUM | trivial view delegating to _claimable; no known issue |
| C4 | noya | ChainlinkOracleConnector.getTokenDecimals | MEDIUM | returns 10**decimals; trivial correct |
| C5 | size | AccountingLibrary.debtTokenAmountToCollateralTokenAmount | MEDIUM | standard correct debt->collateral conversion; no known issue |

## FP-rate handling (per user refinement)
- strict_clean_fp_rate = (clean items flagged finding|likely_exploitable) / all 5 cleans.
- high_confidence_clean_fp_rate = same over HIGH-confidence cleans only (n=1: C1).
- A flagged non-HIGH clean with plausible source evidence is graded NEEDS_HUMAN, not FALSE_POSITIVE, unless the
  label is HIGH AND the finding is contradicted by source.
