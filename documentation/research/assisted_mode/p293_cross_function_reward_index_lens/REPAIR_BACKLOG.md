# P293 — REPAIR_BACKLOG

Remaining Lens-3 / pipeline gaps after P293 (priority: H/M/L).

- **[M] `liquidateUser` lens precision.** A liquidation entry fires GLOBAL_INDEX_NOT_PAIRED; the gate's D1 holds it,
  so it is not a false READY, but a liquidation entry is a weaker reward-index candidate than a stake/deposit entry.
  Consider gating GLOBAL_INDEX_NOT_PAIRED to entries whose primary effect is a share INCREASE.
- **[M] In-span pending detection misses comma-arg ratios.** `_L3_RATIO` requires a `*…/…`; helpers like
  `ceilDiv(a*b, c)` (comma) are not detected in-span, so the lens relied on the sibling. Add a `div-like(a*b, c)`
  call form to in-span pending detection for robustness on other targets.
- **[M] `runner_up_mechanism` fill is generic.** The P293 fill supplies a truthful but non-specific runner-up. A
  real runner-up (e.g. the rounding-direction alternative) would be stronger evidence — derive it from the
  bound_semantics rounding helper when present.
- **[M] base-package completeness for admitted internal loci.** `root_cause`/`runner_up_mechanism` are absent on
  admitted internal-locus packages and had to be filled at the deriver. The cleaner home is the admission package
  builder (P292), but that is do-not-edit this phase. Backlog: fill these at admission time.
- **[L] cross-contract reward index.** The lens resolves same-contract siblings + same-/library trace callees; a
  reward index split across UNRELATED contracts (external dispatch) is fail-closed (`LENS3_TRACE_UNRESOLVED`).
  Needs the cross_contract_sibling_parity detector as an evidence helper (the corrected-reference lever).
- **[L] Pattern B ordering is positional, not data-flow.** `_l3_share_before_checkpoint` uses textual position of
  the first checkpoint marker; a checkpoint inside a branch could be mis-ordered. Acceptable (fail-open toward
  refute is the safe direction) but noted.
