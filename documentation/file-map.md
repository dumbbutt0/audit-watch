# File Map

Comprehensive reference of key files in the Audit-Watch repository.

---

## Root Files

| Path | Purpose | Produced by | Consumed by |
|------|---------|-------------|-------------|
| `CLAUDE.md` | Authoritative pipeline reference; Claude Code reads this for all audit instructions | Human | Claude Code |
| `SETUP.md` | Installation and setup guide | Human | Human |
| `requirements.txt` | Python dependencies | Human | `pip install` |
| `run_pipeline.sh` | Shell script runner for common pipeline commands | Human | Human / CI |
| `.mcp.json` | MCP server registration | Human | Claude Code MCP layer |
| `.env` | API keys and environment variables (gitignored) | Human | All scripts |

---

## config/

| Path | Purpose | Produced by | Consumed by |
|------|---------|-------------|-------------|
| `config/agent_policy.json` | Run mode (fast/normal/deep), multi-pass settings, invalidation tags, human review criteria | Human | All scripts via `audit_context.py` |
| `config/zero_trust_policy.json` | Trusted/untrusted paths, agent write boundaries, network allowlist, sandbox hardening | Human | `sandbox_check.py`, agents |
| `config/active_audit.json` | Currently active audit ID | `audit_manager.py` | All scripts via `audit_context.py` |
| `config/phone_commands.md` | Phone control command → action mapping reference | Human | Claude Code |

---

## scripts/

| Path | Purpose | Produces | Consumes |
|------|---------|---------|---------|
| `scripts/audit_context.py` | Central path resolution for all per-audit paths | N/A | All pipeline scripts |
| `scripts/audit_manager.py` | Create/switch/list audit workspaces | `meta.json`, `active_audit.json` | Human |
| `scripts/sandbox_check.py` | Prompt injection scan (Step 0.5) | stdout flag list | Called before any agent |
| `scripts/extract_invariants.py` | Step 0a: protocol invariant extraction | `data/invariants/protocol_invariants.json` | `map_interactions.py`, `deep_trace.py` |
| `scripts/map_interactions.py` | Step 0b: call graph and dangerous chains | `data/interactions/call_graph.json`, `dangerous_chains.json` | `deep_trace.py` |
| `scripts/deep_trace.py` | Step 0c: forward hop-by-hop trace | `data/threads/promising_threads.jsonl`, `output/findings_deep_trace.json` | `escalate_threads.py` |
| `scripts/backward_trace.py` | Step 0c-bis: sink-to-source trace | `data/threads/promising_threads.jsonl` (BT- prefix) | `escalate_threads.py` |
| `scripts/escalate_threads.py` | Step 0d: convert threads to findings | `output/findings_deep_trace.json` | `report_generator.py` |
| `scripts/generate_fuzzing_harness.py` | Step 0d-fuzz: Echidna property generation | `data/threads/fuzzing_threads.jsonl` | Human / Echidna |
| `scripts/smt_check_invariants.py` | Step 0e: Z3 arithmetic falsification | `output/findings_smt.json` | `report_generator.py` |
| `scripts/multi_tx_trace.py` | Step 0f: multi-transaction TOCTOU analysis | `data/threads/promising_threads.jsonl` (MT- prefix) | `escalate_threads.py` |
| `scripts/run_deep_analysis.py` | Convenience orchestrator for Steps 0a-0f | All Step 0 outputs | Human |
| `scripts/defense_mapper.py` | Step 1.5: maps modifiers onto findings | `output/defense_map.json` | `pre_submission_gate.py` |
| `scripts/analyze_test_coverage.py` | Step 1: test coverage gap analysis | `output/coverage_gaps.json` | All Step 2 agents |
| `scripts/reference_diff.py` | Post-Step 2: compare against Aave/Compound/Uniswap reference | `output/findings_reference_diff.json` | `report_generator.py` |
| `scripts/cross_agent_connector.py` | Step 2.5: holistic cross-agent compound synthesis | `output/findings_cross_agent.json` | `synthesize_compound_findings.py` |
| `scripts/synthesize_compound_findings.py` | Step 3: 12-pattern compound synthesis | `output/findings_compound_synthesis.json` | `report_generator.py` |
| `scripts/validate_agent_output.py` | Step 3: output validation gate | stdout pass/fail | `report_generator.py` |
| `scripts/run_impact_chain_escalation.py` | Step 3.4: ICE enrichment | `output/findings_ice.json`, `ice_manual_review.jsonl`, `ice_poc_required.jsonl` | `submission_writer.md` |
| `scripts/multi_pass_confirm.py` | Step 3.5: multi-pass LLM confirmation | `output/findings_confirmed.json` | `human_review_classifier.py` |
| `scripts/fp_pattern_check.py` | Step 3.6: FP pattern scan | `data/fp_autopsies/pattern_check_results.jsonl` | `pre_submission_gate.py` |
| `scripts/pre_submission_gate.py` | Step 3.7: 8-gate pre-submission filter | `data/triage/gate_results.jsonl` | `triage_findings.py` |
| `scripts/triage_findings.py` | Step 4: Claude triage agent | `data/triage/submit.jsonl`, `poc_required.jsonl`, `downgraded.jsonl`, `merged.jsonl`, `rejected.jsonl` | `build_poc_queue.py` |
| `scripts/build_poc_queue.py` | Step 4: ordered PoC work queue | `data/triage/poc_queue.jsonl` | `generate_poc_plan.py` |
| `scripts/human_review_classifier.py` | Step 4.5: AI/human routing | `data/triage/human_review_queue.jsonl`, `ai_confirmed.jsonl` | Human |
| `scripts/final_submission_pack.py` | Steps 4/5: contest-ready submission | `output/submission_pack.md`, `submission_pack.json` | Human |
| `scripts/run_specialist_review.py` | Step 5: orchestrates all specialist review scripts | All Step 5 outputs | Human |
| `scripts/model_exploitability.py` | Step 5: attacker model | `data/exploitability/models.jsonl` | `pre_submission_gate.py`, `calibrate_severity.py` |
| `scripts/estimate_duplicate_risk.py` | Step 5: duplicate risk | `data/duplicates/risk.jsonl`, `clusters.jsonl` | `pre_submission_gate.py` |
| `scripts/calibrate_severity.py` | Step 5: final severity | `data/severity/calibrated.jsonl` | `final_submission_pack.py` |
| `scripts/run_integrated_poc.py` | Step 5: integrated PoC runner | `data/runtime_poc/results.jsonl` | `analyze_poc_completeness.py` |
| `scripts/judge_simulate.py` | Step 5: judge simulation | `data/judge_simulation/results.jsonl` | `pre_submission_gate.py` |
| `scripts/profile_target_repo.py` | Step 6: repo language/framework detection | `data/poc_queue/repo_profile.json` | `generate_poc_plan.py` |
| `scripts/generate_poc_plan.py` | Step 6: PoC strategy planning | `data/poc_queue/<ID>_plan.json` | `generate_poc_test.py` |
| `scripts/generate_poc_test.py` | Step 6: PoC code generation | Test files in `pocs/<audit>/` | `run_poc_tests.py` |
| `scripts/run_poc_tests.py` | Step 6: PoC test execution | `data/poc_queue/<ID>_result.json`, `data/runtime_poc/results.jsonl` | `summarize_poc_results.py` |
| `scripts/summarize_poc_results.py` | Step 6: PoC evidence report | `reports/poc_evidence.md` | Human |
| `scripts/run_quality_checklist.py` | Step 7: 7-question checklist | `data/quality_checklist/results.jsonl` | `analyze_poc_completeness.py` |
| `scripts/analyze_poc_completeness.py` | Step 8: completeness gate | `output/poc_completeness/<ID>.json`, `output/poc_upgrade_tasks/<ID>_upgrade.md` | Human |
| `scripts/generate_status.py` | Compact status for dashboard / phone | `output/status.json` | Dashboard, human |
| `scripts/dashboard.py` | Audit progress dashboard server (port 8765) | N/A | Human browser |
| `scripts/record_fp_autopsy.py` | FP autopsy recording | `data/fp_autopsies/rejection_rules.jsonl`, `<ID>_autopsy.json` | `fp_pattern_check.py` |
| `scripts/ingest_ground_truth.py` | Record verified contest outcomes | `data/evaluation/ground_truth.jsonl` | `evaluate_pipeline_accuracy.py` |
| `scripts/evaluate_pipeline_accuracy.py` | Pipeline accuracy metrics | `data/evaluation/accuracy_report.json` | Human |
| `scripts/ingest_judging_results.py` | Record judge verdicts | Per-finding records | `ingest_ground_truth.py` |
| `scripts/solodit_scraper.py` | Build/update Chroma KB from Solodit | `kb/chroma/` | `retriever.py` |
| `scripts/ingest_c4_reports.py` | Ingest Code4rena/Sherlock findings into KB | `kb/chroma/` | `retriever.py` |
| `scripts/migrate_to_audit.py` | Migrate legacy flat output to audit workspace | `audits/<id>/` | Human (one-time) |
| `scripts/decision_logic.py` | `/continue` command decision logic | N/A | Phone control mode |
| `scripts/severity_calibrator.py` | Severity calibration agent wrapper | `data/severity/calibrated.jsonl` | `calibrate_severity.py` |
| `scripts/register_pc_findings.py` | Register protocol_context findings in data/findings/ | `data/findings/<ID>.json` | `generate_status.py` |

---

## tools/

| Path | Purpose | Produces | Consumes |
|------|---------|---------|---------|
| `tools/static_analysis.py` | Step 1: slither + solc AST/CFG | `output/static.json` | All Step 2 agents |
| `tools/retriever.py` | Query local Chroma KB (Solodit) | JSON array to stdout | Agents (subprocess call) |
| `tools/immunefi_retriever.py` | Query Immunefi via MCP | JSON array to stdout | Agents (subprocess call) |
| `tools/report_generator.py` | Step 3: merge findings, write reports | `output/merged_findings.json`, `audit_report.md`, `audit_report.json` | `triage_findings.py` |
| `tools/verify_setup.py` | Pre-flight check | stdout pass/fail | Human |
| `tools/kb_mcp_server.py` | MCP server for local KB | N/A | Claude Code MCP layer |
| `tools/onchain_mcp_server.py` | MCP server for on-chain data | N/A | Claude Code MCP layer |
| `tools/quicknode_mcp.py` | Live bytecode/storage via QuickNode | JSON to stdout | Agents (subprocess call) |
| `tools/dune_mcp.py` | Protocol TVL/volume via Dune | JSON to stdout | Agents (subprocess call) |
| `tools/graph_mcp.py` | Historical state via The Graph | JSON to stdout | Agents (subprocess call) |
| `tools/chainlist_mcp.py` | Chain metadata | JSON to stdout | Agents (subprocess call) |
| `tools/glider_tool.py` | Cross-repo variant analysis via Glider | stdout findings | `report_generator.py` |
| `tools/primitives_retriever.py` | Retrieve primitive building-block patterns | JSON to stdout | Agents |

---

## agents/

All 34 agent specification files. See [agents.md](agents.md) for the full reference.

| Pattern | Example | Purpose |
|---------|---------|---------|
| Core finding agents | `agents/reentrancy.md` | Specialist vulnerability finding (always run in Step 2) |
| Synthesis agents | `agents/compound_synthesis.md` | Combine/analyze findings (called by scripts) |
| Infrastructure agents | `agents/invariant_extractor.md` | Build analysis inputs (called in Step 0) |
| Conditional agents | `agents/erc4626.md` | Only spawned when trigger condition met |

---

## prompts/

All 17 prompt files. See [prompts.md](prompts.md) for the full reference.

| Path | Used by |
|------|---------|
| `prompts/human_auditor_methodology.md` | All Step 2 specialist agents |
| `prompts/impact_chain_escalation.md` | All agents + `run_impact_chain_escalation.py` |
| `prompts/triager.md` | `scripts/triage_findings.py` |
| `prompts/submission_writer.md` | `scripts/final_submission_pack.py` |
| `prompts/poc_planner.md` | `scripts/generate_poc_plan.py` |
| `prompts/poc_writer.md` | `scripts/generate_poc_test.py` |
| `prompts/poc_reviewer.md` | `scripts/run_poc_tests.py` |
| `prompts/poc_quality_checklist.md` | `scripts/run_quality_checklist.py` |

---

## schemas/

| Path | Describes |
|------|---------|
| `schema/findings_schema.json` | Canonical finding shape (all agent outputs) |
| `schemas/triage.schema.json` | Triage output shape |
| `schemas/exploitability.schema.json` | Exploitability model |
| `schemas/duplicate_risk.schema.json` | Duplicate risk assessment |
| `schemas/judge_simulation.schema.json` | Judge simulation result |
| `schemas/severity_calibration.schema.json` | Severity calibration output |
| `schemas/severity_learning_record.schema.json` | Historical severity rule |
| `schemas/poc_plan.schema.json` | PoC planning output |
| `schemas/poc_result.schema.json` | PoC execution result |
| `schemas/poc_queue.schema.json` | PoC work queue entry |
| `schemas/runtime_poc.schema.json` | Runtime PoC status |
| `schemas/invariants.schema.json` | Protocol invariant format |
| `schemas/call_graph.schema.json` | Cross-system call graph |
| `schemas/thread.schema.json` | Deep trace thread format |
| `schemas/reasoning_graph.schema.json` | Full reasoning graph with all node types |
| `schemas/viz_event.schema.json` | Single VizEvent emitted by pipeline |

---

## viz/

| Path | Purpose |
|------|---------|
| `viz/server.py` | FastAPI + WebSocket reasoning graph server (port 8766) |
| `viz/session.py` | Session ID management (create/get/list sessions) |
| `viz/event_emitter.py` | Zero-friction event emission for pipeline scripts |
| `viz/graph_state.py` | In-memory reasoning graph state manager |
| `viz/replay.py` | Session replay logic (at=N query parameter) |
| `viz/frontend/index.html` | D3.js reasoning graph frontend |

---

## dashboard/

| Path | Purpose |
|------|---------|
| `dashboard/index.html` | Audit progress dashboard HTML |
| `dashboard/app.js` | Dashboard JavaScript (served by `scripts/dashboard.py`) |

---

## audits/ (workspace structure)

| Path | Purpose |
|------|---------|
| `audits/<id>/meta.json` | Contest metadata (platform, scope, deadline, max_bounty) |
| `audits/<id>/output/` | All findings JSON, reports, submission packs |
| `audits/<id>/data/triage/` | submit/poc_required/rejected/gate_results JSONL files |
| `audits/<id>/data/findings/` | Per-finding definition JSON files |
| `audits/<id>/data/exploitability/` | Attacker models |
| `audits/<id>/data/duplicates/` | Duplicate risk assessments |
| `audits/<id>/data/severity/` | Calibrated severity records |
| `audits/<id>/data/runtime_poc/` | PoC test results |
| `audits/<id>/data/judge_simulation/` | Judge verdict predictions |
| `audits/<id>/data/threads/` | Deep trace threads (promising/dead/fuzzing) |
| `audits/<id>/data/invariants/` | Protocol invariants |
| `audits/<id>/data/interactions/` | Call graph and dangerous chains |
| `audits/<id>/data/fp_autopsies/` | Per-audit FP rejection rules |
| `audits/<id>/data/evaluation/` | Ground truth calibration corpus (human-only write) |
| `audits/<id>/pocs/` | Generated PoC test crates |
| `audits/<id>/reports/` | poc_evidence.md |

---

## templates/

| Path | Purpose |
|------|---------|
| `templates/proof_requirements/<bug_class>.json` | Proof requirement templates for PoC completeness gate |

Available templates: `reentrancy_forced_liquidation.json`, `close_factor_bypass.json`, `liquidation_dos.json`, `missing_auth_allowance_theft.json`
