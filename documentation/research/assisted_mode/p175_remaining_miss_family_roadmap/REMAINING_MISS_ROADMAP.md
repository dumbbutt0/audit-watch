# P175 — Cross-corpus remaining-miss family roadmap

**Question (the user's):** after P174, do the remaining unrecovered answer-key findings cluster into 2–3
dominant root-cause families (→ taxonomy ROI still high), or are they scattered across many unrelated
architectures (→ taxonomy ROI dropping)? This re-cuts the P171 quantamm family matrix **post-P174** and
extends a family lens across the eval portfolio, scoring each family by
`remaining_misses × source_detectability × expected_precision`.

Reproduce: `python documentation/research/assisted_mode/p175_remaining_miss_family_roadmap/family_roadmap.py`
(read-only; emits `family_scoring.json`). Scoring priors live in `family_rules.json` — edit + re-run to re-rank.

## Corpus coverage
9 eval corpora, 232 findings. **6 fully family-scored** (carry answer-key titles); **3 coverage-limited**
(no titles → counted, not family-scored).

| corpus | n | recovered/touched | remaining | note |
|---|--:|--:|--:|---|
| quantamm | 44 | **19** | **25** | post-P174 override (F1 6 + math-estimator 5 flip miss→recovered) |
| zaros | 70 | 8 | 62 | perps/credit MME |
| revert-lend | 31 | 4 | 27 | lending/NFT-LP |
| panoptic | 22 | 3 | 19 | options/Uniswap-v4 |
| recall | 13 | 5 | 8 | IPC/subnet |
| silo | 6 | 5 | 1 | lending |
| ark / hybra / swan-dria | 46 | 25 | 21 | coverage-limited (count-only) |

Excluded: `quantamm-2024-12-strict-eval` (duplicate of the quantamm corpus), `beanstalk-2024-05-eval2`
(file is an `upgrades_applied` log, not a finding matrix).

## Family roadmap (scored)
Ranked by `priority = remaining × detectability × precision`; severity-weighted overlay
(`prioSW = sevWeighted × det × prec`, High=3/Med=2/Low=1) and reportable-yield shown alongside.
`det`/`prec` are transparent priors from `family_rules.json` (P171 + portfolio judgment).

| family | remain | sevW | det | prec | **prio** | prioSW | Highs | yield | shipped lens |
|---|--:|--:|--:|--:|--:|--:|--:|---|---|
| oracle_robustness | 14 | 20 | 3 | 2 | **84** | 120 | 0 | low (DoS/Low) | — |
| liquidation_accounting | 15 | 31 | 2 | 2 | **60** | 124 | 2 | med-high | — |
| hook_lifecycle | 10 | 21 | 2 | 2 | **40** | 84 | 2 | med | — |
| fee_accounting | 20 | 40 | 1 | 2 | **40** | 80 | 5 | med | — |
| vault_accounting | 8 | 15 | 2 | 2 | 32 | 60 | 1 | med | — |
| accounting_drift | 31 | 68 | 1 | 1 | 31 | 68 | 8 | med (deep, FP-prone) | — |
| arithmetic_overflow | 7 | 17 | 2 | 2 | 28 | 68 | 3 | med | — |
| reentrancy | 3 | 9 | 3 | 3 | 27 | 81 | 3 | high | yes (specialist) |
| estimator_math | 6 | 15 | 2 | 2 | 24 | 60 | 0 | med-high | yes (math-estimator) |
| authorization_mismatch | 6 | 14 | 2 | 2 | 24 | 56 | 0 | med-high | — |
| dos_griefing | 7 | 16 | 2 | 1 | 14 | 32 | 0 | low-med | — |
| rounding_with_impact | 3 | 6 | 2 | 2 | 12 | 24 | — | med | — |
| slippage_deadline | 2 | 4 | 3 | 2 | 12 | 24 | — | low-med | — |
| recipient_beneficiary | 3 | 5 | 2 | 2 | 12 | 20 | — | med | — |
| lifecycle_hygiene | 7 | 8 | 1 | 1 | 7 | 8 | — | low | — |

## Clustering verdict — the answer
**The remaining misses do NOT cluster into 2–3 dominant families.** Across the OPEN families (excluding the
already-shipped reentrancy + estimator lenses), of 133 open remaining misses:

- **top-2 = 21.8% · top-3 = 29.3% · top-4 = 44.4%.**

Per the user's own criterion (70–80% in 2–3 families ⇒ ROI high; scattered ⇒ ROI dropping), the surface is
**scattered → broad generic-taxonomy ROI is dropping.** And the misses are strongly **corpus/architecture-
specific**, not portfolio-wide families:
- zaros (perps/credit): `accounting_drift` 23 + `fee_accounting` 12 — credit-capacity / realized-debt /
  state-desync dominates.
- revert-lend (lending): `liquidation_accounting` 7 + `accounting_drift` 5.
- quantamm (dynamic-weight AMM): `hook_lifecycle` 7 (quantamm-only) + `oracle_robustness` 6.
- panoptic (options): `liquidation_accounting` 4 + `oracle_robustness` 3.

A single new generic selector would recover only a small, single-corpus slice of the portfolio. This matches
the standing platform reality (CLAUDE.md): every validated research family is **architecture-narrow**.

## Formula-vs-value tension (read before picking a target)
- **`oracle_robustness` tops the raw formula (84) but is a trap for reportable recall:** 0 Highs, all
  Low/Medium DoS-flavored. Building it raises *touched-recall* cosmetics without recovering reportable bugs.
- **`accounting_drift` is the biggest pile (31) and richest in Highs (8) but scores lowest (det=1×prec=1):**
  deep cross-function state-desync is FP-prone and not a clean two-signal pattern. This is **deep-pass-routing /
  guarded-downstream territory (already shipped), not a new pattern detector.**
- The families that are simultaneously **buildable AND reportable-valuable** are `liquidation_accounting`
  (prioSW 124, 2 Highs, med-high yield), `hook_lifecycle` (2 Highs, the P171 F3 candidate), and
  `fee_accounting` (5 Highs).

## Recommendation (go/no-go — no selector built in P175)
1. **No new generic selector is justified by clustering.** The scattered, corpus-specific surface means the
   recall frontier has moved past "add another global family."
2. **If one selector is built next: `hook_lifecycle` (F3).** Already scoped in P171; bounded, Balancer-V3-
   specific, 2 Highs; it mirrors F1's "narrow-but-FP-tight, re-surface-only" model that worked in P174. Honest
   caveat: portfolio ROI ≈ the quantamm 7 — narrow, like F1.
3. **Do NOT build `oracle_robustness` as a reportable-recall play** despite its #1 formula rank (yield-low).
4. **`accounting_drift` → invest in the already-shipped deep-pass routing + guarded-downstream, not a pattern
   lens.** That is the right tool for the FP-prone state-desync long tail (zaros/revert-lend).
5. **Highest-leverage move overall:** measure how much of the scattered accounting/state-desync tail the
   *already-shipped* guarded-downstream + deep-pass routing recovers on zaros/revert-lend (currently unmeasured)
   before building anything new — the P174 lesson (the misses were over-cleared, not un-seen) likely repeats.

## Limitations (honest)
- **Recovery is measured only on quantamm (post-P174).** Other corpora reflect their original eval-run
  match-matrix state; the now-shipped lenses (estimator, reentrancy, F1) may already address some of their
  remaining misses — unmeasured here. So cross-corpus "remaining" is an upper bound on what's truly uncovered.
- **Non-quantamm family tags are title-derived** keyword classification (`family_rules.json`), approximate;
  5 idiosyncratic findings use explicit `manual_overrides`; family boundaries (liquidation/accounting/rounding)
  are fuzzy. quantamm uses the P171 hand-tags verbatim.
- **3 coverage-limited corpora (21 remaining misses) are excluded** from family scoring (no titles).
- **det/prec are priors (judgment), not measurements** — exposed in `family_rules.json` for re-scoring.
