# P139 — Noya Measurement

Surface advisories → run wrapper → generate review gate (active=noya, restored to quantamm after).

| Check | Result |
|---|---|
| value-provenance jobs produced | 2 (`SolvencyV2.convertAmountsToValues`, `NoyaValueOracle._getValue`) |
| H-03 target `NoyaValueOracle._getValue` present | ✅ |
| config-setter false triggers (update*) | 0 (excluded after trigger tightening) |
| auto_run_status | pending_manual_execution (both) — honest (no non-interactive runner) |
| prompt_decision | pending (no fabricated decision) |
| advisory_only / submission_ready=false / requires_human_review=true | ✅ all |
| rendered under "Value Provenance Deep-Pass Results — advisory only" | ✅ |
| "requires human review and PoC" disclaimer | ✅ |
| in Validated Findings table | ❌ (correctly excluded) |
| Confirmed findings count | 0 (unchanged) |
| pipeline blocked | no |
| master gate off → output | ran:False (reversible) |

## Trigger tightening (found + fixed during measurement)
First run produced 5 jobs that INCLUDED config-setter loops (`updateDefaultPriceSource`/`updateAssetPriceSource`)
and EXCLUDED the H-03 target — caused by a fixed 40-line body window overshooting into neighboring functions +
accepting any call. Fixed: read the EXACT function span from `coverage_manifest.json` and require a
value-CONVERSION call in the loop region. Re-run: 5 → 2 jobs, config-setters gone, `NoyaValueOracle._getValue`
surfaced. (Same signal-precision lesson as P135's confidence-prioritized caps.)

## Artifacts left audit-local (research)
`audits/noya-2024-04-eval/output/value_provenance_advisory_results.json` + `value_provenance_jobs/*.md` +
`mechanism_advisory_context.json` (from surfacing). noya `review_gate.md` removed; `session.json` +
`human_review_queue.jsonl` restored to pre-P139 state.
