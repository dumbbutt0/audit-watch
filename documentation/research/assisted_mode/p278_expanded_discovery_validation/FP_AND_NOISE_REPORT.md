# P278 — FP_AND_NOISE_REPORT

## Severe concluded/reportable FP: **0** (before and after budget expansion)
The phase exercises only the upstream queue + an advisory evidence/readiness gate. Nothing is concluded/reported/given
severity; the strict late gate (runtime + FP refutation) is not reached. Every decision carries the advisory contract
(severity null, all promotion flags false). `outputs/fp_noise_report.json`.

## Incremental noise from budget 10 vs 5
Validation-queue avg **7.0** (vs ~5 at budget 5) — about +24 advisory candidates corpus-wide. All are advisory-only and
**NEEDS_MORE_EVIDENCE** (none reportable). Bounded by validation-queue budget 10 + PoC budget 5. severe FP stays 0.

## Where candidates fail (missing-dimension frequency, the repair signal)
All 84 auto candidates miss the **exploitability core**: attacker_model · attacker_controlled_inputs ·
state_value_liveness_delta · victim_gainer · terminality_or_amplification · tx_sequence · poc_assertion ·
refutation_result (each missing in 84/84). root_cause/source_refs are present (from `source_backed_trigger`);
runner_up_mechanism present in 80/84. So the gate correctly admits the hypothesis layer and blocks on the
operator-to-derive exploitability layer.

## Taxonomy
- advisory-only NEEDS_MORE_EVIDENCE: 84 (not FPs — incomplete, not wrong).
- non-awarded TP / same-area-wrong / benign: not adjudicated in this mapping phase (would need completion/PoC; the
  hand-sample refutation notes show the discipline).
- unresolved assumptions: tracked per package; the hand sample's assumptions are bounded and do not carry the core claim.
- **severe concluded/reportable FP: 0.**

## Anti-monoculture
Satisfied 11/12 contests; only quantamm (queue=4, 3 classes) trips the 40% rule — a small-queue artifact (4 candidates
cannot keep a class <40% while covering ≥3 classes), not a routing defect.
