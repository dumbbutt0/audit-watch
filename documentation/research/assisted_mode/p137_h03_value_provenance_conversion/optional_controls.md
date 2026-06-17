# P137 — Controls (specificity / over-flag measurement)

3 control functions, each a fresh blind subagent run (same prompt). Goal: does the value-provenance prompt
over-flag clean / already-covered code?

| Control | Class | Blind decision | Correct? | Note |
|---|---|---|---|---|
| `MorphoBlueConnector.convertCToL` | clean correct conversion | **strong_clear** | ✅ (no over-flag) | rejected unused-param / external-trust as out-of-scope |
| `ChainlinkOracleConnector.getValue` | single-hop oracle (units/decimals = H-01 area) | **needs_human** | ✅ (no false finding) | surfaced the inverse-branch decimals concern but routed to human, not asserted |
| `MorphoBlueConnector._getPositionTVL` | connector TVL (CPA-caught H-19) | **finding** | ✅ mechanism (sign error) | **aided**: my packet annotated supply/collateral=asset, borrow=DEBT — a leading role hint; discount as blind evidence |

## Read
- **No false positive on the clean control** (convertCToL → strong_clear) → the prompt is specific, not noisy.
- The single-hop oracle returned **needs_human** (careful uncertainty), not a confident wrong finding → good
  discipline (it even partially sensed the real H-01 units issue without over-claiming).
- The TVL control returned a correct `finding`, but because my bundle handed it the asset/liability roles, it is
  not a clean demonstration of unaided generalization — noted honestly.

## Limitation
n is tiny (1 target + 3 controls, 1 aided). This establishes the prompt CAN blind-discover H-03 and is specific on
a clean control; it does NOT establish a robust precision/recall rate. A larger blind value-provenance corpus
would be needed before any automation beyond advisory routing.
