# Context Flow Map

The file-handoff DAG end-to-end, and the points where context is dropped.

## The DAG

```
                         contract path (user)
                               │
                 ┌─────────────┴───────────────┐
       intake_contracts.py            generate_scope_inventory.py
   audits/<id>/contracts/  ───────────► output/scope_inventory.md
   meta.primary_contract_dir
                               │
                       tools/static_analysis.py
                          output/static.json ──────────────┐
                               │                            │
        run_deep_analysis.py (0a–0f)                generate_contract_context.py
   data/invariants/*  data/threads/promising_threads.jsonl   notes/contract_context.md
                               │                            notes/static_analysis.md
                               │                            notes/points_of_interest.jsonl
                     agents/attacker_mindset.md
                       output/attack_surface.json
                               │
            defense_mapper.py + generate_context_pack.py
              output/defense_map.json   output/context_pack.md   output/kb_crossref.md
                               │
         ┌─────────────────────┴──────────────────────┐
   /ite-audit → 16 specialists                         │
   output/findings_<agent>.json ×16                    │
         │                                              │
   cross_agent_connector.py → findings_cross_agent.json│
         │                                              │
   synthesize_compound_findings.py + report_generator.py
              output/merged_findings.json  ◄─── (dedup choke point)
         │
   run_impact_chain_escalation.py → output/chains.md
         │
   multi_pass_confirm.py → findings_confirmed.json
         │
   fp_pattern_check / pre_submission_gate / dupe_screen
         │
   triage_findings.py (or /triage skill)
   data/triage/{buckets}.jsonl + data/triage/<id>.md
         │
   generate_review_gate.py → output/review_gate.md   ███ PAUSE ███
         │  (human picks finding IDs)
   generate_poc_* / run_poc_tests → pocs/<id>/ + data/runtime_poc/results.jsonl
         │
   run_quality_checklist / analyze_poc_completeness
         │
   final_submission_pack.py → output/submission_pack.md
```

## Context-loss points and fixes

1. **Intake → workspace gap (FIXED).** Previously the source was a shared repo-root
   `contracts/`; nothing tied a finding's `location.file` back to *which audit* owned it, and a
   second downloaded repo could shadow the first. → `intake_contracts.py` makes the association
   explicit (`audits/<id>/contracts/`, `meta.primary_contract_dir`) and refuses to overwrite.

2. **Deep-analysis artifacts under-consumed.** `data/invariants/*` and
   `data/threads/promising_threads.jsonl` are produced in Stage 4 but specialists in Stage 6
   don't reliably re-read them, so invariant context is lost between stages. → This pass
   documents them as required specialist inputs (see `stage_interaction_map.md` row 6);
   programmatic enforcement (a coverage gate that fails if a specialist ignored a high-suspicion
   invariant touching its category) is staged for the next pass.

3. **Merge choke point (FIXED).** `merged_findings.json` is the single funnel into triage. If
   the merge drops a distinct finding, it is invisible downstream forever (no stage re-reads the
   raw `findings_<agent>.json` after merge). The Beanstalk OR-001/OR-002 collapse happened here.
   → `dedup_and_merge_policy.md` + the report_generator guard. **`findings/raw/` now preserves
   the pre-merge set** so a dropped finding is at least recoverable by a human.

4. **Clearance = silent context destruction (FIXED).** An agent writing "works as designed"
   deletes a thread of investigation with no artifact. → clearing safety-net code now must emit
   an `unresolved_invariant` finding (an artifact that survives), routed to the human queue.

5. **Human-facing vs machine context split (FIXED).** Findings/notes were buried in `output/`
   and `data/`. → `findings/` and `notes/` give a human a clean read path without touching the
   substrate the scripts depend on.

## Invariant: no stage reads from a human-facing view

The sync into `findings/` and `notes/` is one-directional (substrate → view). No pipeline
script reads those views, so a stale or hand-edited view can never corrupt a pipeline run.
