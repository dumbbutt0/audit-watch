# Research prompt/spec — Recall-First Shape Sweep (P262)

**RESEARCH-ONLY · DEFAULT-OFF · UN-WIRED · ADVISORY.** Not a production prompt; not referenced by run_pipeline /
agent_policy / routing / dashboard. Companion to `scripts/research/recall_first_shape_sweep.py`.

## One-shot recall fix
The P259 leak = **early locus pruning** (manual selection narrows to 2–5 loci before shape discovery runs on the
award-carrying surface). This sweep **moves shape discovery BEFORE narrow selection**: it forces shape discovery on
a bounded high-risk surface set (recall-first clauses 1–5), adds optional lower-priority **T9** math/units recall,
and hands a BOUNDED candidate set to downstream Profile B / Profile C ranking + the unchanged five completion ops.

## Operator usage
1. Run isolated checkpoints (accounting + state-transition) on the target manifest.
2. (optional) Run the P260 prioritizer; pass `--prioritizer` to reuse its ranking.
3. Run `recall_first_shape_sweep.py … --out … [--md …]`.
4. For each swept locus (RECALL_CANDIDATE_ONLY), answer its mechanism `falsification_question` + fill the
   operator-to-derive fields, then feed top mechanisms to Profile B/C ranking → five-op completion → FP refutation.

## Hard guarantees
Advisory only: emits NO severity / concluded / vulnerability / reportable / submission_ready (runtime-asserted).
Bounded (≤25 loci, ≤5 mech/locus, ≤30 mech total). Promotion-gated (see FP_GUARD.md). T9 ranked last (never
dominates the subtle-accounting path). Requires no answer key. Backtest is necessary-not-sufficient; the real proof
is a fresh end-to-end scored run.
