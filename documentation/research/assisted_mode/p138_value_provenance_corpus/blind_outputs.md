# P138 — Blind Outputs (verbatim subagent decisions)

10 fresh uncontaminated general-purpose subagents, each given ONLY the deep_pass_value_provenance prompt + one
neutral code bundle (no repo/answer-key access). I authored none of the decisions. (Full reasoning captured in
the run transcript; decisions + agent ids below.)

## Buggy items
| id | function | blind decision | shape (subagent's words) | agent |
|---|---|---|---|---|
| B1 | NoyaValueOracle._getValue | **finding** (high) | stale/static loop var: in-loop uses static `asset` not updated `quotingToken` | abb4f91f37865f53c |
| B2 | MorphoBlueConnector._getPositionTVL | **finding** (high) | debt-term-sign-inversion: `+ borrowAmount` instead of subtract | ac187eac0d7fb82ff |
| B3 | BalancerConnector._getPositionTVL | **strong_clear** (high) | concluded `token1bal/_weight` extrapolation is the correct standard formula | a2ca4f387c3e69c76 |
| B4 | SellCreditMarket.validateSellCreditMarket | **needs_human** (medium) | wrong_basis_validation: cash `params.amount` vs CREDIT-named `minimumCreditBorrowAToken` | a281e3db7ab349438 |
| B5 | RewardsDistributor.claim_many | **finding** (high) | recipient under-resolved: ownerOf vs avm.getOriginalOwner for AVM-managed tokenIds | a67fb918317d02d07 |

## Clean items
| id | function | blind decision | clean_label_confidence | agent |
|---|---|---|---|---|
| C1 | RewardsDistributor.claim | **strong_clear** (high) | HIGH | a8b0c3cd763de3d36 |
| C2 | MorphoBlueConnector.convertCToL | **strong_clear** (high) | MEDIUM | ad49270e787be5c47 |
| C3 | RewardsDistributor.claimable | **strong_clear** (high) | MEDIUM | af34d02a9bfb2d68a |
| C4 | ChainlinkOracleConnector.getTokenDecimals | **strong_clear** (high) | MEDIUM | a5dc9828a2916d98f |
| C5 | AccountingLibrary.debtTokenAmountToCollateralTokenAmount | **strong_clear** (high) | MEDIUM | a403bf1955e6383ae |

Notable blind reasoning quality: B1 traced per-iteration (hop1 uses asset on an s0-denominated amount); B2 derived
"TVL = owned − owed" and flagged the `+` sign; B4 found the exact cash-vs-credit basis mismatch but honestly
routed to needs_human (couldn't trace exploit direction from the bundle); B3 produced sound weighted-pool math
and cleared (a genuine recall miss on the subtle H-13). All 5 cleans cleared with explicit no-divergence reasoning.
