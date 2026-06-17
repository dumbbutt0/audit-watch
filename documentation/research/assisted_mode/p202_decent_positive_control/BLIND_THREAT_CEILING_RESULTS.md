# P202 — blind threat-ceiling results (FREEZE 1)

14 Sonnet subagents, one per pre-registered surface, each on production `deep_trace.md` (`ef93a6c2`) + verbatim
source only. Prompts leak-scan CLEAN; raw outputs verbatim in `raw_outputs/decent-*.json`, output leak-scan CLEAN;
all 14 valid JSON. **FREEZE 1 hash** (md5 first-8 of concatenated raw outputs): `54abf9ca`.

## Verdict distribution (threat ceiling, pre-calibration)
| verdict | count |
|---|---|
| CRITICAL_THREAD | 6 (decent-01,02,03,06,07,09) |
| HIGH_THREAD | 7 (decent-04,05,08,10,11,12,13) |
| MEDIUM_THREAD | 1 (decent-14 access-control setters) |

**13/14 ≥ HIGH (92.9%)** — reproduces the over-HIGH ceiling skew. Unlike zetachain (P201, off-chain Highs), the
blind run here surfaces **contract-level value-flow mechanisms** (receiveFromBridge access-control, DcntEth
setRouter mint/burn, UniSwapper public swap, sgReceive source-validation, bridge accounting), several of which are
strong permissionless-theft candidates.

## Per-surface (blind)
| id | surface | verdict |
|---|---|---|
| decent-01 | UTB.swapAndExecute | CRITICAL |
| decent-02 | UTB.bridgeAndExecute | CRITICAL |
| decent-03 | UTB.receiveFromBridge | CRITICAL |
| decent-04 | UTBExecutor.execute | HIGH |
| decent-05 | UTBFeeCollector | HIGH |
| decent-06 | UniSwapper | CRITICAL |
| decent-07 | StargateBridgeAdapter | CRITICAL |
| decent-08 | DecentBridgeAdapter | HIGH |
| decent-09 | DcntEth mint/burn/setRouter | CRITICAL |
| decent-10 | DecentEthRouter.bridge | HIGH |
| decent-11 | DecentEthRouter.onOFTReceived | HIGH |
| decent-12 | DecentEthRouter.redeem/liquidity | HIGH |
| decent-13 | DecentBridgeExecutor.execute | HIGH |
| decent-14 | access-control setters | MEDIUM |

Recall note (not scored here): the blind run re-derives many plausible bridge value-flow mechanisms. Which map to
*awarded* findings is determined only post-freeze (scoring); these are blind candidates, not confirmed awarded bugs.
Calibration is applied next by a **fresh firewall subagent** (FREEZE 2), then scored.
