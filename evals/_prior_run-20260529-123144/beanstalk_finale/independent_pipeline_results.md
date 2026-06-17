# Phase 2 — Independent Pipeline Results (Beanstalk Finale)

## Provenance & integrity (read first)
These independent results are the **pre-existing blind run** of Audit-Watch on this target:
`audits/beanstalk-2024-05/` — workspace `created_at` `2026-05-28T21:49:53Z`, finding artifacts
timestamped through `2026-05-29 07:57`. That run completed **before** the answer key was opened in
this project. No pipeline stage was re-run for this eval, and **no API calls were made** (the
operator is now answer-key-aware; re-running would not be blind and the eval requires zero spend).
Raw artifacts are copied verbatim into `evals/beanstalk_finale/artifacts/`.

**Scope of the run (honest caveat):** the LLM-backed validation half (cross-agent, compound
synthesis, multi-pass confirm, triage, PoC) did **not** execute that session — no API key. So these
are the **raw detection-layer** findings. A "HIT" downstream means *a detector found the bug*, not
*the pipeline would have submitted it*. Triage buckets and `pocs/` are empty; PoC status = none for
every finding.

## What ran vs. did not
- **Ran (deterministic / in-session):** Slither static analysis → `static.json`; attacker-mindset
  surface map → `attack_surface.json`; coverage gaps; context pack; **16 specialist agents**
  (Step 2); deterministic merge (`report_generator.py`) → `merged_findings.json`.
- **Did NOT run (API-dependent):** cross_agent_connector (2.5), synthesize_compound (3),
  multi_pass_confirm (3.5), triage (4), PoC (6).

## Coverage of the required domains
All seven requested domains were covered by at least one specialist:
- **L2 migration / reseed init:** US-001, BSA-001/003, LG-001, CC-002 (ReseedSilo, ReseedField, ReseedBarn, L2ContractMigrationFacet, BeanL1RecieverFacet).
- **Oracle (price/decimals/heartbeat/TWAP/chain):** AR-001, OR-003, TI-004, AR-002 (LibChainlinkOracle, LibUsdOracle, LibWell).
- **Silo/Stalk/Roots/BDV/mow/rain/flood/SoP:** SN-001, EA-003, EA-002 (LibFlood), US/BSA reseed stalk/roots.
- **Field/Plot/allowance/plot-index:** DS-001 (LibDibbler plotIndexes), SG-001 (MarketplaceFacet pod allowance).
- **Tractor/Pipeline/Farm/arbitrary-call/ABI:** TI-003 (PIPELINE), AC-003 (UnwrapAndSendETH), AM-019 (Pipeline).
- **Protocol peg integrity / invariants:** PC-001 (totalDeltaB), FL-001 (deltaB/peg bound).
- **EIP-712/permit/auth/events/replay:** AC-001 (replay), AC-002/TI-001 (domain separator/chainId).

## Independent findings — 44 total (raw detection layer)
`by_severity`: Critical 2 · High 12 · Medium 6 · Low 22 · Informational 2. Full structured set in
`independent_findings.json`. Contract-vulnerability findings (excluding the 22 attacker-mindset
hypotheses and supply-chain noise — see `rejected_candidates.md`):

| ID | Sev | Contract / function | One-line |
|---|---|---|---|
| US-001 | Critical | ReseedSilo.reseedSiloDeposit | Reseed leaves total Stalk/Roots + per-account Roots unset |
| AC-001 | High | L2ContractMigrationFacet.redeemDepositsAndInternalBalances | Signed redemption replayable (no nonce) |
| AR-001 | High | LibChainlinkOracle.getTokenPrice | Inverted lookback ternary → spot instead of TWAP |
| BSA-001 | High | ReseedSilo.reseedSiloDeposit | Reads stalkIssuedPerBdv before ReseedWhitelist sets it → ~0 stalk |
| DS-001 | High | LibDibbler.findPlotIndexForAccount | Unbounded plotIndexes growth bricks victim harvest/transfer |
| EA-001 | High | LibConvert.calculateConvertCapacity | Shared per-block convert-cap sandwich burns victim stalk |
| FL-001 | High | LibDeltaB.currentDeltaB | Convert peg bound + penalty use spot getReserves() (flash-manipulable) |
| LG-001 | High | ReseedField.init | Loop increments i not j → field migration bricked |
| SG-001 | High | MarketplaceFacet.transferPlots | Args transposed → pod allowance never consumed |
| SN-001 | High | LibFlood.balanceOfPlenty | Plenty paid on live roots vs fixed rain.roots divisor |
| TI-001 | High | C.getChainId | EIP-712 domain hardcodes chainId=1 |
| TI-002 | High | LibWeth.wrap/unwrap | Hardcoded mainnet WETH bricks wrap/unwrap on L2 |
| TI-003 | High | LibPipelineConvert.executePipelineConvert | Hardcoded mainnet PIPELINE misroutes convert funds on L2 |
| AR-002 | Medium | LibWell.getWellTwaUsdLiquidityFromReserves | Hardcoded 18-decimal non-Bean token assumption |
| BSA-003 | Medium | L2ContractMigrationFacet.addMigratedDepositsToAccount | Ignores verified internalBalances; zeroes global totals |
| CC-002 | Medium | BeanL1RecieverFacet.recieveL1Beans | EXTERNAL_L1_BEANS=0, no setter → always reverts |
| EA-002 | Medium | LibFlood.sopWell | SOP swap minAmountOut=0, max deadline (sandwichable) |
| TI-004 | Medium | LibUsdOracle.getUsdPrice | Hardcoded mainnet oracle/token addrs break L2 feeds |
| TI-005 | Medium | Fertilizer1155._safeMint | Acceptance check can brick mintFertilizer for contracts |
| AC-002 | Low | LibTractor._domainSeparatorV4 | Uses BLUEPRINT_TYPE_HASH not EIP712Domain typehash |
| DS-002 | Low | ClaimFacet.claimAllPlenty | Loops whitelisted Wells with external send (DoS) |
| DS-003 | Low | ReseedBarn.mintFertilizers | Nested unbounded loops OOG risk on L2 |
| EA-003 | Low | LibFlood.handleRainAndSops | Per-account rainRoots may diverge from global rain.roots |
| OR-003 | Low | LibChainlinkOracle.getTwap | getTwap aborts to 0 if a historical round is unavailable |
| PC-001 | Low | SeasonGettersFacet.totalDeltaB | Sums only BEAN_ETH_WELL, not all minting wells |
| RE-003 | Low | Fertilizer._update | Diamond↔Fertilizer callback unguarded by shared nonReentrant |
| AC-003 | Low | UnwrapAndSendETH.unwrapAndSendETH | Sweeps full WETH to caller-supplied address |

Duplicate clustering: the deterministic merge collapsed 70 raw → 44; **one known wrongful collapse**
(OR-001 Chainlink inversion vs OR-002 LibUsdOracle wstETH branch — distinct bugs, same function
name, different files). Otherwise it linked rather than dropped.
