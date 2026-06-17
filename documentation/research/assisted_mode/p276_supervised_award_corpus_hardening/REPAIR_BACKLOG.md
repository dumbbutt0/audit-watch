# P276 — REPAIR_BACKLOG (general, source-derived; no target-specific hard-coding)

This phase **proposes** repairs; it edits **no** module. Machine-readable: `outputs/repair_backlog.json`. Every signal
is a structural source pattern that catches a FAMILY of awards — **no contest names / award titles / award text**.

| id | failed_stage | n | knob | priority | general source-derived signal |
|---|---|---|---|---|---|
| R1 | COVERAGE_CLASS_GAP | 41 | coverage-class | **1** | derive class signals from generated-mechanism BODY (source_backed_trigger / affected_state / attacker_action), not just locus name tokens; widen KEEP when a locus spans multiple plausible classes |
| R2 | RECALL_GAP | 30 | recall | 2 | add sweep clauses for under-covered primitives (authorization-modifier presence, external-call-before-state-write, signature/nonce checks); raise top-N / checkpoint breadth |
| R5 | COMPLETION_GAP | 57 | PoC-scaffold | 2 | generalize the P271 lending scaffold to access/order/share/DoS so surfaced+routed mechanisms convert to exact at higher throughput (gate stays strict) |
| R3 | MANIFEST_GAP | 16 | manifest | 3 | enumerate inherited/library/abstract functions reachable from in-scope contracts + integration entrypoints (oracle adapters, hooks) |
| R4 | COVERAGE_CLASS_GAP (oracle/external) | 6 | coverage-class | 4 | add oracle markers (latestRoundData/getReserves/slot0/twap staleness) + external markers (hook/bridge/adapter/wrap) to recall templates + class signals |
| R6 | DUPLICATE_OR_REPORT_ONLY_AMBIGUITY | 105 | eval-data | 5 | backfill affected-contract/function on title-only award keys (measurement enablement, not a pipeline repair) |

## Priority rationale
- **R1 (routing) is #1:** the largest *actionable upstream* leak is surfaced→routed (96→57). Awards surface but their
  class isn't routed because class signals come from names/titles, not mechanism bodies. Fixing this is low-FP-risk
  (still advisory) and high-lift.
- **R2 (recall) + R5 (PoC scaffold) are #2:** recall depth (30 in-manifest-but-unsurfaced) and converting the 57
  already-surfaced mechanisms to exact (the completion tail) are the next biggest gains.
- **R3/R4 (manifest + weak classes):** structural enumeration + oracle/external markers close the smaller, class-
  specific gaps (ORACLE 0/4, EXTERNAL 1/2).
- **R6:** data enrichment so the 105 title-only awards become measurable.

**Discipline:** all repairs land in a separate, explicitly-approved phase. Frozen modules stay byte-identical until
then. No repair references a specific contest/finding.
