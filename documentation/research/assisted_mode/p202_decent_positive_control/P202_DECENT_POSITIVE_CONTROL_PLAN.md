# P202 — decent positive-control validation (plan)

## Goal
First **two-sided** out-of-sample test of the refined mechanism-level severity gate: does it **preserve genuine
contract-level Highs** (the axis P200/P201 never validated) while still **demoting Medium over-HIGH**? Corpus =
decent-2024-01 (PCS-accepted positive control: 4H/5M, 4 source-reachable contract-Highs incl. theft + permanent-loss).
Offline validation only; gate not wired.

## Contamination handling (central)
Orchestrator is PCS-contaminated → the refined gate is applied by a **fresh cold-start firewall calibration
subagent** (rubric + frozen blind outputs + schema only; no key/PCS/titles/loci). Else result = CONTAMINATED_UPPER_BOUND.
See `CONTAMINATION_MITIGATION.md`.

## Double freeze
FREEZE 1 = blind threat-ceiling raw outputs (14 surfaces). FREEZE 2 = fresh-subagent refined calibration. Both
before the full answer-key read; scoring (orchestrator, answer-aware) only after.

## Sequence
precheck → contamination mitigation → corpus viability (count-only) → source-only 14-surface manifest → blind run
(FREEZE 1) → fresh firewall calibration (FREEZE 2) → controlled answer-key scoring (per-mechanism) → scorecards
(High-preservation + Medium-demotion + secondary) → failure cases → recommendation/decision → integrity + memory.

## Decision space
REFINED_GATE_VALIDATED_TWO_SIDED · REFINED_GATE_PARTIAL · REFINED_GATE_FAILED_FALSE_DEMOTIONS ·
CONTAMINATED_UPPER_BOUND · DATASET_TOO_THIN · INVALID_RUN.

## Guardrails
Read-only/offline; production hashes byte-identical START==END; fresh firewall subagent applies the gate; blind +
calibration frozen before key; mechanism-level scoring; High-preservation + Medium-demotion + secondary measured;
leak-scan; Sonnet; fabrication 0.
