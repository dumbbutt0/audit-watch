# P240 — Second shadow contest scorecard (PoolTogether V5, Code4rena 2024-03)

> Blind base-stack hunt + both advisory lenses (research-only) → freeze → reveal. Freeze hashes (FROZEN_HUNT.md)
> predate the answer-key open; sealed key re-verified byte-identical (never opened during the hunt). Both lenses
> stayed research-advisory (routed_manifest_ids:[]). Mechanism-based scoring.

## Headline
The advisory lenses generalized **cleanly** to a fresh contest (0 candidates, 0 FP, 0 noise) but contributed **0
recall** — because PoolTogether (single-asset ERC4626 vault, no Gnosis-Safe guard) and its awarded findings are
**outside both lens domains**. The blind **base stack** did the work: it recovered the only High and a funds-lock
Medium directly, plus a partial on the hook Medium.

## Recall vs the answer key (9 awarded: 1 High + 8 Medium)
| Metric | Value |
|---|---|
| Raw High recall | **1/1 = 100%** (H-01 = PT-01) |
| Raw Medium recall | 1 clean (M-06) + 1 partial (M-01) of 8 ≈ **19%** |
| Raw overall | 2 clean + 1 partial of 9 |
| **Weighted recall** (High=3, Med=1; total 11) | recovered 3 (H-01) + 1 (M-06) + 0.5 (M-01) = **4.5 ≈ 41%** |
| Precision of pursued (5 base candidates) | ~2.5 awarded-equivalent / 5 ≈ **50%** (PT-03 maps to a known bot-report ERC20-return class = OOS; PT-05 adjacent, not a clean award) |
| Proof conversion | **0** (harnesses BLOCKED_BY_BUILD — no foundry deps shipped) |
| Severity alignment | PT-02→M-06 aligned (Med); PT-04→M-01 aligned (Med); **PT-01→H-01 UNDER-rated** (predicted Med, awarded High) |
| Time on noise | ~0 (no lens noise; all 5 base candidates plausible) |

## Advisory-lens contribution (the core P240 question)
| Metric | Value |
|---|---|
| Safe-management candidates | 0 |
| Hostile-token candidates | 0 |
| Advisory false positives | **0** |
| Awarded findings recovered ONLY because of a lens | **0** |
| Findings ranked higher because of a lens | **0** |
| Advisory noise / wasted effort | **0** |

### Lens-contribution table (per awarded finding)
| Awarded | recovered by base | Safe lens | hostile lens | both | not recovered |
|---|:--:|:--:|:--:|:--:|:--:|
| H-01 | ✅ (PT-01) | — | — | — | — |
| M-01 | ◑ partial (PT-04) | — | — | — | — |
| M-06 | ✅ (PT-02) | — | — | — | — |
| M-02/03/04/05/07/08 | — | — | — | — | ✅ (6 missed) |
No awarded finding was recovered or up-ranked by either lens.

## Baseline reconstruction (with vs without advisory lenses)
The advisory lenses emitted 0 candidates → the run's recall, ranking, and pursued set are **identical** with or
without them. Baseline recall = final recall (4.5/11 weighted). The lenses added neither signal nor noise.

## Ranking impact
None. The frozen queue (PT-01, PT-04, PT-02, PT-03, PT-05) is base-only; advisory queue empty.

## Noise impact
None. 0 advisory candidates → 0 wasted triage effort. (Reinforces P239: lenses stay silent off-domain.)

## Recall-lift vs P235
Not directly comparable (different targets). The honest read across the two shadows: lens recall-lift is
**target-dependent** — large on an **in-domain** target (reNFT: P237/P238 recovered the H-01/H-02/H-04/H-05
families) and **zero on an out-of-domain** target (PoolTogether). P240 did not provide an independent in-domain
recall-lift datapoint because PoolTogether is out of domain.

## Final Verdict

# B — PROMISING_BUT_NEED_MORE_SHADOWS

The lenses behaved cleanly on a fresh contest (0 FP, 0 noise — reinforcing P239's precision generalization), but
this shadow did **not** prove recall-lift because PoolTogether is **out of both lens domains** (single-asset vault,
no Safe guard). The wiring pass condition ("≥1 meaningful awarded-finding contribution OR clear ranking improvement")
was **not met here**. Not A (no contribution); not C (C implies a fair in-domain test that failed — this wasn't one);
not D (zero noise); not E (base recall was actually decent: 100% High + a funds-lock Med).

**Key structural finding:** the lens domains (Gnosis-Safe guards; multi-token/order-selected settlement) are **rare**
in the available fresh corpus — reNFT was the only in-domain example. Independent in-domain recall therefore cannot
be demonstrated on the current corpus; it must come from an in-domain target (a Seaport/marketplace or Safe-guarded
contest) or from live hunting.

## Recommendation: **keep research-only (advisory) + proceed to supervised live hunting**
Evidence to date: 0 FP across reNFT + 20 P239 targets + PoolTogether; recall recovered on the in-domain anchor;
clean silence off-domain. The lenses are demonstrably **safe** (they only ever fire in-domain, with 0 noise), but
their domains are rare, so manufacturing another in-domain shadow has diminishing returns. The most efficient way to
gather the missing in-domain independent-recall evidence is **supervised live hunting** with both lenses running as
advisory signals (zero-noise risk demonstrated). Defer production wiring until an in-domain live/contest hit
confirms independent recall. (Alternative if more controlled evidence is preferred before live hunting: run one more
shadow specifically on an in-domain target — a Seaport-settlement marketplace or a Safe-guarded protocol.) Building
a third (create-time reentrancy) lens is not indicated by this result.
