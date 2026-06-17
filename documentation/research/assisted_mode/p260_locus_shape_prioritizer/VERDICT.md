# P260 — VERDICT

## A — MODULE_READY_FOR_FRESH_HELDOUT
(meaning: backtest is clean enough on the module's target class to justify the P261 fresh-contest PROOF — NOT a
claim of live validation.)

### Why A
The module does its one narrow job and fixes the P259 LOCUS_SELECTION gap on the subtle-accounting-state class:
- **Core fix CONFIRMED:** hybra `GrowthHYBR.deposit` — the P259 award locus that was a checkpoint hit but
  *skipped* — is now **rank #1 with the right template (T8)**. Sentiment bad-debt is placed at the **correct
  locus** (`Pool.rebalanceBadDebt` #6, T7), fixing P259's wrong-locus error.
- Award loci prioritized into top-15 on **6/7** backtest targets; right template on 5/7; bounded output (no noise
  flood); reviewable top-2 hypotheses + B/C handoff; **zero production changes**; no answer key used.
- Failure criteria not triggered for the target class (not noise; skipped-award-locus recovered; hypotheses
  source-backed; output B/C-consumable; research-only/default-off/un-wired).

### Why not B/C/D
- Not C (NOT_USEFUL): it recovered the exact skipped award-locus class P260 was built for (#1).
- Not D (constraint violation): zero production edits; forbidden files byte-identical; active audit unchanged.
- Not B (NEEDS_REFINEMENT) **as the headline** — though B is the honest fallback: the basin math/units miss +
  bakerfi T1-vs-fee + notional partial are real and documented. I choose A because (a) the module's *designed
  scope* is the accounting/state shape class, on which it works, and (b) A explicitly means "ready for the fresh
  PROOF," which is the correct next gate — not "validated." The math/units gap is logged for a future T9 template,
  not a blocker for the P261 proof on accounting/state targets.

### Required next step
**P261 — fresh contest → P260 prioritizer → B/C ranking → five ops → freeze → reveal.** That live run (on a
freshly-acquired unseen award-class-fit subtle contest, since the held-out corpus is exhausted) decides whether
this becomes a real harness path. Backtest necessary, not sufficient.

### Honest caveats
Backtest recall is optimistic (module's signal-set partly determines what it surfaces); basin math/units class
uncovered; some award loci ranked low/partial; deep mechanism correctness still rests on downstream B/C + 5 ops.
