# Pipeline Reference

This document describes every stage of the Audit-Watch pipeline in order. Run stages sequentially unless noted as parallelizable.

---

## Step 0 — Deep Invariant Analysis

**Purpose:** Extract protocol invariants, map the call graph, and trace dangerous multi-hop chains before any pattern-matching agent runs. Finds violations that only emerge when 3+ interacting subsystems are traced simultaneously.

**Input files:** Contract source directory

**Output files:**
- `data/invariants/protocol_invariants.json` — all invariants
- `data/invariants/high_suspicion.json` — invariants with suspicion_score >= 4
- `data/interactions/call_graph.json` — full interaction map
- `data/interactions/dangerous_chains.json` — chains with danger_score >= 4
- `data/threads/promising_threads.jsonl` — threads to escalate (DT/BT/MT prefixes)
- `data/threads/dead_ends.jsonl` — fully traced, no violation
- `data/threads/fuzzing_threads.jsonl` — Echidna-falsified invariants
- `output/findings_deep_trace.json` — findings for triage
- `output/findings_smt.json` — SMT-falsified arithmetic findings

**Scripts/agents involved:**
- `scripts/extract_invariants.py` (spawns `agents/invariant_extractor.md`)
- `scripts/map_interactions.py` (spawns `agents/interaction_mapper.md`)
- `scripts/deep_trace.py` (spawns `agents/deep_trace_agent.md`)
- `scripts/backward_trace.py` (spawns `agents/backward_trace_agent.md`)
- `scripts/escalate_threads.py`
- `scripts/generate_fuzzing_harness.py` (spawns `agents/fuzzing_harness_writer.md`)
- `scripts/smt_check_invariants.py` (uses Z3)
- `scripts/multi_tx_trace.py` (spawns `agents/multi_tx_agent.md`)

**Commands:**
```bash
python scripts/run_deep_analysis.py --contract contracts/
# Deep mode (50 pairs + all optional stages):
python scripts/run_deep_analysis.py --contract contracts/ --mode deep
python scripts/generate_status.py
```

**Success criteria:** `data/invariants/protocol_invariants.json` exists and is non-empty. `data/threads/promising_threads.jsonl` contains at least one thread to escalate (or is empty if the protocol is simple).

**Common failure modes:** Z3 not installed (smt_check_invariants.py skips gracefully). Slither absent (extract_invariants falls back to regex parsing). Contracts with missing imports cause AST parse failures.

**Next stage dependency:** Step 0.25 reads `data/interactions/dangerous_chains.json`; Step 1 does not depend on Step 0 output directly.

---

## Step 0.25 — Attacker Mindset Mapping

**Purpose:** Map the complete attack surface before specialists run, using the ITE (Intent/Technique/Evasion) framework. Implements the Hadex recon-first principle: specialists need to know where to focus.

**Input files:** Contract source, `output/static.json` (if available), `output/findings_protocol_context.json` (if available)

**Output files:**
- `output/attack_surface.json` — all functions scored 1–5 by attack surface value, with per-agent priority hints
- `output/findings_attacker_mindset.json` — ITE hypotheses for score >= 3 functions (AM- prefix)

**Scripts/agents involved:** `agents/attacker_mindset.md` (spawned as a Task)

**Commands:**
```bash
# Spawn via Task tool in Claude Code, or:
python scripts/generate_status.py  # after agent completes
```

**Success criteria:** `output/attack_surface.json` exists with `agent_hints` block. All Step 2 agents must read this file and prioritize functions with `attack_surface_score >= 3`.

**Common failure modes:** Running before `static.json` exists produces a less-detailed surface map; the agent still runs but with lower confidence scores.

**Next stage dependency:** All Step 2 specialist agents read `output/attack_surface.json`.

---

## Step 0.5 — Zero-Trust Sandbox Check

**Purpose:** Detect prompt injection in contract source before feeding it to any AI agent. Malicious NatSpec or comments could attempt to alter audit methodology or severity decisions.

**Input files:** Contract source directory or file

**Output files:** stdout (flag list + exit code)

**Scripts/agents involved:** `scripts/sandbox_check.py`

**Commands:**
```bash
python scripts/sandbox_check.py contracts/
# Proceed with warning if flags raised:
python scripts/sandbox_check.py contracts/ --allow-flagged
```

**Success criteria:** Exit code 0 (no flags raised, or `--allow-flagged` used with human acknowledgment).

**Flags detected:**
- `instruction_comment` — directive phrases in `//` or `/* */` comments
- `self_reference` — "Claude", "Anthropic", "LLM" in comments or strings
- `oversized_natspec` — `@notice` tags > 500 characters
- `embedded_base64` — base64 blobs in comments that decode to readable text
- `homoglyph` — Unicode look-alike characters in identifiers

**Common failure modes:** Flags raised on legitimate test files with long NatSpec. Use `--allow-flagged` after verifying the flag is benign.

**Next stage dependency:** Must run before any agent receives contract source.

---

## Step 1 — Static Pre-Analysis

**Purpose:** Extract AST, CFG, storage layout, taint sinks, modifier lists, and automatic conditional-agent triggers. Also check build dependency supply chain in parallel.

**Input files:** Contract source

**Output files:**
- `output/static.json` — compiler version, functions, state variables, external calls, modifiers, events, CFG edges, tainted sinks, mythril_issues, `is_erc4626`, `has_transient_storage`, `is_proxy`
- `output/coverage_gaps.json` — ranked list of untested public/external functions
- `output/defense_map.json` — defense coverage per finding (from Step 1.5)
- `output/findings_supply_chain.json` — build chain findings (SC- prefix)

**Scripts/agents involved:**
- `tools/static_analysis.py` — wraps slither + solc
- `scripts/analyze_test_coverage.py`
- `agents/supply_chain_check.md` (spawned in parallel with static analysis)
- `scripts/defense_mapper.py` (Step 1.5, after static.json exists)

**Commands:**
```bash
python tools/static_analysis.py contracts/
python scripts/analyze_test_coverage.py --contract contracts/ --tests test/
# After static.json is written:
python scripts/defense_mapper.py
python scripts/generate_status.py
```

**Success criteria:** `output/static.json` exists and contains `functions` array. `output/defense_map.json` written (may be empty if no findings exist yet).

**Common failure modes:** slither not installed or wrong version. solc version mismatch (`solc-select use <version>`). Missing node_modules for Hardhat projects (run `npm install` first).

**Next stage dependency:** All Step 2 agents require `output/static.json`.

### Step 1.5 — Defense Mapper

Runs after static analysis. Resolves inherited modifiers, classifies defense coverage per finding (full/partial/none/unknown), and identifies CFG evasion paths. Findings with `coverage == "full"` and no evasion path are tagged `already_guarded` and hard-rejected in Step 3.7 without any API call.

---

## Step 2 — Specialist Agents (parallel)

**Purpose:** Run all specialist vulnerability-finding agents simultaneously, each focusing on its domain.

**Input files:** Contract source, `output/static.json`, `output/attack_surface.json`, `output/coverage_gaps.json`, `data/invariants/protocol_invariants.json`, `data/threads/promising_threads.jsonl`

**Output files:** `output/findings_<agent_name>.json` for each agent

**Agents (always run):**
- `agents/reentrancy.md` → `output/findings_reentrancy.json`
- `agents/access_control.md` → `output/findings_access_control.json`
- `agents/arithmetic.md` → `output/findings_arithmetic.json`
- `agents/oracle.md` → `output/findings_oracle.json`
- `agents/flash_loan.md` → `output/findings_flash_loan.json`
- `agents/logic.md` → `output/findings_logic.json`
- `agents/dos.md` → `output/findings_dos.json`
- `agents/snapshot.md` → `output/findings_snapshot.json`
- `agents/economic_attack.md` → `output/findings_economic_attack.json`
- `agents/token_integration.md` → `output/findings_token_integration.json`
- `agents/behavioral_state_analysis.md` → `output/findings_behavioral_state_analysis.json`
- `agents/semantic_guard.md` → `output/findings_semantic_guard.json`
- `agents/protocol_context.md` → `output/findings_protocol_context.json`

**Conditional agents:**
- `agents/cross_chain.md` — only if protocol_context identifies bridge/cross_chain/layer2/relayer/rollup
- `agents/upgrade_storage.md` — only if protocol_context identifies ERC-1967/proxy/UUPS/TransparentProxy
- `agents/erc4626.md` — only if `static.json` has `is_erc4626: true` OR protocol_context mentions ERC-4626
- `agents/transient_storage.md` — only if `static.json` has `has_transient_storage: true` OR contract contains TSTORE/TLOAD

**Commands:**
```bash
# All agents spawned as parallel Tasks via Claude Code Task tool
# After all complete:
python scripts/reference_diff.py --contract contracts/
python scripts/generate_status.py
```

**Success criteria:** All `output/findings_*.json` files exist. Each conforms to `schema/findings_schema.json`. Agents that found nothing write `{"findings": [], "agent": "<name>"}`.

**Common failure modes:** Agent API timeout on very large contracts. Context window exceeded — split contracts into smaller files. KB queries returning empty results (check that `python scripts/solodit_scraper.py` was run).

**Next stage dependency:** Step 2.5 requires all findings files to be present.

---

## Step 2.5 — Cross-Agent Connector

**Purpose:** Make one holistic LLM pass over all findings simultaneously to find exploit chains invisible to individual agents or pairwise pattern matching.

**Input files:** All `output/findings_*.json`, `output/attack_surface.json`, `data/threads/promising_threads.jsonl`

**Output files:**
- `output/findings_cross_agent.json` — new CC_CA-NNN compound findings (if severity escalation found)
- Annotations (`compound_with`, `cross_agent_note`) added to existing findings JSON files (if no escalation)

**Scripts/agents involved:** `scripts/cross_agent_connector.py`

**Commands:**
```bash
python scripts/cross_agent_connector.py
```

**Success criteria:** Script completes without error. If compound chains found, `output/findings_cross_agent.json` exists.

**Common failure modes:** Missing findings files from earlier agents. API timeout on large finding sets.

**Next stage dependency:** Step 3 reads `output/findings_cross_agent.json` in the glob pass.

---

## Step 3 — Compound Synthesis and Report Generation

**Purpose:** Evaluate all findings against 12 compound patterns (COMP-A through COMP-L), merge all findings into a single deduplicated report, and validate agent output for injection artifacts.

**Input files:** All `output/findings_*.json` including `findings_cross_agent.json`

**Output files:**
- `output/findings_compound_synthesis.json` — CC-NNN compound findings
- `output/merged_findings.json` — deduplicated and scored findings
- `output/audit_report.md` — human-readable report
- `output/audit_report.json` — machine-readable, matches `schema/findings_schema.json`

**Scripts/agents involved:**
- `scripts/synthesize_compound_findings.py` (spawns `agents/compound_synthesis.md`)
- `tools/report_generator.py` (calls `agents/report_synthesis.md`)
- `scripts/validate_agent_output.py` (called automatically by report_generator)

**Commands:**
```bash
python scripts/synthesize_compound_findings.py
python tools/report_generator.py
```

**Success criteria:** `output/merged_findings.json` exists. `output/audit_report.md` written. Validate step passes (no injection artifacts, no schema violations).

**Common failure modes:** Shell metacharacters in finding descriptions trigger validation failure. Fix the offending agent output then re-run.

---

### Step 3.4 — Impact Chain Escalation (ICE)

**Purpose:** Trace every finding's corrupted state to the first trusted protocol consumer. Severity is valid only when the full chain is confirmed.

**Commands:**
```bash
python scripts/run_impact_chain_escalation.py
python scripts/generate_status.py
```

**Output files:** `output/findings_ice.json`, `output/ice_manual_review.jsonl`, `output/ice_poc_required.jsonl`

See [impact-chain-escalation.md](impact-chain-escalation.md) for the full ICE framework.

---

### Step 3.5 — Multi-Pass Confirmation

**Purpose:** Run High/Critical finding reasoning 3–5 times independently to handle LLM non-determinism. Findings below the confirmation threshold route to human review.

**Configuration:** `config/agent_policy.json` `multi_pass` section — 3 passes for High, 5 for Critical, threshold 0.6.

**Commands:**
```bash
python scripts/multi_pass_confirm.py
python scripts/generate_status.py
```

**Output files:** `output/findings_confirmed.json` — enriched with `confirmation_passes`, `confirmation_score`, `human_review_required`, `human_review_reason`

**Common failure modes:** API error during confirmation passes causes `confirmation_score = 0.0`. Check `human_review_reason` field — it will note the API error.

---

### Step 3.6 — FP Pattern Check

**Purpose:** Scan findings against accumulated false-positive rejection rules from past audits. Findings matching a known-invalid pattern at high similarity are flagged for hard rejection.

**Commands:**
```bash
python scripts/fp_pattern_check.py --all
```

**Output files:** `data/fp_autopsies/pattern_check_results.jsonl`

**Similarity threshold:** 0.85 for reject, 0.6 for warn. Requires rule confidence > 0.8 for automatic reject recommendation.

---

### Step 3.7 — Pre-Submission Gate

**Purpose:** Apply 8 structural validity gates. FAIL assigns a hard invalidation tag. 3+ WARNs routes to human review. Only PASS findings proceed to triage API call.

**Commands:**
```bash
python scripts/pre_submission_gate.py --all
python scripts/generate_status.py
```

**The 8 gates:**

| # | Gate | FAIL condition | Tag applied |
|---|------|----------------|-------------|
| 1 | Reachability | `blocked_by_auth=True` + `can_trigger=False` | `non_exploitable` |
| 2 | State Realism | impossible-state keywords in description | `impossible_state` |
| 3 | Privilege | admin attacker + `realistic=False` + no untrusted-admin argument | `admin_only` |
| 4 | Defense | `coverage == "full"` + no evasion path | `already_guarded` |
| 5 | Economics | `profit_or_damage.type == "none"` + bounded, or attack cost > profit | `no_profitability` |
| 6 | PoC | Critical/High + `needs_poc=True` + `runtime_poc_level == 0` | — |
| 7 | Severity | Judge sim `predicted_outcome == "rejected"` with confidence >= 4 | — |
| 8 | Duplicate | `duplicate_risk == "high"` or FP pattern match > 0.85 | `duplicate_finding` / `duplicate_pattern` |

**Output files:** `data/triage/gate_results.jsonl`

---

## Step 4 — Triage

**Purpose:** Route findings to submission buckets based on 7-component triage score plus the Claude triage agent.

**Commands:**
```bash
python scripts/triage_findings.py
python scripts/build_poc_queue.py
python scripts/final_submission_pack.py
python scripts/generate_status.py
```

**Output files:**
- `data/triage/submit.jsonl` — score >= 28, no PoC needed
- `data/triage/poc_required.jsonl` — score 22–27, needs proof
- `data/triage/downgraded.jsonl` — score 16–21
- `data/triage/merged.jsonl` — duplicate of another finding
- `data/triage/rejected.jsonl` — score < 16 or hard reject
- `data/triage/poc_queue.jsonl` — ordered PoC work queue
- `output/submission_pack.md` — contest-ready report

**Note:** Never run `triage_findings.py --all` on an existing audit. It overwrites `submit.jsonl`. Use `--finding-id` to triage individual new findings.

---

### Step 4.5 — Human Review Classification

**Purpose:** Route findings requiring expert judgment to human review queue. Implements the Hadex 90/10 principle.

**Commands:**
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

**Output files:**
- `data/triage/human_review_queue.jsonl` — needs human auditor validation
- `data/triage/ai_confirmed.jsonl` — AI can handle autonomously

**Routing criteria (2+ triggers → human review):**
1. KB similarity < 0.4 (novel pattern)
2. confirmation_score < 0.6
3. trace_depth >= 3 (multi-hop cross-contract chain)
4. Compound claim with no COMP-* match
5. cross_chain or upgrade_storage category
6. Critical claim without Level 2+ PoC
7. BSA finding (behavioral divergence)
8. Already flagged `human_review_required` by multi_pass_confirm.py

---

## Step 5 — Specialist Review

**Purpose:** Model exploitability, estimate duplicate risk, calibrate severity, generate integrated PoCs, and simulate judge review.

**Commands:**
```bash
python scripts/run_specialist_review.py
# Or individually:
python scripts/model_exploitability.py --all
python scripts/estimate_duplicate_risk.py --all
python scripts/calibrate_severity.py --all
python scripts/run_integrated_poc.py --all
python scripts/judge_simulate.py --all
```

**Output files:**
- `data/exploitability/models.jsonl`
- `data/duplicates/risk.jsonl`, `clusters.jsonl`
- `data/severity/calibrated.jsonl`
- `data/runtime_poc/results.jsonl`
- `data/judge_simulation/results.jsonl`

---

## Step 6 — PoC Generation

**Purpose:** Generate, run, and verify proof-of-concept tests for `poc_required` findings.

**Commands:**
```bash
python scripts/profile_target_repo.py --repo contracts/ --out data/poc_queue/repo_profile.json
python scripts/generate_poc_plan.py --finding-id RE-001
python scripts/generate_poc_test.py --finding-id RE-001 --max-repair-attempts 3
python scripts/run_poc_tests.py --finding-id RE-001
python scripts/summarize_poc_results.py --out reports/poc_evidence.md
```

**Output files:** `data/poc_queue/<ID>_plan.json`, `data/poc_queue/<ID>_result.json`, `pocs/<audit_id>/<ID>/src/lib.rs`

See [poc-development.md](poc-development.md) for the full PoC guide.

---

## Step 7 — Quality Checklist

**Purpose:** Answer 7 questions confirming the PoC actually proves the claimed impact before submission.

**Commands:**
```bash
python scripts/run_quality_checklist.py --finding-id RE-001
python scripts/generate_status.py
```

**Output files:** `data/quality_checklist/results.jsonl`

---

## Step 8 — PoC Completeness Gate

**Purpose:** Verify the PoC proves the claimed severity. Caps severity if proof stops before the claimed impact.

**Commands:**
```bash
python scripts/analyze_poc_completeness.py --all --strict
python scripts/generate_status.py
```

**Output files:** `output/poc_completeness/<ID>.json`, `output/poc_upgrade_tasks/<ID>_upgrade.md`

**Severity ceiling rules:**

| Bug class | L3A ceiling | L3B ceiling | L3C ceiling |
|-----------|-------------|-------------|-------------|
| reentrancy_forced_liquidation | Medium | Medium | High |
| close_factor_bypass | Medium | Medium | High |
| liquidation_dos | Medium | **High** | High |
| missing_auth_allowance_theft | Medium | Medium | High |

After Step 8, regenerate the submission pack:
```bash
python scripts/final_submission_pack.py
python scripts/generate_status.py
```
