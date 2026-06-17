# P213 — failure cases & honest limitations

1. **Fixture-driven, not re-harnessed.** The carve-out criteria for each case are asserted in the fixtures (derived
   from the actual P204/P207/P212 harness records + P206 screening metadata), not re-executed here. SOPH-03's
   `deterministic_l3_proof`/`control_case_present` are backed by the real P212 Stage-1B harness (4/4 pass); the
   negative-control criteria reflect those phases' documented results. P214 (wiring) should pull these fields from the
   actual L3 records, not hand-set fixtures.
2. **Single positive case.** Only SOPH-03 exercises the upgrade path. The rule is general, but it has one real positive
   so far; more deterministic-core-path-DoS positives across corpora would strengthen confidence (parallel to the
   2-corpus discipline used for the original L3 standard).
3. **munchables guard is metadata-level.** munchables DoS "Highs" are kept < High because they lack an executed
   harness (criterion 1) — based on P206 screening, not a fresh harness. If later harnessed and all 10 hold, they could
   legitimately become High (which is the intended behavior, not a bug).
4. **Criterion subjectivity.** `no_workaround`, `affects_class_or_protocol`, `not_optional_griefing` require judgment;
   they are human-review inputs, not auto-derived. The carve-out narrows but does not eliminate reviewer judgment.
5. **Schema delta.** The 10 carve-out fields are NOT in the P208 `L3_READINESS_SCHEMA.json` yet; P214 must add them
   (additive) before wiring.
