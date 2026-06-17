# P293 — LIMITATIONS

- **Supervised, not blind.** P293 was tuned with knowledge that `_increaseUserShare` is the salty target locus. It
  is grounded in source patterns (not the answer key), and the term families/patterns are generic, but
  generalization is UNPROVEN until a fresh blind retest. One confirmed positive + 0 FP earns A for a repair phase;
  it does not prove blind recall.
- **One confirmed positive.** Only `_increaseUserShare` lifts on the corpus. Patterns A/B/C/E are FP-safe and unit
  -tested but have no corpus positive yet (same caveat as P289 lenses 2/3/4).
- **Naming families are heuristic.** `virtualrewards`/`totalrewards` were added as generic reward-debt/accumulator
  synonyms; a protocol using a wholly novel name still misses. Bare `index/reward/acc` are excluded to hold FP=0.
- **Pending detection is textual.** `_L3_RATIO` and `_l3_share_before_checkpoint` are regex/positional, not data-flow
  — see REPAIR_BACKLOG.
- **completion_evidence_deriver edit.** Two base dims are filled at the deriver (scoped, fill-if-missing); the
  architecturally cleaner home is the P292 admission package builder (do-not-edit this phase).
- **No PoC executed.** A PoC-INTENT is recorded for `_increaseUserShare` (Tier-C feasible); no forge test was built
  (the awarded mechanism is recall-graded, not PoC-graded, for this repair phase).
