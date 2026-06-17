# P289 — SETUP

**Phase:** P289 — Loss/Reward Mechanism-Lens Repair (supervised; targeted but general; production authority WITHHELD).
**Status:** RESEARCH-ONLY · ADVISORY · UN-WIRED · default-off · fail-closed.

## What this phase is
P288 localized the binding constraint to EVIDENCE_DERIVATION (recall/precision generalize; mechanism derivation is
lens-bounded). P289 adds **four general source-backed lenses** to the P284 invariant-delta deriver for the
surfaced-but-unlifted ECG-style families: loss/slash-on-stake coupling · bad-debt/loss contagion · reward-index
initialization · share-transfer reward theft. ECG is the supervised EVALUATION target only — **no ECG-specific
hard-coding, no award text in runtime**.

## Integration (reuses P284/P285 machinery; minimal)
New lens detectors in `invariant_delta_deriver.derive()`'s `found` loop, each emitting a liftable
`invariant_delta_status` (LOSS_ON_STAKE_FOUND · BAD_DEBT_CONTAGION_FOUND · REWARD_INDEX_INIT_FOUND ·
SHARE_TRANSFER_THEFT_FOUND) + `lens_name`/`lens_status`. The statuses are added to
`config/research_invariant_delta_deriver.json` `lift_statuses`/`all_statuses`; the gate (`_id_deviation`) and the
completion-deriver core-dim upgrade both read `lift_statuses` from that config → **they lift automatically, no
gate/control-flow edit**. Existing D4.2/D4.3/D4.4/D4.6/D4.7 detectors are byte-behavior-identical.

## Reproduce
Per audit: `completion_evidence_deriver` (manifest + evidence_packages) → `poc_readiness_evidence_gate`. Supervised
re-map: ECG holdout + kelp (P287) + blackhole claim_many (P286) + a prior corpus sample. Outputs under `outputs/`.

## Standing constraints
Research-only; no production authority/submission/severity/reportable/confirmed; no production/contest source edits;
active audit `size-credit-2024-06-blind` symlink unchanged; no target-specific/award-text in runtime; frozen modules
(P260–P273 + P283 tracer + reused detector platform) + forbidden 5 byte-identical.
