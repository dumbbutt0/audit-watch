# Glossary

---

**agent**
A complete task specification in `agents/<name>.md` that Claude Code runs as a parallel Task. An agent has its own goal, input discovery instructions, analysis checklist, and output requirements. Agents write to `output/findings_<name>.json`. Distinct from a prompt (which is an instruction template, not a self-contained task).

**assumption count**
The number of preconditions required for an exploit that are not guaranteed by the protocol. Real exploits typically have 0–2 assumptions. Findings with 4+ assumptions trigger a Gate 2 warning. Tracked in `data/findings/<ID>.json` and in the ground truth corpus.

**audit workspace**
An isolated directory `audits/<audit_id>/` containing all output, data, PoC files, and reports for one contest. Created by `audit_manager.py new <id>`. Project-level files (agents, prompts, schemas, KB) remain at the repo root and are shared across all workspaces.

**behavioral divergence**
A class of vulnerability where the code's documented intent (NatSpec, comments, variable names) and its actual runtime behavior disagree. Found by the Behavioral State Analysis (BSA) agent. Requires human review because resolving the divergence requires judgment about developer intent.

**compound finding**
A finding created by combining two or more lower-severity individual findings into a single higher-severity exploit. Identified by `scripts/synthesize_compound_findings.py` (CC-NNN prefix) or `scripts/cross_agent_connector.py` (CC_CA-NNN prefix).

**confirmation score**
A float 0.0–1.0 representing the fraction of multi-pass confirmation runs that agreed the finding is valid. High findings require 3 passes; Critical require 5. Findings with score < 0.6 are flagged for human review. Set by `scripts/multi_pass_confirm.py`.

**consumer**
A trusted protocol function that reads a corrupted state variable and uses it to make a security-relevant decision (e.g., `deploy()`, `borrow()`, `liquidate()`). Finding a consumer is required before assigning severity above Low. Part of the ICE (Impact Chain Escalation) framework.

**defense map**
The output of `scripts/defense_mapper.py` stored in `output/defense_map.json`. Maps existing contract modifiers (inherited and direct) onto potential finding candidates, classifying coverage as full/partial/none/unknown. Full coverage with no evasion path triggers the `already_guarded` invalidation tag.

**direct proof**
Evidence that a PoC test directly demonstrated the claimed harm — balance change, unauthorized mint, blocked safety function. Contrasted with "plausible escalation" where the impact is inferred from intermediate state. Severity is capped based on what was directly proven, not what seems plausible.

**duplicate**
A finding that shares both the same root cause and the same fix as another finding in the batch. Two findings are NOT duplicates for sharing impact category, title similarity, or general location. Identified by `agents/duplicate_risk_agent.md`.

**event_emitter**
The zero-friction instrumentation module in `viz/event_emitter.py`. Any pipeline script can call `from viz.event_emitter import emit` to emit a VizEvent to the reasoning graph session. Fire-and-forget; never raises; gracefully skips if `VIZ_SESSION_ID` is not set.

**exploit proved**
A PoC test result with `status == "proved"` where an assertion fired that directly demonstrates the bug claim. Contrasted with `inconclusive` (test ran but assertion does not test the actual claim) and `failed` (test ran and the behavior was correct).

**false positive (FP)**
A finding that was submitted but rejected by a contest judge or found to be invalid on review. FP autopsies are recorded with `scripts/record_fp_autopsy.py` and become rejection rules in `data/fp_autopsies/rejection_rules.jsonl` that prevent the same pattern from recurrence.

**finding**
A discrete vulnerability claim from a specialist agent. Identified by a unique ID (`RE-001`, `AC-002`), has a severity level, location, description, impact, recommendation, and confidence score. Conforms to `schema/findings_schema.json`.

**hypothesis**
The reasoning graph representation of a finding candidate at any stage of the pipeline. Has a status (LIVE/CONVERGED/INVALIDATED/PRUNED/ESCALATED) and a confidence score that evolves as evidence accumulates. Displayed as a `HypothesisNode` in the viz dashboard.

**ICE (Impact Chain Escalation)**
The framework defined in `prompts/impact_chain_escalation.md` that requires tracing every finding from root cause → corrupted state → protocol consumer → real protocol action → proven impact before assigning severity. Enforced by `scripts/run_impact_chain_escalation.py`.

**invalidation tag**
A hard tag applied to a finding by `defense_mapper.py`, `pre_submission_gate.py`, or `record_fp_autopsy.py` that prevents it from reaching `submit.jsonl` without explicit human override. Tags are at trust level 5; AI-generated hypotheses (trust level 7) cannot remove them.

**ITE (Intent / Technique / Evasion)**
The attack decomposition framework from the Jason Hadex methodology. For every finding: Intent = what the attacker wants, Technique = how the attack works, Evasion = what protection exists and how it can be bypassed. Applied by `agents/attacker_mindset.md` in Step 0.25.

**KB match**
A result from the Solodit or Immunefi knowledge base that is structurally similar to a current finding. KB matches provide historical precedent, increase finding confidence, and sometimes contain exploit PoCs. Retrieved by `tools/retriever.py` and `tools/immunefi_retriever.py`.

**manual review**
A state where a finding cannot be automatically confirmed or rejected by the pipeline and requires a human auditor to inspect the exploit path. Triggered by 2+ criteria in `scripts/human_review_classifier.py`. Findings in `data/triage/human_review_queue.jsonl` must not be submitted without personal review.

**MCP (Model Context Protocol)**
A protocol for connecting AI models to external data sources. Audit-Watch uses MCP servers for the local KB (`kb_mcp_server.py`), on-chain data (`onchain_mcp_server.py`), and Immunefi reports (`immunefi-audit-competitions`). All MCPs are non-fatal context providers.

**merged findings**
The deduplicated, scored aggregate of all per-agent findings produced by `tools/report_generator.py` and stored in `output/merged_findings.json`. The primary input for all downstream pipeline stages (triage, ICE, confirmation, gates).

**plausible escalation**
An impact path that is logically possible but not directly proved by the PoC. Not sufficient for severity claims above the directly proved level. Contrasted with direct proof.

**PoC level**
A number 0–5 (or L3A/L3B/L3C) indicating how far a proof-of-concept test has progressed toward full impact demonstration. Level 0 = static reasoning only; Level 5/L3C = financial impact directly asserted. Severity ceiling is determined by PoC level and bug class.

**pre-submission gate**
One of 8 structural validity checks run by `scripts/pre_submission_gate.py` before any finding reaches the triage API call. A FAIL assigns an invalidation tag and skips the API call entirely.

**prompt**
An instruction template in `prompts/<name>.md` loaded into agent context to provide a specific reasoning framework, output format, or decision procedure. Distinct from agents: prompts are not standalone tasks; they are context injected into agent runs.

**reasoning graph**
The live visualization of the audit pipeline's cognitive state served by `viz/server.py` on port 8766. Shows hypotheses, branches, evidence, confidence evolution, and invalidations as the pipeline runs.

**rejected**
A finding in `data/triage/rejected.jsonl`. Either hard-rejected by a gate (invalidation tag), scored below threshold by the triage agent (< 16 / 35), or marked as a duplicate. Rejected findings are not permanently lost — recording an FP autopsy prevents recurrence, but the finding data is retained.

**severity ceiling**
The maximum severity a finding can claim given the current PoC evidence. Set by the ICE block (`ice.severity_ceiling`) and the PoC completeness gate. The final calibrated severity is `min(claimed_severity, severity_ceiling)`.

**skill**
A Claude Code slash command defined in `.claude/skills/<name>/SKILL.md`. Skills execute structured audit sub-tasks (e.g., `/reentrancy`, `/surface`, `/ite-audit`) from within a conversation without running the full pipeline.

**submit**
A finding in `data/triage/submit.jsonl` that has passed all gates and been triaged as ready to submit to a contest. Still requires human review if in `human_review_queue.jsonl`.

**triage decision**
The output of `scripts/triage_findings.py` for one finding: submit / poc_required / downgraded / merged / rejected. Made by the Claude triage agent after the local pre-gates have run.

**triage score**
The 7-component score (0–35) used to bucket findings: submit (>= 28), poc_required (22–27), downgraded (16–21), rejected (< 16). Components: attacker_control, sensitive_sink, missing_check_clarity, impact_realism, poc_feasibility, scope_safety, duplicate_risk (inverse).
