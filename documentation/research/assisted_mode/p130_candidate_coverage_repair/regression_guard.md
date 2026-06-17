# P130 — Regression Guard

## Candidate-volume inflation (the primary cost)
| Audit | in-scope fns | high-surface ≥3 before | after | Δ | boosted |
|---|---|---|---|---|---|
| noya (library-heavy) | 377 | 158 | 228 | **+70 (+44%)** | 70 |
| decent (control) | 72 | 46 | 52 | +6 (+13%) | 6 |

- Manifest item count, in-scope count, and contract count are **unchanged** (the repair re-ranks; it does not
  add/enumerate/scope-change anything). avg candidates/contract rises only via the score lift.
- The two-signal gate + per-contract cap (3) are the inflation bound. Capless, the full risk-tag gate would
  have boosted 102 on noya (+65%); the cap holds it to +44%. Sweep over caps (measured):
  cap 2 → +35% (awarded 58%) · **cap 3 → +44% (awarded 74%)** · cap 4 → +50% (awarded 79%). cap=3 chosen as
  the knee of the curve.

## FP / speculative-FP impact
- **At the metric level: unchanged.** `compute_metrics` FP 0.143 and over-severity 0.267 are invariant
  (they read ground truth, not the manifest).
- **Downstream (not yet measured):** a +44% deep-pass population on library-heavy audits means more functions
  routed to specialists, which *could* raise speculative FPs — exactly the `arithmetic` / `economic_attack`
  speculative-reachability family P129 flagged. **This cannot be measured without a full pipeline run**, which
  is out of P130 scope. This is the central uncertainty and the reason for the decision label.
- Mitigation already in place: the boost only lifts to the cutoff (3), not above; risk-tagged helper logic
  still competes on equal footing, and the FP-tight downstream gates (multi-pass confirm, FP autopsy,
  reject-first) are unchanged.

## Runtime impact
- Manifest build is deterministic and the post-pass is O(items); no measurable runtime change on noya (1649
  items) or decent. (The downstream cost is reviewer/specialist time on the larger deep-pass set, not tool runtime.)

## Reversibility
- `library_internal_surface_boost: false` restores prior scoring exactly (test
  `test_flag_off_is_fully_reversible`). The cap is tunable without code change.

## Determinism
- Re-running the repaired tool on noya yielded an identical score vector and the same 70 boosts.

## Verdict on regression
Recall-proxy improves substantially on the library-heavy audit with **no precision-metric regression** and a
**bounded, capped, reversible** volume increase — but the +44% deep-pass inflation on library-heavy audits is
a real reviewer-cost / latent-FP risk that is **unverified downstream**. → favors **ACCEPT_WITH_LIMITS**
(keep the cap; gate behind the flag; confirm downstream FP with a pipeline run before defaulting on for
production submission audits).
