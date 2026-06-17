# P139 — Implementation Summary

## Files (additive)
1. **`scripts/run_value_provenance_advisories.py`** (new) — reads `mechanism_advisory_context.json` →
   `deep_pass_recommendations[]`, applies the H-03-class trigger (exact-span value-conversion-loop signal +
   mock/trivial/confirmed/research-only exclusions + caps), builds a neutral queued job under
   `output/value_provenance_jobs/`, writes `output/value_provenance_advisory_results.json`. SCAFFOLD:
   `auto_run_status=pending_manual_execution` (llm_available()=False); never fabricates a decision; fail-open
   (try/except → never raises into the pipeline); optional gated advisory-only queue append.
2. **`scripts/generate_review_gate.py`** (+`_value_provenance_section()`): renders a "### Value Provenance
   Deep-Pass Results — advisory only" subsection from the results JSON, with the advisory-only +
   requires-human-review-and-PoC disclaimer. Robust to missing/malformed/empty. Results NEVER added to
   `findings` → confirmed count + Validated Findings unchanged.
3. **`config/agent_policy.json`** (+`value_provenance_auto_run` block): master flag + mode (off/eval_only/
   review_only, default review_only) + caps + allowed_prompts + attach/render/research-only toggles.
4. **`run_pipeline.sh`**: `run_value_provenance_advisories.py 2>/dev/null || true` after
   `surface_mechanism_advisories.py`, before `generate_review_gate.py`, in `full` + `review-gate` (non-blocking).
5. **`tests/mechanism_advisory/test_value_provenance_auto_advisory.py`** (new, 14 tests).

## No change to
detector detection logic, severity, submission, gate pass/fail. Research-only stays research-only. No
non-interactive LLM runner invented (api-free → scaffold). The only `_gate`-named edit is the review-gate
render-only subsection.

## Behavior (noya, default)
2 value-provenance jobs (`SolvencyV2.convertAmountsToValues`, `NoyaValueOracle._getValue`), both
pending_manual_execution / advisory_only; rendered in review_gate; confirmed count 0 unchanged; not in Validated
Findings; master gate off → ran:False.
