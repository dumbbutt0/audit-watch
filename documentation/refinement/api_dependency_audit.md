# API Dependency Audit

24 of 76 scripts call the Anthropic API (`claude-sonnet-4-6`) as a **separate** network call —
separate spend, and a hard failure when no key is present (this halted the Beanstalk eval:
`synthesize_compound_findings.py`, `triage_findings.py`, `multi_pass_confirm.py` all raised
`TypeError: Could not resolve authentication method`).

**Strategy (user decision): skill-in-session.** The reasoning these scripts delegate to a
sonnet call can instead be done by Claude Code *in this session* — using the normal
subscription, no API key, no extra credits. The conversion recipe:

> **Recipe:** deterministic **pre-processor** assembles a context bundle on disk → a Claude Code
> **skill** reasons over the bundle in-session and emits structured output → a deterministic
> **writer** validates that output against the schema and writes the substrate artifact.

The first refinement pass converted **triage** as the flagship and built the no-silent-fail guard
`scripts/llm_runtime.py` — **but only wired it into 2 scripts** (`triage_findings.py`,
`multi_pass_confirm.py`); the other ~20 still constructed `anthropic.Anthropic()` directly and
crashed cryptically with no key. A follow-up pass (see "Update — guard now wired everywhere" below)
finished the job: **every** API script now acquires its client through the guard, enforced by a
regression check.

## Disposition table

Dispositions: **SKILL** = convert to skill-in-session · **DET** = replaceable with deterministic
logic (no LLM) · **KEEP-OPT** = leave API-backed but optional + gated.

| Script | Stage | What the API call produces | Disposition |
|---|---|---|---|
| `triage_findings.py` | 4 triage | submit/poc/downgrade/reject bucketing + per-finding markdown | **SKILL (done this pass)** |
| `multi_pass_confirm.py` | 3.5 | 3–5 independent re-confirmations of High/Critical | SKILL |
| `synthesize_compound_findings.py` | 3 | COMP-pattern compound findings | SKILL |
| `cross_agent_connector.py` | 2.5 | cross-agent severity-escalation synthesis | SKILL |
| `calibrate_severity.py` | 5 | most-likely severity pick | SKILL |
| `estimate_duplicate_risk.py` | 5 | duplicate-risk score vs other findings | SKILL (KB part DET) |
| `model_exploitability.py` | 5 | exploit-feasibility model | SKILL |
| `judge_simulate.py` | 5 | 5 adversarial judge personas | SKILL |
| `extract_invariants.py` | 0a | protocol invariants from source | SKILL |
| `map_interactions.py` | 0b | function-interaction graph + dangerous chains | DET (call-graph from AST) + SKILL for ranking |
| `deep_trace.py` | 0c | invariant×interaction threat threads | SKILL |
| `backward_trace.py` | 0c-bis | sink→source reverse reachability | DET (taint from `static.json`) + SKILL |
| `multi_tx_trace.py` | 0c | multi-tx state-machine vulns | SKILL |
| `escalate_threads.py` | synth | promising-thread → finding | SKILL |
| `generate_poc_plan.py` | 5 | PoC test plan | SKILL |
| `generate_poc_test.py` | 5 | PoC test code + repair loop | SKILL |
| `run_integrated_poc.py` | 6 | upgrade harness PoC to real protocol | SKILL |
| `reference_diff.py` | gate | target-vs-reference divergences | SKILL (or KEEP-OPT) |
| `smt_check_invariants.py` | 0e | SMT falsification of arithmetic invariants | KEEP-OPT (z3 is deterministic; LLM only frames) |
| `generate_fuzzing_harness.py` | 0d | Echidna harness from invariants | SKILL |
| `record_fp_autopsy.py` | learning | FP hypothesis extraction | DET (template) + SKILL optional |
| `bulk_fp_autopsy.py` | learning | batch FP pattern rules | SKILL |
| `solodit_scraper.py` | KB | embed + index Solodit findings | KEEP-OPT (embeddings API; offline-cacheable) |
| `dashboard.py` | status | (no LLM in hot path) HTTP server | DET (already) |

## The no-silent-fail guard (`scripts/llm_runtime.py`, NEW)

Every API script imports `require_llm()` / `llm_available()`. Behavior:

- If a key is present → returns a configured client (unchanged behavior).
- If no key → raises a single actionable message naming the **skill-in-session equivalent**
  and the bundle path to use, instead of a deep SDK stack trace. Example:
  `No ANTHROPIC_API_KEY. Run the /triage skill instead (bundle in data/triage/_bundles/).`
- `run_pipeline.sh` calls a pre-flight that prints, before any step, which upcoming steps need
  a key and which have a skill fallback — so a long run never dies halfway.

## Flagship conversion — triage (done this pass)

- `scripts/triage_prepare.py` (DET): reads `merged_findings.json` + gate/dupe results, slices
  the relevant raw source, writes one bundle per finding to `data/triage/_bundles/`.
- `/triage` skill: reasons over the bundles in-session (ICE re-derivation, bucket decision,
  follow-up packet) per `zero_trust_triage_policy.md`.
- `scripts/triage_write.py` (DET): validates the skill's decisions and writes the canonical
  `data/triage/{submit,poc_required,downgraded,merged,rejected}.jsonl` + `<id>.md`.

`triage_findings.py` remains as the API path (now guarded); the skill path is the
credit-free default.

## Update — guard now wired into EVERY API script (zero-API hardening pass)

The earlier text above claimed the guard was on "every API script"; it was not. This pass made it
true and added a graceful default path so a keyless `run_pipeline.sh full` completes end-to-end.

**What changed:**
- **All ~22 API scripts now acquire their client via `scripts/llm_runtime.py`** — never a bare
  `anthropic.Anthropic()`. Required stages use `require_llm(skill=…)` (exits with an actionable
  "export a key or run the skill" message — no cryptic `TypeError`, no surprise spend).
- **`optional_llm(skill)` added** to `llm_runtime.py`: returns a client if a key exists, else prints
  a one-line skip notice and returns `None`. The three default-`full`-path enhancers use it and
  **skip-and-continue** with no key:
  - `cross_agent_connector.py` (2.5) — skips the holistic LLM pass.
  - `synthesize_compound_findings.py` (3) — writes an empty compound set.
  - `multi_pass_confirm.py` (3.5) — writes a `skipped:true` marker; High/Critical keep pre-confirm severity.
  `report_generator.py` (deterministic merge) still produces `merged_findings.json`, so detection
  survives a no-key run.
- **Step 4 triage is now zero-API by default.** With no key, `run_pipeline.sh full` runs
  `triage_prepare.py` (deterministic) and PAUSES with instructions: run the `/triage` skill
  in-session → `python scripts/triage_write.py` → `./run_pipeline.sh review-gate` (a new resume
  subcommand that builds the PoC queue + human-review queue + `review_gate.md`).
- **`run_pipeline.sh` preflight is honest** — it prints the per-stage key/skill/skip plan (no longer
  swallowed with `2>/dev/null || true`) and sets a `HAS_KEY` flag via `llm_runtime.py --have-key`.
- **Regression guard:** `scripts/check_no_bare_anthropic.py` fails CI if any script under
  `scripts/`+`tools/` constructs `anthropic.Anthropic(` directly. Allowlist (with documented
  reasons): `llm_runtime.py` (the guard itself), `solodit_scraper.py` (one-time KB build; already
  key-guarded + lazy import), `dashboard.py` (HTTP server; returns a clean no-key JSON response and
  must not `SystemExit`).

**Verified keyless** (with `ANTHROPIC_API_KEY=`): preflight reports ABSENT with correct per-stage
mapping; `optional_llm` → `None` + skip notice; `require_llm` → `SystemExit` with guidance; the guard
passes; `py_compile` + `bash -n` clean. No API call was made during verification (clients were only
constructed, never invoked), so no credits were spent.

**Still API-backed (no in-session skill yet) — guarded, so they stop with guidance, never silently:**
Step-5 reasoning (`judge_simulate`, `calibrate_severity`, `estimate_duplicate_risk`,
`model_exploitability`, `reference_diff`), PoC generation (`generate_poc_plan`, `generate_poc_test`,
`run_integrated_poc`), and FP autopsies (`record_fp_autopsy`, `bulk_fp_autopsy`). These are off the
`analyze→/ite-audit→full→review_gate` path; converting them is P1/P2 — see `final_recommendations.md`.

## Update — api-free switch + deep-analysis converted (P0)

The **eval-critical path is now fully API-free.** Changes:

- **`config/runtime_policy.json` `{ "api_free": true }`** — `llm_runtime.api_free_mode()` honors it;
  `llm_available()` returns False (so `--have-key` exits 1, every stage routes to its skill) even with
  a key present. `require_llm()`/`optional_llm()` both respect it. `AUDIT_WATCH_API_FREE=0` overrides.
  `ANTHROPIC_API_KEY` is also commented out in `.env`.
- **Step 0 deep analysis converted** to the triplet: `scripts/deep_analysis_prepare.py` →
  `/deep-analysis` skill (reuses `prompts/{invariant_extractor,interaction_mapper,deep_trace,
  impact_chain_escalation}.md` and writes the same canonical artifacts) → `scripts/deep_analysis_write.py`
  (validates, never silent). `run_pipeline.sh analyze` now prepares + PAUSES; `analyze-resume` validates
  and finishes Steps 0.25→1.5. `SKILL_MAP["deep_analysis"].skill = "/deep-analysis"`.
- **Guard:** `scripts/check_api_free.py` fails if any critical-path stage would hard-stop. A
  `PreToolUse(Bash)` hook (`scripts/hooks/block_api_scripts.py`) blocks direct invocation of the
  deprecated API-only scripts in api-free mode and names the skill route. A `Stop` hook
  (`next_skill_reminder.py`) + the extended SessionStart banner surface the next pending `/skill`.
- See `api_free_pipeline.md` for the end-to-end flow and stage→route map.
