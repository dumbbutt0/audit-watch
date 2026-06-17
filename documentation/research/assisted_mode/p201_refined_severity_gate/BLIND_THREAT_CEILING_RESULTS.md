# P201 — blind threat-ceiling results (FREEZE 1)

18 Sonnet subagents, one per pre-registered surface, each on production `deep_trace.md` (`ef93a6c2`) + verbatim
source only. Blind firewall: prompts leak-scan CLEAN; raw outputs verbatim in `raw_outputs/zeta-*.json`, output
leak-scan CLEAN; all 18 valid JSON. **FREEZE 1 hash** (md5 first-8 of concatenated raw outputs): `77d57371`.

## Verdict distribution (threat ceiling, pre-calibration)
| verdict | count |
|---|---|
| HIGH_THREAD | **16** |
| MEDIUM_THREAD | **2** (zeta-01 custody deposit, zeta-14 gas setters) |
| CRITICAL / DEAD_END / NEEDS_MORE_CONTEXT | 0 |

**16/18 ≥HIGH (88.9%)** — reproduces the over-HIGH ceiling skew out-of-sample a third time.

## Per-surface (blind) — counts of carried mechanisms
| id | surface | verdict | #selected mechs |
|---|---|---|---|
| zeta-01 | ERC20Custody.deposit | MEDIUM | 3 |
| zeta-02 | ERC20Custody.withdraw | HIGH | 2 (+1 unresolved) |
| zeta-03 | ERC20Custody TSS/whitelist | HIGH | 2 |
| zeta-04 | ZetaConnector.base updateTss/pause | HIGH | 2 |
| zeta-05 | ZetaConnector.eth send/onReceive/onRevert | HIGH | 3 |
| zeta-06 | ZetaConnector.non-eth | HIGH | 3 |
| zeta-07 | ZetaConnector.non-eth setMaxSupply | HIGH | 1 (+unresolved) |
| zeta-08 | ZetaInteractor | HIGH | 2 |
| zeta-09 | ZRC20.deposit | HIGH | 2 |
| zeta-10 | ZRC20.withdraw/withdrawGasFee | HIGH | 2 |
| zeta-11 | ZRC20 update setters | HIGH | 3 |
| zeta-12 | ZRC20 burn/transferFrom | HIGH | 2 |
| zeta-13 | SystemContract.depositAndCall | HIGH | 2 |
| zeta-14 | SystemContract gas setters | MEDIUM | 2 |
| zeta-15 | ZetaConnectorZEVM send/withdraw | HIGH | 2 |
| zeta-16 | WZETA deposit/withdraw | HIGH | 1 (+unresolved) |
| zeta-17 | ZetaTokenConsumerUniV2 | HIGH | 2 |
| zeta-18 | Zeta.non-eth mint/burn | HIGH | 2 |

Recall note (not scored here): the blind run heavily re-derives cross-chain / auth / value-flow mechanisms
(tx.origin attribution, CEI/reentrancy, TSS-key trust, pause asymmetry, supply/mint trust). Whether each maps to an
*awarded* finding is determined only post-freeze (scoring); these are blind candidates, not confirmed awarded bugs.
Many awarded zetachain Highs live in the off-chain observer layer and are not reachable by this Solidity sample.
