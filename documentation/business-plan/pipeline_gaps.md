# Pipeline Gap Analysis

_Ordered by stage, then ranked by finding quality impact × implementation effort._
_Last updated: 2026-05-23. Items marked ✅ are implemented; ⚠️ partially implemented; 🔲 open._

---

## Stage-by-Stage Analysis

### Step 0: Deep Analysis (invariants, interactions, threads)

**Status: ✅ Implemented (2026-05-23)**

**Previous failure modes:**
- Threads with `suspicion_score == 3` were silently dropped at `extract_invariants.py` line 151 (hard `>= 4` filter). No soft-flag watch list existed.
- Thread-finding join was described in CLAUDE.md as a guideline but never enforced in code — agents were told to check `promising_threads.jsonl` but there was no automated cross-reference.
- No human-readable output existed from Step 0; the human auditor received raw JSONL only.

**Fixes applied (2026-05-23):**

1. **Automated thread-finding join** (`scripts/annotate_findings_with_threads.py`, NEW): Deterministic function-name regex join against `promising_threads.jsonl`. Called as a subprocess at the start of `cross_agent_connector.py main()` before holistic synthesis. Annotates every `findings_*.json` with `thread_refs` (hard overlap), `thread_note`, and `soft_thread_match` (score-3 invariant state-variable overlap). Enforcement is in code, not just a CLAUDE.md guideline.

2. **Ranked human-readable brief** (`scripts/generate_step0_brief.py`, NEW): Writes `output/step0_brief.md` after Stage 0d (thread escalation), before Step 1. Ranks threads by `suspicion_score × severity`, groups by function in a heatmap table, and flags domain-specific patterns (Oracle, DEX/AMM, Flash Loan, Cross-Chain) via keyword scan. Called as Stage 0d-brief in `run_deep_analysis.py`.

3. **Score-3 soft-flag tier**: `extract_invariants.py` now writes `data/invariants/medium_suspicion.json` for score-3 invariants instead of dropping them. `deep_trace.py` gains `--include-medium` flag (active in `--mode deep`) to run a secondary trace pass producing `soft_flag: true` threads with `DT-S-NNN` IDs. `escalate_threads.py` skips soft-flag threads by default (`--include-soft` to override). Soft threads appear in the step0 brief Watch List but are never auto-escalated.

---

### Step 1: Static Analysis + Defense Mapper

**Status: ✅ Implemented**

**Previous failure mode:** `defense_mapper.py` classified `coverage:full` findings that then passed through the 8-gate (Gate 4) anyway, because Gate 4 re-checked coverage independently. Contradictory conclusions between the two steps meant some already_guarded findings reached triage.

**Fix applied (2026-05-21):** Defense mapper is now authoritative. When `coverage:full` + no evasion path, findings are written to `output/defense_rejected.jsonl` at Step 1.5. `triage_findings.py` reads this list and hard-rejects those findings before any other pre-check — before the gate and before any API call. Gate 4 continues to confirm the tag but no longer makes the first determination.

---

### Step 2: Specialist Agent Parallel Execution

**Status: ⚠️ Partially implemented**

**Most common failure mode:** High false positive rate from agents generating findings without completing the ICE chain check. Looking at `rejected.jsonl` across audits, most rejections are `verdict:unknown` — rejected by triage, not by automated gates. Agents submit findings with incomplete chains; the triage agent then has to re-reason about ICE chain validity for every finding.

**Fix applied (pre-existing in triage_findings.py):** The triage pre-check already handles `ice_chain.consumer_found=false` — findings with this field set to false are routed to `poc_required` before the Claude API call. This enforcement exists at the gate; the gap is that agents do not consistently output `ice_chain`.

**Fix applied (2026-05-23):** All 15 finding-specialist agent prompt files (`agents/*.md`) now require the `ice_chain` field in their output schemas. A reasoning instruction was added to each: agents must complete the ICE chain before writing a finding; `consumer_found: false` means include the finding with that flag set (triage routes to `poc_required`) rather than submitting it. Fields required on every finding: `corrupted_state`, `impact`, `consumer_found`, `consumer_function`, `exploit_path`. Files updated: `reentrancy`, `access_control`, `arithmetic`, `oracle`, `flash_loan`, `logic`, `dos`, `snapshot`, `economic_attack`, `token_integration`, `behavioral_state_analysis`, `semantic_guard`, `cross_chain`, `upgrade_storage`, `erc4626`, `transient_storage`.

**Remaining gap:** Agents that were already mid-run when prompts were updated will still produce findings without the field. Enforcement only fires when the field is present and false; findings omitting it entirely bypass the pre-check. Full effectiveness requires re-running specialists on active audits.

---

### Step 2.5: Cross-Agent Connector

**Status: ⚠️ Partially implemented**

**Previous failure mode:** No viz events, no post-run summary, no way to verify the connector was producing escalations.

**Fix applied (2026-05-21):** `cross_agent_connector.py` now emits `HYPOTHESIS_BORN` for each new compound finding and `EVIDENCE_ATTACHED` for each component. Payload fields verified against `graph_state.py` handler requirements.

**Remaining gap:** No post-run summary ("X compound patterns evaluated, Y escalations produced, Z severity bumps"). The connector is now visible in the reasoning graph but still lacks a human-readable brief after each run. Human review of compound candidates before report inclusion would catch the class of miss seen in XTR-003.

---

### Step 3: ICE + Multi-Pass Confirm + FP Gate + Pre-Submission Gate

**Status: ⚠️ Mixed — FP gate bootstrapped, others open**

**FP Gate — previous failure mode:** Zero rejection rules in the FP autopsy corpus. `fp_pattern_check.py` gracefully returned "proceed" for all findings. Step 3.6 was a no-op.

**Fix applied (2026-05-21):** 178 rules now exist in `data/fp_autopsies/rejection_rules.jsonl` — 176 from historical processing, 2 as `duplicate_pattern` entries for CC-001 (TFH) and GAC-001 (Gearbox). `bulk_fp_autopsy.py` now supports `--no-llm` for instant heuristic-rule generation from rejection reasons without API calls (trust_level=2), and writes both project-level and per-audit files. Step 3.6 is now active for the first time.

**ICE manual review — open:** Consumer search via ripgrep misses interface calls, delegatecall paths, and inheritance chains. Low-confidence findings go to `ice_manual_review.jsonl` but there is no evidence this queue is being worked. `generate_status.py` does not surface it.

**Pre-Submission Gate — remaining gap:** The 297 `verdict:unknown` rejections reflect audits where gate data (exploitability, judge simulation) was not populated. If `defense_map.json` or `judge_simulation/results.jsonl` is absent, the gate falls through to "WARN". Gate warnings may be silently accumulating without human review.

---

### Step 4: Triage + Human Review Routing

**Status: ✅ Implemented**

**Previous failure mode:** 47 "Unknown" severity findings in `submit.jsonl` across audits. Triage was running but not always writing severity into the output schema.

**Fix applied (2026-05-21):**
- `scripts/validate_triage_output.py` (new) — validates that every `submit.jsonl` and `poc_required.jsonl` entry has `severity`, `triage_status`, `finding_id`, and `title` populated. `--fix` writes safe defaults; `--strict` exits 1 on violation.
- `final_submission_pack.py` — inline severity check at load time, prints named violating finding IDs.

---

### Step 5: Exploitability + Judge Simulation + Severity Calibration

**Status: ✅ Implemented (gate enforcement) / 🔲 Open (data population)**

**Previous failure mode:** `final_submission_pack.py` warned but did not block when `gate_results.jsonl` was absent. Gate could be silently skipped.

**Fix applied (2026-05-21):** `final_submission_pack.py` now calls `sys.exit(1)` when `gate_results.jsonl` does not exist. `--bypass-gate` override exists for emergencies. `analyze_poc_completeness.py --all` is now invoked automatically at the start of `_check_poc_completeness()` before checking results.

**Remaining gap:** For 8 of 10 audits, `gate_results.jsonl` does not exist, meaning the gate has not been run on historical audits. This enforcement only helps for new runs.

---

### Steps 6–8: PoC Generation, Quality Checklist, Completeness Gate

**Status: ✅ Implemented (enforcement) / 🔲 Open (historical data)**

**Previous failure mode:** `analyze_poc_completeness.py` was not consistently run. PoCs may have been written but not validated at the correct level.

**Fix applied (2026-05-21):** `final_submission_pack.py` now automatically invokes `analyze_poc_completeness.py --all` and blocks on unsupported High/Critical claims. `--bypass-poc` override available.

**Remaining gap:** Of 37 `poc_required` findings across audits, completeness gate data (`output/poc_completeness/`) is not present in historical audit workspaces. Enforcement helps future runs only.

---

## All Gaps Ranked: Finding Quality Impact × Implementation Effort

_Priority = high impact (more valid findings, fewer false positives) × low effort_
_Status column reflects state as of 2026-05-21._

| # | Gap | Impact | Effort | Priority | Status |
|---|-----|--------|--------|----------|--------|
| 1 | FP autopsy loop — bootstrap from existing rejected.jsonl entries | Very High: every future audit improves | instant: `--no-llm` flag now available | P0 | ⚠️ Flag added; bootstrap not yet run against all 297 |
| 2 | Specialist agents don't output `ice_chain` field — triage re-reasons about ICE | High: cuts FP rate | ✅ Done | P1 | ✅ All 15 agent prompts updated (2026-05-23) |
| 3 | Ground truth corpus — 1 verified outcome across 10 audits | High: cannot distinguish good gate from noisy gate | 1h: run `ingest_ground_truth.py` for known outcomes | P1 | 🔲 Open |
| 4 | 47 Unknown severity in submit.jsonl | High: unusable for submission | ✅ Done | P2 | ✅ validate_triage_output.py + inline check |
| 5 | Defense mapper → Gate 4 duplication | Medium: wasted agent processing | ✅ Done | P2 | ✅ defense_rejected.jsonl + triage Step 1.5 check |
| 6 | Viz instrumentation: 5 → 9 of 52 scripts emit events | Medium: debugging visibility | 4h done; 43 scripts still dark | P3 | ⚠️ 4 new scripts instrumented this session |
| 7 | Cross-agent connector observability | Medium: CHAIN-001 was manual | ⚠️ Viz events added; post-run brief missing | P3 | ⚠️ Partial |
| 8 | Gate run not enforced before submission pack | Medium: gate can be skipped silently | ✅ Done | P2 | ✅ sys.exit(1) on missing gate_results.jsonl |
| 9 | ICE manual review queue not surfaced in status | Medium: high-value findings stall | 2h: add to generate_status.py | P3 | 🔲 Open |
| 10 | PoC completeness gate not run automatically | Medium: severity overclaims | ✅ Done | P2 | ✅ auto-invoked in final_submission_pack.py |

---

## Top 5 Pipeline Fixes — Updated Status

**1. ✅ Gate enforcement before submission (was P2, 1h)**
`final_submission_pack.py` now exits on missing gate results and invokes poc completeness automatically. Gate bypasses require explicit flags.

**2. ✅ Severity validation at triage output (was P2, 2h)**
`validate_triage_output.py` validates all triage bucket fields. `--fix` repairs missing severity; `--strict` blocks on violation.

**3. ✅ Defense mapper made terminal at Step 1.5 (was P2, 2h)**
`defense_rejected.jsonl` is written by defense_mapper.py. `triage_findings.py` hard-rejects listed findings before any other pre-check.

**4. ⚠️ FP autopsy bootstrap (was P0, 2h)**
`bulk_fp_autopsy.py --no-llm` now generates heuristic rules from rejection reasons without API calls. 178 rules exist. **Action required:** Run `--no-llm` against all audit workspaces to convert remaining rejections to rules, then run `fp_pattern_check.py --all` to activate them.

**5. ✅ ice_chain enforcement (was P1, 1 week — done 2026-05-23)**
Triage routing (`consumer_found=false` → poc_required) is implemented. All 15 finding-specialist agent prompts now require `ice_chain` with `corrupted_state`, `impact`, `consumer_found`, `consumer_function`, and `exploit_path`. Reasoning instruction added to each: trace the consumer chain before writing; if no consumer found, do not submit — include with `consumer_found: false`.

---

## Next Steps

_Ordered by implementation readiness — items at the top can be completed in the current session or today._

### Immediate (no code changes needed)

**A. Bootstrap FP corpus from all historical rejections**
```bash
python scripts/bulk_fp_autopsy.py --no-llm
python scripts/fp_pattern_check.py --all
```
Converts remaining rejected.jsonl entries into heuristic rules (trust_level=2). Then run without `--no-llm` on high-value audits (gearbox, xterio) to upgrade rules with LLM reasoning.

**B. Run ground truth ingestion for all known outcomes**
```bash
# Xterio — TG-001, TG-002 submitted, awaiting judge
python scripts/audit_manager.py switch xterio-2026-05
python scripts/ingest_ground_truth.py --finding-id TG-001 --outcome accepted --severity high --recorded-by human_review
python scripts/ingest_ground_truth.py --finding-id TG-002 --outcome accepted --severity high --recorded-by human_review

# Gearbox — GAC-001 confirmed duplicate
python scripts/audit_manager.py switch gearbox-2026-05
python scripts/ingest_ground_truth.py --finding-id GAC-001 --outcome duplicate --severity high --rejection-reason "Closed as duplicate of #76929" --recorded-by contest_result

# After outcomes are confirmed, run accuracy evaluation
python scripts/evaluate_pipeline_accuracy.py
```

**C. Run gate on all historical audits**
For each audit workspace, run `python scripts/pre_submission_gate.py --all` to generate `gate_results.jsonl`. This unblocks `final_submission_pack.py` for those workspaces.

---

### This Week (code changes, 1–4h each)

**D. Surface ICE manual review queue in generate_status.py**
Add a section to `output/status.json` that counts entries in `ice_manual_review.jsonl` and lists the top 3 by consumer_search_confidence. These are findings with indirect consumers that cannot be auto-resolved and need a human to trace the call chain.

**E. Cross-agent connector post-run brief**
After `cross_agent_connector.py` completes, write `output/cross_agent_brief.md`: patterns evaluated, escalations produced, severity bumps, compound candidates for human review. Currently the connector runs silently with no summary.

**F. Validate triage output as a required pre-step**
Add `validate_triage_output.py --strict` to the pipeline sequence in `run_pipeline.sh` (or equivalent) immediately after `triage_findings.py`. Currently it can be skipped.

---

### This Month (structural, 1 week)

**G. ✅ Update all specialist agent prompt files to require `ice_chain`** _(done 2026-05-23)_
All 15 finding-specialist prompts updated. `ice_chain` fields: `corrupted_state`, `impact`, `consumer_found`, `consumer_function`, `exploit_path`. Reasoning instruction added to each agent. Triage pre-check was already wired; prompts now enforce consistent output.

**H. ✅ Step 0 human-readable brief and thread-finding join** _(done 2026-05-23)_
`scripts/generate_step0_brief.py` writes `output/step0_brief.md` after Stage 0d, ranking threads by score with a function heatmap and domain pattern alerts (Oracle, DEX/AMM, Flash Loan, Cross-Chain). `scripts/annotate_findings_with_threads.py` enforces the thread-finding join in code at the start of `cross_agent_connector.py`. Score-3 soft-flag tier added (`medium_suspicion.json`, `--include-medium` for deep mode, soft threads in brief Watch List).

**I. Reduce setup friction**
Make `SOLODIT_API_KEY` optional. When absent, fall back to the local Chroma KB only. Currently `verify_setup.py` treats the missing key as a setup failure. The pipeline should degrade gracefully to local-only mode.
