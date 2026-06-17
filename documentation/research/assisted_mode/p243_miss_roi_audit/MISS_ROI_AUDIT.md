# P243 — Miss-Family ROI Audit (read-only attribution; no implementation)

Attributes every awarded finding the FROZEN system missed (primary universe = P241's 5 benchmark contests; P235/P240
folded into the counterfactual) to the ONE improvement most likely to recover it, weights by severity (High=3,
Med=1), and ranks future investment by **measured weighted-recall contribution**. Uses the recorded per-contest
hit/miss labels + read-bounds from P235/P240/P241/P236/P242 — no re-audit, no new candidates. dittoeth's 16 are
theme-level (report >10MB) and classified as a group (unread facets) with that caveat.

## Part A — Miss inventory (P241; 20 H + 37 M = 57 awarded)
Recovered in P241 (excluded from misses): kelp H-03 (KELP-03), kelp M-02 (KELP-02), nextgen H-03 (NEXT-01),
nextgen H-05 (NEXT-03), predy M-06 (hostile-token LENS) = 4 clean + 2 partial (kelp H-01/H-02). **Misses ≈ 51.**

| Contest | Misses (id → severity → root cause) | Tier |
|---|---|---|
| kelp | H-01 oracle heartbeat/deviation arbitrage (oracle) [PARTIAL]; H-02 deposit transfers-before-mint inflates price (accounting/ordering); M-01 strategy-migration share issuance (state) | PARTIAL/NEAR |
| nextgen | H-01 mint reentrancy (callback-before-counter); H-02 ==endTime drain (auction timing); H-04 periodic phases; M-01 artist payout double; M-02 randomizer no-hash; M-03 burn-to-mint dup; M-04 descending-price round; M-05 proceeds wrong recipient [PARTIAL]; M-06 artist sig forgery; M-07 winner blocks payment (callback); M-08 airdrop price spike; M-09 periodic skip-final; M-10 1-sec timing trap; M-11 unchecked return [PARTIAL]; M-12 excess funds not refunded | FULL/PARTIAL |
| dittoeth | 7H + 9M — short-record mgmt / linked-list state corruption / redemption-proposal disputes (all in UNREAD facets) | FULL MISS |
| predy | H-01 slot0 spot-price manip; H-02 margin-check bypass; H-03 cross-pair liquidity steal; H-04 liquidation transfer-from-wrong; M-01 liquidity manipulation; M-02 updateIRMParams no applyInterest; M-03 negative-tick rounding; M-04 Chainlink stale; M-05 GammaTradeMarket removePosition DoS; M-07 reallocation excess to Market; M-08 PriceFeed wrong quote-pair price | FULL MISS |
| fenix | H-01 killGauge emission; M-01 mVeNFT vote DoS; M-02 createV3Gauge wrong factory; M-03 skipped-gauge index; M-04 boostedValue permanentTotalSupply; M-05 dettach revert; M-06 revived-gauge index | FULL MISS |

## Part B+C — Recovery counterfactual + weighted impact (per category)
Each miss → the single highest-leverage recovery category; weighted = 3·High + 1·Med.

| Cat | Recovery family | Misses (raw H/M) | Raw | Weighted | Which |
|---|---|---|---|---|---|
| **K** | Diamond/facet coverage | 7H / 9M | 16 | **30** | dittoeth (unread facets) |
| **A** | Full-surface coverage (heterogeneous unread) | 4H / 10M | 14 | **22** | nextgen Minter/Core (H-04,M-01,M-02,M-03,M-04,M-08,M-09,M-12) + predy trade/reallocation libs (H-02,H-03,H-04,M-02,M-03,M-05,M-07) |
| **L** | Reasoning depth (read but missed) | 2H / 5M | 7 | **11** | kelp H-02,M-01; nextgen H-02,M-05,M-07,M-10,M-11 |
| **J** | Oracle freshness/validity | 2H / 3M | 5 | **9** | kelp H-01; predy H-01,M-01,M-04,M-08 |
| **I** | Reward/emission accounting | 1H / 6M | 7 | **9** | fenix all (ve(3,3) gauge/emission/index) |
| **B** | Create-time reentrancy (P242-A) | 1H / 0M | 1 | **3** | nextgen H-01 |
| **F** | Permit/signature binding | 0H / 1M | 1 | **1** | nextgen M-06 (artist sig forgery) |
| **E** | Hostile-token (P238) | (recovered) | — | — | predy M-06 already recovered by the lens |
| **C,D,G,H,M,N** | 4626 / safe-mgmt / slippage / TWAB / proof / other | 0 | 0 | 0 | none remaining in the P241 miss set (kelp M-02 slippage was recovered) |
| **TOTAL misses** | | 17H / 34M | **51** | **85** | (P241 awarded weighted = 97; recovered ≈ 12; missed ≈ 85) |

## Part D — ROI ranking (by weighted recall gain)
| Rank | Category | Weighted gain | Recall gain (raw) | Generalization | Impl. cost |
|---|---|---|---|---|---|
| 1 | **A+K Full-surface / facet coverage** | **52 (61%)** | 30 misses | HIGH (every architecture) | MED (a Step-3.9 coverage system already exists — this is *operating at full coverage*, not new build) |
| 2 | J Oracle freshness/validity | 9 (11%) | 5 | HIGH (every oracle protocol) | LOW–MED (P237/P238-style detector) |
| 3 | I Reward/emission accounting | 9 (11%) | 7 | MED (ve(3,3)/gauge-specific) | MED |
| 4 | L Reasoning depth | 11 (13%) | 7 | HIGH but DIFFUSE (no single buildable fix) | HIGH (per-finding agent depth, not a detector) |
| 5 | B/C create-time / 4626 (P242, built) | 3 / 0 | 1 | HIGH | DONE (low remaining P241 ROI) |
| 6 | F permit/signature binding | 1 | 1 | HIGH | LOW (but tiny weighted gain) |

## Part E — Coverage analysis
Coverage-bound misses (the relevant code was NOT examined): **A (14) + K (16) = 30 misses, 52 weighted = 61% of all
missed weighted recall.** Breakdown: unread facets (dittoeth, 16) · unread contracts/modules (nextgen MinterContract/
NextGenCore/Randomizers ~7; predy trade/perp/reallocation libs ~7) · unread lifecycle (fenix base-light overlaps I).
**Recall if all relevant code had been covered:** the one FULLY-read target (kelp) recovered 3/5 (clean+partial) ≈
60%. Extrapolating ~60–75% in-contract recovery to the 52 coverage-weighted → **+31 to +39 weighted**, lifting P241
weighted recall from ~12% to **~45–53%** from coverage ALONE.

## Part F — Detector saturation
| Bucket | Weighted | Share | Note |
|---|---|---|---|
| **Coverage-Bound (A+K)** | 52 | **61%** | dominant — unread surface/facets |
| **Family-Bound (J+I+B+F)** | 22 | **26%** | oracle (9) + reward/emission (9) + create-time (3, built) + permit (1) |
| **Reasoning-Bound (L)** | 11 | **13%** | read-but-missed; not a buildable family |
| **Proof-Bound (M)** | 0 | 0% | nothing reached the proof stage (recall miss, not proof miss) |
| Other (N) | 0 | 0% | — |
**Detector expansion has LOW remaining ROI:** even capturing ALL family-bound misses with new detectors adds only
~26% weighted, and that's split across heterogeneous families (oracle + reward/emission). Coverage alone (61%) is
more than 2× all detectors combined.

## Counterfactual recall (P241, weighted denom 97)
| Scenario | Weighted recall |
|---|---|
| Current (frozen system, this benchmark's bounded reads) | ~12% |
| + full-surface/facet coverage | **~45–53%** |
| + P237 safe-management | +0 (no Safe-guard targets in P241) |
| + P238 hostile-token | +0 (predy M-06 already counted) |
| + P242 create-time (B) + 4626 (C) | +~3 (nextgen H-01); 4626 0 in P241 → ~48–56% |
| + top future family (J oracle freshness) | +~9 → **~57–62%** |
Coverage is the giant lever; every detector family is incremental on top of it.

## Final Verdict

# A — COVERAGE_IS_DOMINANT

Coverage-bound misses are 52/85 weighted (**61%**) — more than double all detector-family-bound misses combined
(22, 26%), with reasoning-depth 13% and proof-conversion 0%. Full-surface/facet coverage alone would lift P241
weighted recall from ~12% to ~45–53%; the best remaining detector family (oracle freshness) adds only ~9 weighted on
top. This confirms and quantifies the P241 finding: the binding constraint is reading the full in-scope surface, not
detector breadth.

## Recommendation (ranked by measured weighted-recall gain)
1. **Full-surface coverage enforcement** (A+K, ~52 weighted / 61%) — operate at FULL coverage on every target
   (use the existing Step-3.9 coverage gate as a hard gate; cover all facets/modules/libs before triage). By far the
   highest ROI. This is process/coverage, not a new detector.
2. **Oracle freshness/validity family (J)** (~9 weighted, HIGH generalization, LOW–MED cost) — the single
   highest-ROI *future detector family* if any is built (stale/answeredInRound/heartbeat/spot-vs-TWAP).
3. **Reward/emission accounting (I)** (~9 weighted, MED generalization) — architecture-narrow (ve(3,3)/gauge); build
   only if targeting that architecture class.
4. **Reasoning depth (L)** (~11 weighted but diffuse) — improve per-finding exploit-chain reasoning; not a buildable
   family, addressed by deeper supervised analysis.
5. P242 (create-time/4626), P237/P238 — already built; LOW remaining marginal ROI on this corpus.

**Bottom line:** do NOT build more detector families as the next move — their combined remaining weighted ROI (~26%)
is dominated by coverage (~61%). Invest first in full-surface coverage enforcement; reserve detector work for the
single oracle-freshness family if/when a future detector is justified. (Consistent with P241/P242: next phase is
supervised live hunting at FULL coverage, not another detector cycle.)
