# P287 — DISCOVERY_AND_ROUTING (blind, kelp-2023-11-holdout)

Ran the frozen blind chain on the existing coverage_manifest (no answer-key access):
`p276_corpus_replay` (P264 shadow harness → P273 coverage router → P269 triage) → `expanded_validation_queue`.

## Results
- Advisory candidates (P264 shadow): **13**.
- Coverage classes routed (P273): ACCESS_CONTROL_AUTHORIZATION · SHARE_ROUNDING_PRECISION · UNKNOWN_OTHER.
- Triage (P269): 5 candidates advanced.
- Validation queue (P278): **6** candidates, 3 classes, max_class_fraction 0.33, anti-monoculture OK, 0 injected.
- Guard status: PASS (all advisory/research_only; no severity/routing leakage).

## Validation queue (6)
| candidate | class |
|---|---|
| LRTDepositPool.getRsETHAmountToMint | SHARE_ROUNDING_PRECISION |
| LRTDepositPool.getTotalAssetDeposits | UNKNOWN_OTHER |
| RSETH.burnFrom | SHARE_ROUNDING_PRECISION |
| LRTDepositPool.getAssetDistributionData | UNKNOWN_OTHER |
| LRTConfig.addNewSupportedAsset | ACCESS_CONTROL_AUTHORIZATION |
| LRTConfig.updateAssetDepositLimit | ACCESS_CONTROL_AUTHORIZATION |

The surface routed to the LRT deposit/valuation core (deposit pool, rsETH token, oracle-fed mint) plus admin config —
a sensible attack surface for an LRT protocol. No answer key consulted.
