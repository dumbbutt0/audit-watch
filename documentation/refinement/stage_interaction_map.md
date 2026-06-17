# Stage Interaction Map

The user's 11-stage mental model mapped onto Audit-Watch's internal stages. Each row: the
controlling script/agent, the input artifact it consumes, the output artifact it produces
(the handoff), and notes. **Context flows through files** — every stage reads the prior
stage's artifact from disk.

| # | User stage | Internal stage(s) | Controller | Input artifact | Output artifact (handoff) |
|---|---|---|---|---|---|
| 1 | Scope & intake | 0 Scope inventory | `generate_scope_inventory.py` | contract path | `output/scope_inventory.md` |
| 2 | Contract download & association | 0 Intake (**NEW**) | `intake_contracts.py` | downloaded dir(s) | `audits/<id>/contracts/` + `meta.primary_contract_dir` |
| 3 | Focused contract selection | 0 Context build (**NEW**) + 0.25 surface | `generate_contract_context.py` ; `agents/attacker_mindset.md` | primary dir, `static.json` | `notes/contract_context.md` ; `output/attack_surface.json` |
| 4 | Static analysis & POI discovery | 0.5 sandbox, 1 static, 0a–0f deep | `sandbox_check.py`, `tools/static_analysis.py`, `run_deep_analysis.py` | source | `output/static.json`, `data/invariants/*`, `data/threads/promising_threads.jsonl`, `notes/static_analysis.md`, `notes/points_of_interest.jsonl` |
| 5 | KB & known-finding cross-ref | 1.5 defense + context pack | `defense_mapper.py`, `generate_context_pack.py`, `tools/retriever.py`, `tools/immunefi_retriever.py` | `static.json`, KB, Immunefi MCP | `output/defense_map.json`, `output/context_pack.md`, `output/kb_crossref.md` |
| 6 | Specialist agent review | 2 specialists | `/ite-audit` → 16 `agents/*.md` | `context_pack.md`, `attack_surface.json`, `coverage_gaps.json`, invariants, threads | `output/findings_<agent>.json` (×16) |
| 7 | Dedup & impact chaining | 2.5 cross-agent, 3 compound + merge, 3.4 escalation | `cross_agent_connector.py`, `synthesize_compound_findings.py`, `tools/report_generator.py`, `run_impact_chain_escalation.py` | all `findings_*.json` | `output/findings_cross_agent.json`, `output/merged_findings.json`, `output/chains.md` |
| 8 | Zero-trust triage & validation | 3.5 confirm, 3.6 FP, 3.7 gate, 3.8 dupe, 4 triage | `multi_pass_confirm.py`, `fp_pattern_check.py`, `pre_submission_gate.py`, `pre_submission_dupe_screen.py`, `triage_findings.py` | `merged_findings.json` + KB | `data/triage/{submit,poc_required,downgraded,merged,rejected}.jsonl`, `data/triage/<id>.md` |
| 9 | Human review table | 4 review gate, 4.5 routing | `human_review_classifier.py`, `generate_review_gate.py` | `data/triage/<id>.md` | `output/review_gate.md` (**PAUSE**), `data/triage/human_review_queue.jsonl` |
| 10 | Fork PoC creation | 5–6 PoC | `generate_poc_plan.py`, `generate_poc_test.py`, `run_poc_tests.py`, `run_integrated_poc.py` | selected finding IDs | `pocs/<id>/`, `data/runtime_poc/results.jsonl` |
| 11 | Final report packet | 7 QC, 8 completeness, 9 pack | `run_quality_checklist.py`, `analyze_poc_completeness.py`, `final_submission_pack.py` | PoC results | `output/submission_pack.md`, `output/submissions/<id>_submission.md` |

## The `findings/` + `notes/` bridge (NEW human-facing layer)

Scripts and the 34 agent templates are hard-wired to write/read bare `output/` and `data/…`.
Rewriting all of them is out of scope, so the new human-facing dirs sit **on top** of the
substrate as views:

| Human-facing path | Source of truth (substrate) | Populated by |
|---|---|---|
| `notes/contract_context.md` | (new artifact) | `generate_contract_context.py` |
| `notes/static_analysis.md`, `notes/points_of_interest.jsonl` | `output/static.json` + deep-analysis | `generate_contract_context.py` |
| `findings/raw/` | `output/findings_*.json` | migration / sync step (copy) |
| `findings/validated/` | `data/triage/<id>.md` | migration / sync step (copy) |
| `status/status.json`, `status/session.json` | `generate_status.py`, `session.json` | sync step |

Rule: **the substrate (`output/`, `data/`) remains canonical for scripts; `findings/`+`notes/`
are read-optimized copies for humans.** A sync runs after triage; no script reads from the
human-facing dirs, so they can never desync the pipeline.

## Pause semantics

`run_pipeline.sh full` ends at `generate_review_gate.py` (`sys.exit(0)`). Steps 5–9 only run via
explicit `./run_pipeline.sh poc <id>` or `submit`. This is the single mandatory human gate; the
new `findings/validated/` view is what the human reads there.
