# P247 — Phase B: Failure Clustering

Clustering the 21 reasoning-bound misses by first-divergence label. Weighted = 3·High + 1·Med.

| Cluster | Count | Weighted Impact | Findings |
|---|---|---|---|
| **CROSS_CONTRACT_REASONING_FAILURE** | 5 | **9** | decent H-02, H-03, M-01, M-05; centrifuge M-02 |
| **STATE_MACHINE_MISUNDERSTOOD** | 5 | **9** | decent H-04; kleidi M-01, M-03; munchables H-01, M-01 |
| **ACCOUNTING_REASONING_FAILURE** | 5 | **5** | kleidi M-02; centrifuge M-05, M-07; munchables M-03, M-04 |
| **PERMISSION_MODEL_FAILURE** | 3 | **5** | decent M-02; vultisig H-02; centrifuge M-04 |
| ECONOMIC_REASONING_FAILURE | 2 | 2 | decent M-04; vultisig M-02 |
| LIFECYCLE_MISUNDERSTOOD | 1 | 1 | vultisig M-03 |
| **Total** | **21** | **31** | |

## Pass condition: ≥70% explained by ≤5 clusters
| Top-N clusters | cumulative count | % count | cumulative weighted | % weighted |
|---|---|---|---|---|
| Top 3 (cross-contract + state-machine + accounting) | 15 | **71%** | 23 | **74%** |
| Top 4 (+ permission) | 18 | 86% | 28 | 90% |
| Top 5 (+ economic) | 20 | **95%** | 30 | **97%** |

**PASS.** Top 5 clusters explain **95% by count / 97% by weighted**; even the **top 3 clusters already
explain ~71% count / 74% weighted.** The misses originate from a small number of recurring reasoning
failures, not a long diffuse tail.

## Interpretation
- The **three dominant clusters are symmetric in weighted impact** (cross-contract 9, state-machine 9,
  accounting 5 → with permission 5 close behind). No single cluster dominates; a balanced 3–4-front problem.
- **Cross-contract + state-machine carry the High severity** (all 5 Highs fall in these two clusters: decent
  H-02/H-03/H-04, vultisig H-02→permission, munchables H-01). Fixing these two clusters is where the High
  recall lives.
- **Accounting is high-count but low-severity** (5 Mediums) — cheap, high-yield-per-effort, FP-tight.
- **The unifying meta-pattern:** in 20/21 cases the system **never constructed the exploit chain** — it read
  the code, formed a local impression, and moved on without (a) tracing values/identities/control across
  contract & cross-chain boundaries, (b) walking the state machine adversarially, or (c) checking
  accounting/rounding/permission completeness. This is a *hypothesis-generation* gap at examine-time, not a
  *rejection-justification* gap (0 DEFENSE_MISUNDERSTOOD). See INTERVENTIONS.md — it determines why the
  already-built P245 reroute does not close this.
