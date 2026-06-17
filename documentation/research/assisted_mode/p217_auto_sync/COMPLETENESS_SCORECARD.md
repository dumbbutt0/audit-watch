# P217 — COMPLETENESS SCORECARD (before P216 → after P217)

21 evidence checklist fields per record (safety defaults excluded). Same scorer
(`sync_hunt_findings.score_record`) applied to the P216 mirror (before) and the P217 mirror (after).

**Aggregate: 57% (144/252) → 90% (226/252).** +33 points; +82 fields populated.

| record | before % | after % | Δ | after unknown | after missing |
|--------|---------|---------|----|---------------|---------------|
| ZETA-01 | 57 | 90 | +33 | 2 | 0 |
| ZETA-02 | 52 | 86 | +34 | 3 | 0 |
| ZETA-03 | 61 | 95 | +34 | 1 | 0 |
| ZETA-04 | 61 | 95 | +34 | 1 | 0 |
| ZETA-05 | 57 | 90 | +33 | 2 | 0 |
| ZETA-06 | 57 | 90 | +33 | 2 | 0 |
| ZETA-07 | 61 | 90 | +29 | 2 | 0 |
| ZETA-08 | 57 | 90 | +33 | 2 | 0 |
| ZETA-09 | 52 | 81 | +29 | 4 | 0 |
| ZETA-10 | 57 | 90 | +33 | 2 | 0 |
| ZETA-11 | 61 | 95 | +34 | 1 | 0 |
| ZETA-12 | 47 | 81 | +34 | 4 | 0 |

## Fields newly populated by P217 (from real artifacts; were unknown/MISSING in P216)
`mechanism` (merged.description) · `root_cause` (merged.ite.intent / L3.notes) · `attacker_model` (register) ·
`exploit_steps` (merged.ice_chain.exploit_path, split) · `function_map` (surface + impact_class) ·
`defense_map` (triage.follow_up_packet / L3 control) · `intent_scope_operator_assumptions` ·
`red_flags` (derived from recorded fields) · richer `evidence_backup` / `source_refs`. `MISSING_EVIDENCE` count
dropped to 0 (the P216 exploit_steps MISSING is now sourced).

## Remaining unknowns (honest gaps — no artifact source; NOT invented)
- `novelty_duplicate` — no novelty assessment exists for P215 (all records).
- `l3_status` for ZETA-02 / ZETA-09 / ZETA-12 — no L3 record (Medium/rejected, not High-ceiling); flagged as
  missing-artifact warnings. (ZETA-09/12 also lack a dry-run-queue entry.)

Safety-default fields are **excluded** from the evidence score (they are guarantees, not evidence).
