# P251 — Part E: Recommendation

## Success-criteria scorecard
| Criterion | Target | Result | Pass |
|---|---|---|---|
| State-transition misses → candidates | ≥4/5 | **5/5** | ✅ |
| → exploit chains | ≥3/5 | **5/5** | ✅ |
| ≥1 High with a complete chain | ≥1 | **2** (munchables H-01, decent H-04) | ✅ |
| High-confidence false positives | 0 | **0** (emits no findings, sets no severity) | ✅ |
| Unrelated candidate-volume increase | none | **0** (59 questions → 5 candidates; benign → 0) | ✅ |
| Findings / severity emitted | 0 / 0 | **0 / 0** (asserted on all runs) | ✅ |
| Behaves like a detector / generic noise? | must not | **no** (interrogative; CEI-correct + stateless → 0; tuned away from generic noise) | ✅ |

## Verdict (exactly one)

# A — READY_FOR_DEFAULT_OFF_USE

The state-transition checkpoint passes every success criterion and the architectural invariant. Mirroring the
validated P249 accounting pattern, it **observes** state-transition shapes, **emits interrogative
STATE_TRANSITION_CHECKPOINT records** (8 questions, empty hypothesis, no severity/verdict), **forces candidate
construction**, and routes to the existing precision pipeline. On the 5 P248 state-transition misses it lifted
**0/5 → 5/5 candidates and 0/5 → 5/5 exploit chains, including 2 Highs with complete chains** (H-01, H-04),
while emitting **0 findings / 0 FP** and adding **0** unrelated candidate volume. Recommended as a
**default-off** reasoning aid (`state_transition_checkpoint_enabled:false` ships off; module un-wired).

## Caveats (not failures)
- **Required bounded tuning** during build (S2 loop+set, S3/S4 vocab tightening) — recorded in
  IMPLEMENTATION.md; without it S3/S4 over-fired and S2 missed the kleidi M-01 anchor. State shapes are
  broader than accounting shapes, so a little tuning was expected; volumes are now bounded (59 across 3
  contests).
- **Manifest-coverage dependency:** the S4 anchor (decent H-04) lives in a lib the decent manifest doesn't
  enumerate → the checkpoint (manifest-driven) couldn't observe it via the run; replayed via direct taxonomy.
  This is a P245-coverage gap, not a checkpoint flaw — but it reinforces that checkpoints only fire where
  coverage reaches.
- **Training-confound:** chains reconstructed by answering questions against known ground truth; the next step
  must measure on unseen code.

## Next step (per the phase spec)
This validates the architecture; it does NOT wire into production. The next step is a **forward blind run with
P245 + accounting checkpoint + state-transition checkpoint all enabled** on an unseen target (mirroring P250),
to measure real lift. Only after a forward-blind success should the cross-contract checkpoint be built. The
two checkpoints are independent, default-off, and FP-safe, so enabling both for the forward-blind run is safe.
