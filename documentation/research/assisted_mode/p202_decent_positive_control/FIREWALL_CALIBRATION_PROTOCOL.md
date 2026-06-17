# P202 — firewall calibration protocol

## Why
The orchestrator was PCS-contaminated (transiently exposed to decent High file/mechanism hints), so it cannot author
the answer-key-blind severity calibration without biasing the positive-control test. The calibration must be done by
an agent with **no** such prior.

## Protocol (executed)
A single **fresh, cold-start firewall subagent** was launched (general-purpose, Sonnet). Cold start = no memory of
the orchestrator's PCS exposure or any campaign context. It received in its prompt ONLY:
1. The refined mechanism-level rubric (generic A–F classes + the uniform decision rule; identical to
   `REFINED_SEVERITY_GATE_DESIGN.md`, no decent-specific content).
2. The 5 labels and the 12 evidence dimensions + the output JSON schema.
3. A pointer to the frozen `raw_outputs/decent-*.json` (mechanisms only — NOT the answer key).

Hard prohibitions given to the subagent:
- Read ONLY `raw_outputs/*.json` (+ decent source for verification if needed).
- MUST NOT read any `_sealed_answer_key/`, any `report.md`, `positive_control_screening/`, or memory/MEMORY files.
- No finding lists/titles/severities; grade only from each frozen output's own evidence.

Output: the subagent wrote `OFFLINE_REFINED_CALIBRATION.json` directly (`_meta.calibrated_by =
fresh_firewall_subagent`), graded every mechanism, returned only an aggregate count summary to the orchestrator.

## Result (FREEZE 2 = `90cf2a4f`)
33 mechanisms graded: 8 HIGH_CONFIRMED · 12 MEDIUM_OR_LOWER · 13 NEEDS_HARNESS. 6 surfaces summary HIGH_CONFIRMED
(decent-01/02/03/06/09/12). Calibration JSON leak-scanned: no answer-key tokens.

## Why this makes the run valid (not CONTAMINATED_UPPER_BOUND)
The contamination-sensitive step (severity grading of blind outputs without the key) was performed by an agent that
provably never saw the key, PCS preambles, or the orchestrator's prior. The orchestrator did only:
- **surface sampling** (from source, broad across the 11 required categories — selection-bias bounded by coverage),
- **post-freeze scoring** (answer-aware by definition; prior knowledge does not invalidate answer-aware scoring).
Therefore the calibration is a genuine out-of-sample application and the decision label is a valid validation outcome.

## Residual / honesty
- Surface selection was by the contaminated orchestrator (mitigated by comprehensive coverage, not cherry-picking).
- Mechanism-matching at scoring was by the contaminated orchestrator (answer-aware; recorded with match-quality and
  conservative crediting — see HIGH_PRESERVATION_SCORECARD/FAILURE_CASES, e.g. decent-12 conservatively treated as a
  false/unawarded High rather than an H-04 preservation).
- Process fix for future screening (carried from PCS): screening subagents must emit JSON-only (no free-text
  preamble) so the orchestrator is never exposed in the first place.
