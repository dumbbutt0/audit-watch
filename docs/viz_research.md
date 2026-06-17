# Adversarial Reasoning Visualization — Phase 0 Research

## 0a. Codebase Audit — Data Flow Diagram

```
[Step 0: extract_invariants.py]
  → emits: {invariants[{invariant_id, category, statement, suspicion_score, mutating_functions}]}
  → written to: data/invariants/protocol_invariants.json, data/invariants/high_suspicion.json

[Step 0b: map_interactions.py]
  → emits: {call_graph[], interaction_chains[{chain_id, danger_score, shared_state}], trust_boundary_crossings[]}
  → written to: data/interactions/call_graph.json, data/interactions/dangerous_chains.json

[Step 0c: deep_trace.py]
  → emits: {threads[{thread_id, verdict, violation_path, hop_traces[]}]}
  → written to: data/threads/promising_threads.jsonl, data/threads/dead_ends.jsonl

[Step 0c-bis: backward_trace.py]
  → emits: {threads[]} with BT- prefix IDs
  → appended to: data/threads/promising_threads.jsonl

[Step 0d: escalate_threads.py]
  → reads: data/threads/promising_threads.jsonl
  → calls Claude per thread → spawns specialist agent per category
  → emits: {agent, contract, findings[{...}]} conforming to findings_schema.json
  → written to: output/findings_deep_trace.json

[Step 0.25: attacker_mindset agent]
  → emits: {attack_surface[{function, score, agent_hints}], ite_hypotheses[]}
  → written to: output/attack_surface.json, output/findings_attacker_mindset.json

[Step 0.5: sandbox_check.py]
  → emits: {flags[{type, location, content}], safe: bool}
  → written to: stdout only (not persisted)

[Step 1: tools/static_analysis.py]
  → emits: {compiler_version, functions[], state_variables[], external_calls[],
             modifiers[], events[], cfg_edges[], tainted_sinks[], mythril_issues[],
             is_erc4626, has_transient_storage, is_proxy}
  → written to: output/static.json, output/slither_<contract>.json

[Step 1: tools/static_analysis.py (slither detectors)]
  → emits: detector findings with {check, impact, confidence, description, elements[]}
  → embedded in: output/static.json under mythril_issues / tainted_sinks

[Step 1.5: defense_mapper.py]
  → emits: {findings[{id, applicable_defenses[], coverage, evasion_path, inherited_from}]}
  → written to: output/defense_map.json

[Step 2: 24 specialist agents (parallel)]
  → each emits: {agent, contract, timestamp, findings[{
      id, title, severity, vuln_type, description,
      location.{file, function, line_start, line_end, code_snippet},
      impact, recommendation, confidence,
      ite.{intent, technique, evasion},
      defense_mapping, invalidation_tags, assumption_count,
      confirmation_score, attack_surface_rank, cross_agent_refs
    }]}
  → written to: output/findings_<agent_name>.json

[Step 2.5: cross_agent_connector.py]
  → reads all output/findings_*.json simultaneously
  → emits compound findings {id with CC_CA- prefix, compound_with[], cross_agent_note}
  → written to: output/findings_cross_agent.json

[Step 3: synthesize_compound_findings.py]
  → emits: {findings[{id with CC- prefix, compound_pattern, participating_findings[]}]}
  → written to: output/findings_compound_synthesis.json

[Step 3: tools/report_generator.py]
  → reads all output/findings_*.json
  → deduplicates, scores, merges
  → written to: output/merged_findings.json, output/audit_report.md, output/audit_report.json

[Step 3.4: run_impact_chain_escalation.py]
  → emits: {findings[{id, ice.{corrupted_state, consumers[], poc_level, severity_ceiling, hold}}]}
  → written to: output/findings_ice.json, output/ice_manual_review.jsonl, output/ice_poc_required.jsonl

[Step 3.5: multi_pass_confirm.py]
  → emits: {findings[{id, confirmation_passes, confirmation_score, human_review_required, human_review_reason}]}
  → written to: output/findings_confirmed.json

[Step 3.6: fp_pattern_check.py]
  → emits: {finding_id, recommended_action, similarity_score, matched_rule_id}
  → written to: data/fp_autopsies/pattern_check_results.jsonl

[Step 3.7: pre_submission_gate.py]
  → emits: {finding_id, gates[{gate_id, result, tag_applied}], overall: PASS|FAIL|WARN}
  → written to: data/triage/gate_results.jsonl

[Step 4: triage_findings.py]
  → emits: {finding_id, triage_status, recommended_severity, score,
             score_components.{attacker_control, sensitive_sink, poc_feasibility, ...}}
  → written to: data/triage/submit.jsonl, poc_required.jsonl, downgraded.jsonl, rejected.jsonl

[Step 4.5: human_review_classifier.py]
  → emits: {finding_id, requires_human_review, trigger_count, triggers[]}
  → written to: data/triage/human_review_queue.jsonl, data/triage/ai_confirmed.jsonl

[Step 5: model_exploitability.py]
  → emits: {finding_id, attacker.{type, required_assets, required_permissions},
             control_surface, execution_sequence, profit_or_damage,
             blockers.{auth, allowance, atomicity}, exploitability_score}
  → written to: data/exploitability/models.jsonl

[Step 5: estimate_duplicate_risk.py]
  → emits: {finding_id, duplicate_risk, internal_duplicates[], external_similar_findings}
  → written to: data/duplicates/risk.jsonl, data/duplicates/clusters.jsonl

[Step 5: calibrate_severity.py]
  → emits: {finding_id, original_severity, calibrated_severity, confidence,
             severity_drivers[], rules_applied[], similar_historical_cases[]}
  → written to: data/severity/calibrated.jsonl

[Step 5: judge_simulate.py]
  → emits: {finding_id, predicted_outcome, persona_verdicts.{strict_judge, sponsor, duplicate_hunter}}
  → written to: data/judge_simulation/results.jsonl

[Step 6: run_poc_tests.py / run_integrated_poc.py]
  → emits: {finding_id, status (proved|failed|inconclusive|compile_error),
             test_file, assertion_hit, runtime_level, repair_attempts, evidence_summary}
  → written to: data/poc_queue/<ID>_result.json, data/runtime_poc/results.jsonl

[Step 7: run_quality_checklist.py]
  → emits: {finding_id, checklist[{question, answer, evidence}], overall_pass}
  → written to: data/quality_checklist/results.jsonl

[KB: tools/retriever.py]
  → query: vuln_type + text → Chroma similarity search
  → emits: [{title, severity, description, code, fix, similarity_score}]
  → written to: stdout JSON (called as subprocess by specialist agents)
```

---

## 0b. Event Hook Inventory

| Event Type | Description | Where to Fire | Source |
|---|---|---|---|
| `HYPOTHESIS_BORN` | New potential finding created | Each slither detector result + each specialist finding written | `tools/static_analysis.py`, `tools/report_generator.py` (merge) |
| `BRANCH_CREATED` | Sub-investigation spawned from a finding | Per thread in escalation | `scripts/escalate_threads.py` |
| `EVIDENCE_ATTACHED` | Evidence/context added to finding | KB match, static analysis confirmation | `tools/retriever.py`, `tools/static_analysis.py` |
| `CONFIDENCE_SHIFT` | Severity or confidence rating changes | Severity calibration, multi-pass confirm | `scripts/calibrate_severity.py`, `scripts/multi_pass_confirm.py` |
| `BRANCH_INVALIDATED` | Finding/path rejected (capture reason) | Triage rejected bucket, gate FAIL | `scripts/triage_findings.py`, `scripts/pre_submission_gate.py` |
| `EXPLOIT_PROVED` | PoC test succeeds | PoC status=proved | `scripts/run_poc_tests.py`, `scripts/run_integrated_poc.py` |
| `EXPLOIT_FAILED` | PoC test fails (capture why) | PoC status≠proved | `scripts/run_poc_tests.py`, `scripts/run_integrated_poc.py` |
| `KB_MATCH` | Solodit/Immunefi precedent matched | similarity > 0.75 in retriever | `tools/retriever.py` |
| `AGENT_SPAWNED` | Sub-agent created to investigate branch | Per thread escalation Claude call | `scripts/escalate_threads.py` |
| `TRIAGER_DECISION` | Triage accepts, rejects, or escalates | Per finding bucket assignment | `scripts/triage_findings.py` |

---

## 0c. Integration Surface Analysis

### Option 1: File-based event log (append-only JSONL) + polling
- `emit()` appends one JSON line to `data/sessions/{session_id}/events.jsonl`
- Server polls file every 0.5–1s for new lines
- Pros: zero coupling, trivially safe, no new dependencies
- Cons: polling delay (up to 1s); not true real-time

### Option 2: Redis pub/sub event bus
- `emit()` publishes to Redis channel `viz:{session_id}`
- Server subscribes and forwards to WebSocket clients
- Pros: instant delivery; proper pub/sub
- Cons: requires Redis install/running; large new dependency; overkill for local tool

### Option 3: In-process Python event emitter with websocket bridge
- `emit()` calls a module-level function that puts into `asyncio.Queue`
- Server loop reads from queue and broadcasts
- Pros: lowest latency
- Cons: requires all pipeline scripts to run in same process; conflicts with subprocess usage pattern

### Option 4: SQLite-backed event store with SSE stream
- `emit()` inserts row into SQLite
- Server polls SQLite with `SELECT * WHERE id > last_seen`
- Pros: durable, queryable
- Cons: more complex than JSONL; SQLite write contention under parallel agents

### **Recommendation: Option 1 + watchfiles (not polling)**

Use **append-only JSONL event log** with `watchfiles.awatch()` for file-system notification instead of polling. This gives near-instant delivery (watchfiles uses inotify/kqueue) without any new infrastructure.

- `emit()` → `open(events_file, 'a').write(json_line + '\n')` — one line, thread-safe with lock
- `viz/server.py` → `async for changes in watchfiles.awatch(events_file): tail_new_lines()`
- New lines → parse VizEvent → `graph_state.apply_event()` → `ws.send_json(diff)`
- On WS connect → `ws.send_json(graph_state.snapshot())`

**Why this wins:**
1. Zero shared state — pipeline scripts and server are completely independent processes
2. Server can start before, during, or after the pipeline — replays from beginning on connect
3. Matches the existing dashboard pattern exactly (`watchfiles` already in `requirements.txt`)
4. Non-blocking for pipeline: just a file append — sub-millisecond
5. Durable: JSONL log survives server restarts, enables session replay
6. No new infrastructure dependencies

**New dependencies to add to requirements.txt:**
- `websockets>=12.0` — WebSocket client/server protocol (supplements FastAPI WS)
- `aiohttp>=3.9` — async HTTP client (for any future viz-side HTTP calls)
