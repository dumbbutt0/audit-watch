# Failure Analysis — Beanstalk Finale

Every MISS / PARTIAL with its most-likely pipeline failure label.

## Failure-label frequency (MISS + PARTIAL)

- **Missed accounting invariant** — 14
- **Missed oracle/precision/decimal issue** — 6
- **Missed state transition** — 6
- **Missing domain knowledge** — 4
- **Missed attacker-controlled input** — 4
- **Missed lifecycle edge case** — 3
- **Weak invariant extraction** — 3
- **Severity reasoning failure** — 2
- **Agent did not inspect the correct contract** — 2
- **Architecture mapping failure** — 2
- **Agent found the issue but failed to escalate it** — 1
- **Missed cross-chain or migration edge case** — 1

## Per-finding

| Sub | Class | Failure label | Reason |
|---|---|---|---|
| 90 | PARTIAL | Severity reasoning failure | Pipeline found convert-penalty manipulation (sandwich/spot reserves) but framed it as MEV capacity s |
| 99 | MISS | Agent did not inspect the correct contract | Tractor counter getter never inspected. |
| 128 | PARTIAL | Missed lifecycle edge case | CC-002 found receiveL1Beans always reverts (same broken external-Bean migration), but framed as 'rec |
| 139 | MISS | Weak invariant extraction | Pipeline found the ReseedField loop bug but not the temperature/type-mismatch field-config bug. |
| 140 | PARTIAL | Severity reasoning failure | DS-003 found the same nested mint loop OOG risk but downgraded to Low/admin-robustness; contest rate |
| 142 | MISS | Architecture mapping failure | cross_chain agent explicitly inspected and CLEARED the L1/L2 BRIDGE pair as consistent for OP-stack  |
| 186 | PARTIAL | Missed oracle/precision/decimal issue | Same LibWell decimal/precision family; AR-002 named the liquidity helper but emphasized the price he |
| 200 | MISS | Agent did not inspect the correct contract | beginBarnRaiseMigration oracle-support validation never inspected. |
| 204 | PARTIAL | Missed accounting invariant | snapshot agent found flood/rain root snapshot timing issues but not specifically the double-flood mo |
| 227 | PARTIAL | Missed state transition | BSA-001 found stalk computed ~0 due to whitelist-ordering; overlaps grown-stalk miscalc but via a di |
| 229 | MISS | Weak invariant extraction | Missing scaling-constant in reward math never identified. |
| 239 | PARTIAL | Missed accounting invariant | Pipeline found stalk-amount errors in migration/reseed but not this exact computation. |
| 241 | MISS | Missed accounting invariant | transferStalk rounding formula never analyzed. |
| 242 | MISS | Missed accounting invariant | Pre-migration unmowed-reward forfeiture not detected. |
| 248 | MISS | Missed state transition | Missing depositIdList registration not detected. |
| 259 | MISS | Missing domain knowledge | Non-standard-token permit incompatibility not detected. |
| 260 | PARTIAL | Missed accounting invariant | SN-002 found germination-boundary rainRoots snapshot drift, adjacent to this plenty-loss case. |
| 262 | PARTIAL | Missed accounting invariant | SN-001 covers plenty/roots snapshot mismatch on withdrawal during rain. |
| 267 | MISS | Missed oracle/precision/decimal issue | Hardcoded heartbeat-vs-chain mismatch not analyzed. |
| 272 | PARTIAL | Missed lifecycle edge case | TI-005 found Fertilizer 1155 mint can brick for contract receivers (same barn/1155 surface). |
| 279 | MISS | Agent found the issue but failed to escalate it | access_control AC-004 actively CLEARED the arbitrary-send sinks as non-exploitable — opposite conclu |
| 307 | MISS | Architecture mapping failure | protocol_context CLEARED sunrise as 'one per call by design' — opposite conclusion. |
| 309 | MISS | Missing domain knowledge | ABI-decoding divergence between pipe/farm call paths never inspected. |
| 323 | PARTIAL | Missed accounting invariant | Pipeline found roots never credited in reseed; this is the migration-facet variant. |
| 324 | PARTIAL | Missed state transition | BSA-003 analyzed addMigratedDepositsToAccount accounting gaps but not the missing pre-mow. |
| 330 | PARTIAL | Missed state transition | US-001 caught the roots/totals subset of unset vars; not the full set (e.g. mow/germinate fields). |
| 332 | MISS | Missed accounting invariant | protocol_context CLEARED Invariable/fundsSafu as sound during the migration window — opposite conclu |
| 336 | MISS | Missed accounting invariant | Plenty/SOP balances omitted from migration not detected (BSA-003 covered internal balances, not plen |
| 348 | MISS | Missed attacker-controlled input | Event-actor correctness in ERC1155 batch transfer not inspected. |
| 350 | MISS | Missed oracle/precision/decimal issue | Oracle agents focused on Chainlink/wstETH paths; the Uniswap-oracle USD path was not analyzed. |
| 364 | MISS | Missed attacker-controlled input | Stem-manipulation in transferDeposit not detected. |
| 375 | PARTIAL | Missed accounting invariant | FL-001 analyzed the convert stalk-penalty/spot-reserve path; did not isolate the BDV-decrease stalk- |
| 377 | MISS | Missed accounting invariant | protocol_context CLEARED Invariable entitlement accounting as correct — opposite conclusion. |
| 384 | PARTIAL | Missed accounting invariant | SN-001 covers the rain/flood roots-snapshot mismatch underlying this loss. |
| 396 | MISS | Missed oracle/precision/decimal issue | LibEvaluate.evalPrice price computation not inspected. |
| 412 | PARTIAL | Missed accounting invariant | BSA-003 found global-total overwrite zeroing; balance-loss consequence partially covered. |
| 419 | PARTIAL |  | STRICT downgrade from HIT: same root-cause constant (hardcoded mainnet C.PIPELINE) but the pipeline  |
| 423 | PARTIAL | Missed accounting invariant | SN-001 covers the plenty/roots snapshot mismatch underlying pre-flood withdrawal loss. |
| 433 | MISS | Missing domain knowledge | Gauge fallback-selector logic not inspected. |
| 444 | PARTIAL | Missed state transition | US-001 caught the 'reseed leaves critical state unset' class but named stalk/roots, not recapitalize |
| 447 | PARTIAL | Missed state transition | AR-003 referenced unripe accounting; US-001 the unset-state class — but unripeSettings specifically  |
| 451 | MISS | Missed lifecycle edge case | Active pod-order migration omission not detected. |
| 454 | PARTIAL | Missed attacker-controlled input | EA-003 noted rainRoots/divisor divergence; SN-001 the live-vs-snapshot roots; not framed as convert- |
| 461 | MISS | Weak invariant extraction | protocol_context CLEARED quickSort as sound — opposite conclusion. |
| 469 | MISS | Missed cross-chain or migration edge case | LibDibbler mainnet block-time constants vs L2 not analyzed. |
| 476 | MISS | Missed oracle/precision/decimal issue | Heartbeat-window dead-zone not analyzed. |
| 478 | PARTIAL | Missed oracle/precision/decimal issue | OR-002 found the WSTETH branch ignores lookback; OR-001 the inverted Chainlink conditional — same co |
| 491 | MISS | Missed attacker-controlled input | Zero-amount transferDeposit DoS not detected. |
| 522 | MISS | Missing domain knowledge | Lack of on-chain permit/nonce cancellation not detected. |

## False positives / pipeline-only noise (causes → validation fix)

See `rejected_candidates.md` for the full list. Cause taxonomy:
- **Class A — attacker-mindset hypotheses (AM-001..021, 22 items):** surface hints leaked into the findings corpus. *Why plausible:* scored 3–5 entry points. *Why invalid:* no traced exploit path. *Gate that should catch:* schema/`validate_agent_output` should reject `attacker_mindset` Speculative entries from the corpus. *Source:* agent reasoning (Step 0.25).
- **Class B — supply-chain (SC-001..006, 6 items):** real but OUT OF CONTEST SCOPE (build/CI). *Gate:* route to `build_security_annex.md`, exclude from findings/precision. *Source:* supply_chain_check.
- **Class C — non-exploitable (RE-001/2/3, AC-003):** real code smells, no reachable exploit. *Gate:* exploitability gate on emit (reentrancy ≤ Low without an in-scope hooked token). *Source:* agent reasoning.
- **Class D — informational (AR-003, AC-004):** unreachable pattern / a clearing mislabeled as a finding. *Gate:* confidence floor; clearings belong in `resolved_flags`. *Source:* agent reasoning.
- **Class E — unmatched but source-real (SG-001, EA-002):** likely genuine (SG-001 is a real High that clusters near #505). *Fix:* route to human review, do not suppress. (Not true FPs.)
