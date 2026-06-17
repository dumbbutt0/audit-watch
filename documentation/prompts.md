# Prompts

Prompts are instruction templates in `prompts/`. They differ from agents: **agents** are complete task specifications that Claude Code runs as Tasks (they include their own goals, input discovery, and output instructions). **Prompts** are instruction templates loaded into agent context to provide specific reasoning frameworks, output formats, or decision procedures.

Agents reference prompts with lines like: `prompts/human_auditor_methodology.md — read this as your base reasoning framework.`

---

## Prompt Reference

### triager.md

**File:** `prompts/triager.md`
**Pipeline stage:** Step 4 — used by `scripts/triage_findings.py`
**Inputs:** All findings from `output/merged_findings.json`
**Produces:** Per-finding triage decisions: submit / poc_required / downgraded / merged / rejected

The triage agent system prompt. Instructs the model to evaluate 10 dimensions (attacker reachability, permission, precondition realism, asset at risk, impact directness, scope, duplicate risk, severity match, missing proof, disposition). Includes hard rejection rules for admin-only attacks and victim-allowance preconditions. Used when calling Claude API for nuanced triage decisions after the local pre-gates have run.

---

### triager_code4rena.md

**File:** `prompts/triager_code4rena.md`
**Pipeline stage:** Step 4 — Code4rena specific triage variant
**Inputs:** Same as triager.md
**Produces:** Same structure as triager.md, with Code4rena-specific severity thresholds

Code4rena variant of the triage prompt. Applies contest-specific severity bars (Code4rena Medium requires direct loss; informational/gas findings are typically out of scope for severity rewards).

---

### submission_writer.md

**File:** `prompts/submission_writer.md`
**Pipeline stage:** Step 4 / final submission polish
**Inputs:** Single finding JSON + ICE block + PoC evidence
**Produces:** Contest-ready finding report in standard format

Includes a mandatory 8-question Report Gate that must be answered before writing the report. Specifies the required submission format: title (vulnerability classification + concrete impact), description with Brief/Intro + Vulnerability Details + Impact Details + References sub-sections, Proof of Concept as a separate top-level section. Documents what NOT to include: Severity Justification, Quality Checklist, internal pipeline scores.

---

### poc_planner.md

**File:** `prompts/poc_planner.md`
**Pipeline stage:** Step 6 — used by `scripts/generate_poc_plan.py`
**Inputs:** Finding JSON, repository profile, source code snippet, nearby existing test files
**Produces:** `poc_plan.json` — a structured PoC strategy (approach, setup, attack steps, assertions)

Instructs the model to choose the correct PoC approach (pure_arithmetic / unit_integration / mock_contract / state_machine) and produce a `poc_plan.schema.json`-conforming JSON. Returns ONLY valid JSON — no commentary outside the JSON. Contains planning rules for each approach type.

---

### poc_writer.md

**File:** `prompts/poc_writer.md`
**Pipeline stage:** Step 6 — used by `scripts/generate_poc_test.py`
**Inputs:** Finding JSON, source locations, relevant code snippets, repo profile, nearby existing tests
**Produces:** Test file code (Rust/Solidity/TypeScript depending on framework)

Instructs the model to write minimal, reproducible local tests using the repository's existing test framework. Hard rules: no broadcast, no PRIVATE_KEY, no live network references, no `rm -rf`. Use existing fixtures and helpers.

---

### poc_reviewer.md

**File:** `prompts/poc_reviewer.md`
**Pipeline stage:** Step 6 — used by `scripts/run_poc_tests.py` to interpret results
**Inputs:** Finding JSON, PoC plan, test code, stdout/stderr output, exit code
**Produces:** Status decision: proved / failed / inconclusive / needs_manual_work / compile_error

Decision criteria for "proved": assertion fired that directly demonstrates the bug claim, OR output explicitly prints a value proving wrong behavior. "Inconclusive" when the test runs but the assertion is structurally wrong (does not test the claim).

---

### poc_quality_checklist.md

**File:** `prompts/poc_quality_checklist.md`
**Pipeline stage:** Step 7 — used by `scripts/run_quality_checklist.py`
**Inputs:** Finding JSON, PoC result from `data/runtime_poc/results.jsonl`
**Produces:** 7-question checklist verdict per finding

The 7 questions: (1) Level 2 proved? (2) Level 3 proved? (3) Direct loss? (4) Permissionless? (5) Victim condition realistic? (6) Likely duplicate? (7) One-sentence impact? A finding that cannot answer ✅ or ⚠️ on questions 1–3 should not be submitted as High/Critical.

---

### runtime_poc_executor.md

**File:** `prompts/runtime_poc_executor.md`
**Pipeline stage:** Step 6 — used by `agents/runtime_poc_agent.md`
**Inputs:** Finding JSON, existing harness PoC, repository structure
**Produces:** Upgraded PoC test code at the highest achievable proof level (0–4)

Instructs the model to prefer calling real functions over copying logic, prefer public entrypoints over internal helpers, and use existing test fixtures. Proof levels: 0 (static reasoning only) → 1 (isolated harness) → 2 (real buggy function called) → 3 (real public entrypoint) → 4 (full end-to-end).

---

### impact_chain_escalation.md

**File:** `prompts/impact_chain_escalation.md`
**Pipeline stage:** Step 3.4 (ICE framework) — all agents read this as mandatory context
**Inputs:** Finding, contract source, existing ice block
**Produces:** Enriched ice block with confirmed consumer paths

The core rule: Never stop at a vulnerable state change. Every finding must trace: root cause → corrupted state → protocol consumer → real protocol action → proven impact. Includes 15-stage framework, PoC levels 1–5, severity ceiling assignment rules, and consumer search methodology. This prompt takes precedence over `human_auditor_methodology.md` on severity-assignment rules.

---

### human_auditor_methodology.md

**File:** `prompts/human_auditor_methodology.md`
**Pipeline stage:** Step 2 — read by all specialist agents as base reasoning framework
**Inputs:** N/A (framework document, not data-driven)
**Produces:** Guides agent reasoning approach

Codifies the Hadex methodology: attacker-first thinking, ITE decomposition, assumption counting, multi-hop chain tracing, and human escalation triggers. All specialist agents read this before any pattern-matching. The document describes principles articulated by Jason Hadex (CISO of Ubisoft, founder of Arcanum).

---

### severity_calibrator.md

**File:** `prompts/severity_calibrator.md`
**Pipeline stage:** Step 5 — used by `scripts/calibrate_severity.py`
**Inputs:** Finding JSON, triage record, exploitability model, judge simulation, runtime PoC status, historical severity rules
**Produces:** Calibrated severity label and justification

9 calibration rules applied in order: admin-only → cap at Medium; temporary/reversible impact → cap at Medium; bounded DoS → cap at Medium; oracle-only with no bad debt path → cap at Medium; victim allowance not standard → downgrade one level; harness-only PoC → don't claim High; judge sim predicted downgrade → follow it; PoC proved at lower level → cap at that level's ceiling; compound claim → require confirmed ICE chain.

---

### judge_simulator.md

**File:** `prompts/judge_simulator.md`
**Pipeline stage:** Step 5 — used by `scripts/judge_simulate.py`
**Inputs:** Full finding JSON
**Produces:** `judge_simulation.schema.json` output — predicted outcome, severity, confidence, objections, rewrite suggestions

Applies 5 judge personas: strict contest judge, protocol sponsor, duplicate hunter, severity downgrade judge, practical exploit skeptic. Output includes `persona_verdicts` dict and `final_submit_recommendation` (submit / revise / poc_first / drop).

---

### exploitability_modeler.md

**File:** `prompts/exploitability_modeler.md`
**Pipeline stage:** Step 5 — used by `scripts/model_exploitability.py`
**Inputs:** Finding JSON, triage record
**Produces:** `exploitability.schema.json` output — attacker model, control surface, execution sequence, profit_or_damage, blockers, exploitability_score (1–5)

8-point exploit checklist: (1) permissionless entrypoint? (2) attacker controls inputs? (3) preconditions satisfiable permissionlessly? (4) profit or measurable harm? (5) auth blocker? (6) atomicity rollback? (7) realistic victim? (8) admin-only? Hard rules: no assumed permissions, no assumed victim allowances, no assumed admin compromise unless proved.

---

### duplicate_risk.md

**File:** `prompts/duplicate_risk.md`
**Pipeline stage:** Step 5 — used by `scripts/estimate_duplicate_risk.py`
**Inputs:** Full finding batch
**Produces:** `duplicate_risk.schema.json` output per finding — risk level (low/medium/high), internal and external duplicates, overlap reason, recommended action

Key distinction: findings are only duplicates if they share BOTH same root cause AND same fix. They are not duplicates for sharing impact category, title, or location alone.

---

### deep_trace.md

**File:** `prompts/deep_trace.md`
**Pipeline stage:** Step 0c — used by `scripts/deep_trace.py`
**Inputs:** One high-suspicion invariant, one dangerous interaction chain, relevant source excerpts
**Produces:** Hop-by-hop trace verdict (confirmed violation / no violation / inconclusive)

Structured 5-step trace: (1) entry conditions, (2) hop-by-hop execution, (3) invariant check at each hop, (4) trust boundary analysis, (5) exploit possibility assessment.

---

### interaction_mapper.md

**File:** `prompts/interaction_mapper.md`
**Pipeline stage:** Step 0b — used by `scripts/map_interactions.py`
**Inputs:** Contract source, `output/static.json`
**Produces:** Call graph + interaction chains + trust boundary crossings conforming to `schemas/call_graph.schema.json`

Builds 3 structures: call graph (every external call edge), interaction chains (multi-hop paths up to 7 hops), trust boundary crossings (every point execution enters untrusted context).

---

### invariant_extractor.md

**File:** `prompts/invariant_extractor.md`
**Pipeline stage:** Step 0a — used by `scripts/extract_invariants.py`
**Inputs:** Contract source, `output/static.json`
**Produces:** Array of invariants conforming to `schemas/invariants.schema.json`

Extracts invariants in 6 categories: ACCOUNTING, SOLVENCY, STATE_MACHINE, ACCESS, ARITHMETIC, CROSS_CONTRACT. Each invariant includes a suspicion_score (1–5) where 5 = complex multi-contract logic likely missed by previous audits.
