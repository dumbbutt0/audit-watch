# Failure Analysis — Beanstalk Finale (eval2, API-free)

MISS=38 · PARTIAL=19 · ADJACENT=9 · pipeline-only FP=8.

## Failure-taxonomy histogram (MISS+PARTIAL)

| Taxonomy | Count |
|---|---|
| wrong contract inspected | 12 |
| missed reward accounting edge | 7 |
| missed accounting invariant | 7 |
| missed state transition | 6 |
| missing domain knowledge | 4 |
| missed attacker input | 4 |
| weak invariant extraction | 3 |
| missed oracle/precision | 3 |
| severity reasoning failure | 2 |
| missed lifecycle edge | 2 |
| architecture mapping failure | 2 |
| missed oracle/heartbeat | 2 |
| missed cross-chain/migration edge | 2 |
| found-but-not-escalated | 1 |

## MISS / PARTIAL detail

| sub | sev | class | taxonomy | what was missed | matched |
|---|---|---|---|---|---|
| #30 | High | MISS | wrong contract inspected | SeasonGettersFacet.totalDeltaB well-summation | — |
| #99 | Medium | MISS | wrong contract inspected | TractorFacet counter getter | — |
| #133 | Medium | MISS | wrong contract inspected | LibWeth hardcoded mainnet WETH | — |
| #135 | High | MISS | wrong contract inspected | hardcoded mainnet registry/aggregators/pools | — |
| #139 | Medium | MISS | weak invariant extraction | ReseedField temperature config type mismatch | — |
| #142 | High | MISS | architecture mapping failure | L1/L2 BRIDGE address mismatch | — |
| #184 | Medium | MISS | wrong contract inspected | LibWell 18-decimal hardcoded assumption | — |
| #200 | Medium | MISS | wrong contract inspected | beginBarnRaiseMigration oracle check | — |
| #229 | Medium | MISS | weak invariant extraction | missing scaling factor in reward | — |
| #241 | Medium | MISS | missed accounting invariant | transferStalk rounding formula | — |
| #242 | Medium | MISS | missed reward accounting edge | pre-migration unmowed forfeiture | — |
| #248 | Medium | MISS | missed state transition | missing depositId list registration | — |
| #259 | Medium | MISS | missing domain knowledge | permit token incompatibility | — |
| #267 | Medium | MISS | missed oracle/heartbeat | hardcoded heartbeat vs L2 block cadence | — |
| #272 | Medium | MISS | wrong contract inspected | Fertilizer 1155 migration loss | — |
| #273 | Medium | MISS | wrong contract inspected | _safeMint onERC1155Received acceptance DoS | — |
| #279 | High | MISS | found-but-not-escalated | Tractor refund -> arbitrary call as publisher | — |
| #307 | Medium | MISS | architecture mapping failure | multiple sunrise when enough time passed | — |
| #309 | Medium | MISS | missing domain knowledge | ABI decode divergence pipe vs farm | — |
| #332 | Low | MISS | missed accounting invariant | fundsSafu ineffective during migration window | — |
| #336 | Low | MISS | missed reward accounting edge | plenty/SOP balances omitted from migration | — |
| #348 | Low | MISS | missed attacker input | event-actor correctness in 1155 batch | — |
| #350 | Low | MISS | missed oracle/precision | Uniswap-oracle USD price path | — |
| #364 | Low | MISS | missed attacker input | stem manipulation in transferDeposit | — |
| #375 | Low | MISS | missed accounting invariant | grown-stalk not decreased on BDV drop | — |
| #377 | Low | MISS | missed accounting invariant | Invariable Bean entitlement flaw | — |
| #379 | Low | MISS | wrong contract inspected | plot-spam transfer DoS | — |
| #396 | Low | MISS | wrong contract inspected | LibEvaluate.evalPrice | — |
| #419 | Low | MISS | wrong contract inspected | DepotFacet hardcoded PIPELINE | — |
| #433 | Low | MISS | missing domain knowledge | gauge fallback selector | — |
| #451 | Low | MISS | missed lifecycle edge | active pod-order migration omission | — |
| #452 | High | MISS | wrong contract inspected | ReseedWhitelist ordering -> systematic stalk undercount | — |
| #461 | High | MISS | weak invariant extraction | broken quickSort in flood | — |
| #462 | High | MISS | missed cross-chain/migration edge | no rollback on L2 migration failure | — |
| #469 | Low | MISS | missed cross-chain/migration edge | LibDibbler mainnet block-time constants | — |
| #476 | Low | MISS | missed oracle/heartbeat | heartbeat-window dead-zone | — |
| #491 | Low | MISS | missed attacker input | amount==0 transferDeposit DoS | — |
| #522 | Low | MISS | missing domain knowledge | permit cancellation before deadline | — |
| #90 | High | PARTIAL | severity reasoning failure | the exact BDV-penalty miscalculation framing | FL-001/EA-001 |
| #128 | High | PARTIAL | missed lifecycle edge | the 'stuck on L1 cannot migrate' lifecycle framing | CC-002/BSA-002 |
| #140 | Medium | PARTIAL | severity reasoning failure | the nested mint-loop OOG-on-some-L2s root cause | DS-003 |
| #186 | Medium | PARTIAL | missed oracle/precision | LibWell liquidity-helper decimal bug; LibWell never inspected | BSA-001 |
| #204 | Medium | PARTIAL | missed reward accounting edge | the specific season-boundary user-loss scenario | EA-001 |
| #227 | Medium | PARTIAL | missed state transition | the specific grown-stalk computation error | LG-002/PC-001 |
| #239 | Medium | PARTIAL | missed accounting invariant | this exact stalk computation in L2ContractMigrationFacet | LG-002/PC-001 |
| #260 | Medium | PARTIAL | missed reward accounting edge | the specific season-boundary user-loss scenario | EA-001 |
| #262 | Medium | PARTIAL | missed reward accounting edge | the specific season-boundary user-loss scenario | EA-001 |
| #323 | Medium | PARTIAL | missed accounting invariant | the newly-accrued-stalk migration-facet specific path | PC-001/US-001 |
| #324 | Medium | PARTIAL | missed state transition | the missing pre-mow before crediting | BSA-003/PC-001 |
| #330 | Medium | PARTIAL | missed state transition | full set of unset user vars (mow/germinate) | US-001/PC-001 |
| #384 | Low | PARTIAL | missed reward accounting edge | the specific season-boundary user-loss scenario | EA-001 |
| #412 | Low | PARTIAL | missed accounting invariant | explicit per-user balance-loss consequence | LG-001/BSA-004 |
| #423 | Low | PARTIAL | missed reward accounting edge | the specific season-boundary user-loss scenario | EA-001 |
| #444 | Low | PARTIAL | missed state transition | fert.recapitalized specifically | US-001/PC-001 |
| #447 | Low | PARTIAL | missed state transition | unripeSettings specifically | US-001/PC-001 |
| #454 | Low | PARTIAL | missed attacker input | convert-time rainRoots theft mechanism | EA-001/FL-001 |
| #478 | Low | PARTIAL | missed oracle/precision | the exact LibUsdOracle conditional the auditors flagged | OR-002/BSA-001 |

## Cross-cutting failure themes

1. **Coverage holes from un-inspected contracts (dominant new-vs-prior regression).** eval2 never opened LibWeth, the L2 Chainlink-registry path, DepotFacet's PIPELINE constant, Fertilizer1155 mint-acceptance, LibWell decimal helpers, LibEvaluate, LibDibbler, SeasonGettersFacet, ReseedWhitelist, or the plot/marketplace machinery. Each is a pure silent miss (`wrong contract inspected`). This is the single biggest driver of the drop from prior baseline — the prior run's `token_integration` C.sol-constant sweep (WETH/PIPELINE/registry) and `dos` plot-spam findings simply did not regenerate.
2. **Class-level over-merge masks specific bugs.** The reseed/migration accounting bugs collapsed into 5 canonical findings (CC-001/LG-001/LG-002/PC-001/CC-002). That cluster HIT the headline bugs but turned ~9 distinct public sub-findings (recapitalized, unripeSettings, depositId push, pre-mow, full unset-var set, plenty balances) into PARTIALs/MISSes because the agents reasoned at the invariant level ("globals not seeded") rather than enumerating every unset field.
3. **Reward-accounting lifecycle still un-modeled.** All 6 Silo/Floods findings are PARTIAL — EA-001/DS-004 sensed flood/SoP fragility but produced no season-boundary user-loss scenarios (mow-between-floods, withdraw-during-rain). No state machine of "what is owed across season boundaries" exists.
4. **Adversarial-invariant blindness persists.** Protocol-Integrity is 0/5 meaningful: quickSort (#461), multiple-sunrise (#307), Invariable entitlement (#377), totalDeltaB (#30), gauge fallback (#433) — all either un-inspected or would require attacker-first re-derivation of a safety net.
5. **Oracle precision/heartbeat tail missed.** Uniswap-oracle USD path (#350), LibWell decimals (#184/#186), heartbeat dead-zone (#267/#476), evalPrice (#396) — the oracle agents went deep on Chainlink-logic + wstETH but not breadth across every USD-price source.

## FP analysis

| eval2 id | why plausible | why it should fail validation | gate that should catch | source class |
|---|---|---|---|---|
| AR-001 | Real checked LibRedundantMath256.sub with no floor; underflow would revert sunrise. | Precondition stalk/totalBdv<1e4 reachability never proven; chained to a migration-desync assumption. | Step 3.4 ICE Exploitability gate + Step 3.7 reachability gate | speculative-reachability |
| BSA-005 | NatSpec MUST-ascending not enforced in mintFertilizers. | Input is trusted upgrade calldata, not attacker-controlled; bounded griefing. | Step 3.4 ICE Exploitability (privileged input) | privileged-input |
| DT-011 | No farmers/balances length check -> OOB revert. | Privileged init-only path; totalInternalBalance guard catches mismatch; DoS of a one-shot step. | Step 3.4 ICE Exploitability (privileged init) | privileged-input |
| DS-004 | div-by-(i-1) on last iteration is a real arithmetic edge. | Requires multi-well mixed-sign deltaB during SoP; scope likely never multi-well; not on public list. | Step 3.7 reachability / config-precondition gate | speculative-reachability |
| EA-002 | floodPodline ripens 0.1%/season FIFO; controllable flood schedule. | Bounded economic edge, front-of-line only; auditors did not reward. | Step 3.4 ICE Impact gate (Low economic) | low-impact-economic |
| RE-001 | Arbitrary-call facets genuinely lack nonReentrant. | No concrete reentrant exploit traced; inner facets re-check guards; defense-in-depth only. | Step 3.4 ICE Confidence (no traced consumer) | untraced-defense-in-depth |
| SG-004 | Reseed init facets are external with no modifier. | diamondCut-only at deploy in standard EIP-2535; not independently callable post-cut. | Step 1.5 defense / architecture gate (deploy-time only) | lifecycle-misread |
| OR-005 | No answeredInRound / no min-max bounds is a real Chainlink best-practice gap. | Chainlink is trusted source; 0-on-failure already handles outages; low impact. | Step 3.4 ICE Impact gate | best-practice-low |

Note: zero hallucinations — every pipeline-only finding maps to real code. The FP cost is **unrewarded-but-real** noise (precision/DoS/guard-asymmetry), not fabricated bugs. The dominant FP source class is **speculative-reachability** (AR-001, DS-004) and **privileged/lifecycle-misread** (BSA-005, DT-011, SG-004).