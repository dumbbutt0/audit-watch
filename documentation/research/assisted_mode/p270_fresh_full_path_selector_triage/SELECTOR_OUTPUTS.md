# P270 — SELECTOR_OUTPUTS (Phase 3)

Frozen **P267** selector (`mechanism_pairwise_selector.py`, `b0623b8c88752059`) over B/C top-2 mechanism pairs from
the wise-lending advisory candidates. Dimensions assigned BLIND from source, pre-reveal. Input
`outputs/p270_selector_input.json` (`d754636191f5385f`); decisions `outputs/p270_selector_decisions.json`
(`4bc665965d611573`); guard PASS, 0 violations.

| pair | M1 (high-impact) vs M2 (easy) | outcome | anti-easy-PoC | gap |
|---|---|---|---|---|
| **L1 pendle_share** | PendlePowerFarmToken share-price/first-deposit inflation vs mintFee dust | **KEEP_BOTH** | **YES** | 11 |
| **L2 liquidation** | WiseCore liquidation share/collateral misallocation vs liquidation UX revert | **KEEP_BOTH** | **YES** | 3 |
| **L3 baddebt** | FeeManager bad-debt accounting error vs event/rounding | **KEEP_BOTH** | **YES** | 3 |
| Lneg posnft | PositionNFTs mint (claimed systemic, **unsupported/refuted/privileged**) vs benign | **REFUTE_M1_FIRST** | no | 9 |

## Effect
The selector **preserves all three high-impact award-class mechanisms** (Pendle-share inflation, liquidation
misallocation, bad-debt accounting) via KEEP_BOTH — none is dropped for its easier rival (dust/UX-revert/event). The
unsupported high-drama NFT-mint mechanism is correctly REFUTE_FIRST'd (not pushed on drama). These KEEP_BOTH decisions
feed the impact-first triage (Phase 4). Frozen before triage.
