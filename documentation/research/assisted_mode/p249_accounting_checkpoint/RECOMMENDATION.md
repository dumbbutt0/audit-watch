# P249 — Part E: Recommendation

## Success-criteria scorecard
| Criterion | Target | Result | Pass |
|---|---|---|---|
| Accounting misses → candidates | ≥4/5 | **5/5** | ✅ |
| → exploit chains | ≥3/5 | **5/5** | ✅ |
| High-confidence false positives | 0 | **0** (emits no findings, sets no severity) | ✅ |
| Increase in unrelated **candidate** volume | none | **0** (234 questions → 5 candidates; benign → 0) | ✅ |
| Behaves like a detector? | must not | **no** (interrogative records, 0 conclusions, asserted) | ✅ |

## Verdict (exactly one)

# A — READY_FOR_DEFAULT_OFF_USE

The accounting checkpoint passes every success criterion and the architectural invariant. It **observes** the
accounting shape, **emits interrogative reasoning records** (six questions, empty hypothesis, no severity/no
verdict), **forces candidate construction**, and leaves adjudication to the existing precision pipeline. On
the 5 P248 accounting misses it lifted **0/5 → 5/5 candidates and 0/5 → 5/5 exploit chains**, while emitting
**0 findings** and adding **0** unrelated candidate volume. The examine-time-checkpoint architecture is
validated: it increases candidate birth and exploit-chain construction without behaving like a detector.

It is recommended as a **default-off** reasoning aid (the flag `accounting_checkpoint_enabled:false` ships off;
the module is un-wired). Not A-for-default-ON: see the caveat.

## Caveat (the one real tuning signal, not a failure)
Question-record volume is high (234 across 3 contests). This is reasoning-prompt volume, not FP (every record
is an empty-hypothesis question), so it does not violate any success criterion — but it is heavy for a
default-ON run. **Before any future default-ON decision**, scope firing to higher-attack-surface manifest
items (`attack_surface_score ≥ 3`) and/or batch questions per contract. That is a default-ON tuning step,
distinct from this default-off verdict.

## Why this matters beyond accounting
P249's purpose was to validate the *architecture*, not to recover accounting findings. It did: the
"observe → six questions → forced candidate → route to existing pipeline, never conclude" pattern works and is
FP-safe. **Accounting is now the template** for the next two checkpoints — state-transition (highest absolute
recovery, carries the reasoning Highs) and cross-contract — which P247/P248 expect to recover the majority of
the remaining weighted recall. Those are separate, explicitly-approved build phases.

## Honest limits
- Recovery was demonstrated by the operator answering the checkpoint's questions against contests with known
  ground truth → training-confound caveat stands; the checkpoint guarantees the question is asked at the
  locus, not that the answer is found on an unseen target. A **forward blind run** is the right next
  measurement before building the remaining checkpoints.
- M-04's family label (A5) is imperfect (omission defect); locus + universal questions still carried it.
