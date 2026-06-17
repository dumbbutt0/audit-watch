# P289 — IMPLEMENTATION_NOTES

## Files changed (allow-list only)
| File | Change |
|---|---|
| `scripts/research/invariant_delta_deriver.py` | 4 new lens functions (`_lens_loss_on_stake`, `_lens_bad_debt_contagion`, `_lens_reward_index_init`, `_lens_share_transfer_theft`) + `_lens_rec`/`_name_or_body` helpers; wired into `derive()`'s `found` loop. |
| `config/research_invariant_delta_deriver.json` | 4 new statuses in `lift_statuses`/`all_statuses` + generic lens signal-term lists + `lens_sameblock_guard_regex`. |
| `tests/research/test_p285*` , `test_p286*` (FROZEN pins) and `test_p287*`, `test_p288*` (live re-check exclusion) | hash-pin cascade: the deriver+config were pinned byte-identical by P285–P288; P289 is authorized to edit them, so the downstream pins are bumped to the new hashes (P285/P286) and the two P289-edited files are excluded from the P287/P288 live-vs-baseline re-check (baseline records preserved truthfully). Precedent: P277/P281/P283. |

## How the lift happens with no gate edit
The gate's `_id_deviation` and the completion-deriver core-dim upgrade both read `lift_statuses` from
`research_invariant_delta_deriver.json`. Adding the 4 lens statuses there makes a LENS_MATCH record liftable through the
existing value/state-class path — **no `poc_readiness_evidence_gate.py` control-flow edit**. Strongest-FOUND ordering and
the existing D4.x detectors are unchanged.

## FP defense (the design that kept severe FP=0)
Each lens requires multi-signal coupling (verb + state-term + per-user/global write + a path term), comment-stripped
bodies, MEDIUM confidence ceiling, and explicit refutation conditions (init-to-current → REFUTE; per-term keyed loss →
REFUTE; both-side checkpoint → REFUTE). Generic Solidity vocabulary only — no ECG names/constants, no award text. The
existing value/state-class + D1 + core-dim gates remain in force. Corpus-wide (7 prior eval audits + ECG + kelp +
blackhole + panoptic): **2 lens matches total, 1 lift (the exact awarded ECG H-04), 0 false READY, severe FP=0.**

## New hashes (recorded for downstream pins)
`invariant_delta_deriver.py` = `cf7de22e7bb29fd7`; `research_invariant_delta_deriver.json` = `39d3cf44736d78e8`.
