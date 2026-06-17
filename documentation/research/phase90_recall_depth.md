# Phase 90 — Recall / depth improvement (analysis + prompt + taxonomy)

Analysis-and-aids phase over the frozen corpora (P81e/P85/P87/P89). **No blind eval. No severity-gate change**
(gate frozen at P88 `193abf9f` — P90 found no new gate failure). No historical re-scoring. All artifacts under
`documentation/research/_p90_recall_depth/`.

## A — Recall cap analysis (`recall_cap_table.json`, `recall_cap_report.md`)
Reconstructed full lens ranks + awarded→entry-function maps for all 4 phases. **Conclusion: a bigger global
lead cap is low-value.** Going from the cap used (8–12) to top-16/20 captures **0** extra awarded surfaces in
3 of 4 phases (+1 in P81e at top-20). Misses are dominated by **depth (rejected, 21)** and **negative-space /
internal (17)**, not below-cutoff (5). **Recommended policy:** keep global `top-12` (≤2 contracts) / `top-16`
(larger), **add a per-in-scope-contract floor of top-2** (covers low-scoring security contracts like
TraitForge `EntropyGenerator` → H-06/M-01/M-05), and **drive selected leads' `NOT_RUN`→0** (P89 H-01 was a
throughput loss, not a cap loss).

## B — Depth miss taxonomy (`depth_miss_taxonomy.json`, `depth_miss_report.md`)
Fix-owner distribution across the misses: **deep_pass (conversion depth) = 8** (the dominant loss),
lead_selection = 5, taxonomy = 4, maximal_consequence_check = 3, severity_gate_input = 2, adversarial = 1,
**severity_gate_logic = 0** (validated, untouched). Recurring patterns: wrong-harmlessness calls,
un-enumerated mechanisms, **High under-labelled Medium** (P87 H-01, P89 H-05), admin-footgun misclassification
(P87 H-03), self-inflicted-vs-involuntary misread (P87 M-18, P85 M-01).

## C — Maximal-consequence impact check (`maximal_consequence_prompt.md` + `scripts/investigation/maximal_consequence_check.py` + `config/maximal_consequence_check.json`)
An **advisory, un-wired** aid that, before severity labelling, tests the maximal plausible consequence and
recommends escalation + which gate markers to attach — the **same `high_liveness_markers` / `involuntary`
tags the existing P88 gate already consumes** (the gate is *not* modified). Reject-first: escalation requires
`source_backed`; a bounded/lazy issue with no concrete consequence is never escalated. Verified end-to-end
(check → attach markers → unchanged gate reports `high`). Regression-tested against P89 H-05, P87 H-01 (→High),
P87 H-03 (admin footgun → user harm), P87 M-18 (involuntary kept), and updateTaxRate (bounded → no escalation).

## D — P84 taxonomy additions (reject-first handoff types, no generator code change)
- **`access_control_index_integrity`** — Phi H-05 class (public internal-style index mutator corrupts arbitrary
  address's bookkeeping → downstream revert / mis-accounting).
- **`signature_replay_authorization`** — Phi H-01/H-02 class (replayable/re-bindable signature/merkle auth).
- **Deferred:** `negative_space_missing_function` — only one confirmed instance (P81e M-01); not yet justified.
Both new types generate reject-first `DO_NOT_SUBMIT`, un-promotable bundles (added to handoff `SEED_TYPES`).

## Verification
- `~/.local/bin/pytest` over investigation/handoff/funnel/human_validation/candidate_detail/candidates →
  **202 pass** (incl. 9 new maximal-consequence tests + 2 new handoff types).
- **`severity_impact_gate.py` UNCHANGED** (`193abf9f`); deep_pass `57c29fff` / hygiene `b9e18f29` / transitions
  `2c00069c` / lead_schema `3c57f04e` / abc_eval `5e0d855d` / surface_recall_lens `29a7b915` /
  surface_recall_score `fd3c7543` / funnel `720e9092` / handoff_generator `9c2c89cb` byte-identical.
- Prior frozen artifacts unmutated; no production wiring (no-wiring grep CLEAN).

## Pass — P90 delivered
recommended lead-cap policy ✓ · miss taxonomy with fix ownership ✓ · maximal-consequence check reducing
High→Medium under-labelling (verified) ✓ · two justified P84 taxonomy types ✓ · tests + docs ✓ — **without
changing historical scores or weakening severity-FP controls** (gate frozen).

## Next — P91
Fifth fresh sealed-key blind run adopting: **top-16 + per-contract top-2 floor + NOT_RUN→0** (P90-A), the
**maximal-consequence prompt** in the deep pass / adversarial review (P90-C), and the **two new P84 types**
(P90-D). Measure whether conversion recall + correct High labelling improve **while maintaining 0 severity FP**.
The deep-pass depth gap (B's largest bucket) is the primary thing P91 should move.
