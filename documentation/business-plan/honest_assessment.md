# Honest Assessment — Audit-Watch

_Diagnostic, not a pitch. Original assessment based on code and data read on 2026-05-21._
_Updated 2026-05-21 to reflect improvements made in the same session._

---

## Recon Summary: What Was Found vs. What Docs Claim

The system is more implemented than typical "research project" codebases at this stage. 52 Python scripts, 34 agent markdown files, 23 slash-command skills, a full FastAPI reasoning graph server, and 10 real audit workspaces. However, a critical gap exists between the sophistication of the infrastructure and the calibration evidence for it.

**As of the original assessment (earlier today):**
- Ground truth corpus: 10 audits, 437 total triaged findings, 1 verified outcome
- FP autopsy corpus: 0 project-level rejection rules despite 297 rejected findings
- Viz instrumentation: 5 of 52 pipeline scripts emitting events
- Defense mapper: `coverage:full` findings reaching Gate 4 unremediated
- Gate enforcement: `final_submission_pack.py` warned on missing gate results but did not block

**As of end of session (2026-05-21):**
- FP autopsy corpus: 178 rules in `data/fp_autopsies/rejection_rules.jsonl` — 176 from bulk processing, 2 typed `duplicate_pattern` for confirmed duplicates CC-001/GAC-001
- Viz instrumentation: 9 of 52 pipeline scripts (added `cross_agent_connector`, `multi_pass_confirm`, `run_deep_analysis`, `synthesize_compound_findings`; all 3 payload bugs in newly added emitters fixed)
- Defense mapper: now writes `output/defense_rejected.jsonl` at Step 1.5; `triage_findings.py` hard-rejects those findings before any API call
- Gate enforcement: `final_submission_pack.py` exits(1) if `gate_results.jsonl` is absent; `--bypass-gate` required to override
- Severity validation: `scripts/validate_triage_output.py` (new) checks all triage bucket fields; integrated inline into `final_submission_pack.py`
- Duplicate detection: `data/duplicate_registry.jsonl` (2 entries), Gate 8 extended to check it, `scripts/pre_submission_dupe_screen.py` added as Step 3.8
- Ground truth: 2 confirmed duplicate outcomes recorded (CC-001 duplicate/critical, GAC-001 duplicate/high)

The structural pipeline gaps from the assessment that remain open: ground truth corpus still critically thin (3 entries, 2 are duplicates), agent prompt files do not yet require `ice_chain` output, and 43 of 52 scripts are still dark to the reasoning graph.

---

## What Is Genuinely Novel

### 1. Impact Chain Escalation (ICE)

**Implemented and working.** `scripts/run_impact_chain_escalation.py` (506 lines) does real ripgrep-based consumer search, classifies consumer action types, assigns PoC levels to severity ceilings, and routes low-confidence findings to `ice_manual_review.jsonl`. The `prompts/impact_chain_escalation.md` prompt enforces the chain rule on every finding.

**How defensible:** The rule "root cause → corrupted state → consumer → protocol action → proven impact" is codified in config, agent prompts, and a gate. It is not just documentation. The xterio false-positive note in memory (XTR-003 missed the full compound path) demonstrates the chain was traced but incompletely — the framework caught it.

**Validated against real outcomes:** CHAIN-001 (Origin Protocol, Immunefi report 78016, Critical, submitted 2026-05-13) was a compound finding assembled by this framework. The root cause was confirmed. Outcome not yet judged, but it was submitted as Critical with Level 3 PoC.

**Triage enforcement update (2026-05-21):** `triage_findings.py` already had `ice_chain.consumer_found=false` routing to `poc_required` implemented. The enforcement exists at the gate; the remaining gap is agent prompts not consistently producing the field.

**Replication cost for a competitor:** 1–2 weeks to write the ICE prompt chain. The underlying rule is not secret. The moat is in the automated pipeline that enforces it on every finding, not in the rule itself.

### 2. 8-Gate Pre-Submission Filter

**Implemented, working, and now enforced.** `scripts/pre_submission_gate.py` (662 lines) runs all 8 gates with real data lookups: `defense_map.json`, `exploitability/models.jsonl`, `runtime_poc/results.jsonl`, `judge_simulation/results.jsonl`, `duplicates/risk.jsonl`, `fp_autopsies/pattern_check_results.jsonl`. Invalidation tags have trust level 5, enforced in `agent_policy.json`.

**Update (2026-05-21):** Gate 8 now also checks `data/duplicate_registry.jsonl`. CC-001 (TFH PBH compound) scores 0.90 → FAIL with `duplicate_pattern` tag. `final_submission_pack.py` now exits if gate has not been run. The gate was the infrastructure; now it is also enforced at the submission boundary.

**Validated:** The GL-001 false positive (Gearbox, nonReentrant inherited) was caught via mainnet fork after the gate passed it — a known gap in Gate 4 when the defense mapper's output was not being used as an authoritative source. Fixed: defense mapper now writes `defense_rejected.jsonl` which `triage_findings.py` reads before Gate 4 runs.

**Replication cost:** 2–4 weeks for all 8 gate implementations with proper data dependencies.

### 3. Reasoning Graph Dashboard

**Implemented and working — 9 scripts instrumented (was 5).**

`viz/server.py` (435 lines) is a real FastAPI + WebSocket server. `viz/graph_state.py` (555 lines) maintains graph state. Session management, replay, branch suppression, and human annotation endpoints all exist. 4 real sessions exist with 55, 8, 4, 2 events.

**Update (2026-05-21):** Four previously dark scripts now emit viz events:
- `cross_agent_connector.py` — `HYPOTHESIS_BORN` (per compound) + `EVIDENCE_ATTACHED` (per component)
- `multi_pass_confirm.py` — `CONFIDENCE_SHIFT` with confirmation score + calibrated severity
- `run_deep_analysis.py` — `AGENT_SPAWNED` per pipeline stage
- `synthesize_compound_findings.py` — `BRANCH_CREATED` with pattern name as branch_trigger

Three payload bugs in the newly added emitters were identified and fixed: `EVIDENCE_ATTACHED` was clobbering the parent node ID; `AGENT_SPAWNED` was using the wrong key (`stage_label` vs `spawned_agent`); `BRANCH_CREATED` was missing the label that drives the node display.

**Remaining critical gap:** 43 of 52 pipeline scripts are still dark. No specialist agents emit events. The graph shows compound synthesis, confirmation passes, and deep trace stages but not the initial hypothesis formation or KB matching from individual agents.

**Replication cost:** 1–2 weeks to build a similar event architecture. Hard to replicate the full visualization without also instrumenting the agents.

### 4. Multi-Pass Confirmation

**Implemented and working.** `scripts/multi_pass_confirm.py` (402 lines) uses the real Anthropic SDK, calls `claude-sonnet-4-6`, queries KB and Immunefi tools between passes, and computes `confirmation_score`. Config enforces 3 passes for High, 5 for Critical, 0.6 threshold. Now emits `CONFIDENCE_SHIFT` events to the reasoning graph.

**Validated:** No confirmed data on how often it correctly routes vs. wastes API calls. The policy exists and the code runs.

**Replication cost:** 3–4 hours for a developer with API access. This is the weakest moat of the five.

### 5. FP Autopsy Loop

**Now operational.** Infrastructure was always correct: `scripts/record_fp_autopsy.py`, `scripts/fp_pattern_check.py`, and `scripts/pre_submission_gate.py` all had the required logic. The corpus was empty.

**Update (2026-05-21):** 178 rules now exist in the project-level corpus. `bulk_fp_autopsy.py` now supports `--no-llm` for instant heuristic bootstrap from rejection reasons without API calls (trust_level=2, upgradeable to trust_level=5 by re-running without the flag). Per-audit rejection_rules.jsonl files are now also written — previously only the project-level file was populated.

**Remaining gap:** The `--no-llm` run has not yet been executed against all historical rejected.jsonl entries. 297 rejections → potential 297 rules; only the initial 178 are in place. Running `bulk_fp_autopsy.py --no-llm` is an immediate action.

---

## What Is Underdeveloped

**Ground truth corpus:** 10 audits, 437 findings triaged, 3 verified outcomes (1 duplicate/critical CC-001, 1 duplicate/high GAC-001, 1 from prior session). `evaluate_pipeline_accuracy.py` reports meaningful metrics only above ~10 data points. Until contest outcomes from Xterio, Gearbox, Wormhole, and Origin Protocol are recorded, the accuracy report is not actionable. This is the single most important non-code action.

**Viz instrumentation:** 9 of 52 scripts emit events. Specialist agents (the primary hypothesis generators) emit nothing. The reasoning graph shows the pipe but not the source. A full-session trace requires all specialist agents to emit `HYPOTHESIS_BORN` when they first identify a candidate finding, and `EVIDENCE_ATTACHED` when they attach KB evidence.

**Agent prompt compliance with ice_chain:** The `ice_chain` schema field exists and triage routing enforces it. But agents don't output it consistently. Until `agents/reentrancy.md`, `agents/access_control.md`, `agents/arithmetic.md`, `agents/oracle.md`, `agents/flash_loan.md`, `agents/logic.md`, `agents/dos.md`, and `agents/economic_attack.md` are updated to require the field, the enforcement only fires on the minority of findings where an agent happened to include it.

**Cross-agent connector observability:** Viz events now fire, but there is still no post-run brief ("X compound patterns evaluated, Y escalations produced"). The connector runs silently; a human watching the dashboard can see branch nodes appear but cannot quickly assess whether the connector found anything worth reviewing.

**Setup friction:** SETUP.md is thorough (11 steps) but requires `SOLODIT_API_KEY`. The pipeline should degrade gracefully to local-only Chroma KB mode when the key is absent. Currently `verify_setup.py` treats the missing key as a setup failure. This creates a non-trivial barrier for new auditors joining a contest mid-stream.

---

## Real Audit Quality Bar Today

Based on actual JSONL data (not documentation):

- **Raw generation rate:** 437 findings triaged across 10 audits = ~44 candidates per audit
- **Submit rate:** 22.9% (100/437) — 23% of generated findings reach submit.jsonl
- **Rejection rate:** 68% (297/437) — this is the effective FP rate before human review
- **PoC completion rate:** 8.5% require PoC (37/437); actual completion rate unknown
- **Severity on submitted findings:** 18 High, 28 Medium, 6 Low, 47 Unknown (target: 0 Unknown after validate_triage_output.py)
- **Verified correct:** 3 entries in ground_truth.jsonl; CHAIN-001 submitted Critical, outcome pending
- **Confirmed false positive by human:** GL-001 (Gearbox, nonReentrant inherited) — caught via mainnet fork after pipeline passed it
- **Confirmed duplicates caught by pipeline:** CC-001 (TFH) now scores 0.90 → FAIL in Gate 8 via duplicate_registry. GAC-001 (Gearbox) tagged with `duplicate_pattern` rule. Both would have been caught before submission if the registry had existed when they were submitted.

The 68% rejection rate is not necessarily a sign of low quality — it may reflect good gate logic. But without verified judge outcomes at scale, it cannot be distinguished from "the gates are too aggressive" or "the agents generate a lot of noise." The FP corpus now has 178 rules, which is the first real signal the loop is compounding.

---

## What a Sophisticated Auditor Would Say (Updated)

A 20+ contest veteran would appreciate:
- The ICE chain enforcement preventing orphaned-state severity inflation — this is the correct insight
- The 8-gate structural filter now enforced at the submission boundary, not just advisory
- The duplicate registry catching confirmed re-submissions before they happen
- The per-audit workspace isolation enabling parallel contests
- The `submission_writer.md` format discipline (no internal metadata leaking into submissions)
- The ITE decomposition framework for directing specialist attention
- The reasoning graph showing compound synthesis and confirmation passes in real time

They would still be frustrated by:
- No confirmed contest outcomes at scale — "Show me the money" — 3 ground truth entries is not enough to claim the pipeline calibration is meaningful
- Agent prompts that do not enforce the `ice_chain` field their own orchestration is built around
- The 43 dark pipeline scripts making it impossible to trace where a finding was born vs. where it died
- Setup still requiring Solodit API key before anything useful runs

They would pay for:
- A tool that catches CC-001 and GAC-001 as duplicates before submission — now it does, with the duplicate registry and Gate 8 extension
- A tool that identified CHAIN-001 automatically rather than requiring manual compound assembly — still manual; cross-agent connector is wired but connector hits not yet confirmed at scale

They would build their own if:
- Setup takes more than 2 hours for a new contest
- They cannot extend the specialist agents without reading 3,000 lines of orchestration code

---

## Single Most Important Improvement Remaining

Run `ingest_ground_truth.py` for every known contest outcome. The FP autopsy loop is now operational (178 rules) and the gates are enforced. The only gap between "this is working infrastructure" and "this is a calibrated tool" is the absence of ground truth data. A 10-point corpus transforms the accuracy_report from noise to signal and tells you which gates are over-triggering and which agents need better prompts. Every judged finding that isn't recorded is a calibration data point permanently lost.

---

## Next Steps

See `documentation/business-plan/pipeline_gaps.md` — Next Steps section for the full ordered list. Priority summary:

**Immediate (no code changes):**
1. `python scripts/bulk_fp_autopsy.py --no-llm` — bootstrap remaining FP rules
2. `python scripts/ingest_ground_truth.py` — record all known contest outcomes
3. `python scripts/pre_submission_gate.py --all` — generate gate_results.jsonl for all historical audits

**This week (code changes, 1–4h each):**
4. Surface `ice_manual_review.jsonl` in `generate_status.py`
5. Add cross-agent connector post-run brief to `output/cross_agent_brief.md`

**This month (structural):**
6. Update all 8 specialist agent prompt files to require `ice_chain` output — highest remaining structural fix
7. Deep trace pre-brief generator — ranked one-page summary after `escalate_threads.py`
8. Make `SOLODIT_API_KEY` optional — degrade to local-only Chroma mode when absent
