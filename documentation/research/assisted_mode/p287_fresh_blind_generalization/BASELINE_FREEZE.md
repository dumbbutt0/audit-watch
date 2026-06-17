# P287 — BASELINE_FREEZE

Full hashes in `outputs/hash_manifest.json`. Recorded BEFORE running any discovery on the target.

## Target
`kelp-2023-11-holdout` · source hash `8918979344a4d19b…` · H/M count 5 (3H/2M, content-light) · answer key SEALED
(no local findings; external public report NOT opened pre-reveal).

## Frozen stack (sha256-16, all present)
P260 locus_shape_prioritizer · P262 recall_first_shape_sweep · P264 recall_first_harness · P267
mechanism_pairwise_selector · P269 impact_first_poc_triage · P273 award_class_coverage_router (`6debb753…`) + config
(`91f9deac…`) · P278 expanded_validation_queue + config · P279/P282/P283/P284 completion_evidence_deriver (`c41eaf9d…`) ·
P281/P285 source_span_guard_extractor (`cd472bd8…`) + research_poc_readiness_gate.json · gate poc_readiness_evidence_gate
(`9a4e3834…`) · P283 cross_function_value_tracer (`f28f0620…`) + config · P284 invariant_delta_deriver (`dd549b9f…`) +
config (`3eb86fcc…`) · p276_corpus_replay (blind discovery driver) · reused detector platform (sibling_function_parity,
registry_position_lifecycle, omitted_term_dataflow_gate, bound_semantics_gate) · P271 checklist.

## Forbidden 5 (sha256-8)
dashboard_sync `c1af70e1` · deep_trace.md `c095c426` · min_confirm_gate `2a15169a` · confirm_gate `afc481c9` ·
validate_p208_l3_readiness `ae55eb80`.

## Active audit
`output` → `audits/size-credit-2024-06-blind/output` (unchanged).

## Command plan (blind, award-free)
1. `p276_corpus_replay.py --audit-id kelp-2023-11-holdout --out-dir <run>` → shadow harness + P273 coverage + P269 triage.
2. `expanded_validation_queue.py --replay-dir <run> --out-dir <run>` → validation_queue + evidence_packages.
3. `completion_evidence_deriver.py --manifest audits/kelp-2023-11-holdout/output/coverage_manifest.json --packages
   evidence_packages.json --out derived.json` (P279/P282/P283/P284).
4. `poc_readiness_evidence_gate.py --packages derived.json --out readiness.json` (P281/P285).
5. Freeze pre-reveal artifacts + hashes → PoC-intent → ≤3 PoCs → PRE_REVEAL_GATE → reveal.

## No-tuning / no-repair attestation
The frozen stack is run as-is. No module edited during the run (hashes re-verified at the end).
