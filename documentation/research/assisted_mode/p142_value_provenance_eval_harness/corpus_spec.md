# P142 — Corpus Spec

Seed dataset: `data/research/value_provenance_eval/corpus.jsonl` — one JSON row per eval item, seeded from the
**real recorded** P137/P138/P141 blind outcomes (no fabrication). 11 rows across 3 architectures.

## Row fields
| field | meaning |
|---|---|
| `item_id` | stable id (P138 B1..B5 / C1..C5, or P141-SOLV) |
| `arch` | noya / blackhole / size |
| `audit_id`, `contract`, `function`, `file_path` | location (informational; harness reads no source) |
| `label` | `buggy` or `clean` (ground-truth label for recall / clean-FP) |
| `expected_shape` | mechanism shape label |
| `recorded_decision` | the REAL blind decision: finding / likely_exploitable / needs_human / strong_clear / error |
| `confidence` | the recorded confidence |
| `clean_label_confidence` | for cleans: HIGH/MEDIUM (P138 schema) |
| `source_phase` | P137 / P138 / P141 |
| `blind_output_ref` | **provenance**: deliverable path + `#<agent_id>` (refused if absent) |

## Seeded items
| item | arch | contract.function | label | recorded_decision | provenance agent |
|---|---|---|---|---|---|
| B1 | noya | NoyaValueOracle._getValue | buggy | finding | abb4f91f37865f53c |
| B2 | noya | MorphoBlueConnector._getPositionTVL | buggy | finding | ac187eac0d7fb82ff |
| B3 | noya | BalancerConnector._getPositionTVL | buggy | strong_clear (MISS) | a2ca4f387c3e69c76 |
| B4 | size | SellCreditMarket.validateSellCreditMarket | buggy | needs_human | a281e3db7ab349438 |
| B5 | blackhole | RewardsDistributor.claim_many | buggy | finding | a67fb918317d02d07 |
| C1 | blackhole | RewardsDistributor.claim | clean (HIGH) | strong_clear | a8b0c3cd763de3d36 |
| C2 | noya | MorphoBlueConnector.convertCToL | clean (MED) | strong_clear | ad49270e787be5c47 |
| C3 | blackhole | RewardsDistributor.claimable | clean (MED) | strong_clear | af34d02a9bfb2d68a |
| C4 | noya | ChainlinkOracleConnector.getTokenDecimals | clean (MED) | strong_clear | a5dc9828a2916d98f |
| C5 | size | AccountingLibrary.debtTokenAmountToCollateralTokenAmount | clean (MED) | strong_clear | a403bf1955e6383ae |
| P141-SOLV | noya | SolvencyV2.convertAmountsToValues | clean (HIGH) | strong_clear | aa6d4aac2a89ed1b9 |

## Extending the corpus
Add a row with provenance to replay an existing recorded outcome, OR add a row + have an operator run the
in-session `deep_pass_value_provenance` skill and drop a P140-schema completion artifact (the harness ingests it
the same way). A row lacking `blind_output_ref`/valid `recorded_decision` is **refused** — the harness never
invents a decision.
