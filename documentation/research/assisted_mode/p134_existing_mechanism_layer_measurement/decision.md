# P134 — Decision

## Decision: **ROUTING_GAP_NOT_DETECTOR_GAP**

The existing mechanism-depth detectors **already catch the P133 visible-but-MISS class** — useful detector
recall **7/8 (88%)**, and **all 3 P133 MISS recovered** (H-01 HIT via units_invariant, H-13 HIT via
connector_position_accounting, H-14 PARTIAL via arithmetic_conservation) — but the recovering outputs largely
**do not reach human review** (units_invariant is report-only; semantic_tvl_completeness is research-only;
connector_position_accounting / arithmetic_conservation escalate only in strict-full-audit). The dominant
remaining work is **routing/surfacing, not detection**. **No new mechanism detector is justified.**

### Why this label (per rubric)
- Not `TRUE_DETECTOR_GAP_FOUND`: only **1/8** is a genuine detector gap (H-03, a logic loop-variable bug that no
  value-computation taxonomy targets — and it is catchable by the existing deep-pass *prompt*, not a new detector).
- Not `BLOCKED_BY_ENVIRONMENT`: all 5 detectors ran read-time; no Slither/import/source block.
- Not `MEASURED_LAYER_RECOVERS_GAP` outright: the layer *detects* the gap, but the catches don't reach review, so
  the operative fix is routing — `ROUTING_GAP_NOT_DETECTOR_GAP` is the sharper, more actionable call.
- `MEASURED_LAYER_PARTIALLY_RECOVERS_GAP` is close, but the residual is overwhelmingly routing (+1 logic bug),
  not missing mechanism coverage — so the routing label is more precise.

## Final response

**What this phase measured** — whether the existing mechanism-depth detectors recover the P133 noya
boost-delta MISS/PARTIAL classes, and the true residual — by running all 5 on noya and scoring against the 8
awarded targets (strict: right-function-only = PARTIAL).

**Existing mechanism layers inspected** — connector_position_accounting (advisory), arithmetic_conservation
(advisory), units_invariant (report-only), semantic_tvl_completeness (research-only), registry_position_lifecycle
(research-only). All read-time; none need Slither.

**Detector run results** — all 5 passed read-time on noya (no environment block). Candidates: CPA 7, AC 9,
units 45, STC 11, RPL 3.

**P133 MISS/PARTIAL recovery** — combined layer: **HIT 4 / PARTIAL 3 / MISS 1** = useful **7/8 (88%)**, strict
4/8 (vs P133 surface 5/8 useful, 2/8 strict). **All 3 P133 MISS recovered** (H-01, H-13 HIT; H-14 PARTIAL);
P133 PARTIAL H-06 **upgraded to HIT** (semantic omission). Bonus: registry_position_lifecycle independently
recovers **H-23 + H-18** (outside the 8).

**Routing finding** — the catches mostly don't reach review: units_invariant (H-01) is report-only;
semantic_tvl_completeness (H-06) is research-only; CPA/AC (H-13/H-19/H-14/H-22/H-15) escalate only in
strict-full-audit. The detection is strong; the surfacing is weak.

**True residual gaps** — (1) **H-03** `NoyaValueOracle._getValue`, a logic loop-variable bug with no static
mechanism taxonomy → route to the existing `deep_pass_value_provenance` prompt (not a new detector);
(2) PARTIAL precision on H-22/H-15/H-14 → deep-pass prompt + advisory surfacing; (3) **routing** (dominant) →
surface advisory/report/research output to review without promoting to submission-ready.

**Decision** — ROUTING_GAP_NOT_DETECTOR_GAP.

**Tests / integrity** — no production code changed; detector runs wrote only audit-local `output/*_audit.json`;
`rank_signal_probe --self-test` OK; full `pytest -q` unchanged (1586 passed / 2 pre-existing snapshot fails / 4
skipped); active audit restored to `quantamm-2024-12-eval`.

**Deliverables** — `documentation/research/assisted_mode/p134_existing_mechanism_layer_measurement/`
(problem_statement, mechanism_infra_map, p133_target_matrix, commands_and_outputs, detector_scorecard,
routing_analysis, residual_gap_analysis, decision .md + metrics.json + runtime_output.txt).

**Next recommended phase (P135)** — a **routing/surfacing** phase (no new detector): surface
connector_position_accounting / arithmetic_conservation / units_invariant / semantic_tvl_completeness output as
**advisory evidence in the standard review package + human_review_queue context** (non-submission-ready), with an
A/B showing the P133 MISS now reach review; and route oracle-multi-hop-loop candidates (H-03 class) through the
existing deep-pass value-provenance prompt. Keep research-only detectors research-only pending the 5-criteria bar.
