# P202 — contamination mitigation

## The contamination
During PCS (positive-control screening), the firewall screening subagents over-returned: their free-text reasoning
preambles named some decent files/High-mechanism hints before the JSON. The **orchestrator was transiently exposed**
to those preambles. Only the JSON tallies were persisted (no titles/loci). Consequence: the orchestrator now holds
**partial prior knowledge of decent's High mechanisms/loci** — so the orchestrator cannot be trusted to author the
"answer-key-blind" severity calibration.

## Which step is contamination-sensitive?
The contamination-sensitive step is the **severity calibration** (grading blind outputs' mechanisms HIGH/Medium/
Harness without the answer key). If the grader already knows which mechanisms are awarded Highs, "confirming" them is
not a blind test. Other steps are **not** sensitive:
- **Blind threat-ceiling run** — subagents get only source; their verdicts don't depend on the orchestrator.
- **Surface sampling** — done from source only; selection-bias risk handled by **comprehensive coverage** of all 11
  required categories (not cherry-picking known-High loci).
- **Post-freeze scoring** — legitimately answer-aware by definition (reads the report after both freezes); the
  orchestrator's prior knowledge does not invalidate scoring, which always uses the answer key.

## Mitigation (mandatory)
The refined-gate calibration is authored by a **fresh, cold-start firewall calibration subagent** that receives ONLY:
- the frozen blind `raw_outputs/` (mechanisms only — NOT the answer key),
- the refined mechanism-level rubric (generic A–F class rules + uniform decision rule; not decent-specific),
- the output schema (per-mechanism label + 12 evidence dimensions).

It is explicitly forbidden from reading `_sealed_answer_key/`, and receives **no** answer-key titles, **no** PCS
preambles/hints, **no** decent finding details beyond count-only viability (4H/5M). A cold subagent has **no memory**
of the orchestrator's PCS exposure → uncontaminated by construction. Its output (`OFFLINE_REFINED_CALIBRATION.json`)
is frozen (FREEZE 2) before any full answer-key read.

## Residual risks & how they are bounded
- **Surface-selection bias** (orchestrator picks the sample): bounded by registering all 11 required categories
  across 14 surfaces (broad, not targeted at known-High loci).
- **Mechanism-matching during scoring** (orchestrator maps blind mechanisms → awarded findings, answer-aware):
  recorded with match-quality (strong/partial/loose/miss) + cited evidence, conservatively, as in P200/P201.
- **Rubric wording**: the rubric handed to the subagent is the generic P201 design (`REFINED_SEVERITY_GATE_DESIGN`),
  containing no decent-specific guidance.

## Decision rule
If the fresh firewall subagent authored the calibration as specified → result is a **valid out-of-sample
validation** (VALIDATED_TWO_SIDED / PARTIAL / FAILED_FALSE_DEMOTIONS as the data shows). If the orchestrator had
applied the gate, or PCS hints leaked into calibration, or no fresh subagent was used → the result would be labeled
**CONTAMINATED_UPPER_BOUND**. This phase uses the fresh subagent; the calibration provenance is recorded in
`FIREWALL_CALIBRATION_PROTOCOL.md` and `integrity_checks.md`.
