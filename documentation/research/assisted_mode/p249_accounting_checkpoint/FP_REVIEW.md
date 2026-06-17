# P249 — Part D: False-Positive Review

The success bar: **0 high-confidence false positives** and **no increase in unrelated candidate volume**. The
checkpoint clears both *by construction*, because firing is interrogative.

## 1. The checkpoint emits zero findings (invariant verified)
Across all three contest runs: `emits_findings:false`, `concludes_vulnerability:false`,
`output_type:"reasoning_records"`, and **records carrying a conclusion (severity/concluded) = 0**. Every
record has `severity:null`, `confidence:null`, `exploit_hypothesis:""`. A thing that emits no findings and
sets no severity cannot produce a high-confidence false positive. (Runtime assert in the runner + unit test
`test_checkpoint_never_concludes_or_sets_severity`.)

## 2. Question-record volume ≠ candidate volume (firing ≠ finding)
| Contest | question-records emitted | constructed candidates (after answering) | findings emitted |
|---|---|---|---|
| kleidi | 20 | (the 1 real: M-02) | 0 |
| centrifuge | 125 | (the 2 real: M-05, M-07) | 0 |
| munchables | 89 | (the 2 real: M-03, M-04) | 0 |
| **Total** | **234** | **5** | **0** |
The checkpoint asks 234 questions; only 5 become candidates once answered. Unrelated **candidate** volume
increase = **0** (a candidate only exists after the operator answers a question "yes" with a value path). A
detector emitting 234 findings would be catastrophic; a checkpoint asking 234 questions is the design.

## 3. Benign accounting code → questions resolve to "no" → no candidate
Sampled benign question-records (centrifuge) and answered the six questions:
| Function | family fired | Q1–Q6 answers | exploit_hypothesis | advances? |
|---|---|---|---|---|
| `totalAssets` (view) | A1 | all "no" (pure view, no state change) | "" | no |
| `convertToShares` (view) | A1 | all "no" (read-only conversion) | "" | no |
| `maxDeposit` (view) | A4 | all "no" (returns a stored limit) | "" | no |
| `previewDeposit` (view) | A1 | all "no" | "" | no |
| `transferFrom` (standard) | A3 | all "no" (1:1 transfer, conserved) | "" | no |
These fire (they are accounting-shaped) but answering the questions yields no value path → no candidate. The
record stays an empty-hypothesis question.

## 4. Non-accounting code fires nothing
Negative control — `Guard.checkTransaction` (pure access-control, no accounting): **0 families fired**. The
checkpoint is scoped to accounting shapes; it does not blanket the codebase.

## Conclusion
- High-confidence false positives: **0** (emits no findings, sets no severity).
- Unrelated candidate-volume increase: **0** (only 5 candidates constructed, all real; benign records resolve
  to no-candidate).
- **Operator-burden caveat (the real tuning signal):** 234 question-records is high — that is reasoning-prompt
  volume, not FP, but it is heavy for a default-ON run. Before any default-ON consideration, scope the
  checkpoint to higher-attack-surface manifest items (e.g. `attack_surface_score ≥ 3`) and/or batch questions
  per contract. As a **default-off** reasoning aid it is FP-safe today.
