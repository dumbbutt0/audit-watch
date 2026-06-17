# P131 — Specialist Review of the Boost-Delta (in-session, source-grounded)

In-session specialist + ICE reasoning over the boost-delta. Recall arm read in full; FP arm categorized
(60 fns) with representatives read. This is a reviewer assessment, not the automated 13-specialist stack.

## Recall arm — are the now-visible awarded functions genuinely reviewable?
| Function | Mechanism | Source observation | Discoverability |
|---|---|---|---|
| `BalancerConnector._getPositionTVL` | value_exit | TVL from **spot** `getPoolTokens` balances × single-token oracle / weight / `totalSupply` — classic manipulable-LP / read-only-reentrancy spot-TVL | **HIGH** (economic/oracle) |
| `ChainlinkOracleConnector.getValue` | value_exit | delegates to `getValueFromChainlinkFeed`; feed read — staleness/heartbeat/L2-sequencer surface | **HIGH** (oracle) |
| `NoyaValueOracle._getValue` | value_exit | multi-hop source chaining loop (`for sources[i]`), path-dependent valuation | **MED-HIGH** (oracle) |
| `*Connector._getPositionTVL` (Aerodrome/Morpho/Pendle/Silo) | value_exit | same spot-balance TVL-computation class as Balancer | **MED-HIGH** |

All 8 sit in exactly the `value_exit`/oracle surface the awarded bugs occupy. **OFF they score 2 → cheap-sweep
(clear-biased) → the P129 "under-ranked / wrong-contract" miss pattern.** ON they enter deep-pass where a
specialist would plausibly surface them. ⇒ the recall gain is **real, not nominal** (visibility is necessary
and these functions are substantively reviewable).

## FP arm — do the 60 non-awarded boosted functions inflate FP?
| Category | n | Assessment |
|---|---|---|
| on-class value/TVL/price logic | 37 (62%) | **Not FP** — same manipulable-value surface as the awarded bugs (e.g. `CompoundConnector._getPositionTVL` has `positiveBalance - negativeBalance` feeding a value → legit underflow/manipulation lead). Connectors not awarded ≠ safe; valid-unawarded → **needs_human_review**. |
| trivial getters / metadata | 12 (20%) | **Mild noise** — e.g. `AaveConnector._getUnderlyingTokens` returns `new address[](0)` (pure, empty). A specialist clears instantly; ~zero speculative-flag risk. |
| other | 8 (13%) | mixed; mostly view helpers. |
| **mock contract** (`ConnectorMock2`) | 3 (5%) | **Genuine noise** — a mock got boosted; its file `ConnectorMock2.sol` isn't caught by the `Mock*.sol` exclude glob. Fixable. |

## Speculative-FP (P129's `arithmetic`/`economic_attack`) check
The boosted set is **view value-getters**, not state-changing complexity. The on-class ones are legitimate
`value_exit` leads (an economic/arithmetic specialist reviewing them is doing useful work); the trivial/mock
ones clear fast. **No mechanism by which the boost manufactures speculative arithmetic/economic_attack FPs** —
it does not add new state-mutating call paths, only re-ranks existing read logic. So the P129 FP-source concern
is **not realized** by this boost.

## Net
- Recall: **real** (+8 awarded value_exit/oracle functions made reviewable).
- FP-tendency: **low-moderate and mostly benign** — ~62% productive on-class widening, ~21% trimmable noise
  (trivial getters + mock), no speculative-FP inflation. Non-awarded confirmed leads → needs_human_review.
