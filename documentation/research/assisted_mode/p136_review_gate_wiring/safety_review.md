# P136 — Safety Review (extra constraints 1–9)

| # | Constraint | Result |
|---|---|---|
| 1 | Every new `run_pipeline.sh` command non-blocking with `|| true` | ✅ units audit `2>/dev/null || true`; both surfacing calls `2>/dev/null || true` |
| 2 | No research-only detectors in the production advisory battery | ✅ only `units_invariant_audit` added (report-only); semantic_tvl / registry_position_lifecycle NOT added |
| 3 | No change to confirmed counts / Validated Findings / severity / gates / submission | ✅ advisories never enter `findings`; count = `len(findings)` unchanged; no severity/gate/submission code touched |
| 4 | review_gate advisory section visually separate + titled "NOT confirmed" | ✅ `## Advisory Context — NOT confirmed (mechanism detectors)` after a `---`, after Finding Details |
| 5 | Every advisory row carries advisory_only/submission_ready=false semantics | ✅ bold disclaimer covers all rows; source JSON entries also carry `advisory_only:true`/`submission_ready:false` |
| 6 | Missing/malformed/disabled/empty context → continue, no section, no error | ✅ tested: `test_missing_context_no_section_no_error`, `test_malformed_context_no_error`, `test_disabled_context_no_section`, `test_empty_context_no_section` |
| 7 | Tests prove advisories not in Validated Findings | ✅ `test_advisory_not_in_validated_findings` + noya check |
| 8 | `bash -n run_pipeline.sh` + focused review-gate tests before full suite | ✅ bash -n OK; focused 21 passed before the full run |
| 9 | Restore active audit to quantamm after noya measurement | ✅ active-audit pointer restored to `quantamm-2024-12-eval` |

## Additional safety
- Surfacing/units cannot block the coverage / min-confirm / bridge-thread gates (they run as `|| true`; gates
  are unchanged and still execute and can still block independently).
- Master gate off → 0 surfaced → no advisory section (reversible, verified).
- Nothing auto-submitted; no platform path touched; P130–P135 behavior preserved (only additive code).
- Known benign audit-local artifact: noya `session.json` `active_step` set to 4 by the review-gate generation
  (non-active eval audit, no pre-existing backup); noya `review_gate.md` removed; `mechanism_advisory_context.json`
  left reflecting the real ON surfacing. Production active audit (quantamm) untouched.
