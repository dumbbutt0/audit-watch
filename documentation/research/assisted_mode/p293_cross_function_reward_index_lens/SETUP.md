# P293 — SETUP

**Phase:** Cross-Function Reward-Index Lens Repair (supervised; not blind; production authority WITHHELD).
**Goal:** repair the P292 residual — internal reward/share/index loci are surfaced (P291) and admitted (P292) and
reach Lens 3, but Lens 3 could not LIFT because reward-index evidence is span-local-invisible or non-standardly named.
P293 makes the reward-index lens cross-function aware + naming-flexible, without relaxing the READY gate.

## Stance
- Research-only · advisory · no production authority · no auto-submission · no final severity · no reportable /
  submission-ready / confirmed outputs · no production/contest source edits · active audit unchanged.
- No answer-key / target hard-coding · no issue-title/body usage · forbidden files byte-identical.

## Active audit
`output` → `audits/size-credit-2024-06-blind/output` (unchanged; salty/etc. read read-only via audit-id paths).

## Allowed edits (this phase)
- `scripts/research/invariant_delta_deriver.py` — Lens-3 cross-function family.
- `config/research_invariant_delta_deriver.json` — broadened term families + lens3 status/pattern enums.
- `scripts/research/completion_evidence_deriver.py` — minimal fill-if-missing of two base dims on a P293 lift
  (the "absolutely necessary" carve-out; scoped to `lens_name == reward_index_cross`).
- `tests/research/test_p293_cross_function_reward_index_lens.py` + this docs dir.

## Kept byte-identical (verified)
`cross_function_value_tracer.py` (the deriver re-resolves callee bodies itself) and
`poc_readiness_evidence_gate.py` (lifts via config `lift_statuses` — no gate edit needed), plus the P273 router and
the reused 0-FP detector classifiers, plus the forbidden 5.

## How to reproduce the remap
`python3 documentation/research/assisted_mode/p293_cross_function_reward_index_lens/remap_driver.py`
(runs p276_corpus_replay → expanded_validation_queue → completion_evidence_deriver → gate over 8 targets).
