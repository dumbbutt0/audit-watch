# P287 — EVIDENCE_AND_READY_GATE (blind, kelp)

Ran `completion_evidence_deriver` (P279/P282/P283/P284) + `poc_readiness_evidence_gate` (P281/P285). severe FP=0, guard
PASS. status_tally: READY_FOR_POC_INTENT 1 · NEEDS_MORE_EVIDENCE 1 · INLINE_GUARD_REFUTED 4.

## Per-candidate
| candidate | status | basis |
|---|---|---|
| **LRTDepositPool.getRsETHAmountToMint** | **READY_FOR_POC_INTENT** | P284 D4.6 oracle-normalization REFERENCE_FOUND (MEDIUM): the rsETH mint valuation `(amount * getAssetPrice(asset)) / getRSETHPrice()` consumes an oracle price with no in-span decimals-normalization / staleness check; D1 inline_guard=False (view, no access guard); core dims upgraded MEDIUM/MEDIUM/MEDIUM. |
| LRTDepositPool.getTotalAssetDeposits | NEEDS_MORE_EVIDENCE | UNKNOWN class; value-flow present, no source-backed deviation. |
| RSETH.burnFrom | INLINE_GUARD_REFUTED | real role guard (burn role) — P285 D1 EXECUTION_GUARD. |
| LRTDepositPool.getAssetDistributionData | INLINE_GUARD_REFUTED | guarded read. |
| LRTConfig.addNewSupportedAsset | INLINE_GUARD_REFUTED | `onlyLRTAdmin` modifier — EXECUTION_GUARD. |
| LRTConfig.updateAssetDepositLimit | INLINE_GUARD_REFUTED | `onlyLRTManager` modifier — EXECUTION_GUARD. |

## READY candidate — source faithfulness (pre-reveal, source only)
`LRTDepositPool.getRsETHAmountToMint`: `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) /
lrtOracle.getRSETHPrice();`. The price provider `ChainlinkPriceOracle.getAssetPrice` returns
`AggregatorInterface(feed).latestAnswer()` — **raw `latestAnswer()` with NO staleness (`updatedAt`/`roundId`) check and
no decimals normalization** (the classic deprecated-Chainlink anti-pattern). So the pipeline's D4.6 mechanism is
SOURCE-FAITHFUL: the mint valuation depends on an unguarded, potentially-stale price. (Locus flagged = the consumer
`getRsETHAmountToMint`; the flaw lives in the `ChainlinkPriceOracle.getAssetPrice` it transitively calls — same-area,
correct mechanism.)

## Precision note
The 4 INLINE_GUARD_REFUTED are genuine admin/role-guarded functions (P285 D1 holding on a fresh target). The one READY is
the one value-flow candidate with a source-backed deviation. severe FP=0.
