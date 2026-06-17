# Final Recommendations

## Done this pass

1. **8 refinement docs** (this folder) — the canonical reference for how every stage interacts.
2. **Workspace layout + migration** — every audit gains `contracts/`, `contracts/_sources/`,
   `notes/`, `findings/{raw,validated}/`, `status/`; substrate (`output/`, `data/`) untouched;
   migration is dry-run-gated and additive.
3. **Contract intake + association** — `intake_contracts.py` (no-overwrite, `--replace-primary`)
   + `generate_contract_context.py` (deterministic `notes/contract_context.md`).
4. **API no-silent-fail, now wired end-to-end (zero-API hardening pass)** — the
   `scripts/llm_runtime.py` guard is now in **every** API script via `require_llm`, with a new
   `optional_llm` skip-and-continue for the three default-path enhancers (cross-agent 2.5,
   compound 3, multi-pass 3.5). `run_pipeline.sh` has an honest pre-flight + `HAS_KEY` detection;
   keyless Step 4 routes to the `/triage` skill, then `./run_pipeline.sh review-gate` resumes.
   Regression guard `scripts/check_no_bare_anthropic.py` blocks any new bare `anthropic.Anthropic()`.
   **A keyless `full` run now completes through the pause without spending credits.** Details:
   `api_dependency_audit.md` → "Update — guard now wired everywhere".
5. **Flagship skill-in-session conversion** — `triage` (`triage_prepare.py` → `/triage` →
   `triage_write.py`), the reusable pattern for the rest.
6. **No-silent-clearance gate** — disproof requirement in 3 prompts + enforced in
   `validate_agent_output.py`; `attacker_mindset` hypotheses kept out of the findings corpus;
   `supply_chain_check` routed to a build-security annex.
7. **Dedup fix** — five-axis merge + different-file guard in `report_generator.py`, regression
   fixture enforced.

## Staged next (in priority order)

1. **Convert the remaining API scripts to true skill-in-session** using the documented recipe.
   (They are now all guarded — skip-or-stop cleanly with no key — but only `triage` reasons
   in-session; the rest still need a key to add their value.) Highest value: `multi_pass_confirm`,
   `synthesize_compound_findings`, `cross_agent_connector`, the Stage-5 specialist-review quartet
   (`model_exploitability`, `estimate_duplicate_risk`, `calibrate_severity`, `judge_simulate`).
2. **Deep-analysis intake conversion** (`extract_invariants`, `map_interactions`, `deep_trace`,
   `multi_tx_trace`, `backward_trace`) — biggest single API consumer; partly deterministic
   (call-graph/taint from `static.json`) + skill for ranking.
3. **Coverage-enforcement gate** — fail Stage 6 if a specialist ignored a high-suspicion
   invariant in its category (closes the Beanstalk "didn't look" silent misses).
4. **Economic-invariant / peg specialist agent** — the worst-covered Beanstalk category (17%).
5. **Reseed-completeness + reward-lifecycle skills** — convert the concentrated Beanstalk
   PARTIAL clusters into HITs.

## API dependencies that remain (after this pass)

All API scripts still *function* with a key and are now uniformly guarded. The **default `full`
path completes with no key**: the 2.5 / 3 / 3.5 enhancers skip-and-continue (deterministic merge
carries detection) and triage runs via the `/triage` skill. The stages without a skill yet
(deep-analysis 0a–0f, the Stage-5 reasoning quartet, PoC generation, FP autopsies) are *required*
stages: invoked without a key they **stop with an actionable message** (export a key or await the
skill conversion) — never a crash, never a silent spend. `solodit_scraper.py` (embeddings) and
`smt_check_invariants.py` (z3 framing) stay API-optional. Note: a key in `.env` is auto-loaded, so
to force the zero-API path for testing, run with `ANTHROPIC_API_KEY=`.

## How to run the refined pipeline

```
# 1. Intake — associate source with the active audit
python scripts/audit_manager.py new <id>        # or switch <id>
python scripts/intake_contracts.py <downloaded-dir> [<more-dirs>]   # --replace-primary to redo
python scripts/generate_contract_context.py      # writes notes/contract_context.md

# 2. Pre-analysis (Steps 0.5→1.5)
./run_pipeline.sh analyze <primary-contract-dir> # prints API/skill pre-flight first

# 3. Specialists (Step 2)
/ite-audit

# 4. Synthesis → triage → PAUSE (Steps 2.5→4)
./run_pipeline.sh full          # zero-API: 2.5/3/3.5 skip; pauses at triage with instructions:
#   → run the /triage skill in Claude Code  → python scripts/triage_write.py
#   → ./run_pipeline.sh review-gate   (builds PoC queue + human review + review_gate.md)

# 5. Review the human table, then PoC selected IDs
#    read audits/<id>/findings/validated/ and output/review_gate.md
./run_pipeline.sh poc <finding-id>
```

## What to review before the next live audit

1. **The migration dry-run report** (`migration_dryrun.md`) — confirm no substrate touched.
2. **The clearance gate** — eyeball that `protocol_context`/`semantic_guard` now emit
   `unresolved_invariant` rather than clearing; this was the costliest Beanstalk failure.
3. **The dedup fixture result** — distinct same-file findings stay separate.
4. **`notes/contract_context.md` on the real target** — is the navigation index rich enough to
   focus the specialists? This is the new front-door for context quality.
5. **Decide the API posture** — either provision a key for the un-converted steps, or wait for
   the staged skill conversions before relying on `full`/`submit` end-to-end.
