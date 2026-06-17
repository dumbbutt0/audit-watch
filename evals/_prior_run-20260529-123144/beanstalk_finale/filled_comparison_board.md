# Filled Comparison Board — Beanstalk Finale (STRICT scoring)

Independent run = blind artifacts in `audits/beanstalk-2024-05/` (pre-answer-key). PoC existed = No for all (no PoCs generated that run). Scoring rule = STRICT.

**HIT 23 · PARTIAL 22 · ADJACENT 9 · MISS 27** of 81 · meaningful (HIT+PARTIAL) 45 (55%) · any-touch 54 (66%)

| Sub | Sev | Category | Class | Match | Pipeline ID | Agent | Pipe Sev | Sev✓ | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 30 | L | Protocol Integrity | HIT | EXACT | PC-001 | protocol_context | Low | yes | PC-001 found totalDeltaB() sums only BEAN_ETH_WELL not all minting wells — exact root caus |
| 37 | M | Auth/Permit | HIT | EXACT | AC-002 | access_control | Low | no (Low→Medium) | AC-002 flagged _domainSeparatorV4 using BLUEPRINT_TYPE_HASH instead of EIP712Domain typeha |
| 68 | L | Oracle | HIT | EXACT | OR-001/AR-001 | oracle | (merged-pre) | n/a | Same inverted-ternary root cause in LibChainlinkOracle.getTokenPrice; OR-001 traced the co |
| 90 | H | Silo/Convert | PARTIAL | PARTIAL | FL-001/EA-001 | flash_loan | High | yes | Pipeline found convert-penalty manipulation (sandwich/spot reserves) but framed it as MEV  |
| 99 | L | Tractor | MISS | MISSED | — | — | (merged-pre) | n/a | Tractor counter getter never inspected. |
| 128 | M | L2 Migration | PARTIAL | PARTIAL | CC-002 | cross_chain | Medium | yes | CC-002 found receiveL1Beans always reverts (same broken external-Bean migration), but fram |
| 131 | L | L2 Migration | HIT | EXACT | CC-002 | cross_chain | Medium | no (Medium→Low) | CC-002 nailed EXTERNAL_L1_BEANS=0 constant with no setter -> require always reverts. |
| 133 | L | L2 Migration | HIT | EXACT | TI-002 | token_integration | High | no (High→Low) | TI-002 found hardcoded mainnet WETH bricking wrap/unwrap on L2. |
| 135 | M | Oracle/L2 | HIT | EXACT | TI-004 | token_integration | Medium | yes | TI-004 found hardcoded mainnet Chainlink registry/aggregators/pools and token-identity bra |
| 139 | L | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | Pipeline found the ReseedField loop bug but not the temperature/type-mismatch field-config |
| 140 | L | L2 Migration | PARTIAL | PARTIAL | DS-003 | dos | Low | yes | DS-003 found the same nested mint loop OOG risk but downgraded to Low/admin-robustness; co |
| 142 | L | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | cross_chain agent explicitly inspected and CLEARED the L1/L2 BRIDGE pair as consistent for |
| 184 | L | Oracle | HIT | EXACT | AR-002 | arithmetic | Medium | no (Medium→Low) | AR-002 found the hardcoded 1e18/1e6 18-decimal assumption in LibWell helpers. |
| 186 | L | Oracle | PARTIAL | PARTIAL | AR-002 | arithmetic | Medium | no (Medium→Low) | Same LibWell decimal/precision family; AR-002 named the liquidity helper but emphasized th |
| 200 | L | Oracle/Barn | MISS | MISSED | — | — | (merged-pre) | n/a | beginBarnRaiseMigration oracle-support validation never inspected. |
| 204 | L | Silo/Floods | PARTIAL | PARTIAL | SN-001/SN-002 | snapshot | High | no (High→Low) | snapshot agent found flood/rain root snapshot timing issues but not specifically the doubl |
| 224 | H | L2 Migration | HIT | EXACT | BSA-003/US-001 | behavioral_state_analysis | Medium | no (Medium→High) | BSA-003 found migration zeroes/never-increments global silo totals; US-001 the same class  |
| 227 | H | L2 Migration | PARTIAL | PARTIAL | BSA-001 | behavioral_state_analysis | High | yes | BSA-001 found stalk computed ~0 due to whitelist-ordering; overlaps grown-stalk miscalc bu |
| 228 | M | Auth/Permit | HIT | EXACT | AC-002/TI-001 | access_control | Low | no (Low→Medium) | AC-002 (typehash) + TI-001 (hardcoded chainId) both hit the domain separator defect. |
| 229 | L | Silo/Rewards | MISS | MISSED | — | — | (merged-pre) | n/a | Missing scaling-constant in reward math never identified. |
| 239 | H | L2 Migration | PARTIAL | PARTIAL | BSA-001 | behavioral_state_analysis | High | yes | Pipeline found stalk-amount errors in migration/reseed but not this exact computation. |
| 241 | M | Silo/Stalk | MISS | MISSED | — | — | (merged-pre) | n/a | transferStalk rounding formula never analyzed. |
| 242 | M | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | Pre-migration unmowed-reward forfeiture not detected. |
| 248 | M | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | Missing depositIdList registration not detected. |
| 251 | H | L2 Migration | HIT | EXACT | US-001/LG-003 | upgrade_storage | Critical | no (Critical→High) | US-001/LG-003 found global silo.stalk/roots never seeded in reseed. |
| 259 | L | Auth/Permit | MISS | MISSED | — | — | (merged-pre) | n/a | Non-standard-token permit incompatibility not detected. |
| 260 | M | Silo/Floods | PARTIAL | PARTIAL | SN-002 | snapshot | (merged-pre) | n/a | SN-002 found germination-boundary rainRoots snapshot drift, adjacent to this plenty-loss c |
| 261 | L | Field/Plots | ADJACENT | ADJACENT | DS-001 | dos | High | n/a | DS-001 found plot-array griefing (spam) in the same plotIndexes machinery, but not the del |
| 262 | M | Silo/Floods | PARTIAL | PARTIAL | SN-001 | snapshot | High | no (High→Medium) | SN-001 covers plenty/roots snapshot mismatch on withdrawal during rain. |
| 267 | L | Oracle/L2 | MISS | MISSED | — | — | (merged-pre) | n/a | Hardcoded heartbeat-vs-chain mismatch not analyzed. |
| 272 | M | L2 Migration/Barn | PARTIAL | PARTIAL | TI-005 | token_integration | Medium | yes | TI-005 found Fertilizer 1155 mint can brick for contract receivers (same barn/1155 surface |
| 273 | L | Barn/ERC1155 | HIT | EXACT | TI-005 | token_integration | Medium | no (Medium→Low) | TI-005 found _safeMint acceptance check reverts mint for contract buyers without onERC1155 |
| 279 | H | Tractor | MISS | MISSED | — | — | (merged-pre) | n/a | access_control AC-004 actively CLEARED the arbitrary-send sinks as non-exploitable — oppos |
| 303 | H | Oracle | HIT | EXACT | OR-001/AR-001 | oracle | (merged-pre) | n/a | OR-001/AR-001 found the inverted ternary returning spot when TWAP requested — exact match. |
| 307 | M | Protocol Integrity | MISS | MISSED | — | — | (merged-pre) | n/a | protocol_context CLEARED sunrise as 'one per call by design' — opposite conclusion. |
| 309 | L | Pipeline/Tractor | MISS | MISSED | — | — | (merged-pre) | n/a | ABI-decoding divergence between pipe/farm call paths never inspected. |
| 319 | L | Silo/Whitelist | ADJACENT | ADJACENT | DS-002 | dos | Low | n/a | DS-002 found claimAllPlenty reverts if a whitelisted token send fails — related plenty-cla |
| 320 | L | L2 Migration | HIT | EXACT | CC-003 | cross_chain | (merged-pre) | n/a | CC-003 flagged MERKLE_ROOT placeholder ('todo: update with correct root'). |
| 323 | M | L2 Migration | PARTIAL | PARTIAL | US-001/LG-003 | upgrade_storage | Critical | no (Critical→Medium) | Pipeline found roots never credited in reseed; this is the migration-facet variant. |
| 324 | M | L2 Migration | PARTIAL | PARTIAL | BSA-003 | behavioral_state_analysis | Medium | yes | BSA-003 analyzed addMigratedDepositsToAccount accounting gaps but not the missing pre-mow. |
| 325 | H | L2 Migration | HIT | EXACT | BSA-003 | behavioral_state_analysis | Medium | no (Medium→High) | BSA-003 found internalBalances are proven in the leaf but never credited. |
| 327 | H | L2 Migration | HIT | EXACT | LG-003/US-001 | logic | (merged-pre) | n/a | LG-003/US-001 found per-account roots never set in reseed. |
| 328 | H | L2 Migration | HIT | EXACT | LG-002/US-002 | logic | (merged-pre) | n/a | LG-002/US-002 found '=' instead of '+=' overwriting prior tokens' stalk. |
| 330 | M | L2 Migration | PARTIAL | PARTIAL | US-001 | upgrade_storage | Critical | no (Critical→Medium) | US-001 caught the roots/totals subset of unset vars; not the full set (e.g. mow/germinate  |
| 332 | L | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | protocol_context CLEARED Invariable/fundsSafu as sound during the migration window — oppos |
| 336 | L | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | Plenty/SOP balances omitted from migration not detected (BSA-003 covered internal balances |
| 348 | L | Auth/Events | MISS | MISSED | — | — | (merged-pre) | n/a | Event-actor correctness in ERC1155 batch transfer not inspected. |
| 350 | H | Oracle | MISS | MISSED | — | — | (merged-pre) | n/a | Oracle agents focused on Chainlink/wstETH paths; the Uniswap-oracle USD path was not analy |
| 357 | M | L2 Migration | ADJACENT | ADJACENT | LG-001/US-003 | logic | High | n/a | Pipeline found a different ReseedField.init bug (loop counter); the storage-layout/config  |
| 364 | M | Silo/Stalk | MISS | MISSED | — | — | (merged-pre) | n/a | Stem-manipulation in transferDeposit not detected. |
| 375 | H | Silo/Convert | PARTIAL | PARTIAL | FL-001 | flash_loan | High | yes | FL-001 analyzed the convert stalk-penalty/spot-reserve path; did not isolate the BDV-decre |
| 377 | M | Protocol Integrity | MISS | MISSED | — | — | (merged-pre) | n/a | protocol_context CLEARED Invariable entitlement accounting as correct — opposite conclusio |
| 378 | L | Oracle | ADJACENT | ADJACENT | TI-004/OR-003 | token_integration | Medium | n/a | TI-004/OR-003 noted oracle path fragility/revert-to-0; not the specific non-core-token rev |
| 379 | M | Field/Plots | HIT | EXACT | DS-001 | dos | High | no (High→Medium) | DS-001 found unbounded plotIndexes growth via consent-less transferPlot bricking harvest/t |
| 384 | M | Silo/Floods | PARTIAL | PARTIAL | SN-001 | snapshot | High | no (High→Medium) | SN-001 covers the rain/flood roots-snapshot mismatch underlying this loss. |
| 395 | H | Oracle | ADJACENT | ADJACENT | OR-003 | oracle | Low | n/a | OR-003 found getTwap aborts to 0 (a DoS-to-zero), adjacent to the peg-compromise claim. |
| 396 | H | Protocol Integrity/Oracle | MISS | MISSED | — | — | (merged-pre) | n/a | LibEvaluate.evalPrice price computation not inspected. |
| 397 | H | L2 Migration | HIT | EXACT | BSA-002/AC-001/CC-001 | behavioral_state_analysis | (merged-pre) | n/a | Three agents independently found no-nonce/no-consumed-flag replay re-crediting stalk/roots |
| 398 | M | L2 Migration | HIT | EXACT | LG-001/US-003 | logic | High | no (High→Medium) | LG-001/US-003 found inner loop increments i instead of j -> OOB revert. |
| 401 | M | L2 Migration | ADJACENT | ADJACENT | BSA-001 | behavioral_state_analysis | High | n/a | BSA-001 analyzed ReseedWhitelist ordering; the array-OOB revert in init is a distinct bug  |
| 411 | H | L2 Migration | HIT | EXACT | BSA-003 | behavioral_state_analysis | Medium | no (Medium→High) | BSA-003 found totalDeposited/Bdv left 0 and overwriting reseed totals. |
| 412 | H | L2 Migration | PARTIAL | PARTIAL | BSA-003 | behavioral_state_analysis | Medium | no (Medium→High) | BSA-003 found global-total overwrite zeroing; balance-loss consequence partially covered. |
| 419 | L | Tractor/Pipeline | PARTIAL | PARTIAL | TI-003 | token_integration | High | no (High→Low) | STRICT downgrade from HIT: same root-cause constant (hardcoded mainnet C.PIPELINE) but the |
| 423 | M | Silo/Floods | PARTIAL | PARTIAL | SN-001 | snapshot | High | no (High→Medium) | SN-001 covers the plenty/roots snapshot mismatch underlying pre-flood withdrawal loss. |
| 433 | M | Protocol Integrity | MISS | MISSED | — | — | (merged-pre) | n/a | Gauge fallback-selector logic not inspected. |
| 444 | H | L2 Migration/Barn | PARTIAL | PARTIAL | US-001 | upgrade_storage | Critical | no (Critical→High) | US-001 caught the 'reseed leaves critical state unset' class but named stalk/roots, not re |
| 447 | H | L2 Migration | PARTIAL | PARTIAL | US-001/AR-003 | upgrade_storage | Critical | no (Critical→High) | AR-003 referenced unripe accounting; US-001 the unset-state class — but unripeSettings spe |
| 451 | M | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | Active pod-order migration omission not detected. |
| 452 | H | L2 Migration | HIT | EXACT | BSA-001 | behavioral_state_analysis | High | yes | BSA-001 found stalkIssuedPerBdv read as 0 (ordering) -> systematic stalk undercount, exact |
| 454 | M | Silo/Floods | PARTIAL | PARTIAL | EA-003/SN-001 | economic_attack | Low | no (Low→Medium) | EA-003 noted rainRoots/divisor divergence; SN-001 the live-vs-snapshot roots; not framed a |
| 461 | M | Protocol Integrity | MISS | MISSED | — | — | (merged-pre) | n/a | protocol_context CLEARED quickSort as sound — opposite conclusion. |
| 462 | H | L2 Migration | ADJACENT | ADJACENT | CC-002 | cross_chain | Medium | n/a | CC-002 found the burn-then-revert receiver gap; the no-rollback-on-L2-failure framing is a |
| 469 | L | L2 Migration | MISS | MISSED | — | — | (merged-pre) | n/a | LibDibbler mainnet block-time constants vs L2 not analyzed. |
| 471 | M | L2 Migration | HIT | EXACT | CC-001/CC-003 | cross_chain | (merged-pre) | n/a | CC-001 found no-nonce replay; CC-003 noted the hardcoded chainId in the migration domain. |
| 476 | M | Oracle | MISS | MISSED | — | — | (merged-pre) | n/a | Heartbeat-window dead-zone not analyzed. |
| 478 | M | Oracle | PARTIAL | PARTIAL | OR-002/OR-001 | oracle | (merged-pre) | n/a | OR-002 found the WSTETH branch ignores lookback; OR-001 the inverted Chainlink conditional |
| 485 | L | Field/Plots | ADJACENT | ADJACENT | DS-001 | dos | High | n/a | DS-001 worked the plotIndexes array but via griefing transfer, not the sow-duplication pat |
| 491 | M | Silo/Stalk | MISS | MISSED | — | — | (merged-pre) | n/a | Zero-amount transferDeposit DoS not detected. |
| 505 | L | Field/Plots | ADJACENT | ADJACENT | SG-001 | semantic_guard | High | n/a | SG-001 found a DIFFERENT (and arguably worse) bug in the same pod-allowance mechanism: tra |
| 519 | M | Silo/Convert | HIT | EXACT | EA-001 | economic_attack | High | no (High→Medium) | EA-001 found the per-block shared convert-capacity accumulator sandwich forcing penalties  |
| 522 | L | Auth/Permit | MISS | MISSED | — | — | (merged-pre) | n/a | Lack of on-chain permit/nonce cancellation not detected. |
