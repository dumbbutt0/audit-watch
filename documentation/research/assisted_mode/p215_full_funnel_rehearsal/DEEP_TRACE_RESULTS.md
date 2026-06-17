# P215 — DEEP_TRACE RESULTS (bounded blind discovery)

5 key-blind deep_trace Sonnet subagents over the value clusters (source-only; sealed answer key never accessed;
each emitted JSON only). ~18 genuine raw hits + 6 refuted surfaces → root-cause-deduped to **12 routed candidates**
(cap = 12). Folded: the admin-TSS-rotation family (custody+connector+ZetaNonEth) → ZETA-03; UniV3+PancakeV3
`getEthFromZeta` nonReentrant pair → ZETA-10.

| Cluster (subagent) | Genuine hits | Routed candidate(s) |
|---|---|---|
| evm_custody | withdraw FoT insolvency; deposit zetaFee FoT; TSS rotation no timelock; connector self-rotation | ZETA-01, ZETA-02, ZETA-03 |
| cross_chain_msg | onReceive no whenNotPaused; no internalSendHash dedup; interactor empty-bytes bypass; onRevert no send-binding | ZETA-04, ZETA-05, ZETA-06 |
| zevm_gas_fee | GAS_LIMIT=0 zero fee; mutable SYSTEM_CONTRACT mint authority; Deposit-event from; rogue connector constructor | ZETA-07, ZETA-08, ZETA-09 |
| amm_consumer | UniV3/PancakeV3 nonReentrant; Trident getPools()[0]; deadline=block.timestamp+200 | ZETA-10, ZETA-11, ZETA-12 |
| token_supply | ZetaNonEth self-rotate mint; renounce collapses 2-party; WZETA uint(-1); no supply cap | (folded → ZETA-03) |

## Routed candidates (12) — claimed ceiling
1 Critical (ZETA-03) · 7 High (ZETA-01,04,05,06,08,10,11) · 4 Medium (ZETA-02,07,09,12).
Permissionless: ZETA-09, ZETA-10, ZETA-12 (+ ZETA-11 via pool front-run). Privileged: ZETA-03, ZETA-05, ZETA-08
(+ ZETA-04 via TSS). Conditional: ZETA-01, ZETA-02, ZETA-06.

## Refuted / early-rejected at discovery (recorded, not routed)
ZETA-R1 deposit reentrancy (nonReentrant present) · ZETA-R2 whitelist bypass (onlyTSS) · ZETA-R3 ZRC20 transferFrom
CEI (atomic revert) · ZETA-R4 WZETA uint(-1) infinite allowance (canonical WETH) · ZETA-R5 Deposit `from` event
attribution (informational) · ZETA-R6 ZetaNonEth no supply cap (folded; relies on out-of-scope connector trust).

Full register + per-candidate fields: `CANDIDATE_REGISTER.json`. Substrate: `output/findings_deep_trace.json` →
`output/merged_findings.json` (1 Critical + 7 High + 4 Medium).
