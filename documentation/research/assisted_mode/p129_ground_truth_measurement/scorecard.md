# P129 — Scorecard

Confidence: **LOW / directional** (single fully-measured audit, n=15 outcome records). Small-n; treat as
a first honest data point, not a robust rate.

## Per-audit

### beanstalk-2024-05 — FULL (discovery recall + precision/FP + severity)
Known awarded (public): **81**. Source: `evals/beanstalk_finale/match_matrix.json` + `scorecard.json`.

| Bucket | Count | |
|---|---|---|
| HIT (exact) | 15 | exact-hit recall = **18.5%** |
| PARTIAL | 19 | useful-detection recall (HIT+PARTIAL) = **42.0%** |
| ADJACENT | 9 | any-touch recall (HIT+PARTIAL+ADJ) = **53.1%** |
| MISS | 38 | |

Recall by severity (useful = meaningful/n): High **13/22 = 59%** · Medium **14/31 = 45%** · Low **7/28 = 25%**.
**Regression note:** this api-free run scored meaningful 42.0% vs a prior baseline 55.6% (**−13.6 pp**) —
the credit-free in-session path under-performs the prior run on the same contest.

Precision / FP / severity (n=15 ground-truthed promoted findings):
| Metric | Value | Target | |
|---|---|---|---|
| Valid-finding rate | 0.80 (12/15) | — | |
| **False-positive rate** | **0.143 (2/14)** | < 0.10 | ❌ |
| Duplicate rate | 0.067 (1/15) | — | |
| Outcome accuracy | 0.867 | > 0.80 | ✅ |
| **Over-severity rate** (downgrade) | **0.267 (4/15)** | — | claimed > truth |
| Severity accuracy (indicative) | 0.333 | > 0.70 | ❌ |
| TP / FP / FN | 12 / 2 / 0 | | |

Per-agent reliability (valid / valid+invalid): `access_control 1.0` · `behavioral_state_analysis 1.0` ·
`logic 1.0` · `snapshot/flash_loan/dos/cross_chain/protocol_context/upgrade_storage 1.0` ·
`economic_attack 0.5` · **`arithmetic 0.0 (0/2)`**. The 2 FPs trace to `arithmetic` (AR-001) and
`economic_attack` (EA-002); the internal dup AR-002 is also `arithmetic`.

### decent (2024-01) — LEAD-recall (earlier funnel)
Known awarded: **9** (4H/5M). `_p81b/decent/recall_score.json`: lead_recall **100%** (9/9 DIRECT),
mechanism-naming match 9/9. Caveat: this is "a read-time lead touched the awarded function," **not** a
confirmed finding — an upper bound, not end-to-end recall.

### noya — LEAD-recall (earlier funnel)
Known awarded: **19**. `_p81b/noya/recall_score.json`: covered **18/19 = 94.7%** (DIRECT 9, ADJ 9, MISS 1),
direct **47.4%**, mechanism-naming match 7/19. Same lead-level caveat.

### Holdout denominators — recall PENDING_RUN
centrifuge 8 (8M) · pooltogether 9 (1H/8M) · predy 12 (4H/8M) · zetachain 48 (14H/34M) = **77** awarded,
catalogued in `holdout_awarded_inventory.json`. No local pipeline output ⇒ recall not yet computable.

## Overall (measured)
| Metric | Value | n | Confidence |
|---|---|---|---|
| Discovery recall — useful (beanstalk, full pipeline) | **42.0%** | 81 | directional |
| Discovery recall — any-touch (beanstalk) | 53.1% | 81 | directional |
| Lead-recall (decent / noya, earlier funnel) | 100% / 94.7% | 9 / 19 | upper bound |
| **False-positive rate** | **0.143** | 14 | directional |
| Valid-finding (promotion precision) | 0.80 | 15 | directional |
| **Over-severity rate** | **0.267** | 15 | directional |
| Severity accuracy (indicative) | 0.333 | 15 | weak |
| Duplicate rate | 0.067 | 15 | directional |
| PoC success (carried, unchanged) | 0.857 | 14 | prior |
| Duplicate-risk rate (public-known) | not measured | — | — |

## Still unmeasured
- Discovery recall on the 4 holdouts (77 issues) — needs a pipeline run.
- Reliable severity accuracy (public per-finding severity is inferred; run did not persist per-finding severity).
- Duplicate-risk / public-known rate against live platform state.
- Gate precision (no rejected-bucket reconstructed).
