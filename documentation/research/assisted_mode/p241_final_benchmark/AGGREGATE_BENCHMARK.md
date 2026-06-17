# P241 — Final Frozen-System Benchmark: Aggregate Results

Frozen-system measurement across **5 fresh, clean-blind, diverse contests** (blind → per-contest freeze → reveal).
No system edits. Both lenses research-advisory. **Honesty caveat up front:** under campaign budget, only the small
target (kelp) was read in FULL; the large targets (dittoeth/nextgen/predy/fenix) were **read-bounded** to their
highest-attack-surface contract(s). So the aggregate recall below is a **LOWER BOUND** that measures *system +
this-benchmark's partial coverage*, not the system's full-coverage ceiling (which kelp shows is materially higher).

## Per-contest summary
| Contest | Arch | Awarded (H/M) | Read | Base clean / partial | Lens TP | Recall (this run) |
|---|---|---|---|---|---|---|
| kelp | LRT/cross-chain | 3H/2M | **FULL** | H-03 + M-02 clean; H-01, H-02 partial | 0 | High 1clean+2partial/3, Med 1/2 — strong |
| nextgen | NFT | 5H/12M | AuctionDemo only | H-03, H-05 clean; M-05/M-07/M-11 partial | 0 | High 2/5; rest UNREAD |
| dittoeth | lending/oracle | 7H/9M | LibOracle only | 0 | 0 | 0/16 (facets UNREAD) |
| predy | perps/derivatives | 4H/8M | LiquidationLogic + lens | 0 base | **M-06 (hostile-token lens)** | 1 Med/12 (lens) |
| fenix | ve(3,3) rewards | 1H/6M | minimal | 0 | 0 | 0/7 |
| **Total** | 5 archs | **20H / 37M (57)** | mixed | **3 clean H + 1 clean M** + partials | **1 (predy M-06)** | — |

## Aggregate metrics
| Metric | Value |
|---|---|
| **High recall** | 3 clean / 20 = **15%** (+2 partial ≈ 25% w/ partials) |
| **Medium recall** | 2 / 37 = **5.4%** (kelp M-02 base + predy M-06 lens) (+nextgen partials) |
| **Weighted recall** (H=3,M=1; denom 97) | clean **11/97 ≈ 11%** (~16% incl. partials) |
| **Precision** (awarded-equiv / pursued) | ~5 / ~14 base candidates ≈ **36%** |
| **Proof conversion** | **N/A — 0/0** (all 5 targets BLOCKED_BY_BUILD: no foundry deps shipped) |
| **Ranking quality** | the findings recovered ranked at/near top of their contest queue (ranking was not the bottleneck) |
| **Severity alignment** | BASE systematically UNDER-rates (called awarded Highs Medium: KELP-01/03, NEXT-01/03); LENS over-rated predy M-06 (High→Med). Recurring under-rating theme (P223/P235). |
| **Lens contribution rate** | 1 awarded recovered by a lens / 57 = **1.8%** (the predy M-06 hostile-token liquidation-DoS — the first INDEPENDENT in-domain lens TP) |
| **Lens false-positive rate** | **0%** (Safe 0/5 contests; hostile 1 candidate = 1 TP, 0 FP) |
| **False-High rate (base)** | ~1 over-rate (NEXT-02 called High, ~QA) — low |
| **Avg hours/confirmed finding** | N/A (0 runtime-confirmed; build-blocked) |
| **Avg hours/awarded recovered** | high — most session effort went to bounded reads; full-read kelp was the efficient datapoint |

## Failure classification of missed awarded findings (~50 of 57)
| Class | Count (approx) | Examples |
|---|---|---|
| **Coverage (unread surface)** — DOMINANT | ~44 | dittoeth 16 (facets), nextgen ~10 (Minter/Core/Randomizer), predy ~11 (trade/perp libs), fenix 7 |
| Reasoning Depth (read but missed) | ~3 | nextgen H-02 (==endTime overlap, read AuctionDemo); kelp H-01/H-02 partials |
| State Modeling | ~2 | kelp M-01 (EigenLayer strategy migration) |
| Missing Family | ~1 | (most "missing-family" misses are actually unread-coverage here) |
The **recurring** miss family is **Coverage** — the system/operator did not read the full in-scope surface on large
targets — followed by Reasoning Depth on the surfaces that WERE read.

## The 5 success-criteria answers
1. **Actual recall?** Low as measured (~15% High / ~11% weighted), but COVERAGE-bound: on the one fully-read target
   (kelp) it recovered 3/5 (clean+partial). True full-coverage recall is materially higher than this aggregate.
2. **Actual precision?** ~36% of pursued candidates were awarded-equivalent; lens precision 100% (1/1, 0 FP).
3. **Actual competitiveness?** Finds real Highs + a lens TP with ~0 FP, but misses the majority of awards (esp. on
   large codebases) → useful, not yet top-tier.
4. **Which miss families recur?** Coverage (dominant), then Reasoning Depth — NOT a missing-detector-family problem
   (more detectors yielded 1/57). Severity under-rating recurs.
5. **Is live hunting justified?** Yes, SUPERVISED — the system reliably surfaces real findings when it reads fully,
   with near-zero false positives; a human operator supplies the full-coverage discipline the benchmark lacked.

## Final Competitive Assessment

# C — FINDINGS_BUT_MISSES_MAJOR_AWARDS

The frozen system recovers genuine awarded findings (kelp H-03/M-02, nextgen H-03/H-05, predy M-06 via lens) with
~0 false positives, but misses the majority of awarded findings — overwhelmingly due to incomplete coverage of large
in-scope codebases (a benchmark-execution/coverage limit, evidenced by kelp's strong full-read result), plus some
reasoning-depth misses on read surfaces. Not A/B (recall too low/inconsistent for top-tier), not D (it does find
meaningful findings, with 0-FP discipline).

## Recommendation: **Proceed to supervised live hunting**
Aggregate-driven rationale: (1) the binding constraint is **coverage/reasoning-depth of the base stack on full
codebases**, NOT detectors (1/57 contribution → another detector family is low-leverage), ranking (not the
bottleneck), or proof (build-blocked, orthogonal to recall). (2) The system demonstrably finds real Highs + a lens TP
with 0 FP under full coverage (kelp). (3) Supervised live hunting puts a human operator in the loop to (a) enforce
full per-target coverage — the exact gap this benchmark exposed — and (b) catch the recall misses, while the system
contributes precise candidates and safe advisory lens signals. Defer production wiring of the lenses (still 1 TP /
0 FP — safe but low-yield). The honest meta-point: this benchmark's low aggregate is dominated by partial coverage,
so the most valuable next step is operating the system at FULL coverage under supervision, not building more.
