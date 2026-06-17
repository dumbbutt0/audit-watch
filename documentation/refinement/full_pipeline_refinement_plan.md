# Audit-Watch — Full Pipeline Refinement Plan

_Status: implemented in the 2026-05-29 refinement pass. This is the canonical narrative; the
companion docs in this folder hold the per-topic detail._

## What the system does

Audit-Watch is a staged smart-contract auditing pipeline. It moves a target from raw scope
intake to a contest-ready submission pack through ~14 internal stages, orchestrated by
`run_pipeline.sh` (`analyze | full | poc | submit`) and the `/ite-audit` Claude Code skill.
Work is isolated per audit under `audits/<id>/`; all paths resolve through
`scripts/audit_context.py`. State flows **through files on disk**, not in-memory — every stage
reads its inputs from the previous stage's output artifact. There is one human-in-the-loop
pause: `generate_review_gate.py` writes `output/review_gate.md` and stops before PoCs.

Inventory: **76 Python scripts** (52 deterministic, 24 calling the Anthropic API), **34 agent
templates** in `agents/`, **23 skills** in `.claude/skills/`, a 636MB Chroma KB (`kb/chroma/`),
wired MCP servers (`onchain-context`, `kb-search`), and proof-requirement templates.

## Where each stage begins and ends

See `stage_interaction_map.md` for the full table. Headline handoff chain:

```
scope_inventory.md → static.json → attack_surface.json → context_pack.md
  → findings_<agent>.json (×16) → findings_cross_agent.json
  → merged_findings.json → findings_confirmed.json → gate/dupe results
  → data/triage/{buckets}.jsonl + data/triage/<id>.md → review_gate.md  [PAUSE]
  → pocs/<id>/ + runtime_poc/results.jsonl → submission_pack.md
```

## Where context is lost (and the fix)

1. **Contract intake is ambiguous.** Source lives in a shared repo-root `contracts/`, not in
   the audit workspace; there is no "primary directory" selection and no consolidated
   context file. → **Fix:** `intake_contracts.py` copies source into `audits/<id>/contracts/`
   and records the association; `generate_contract_context.py` emits `notes/contract_context.md`
   (a single deep navigation index). See `context_flow_map.md`.
2. **Specialists don't always re-read the deep-analysis artifacts.** `data/invariants/` and
   `data/threads/promising_threads.jsonl` exist but are inconsistently consumed. → Documented
   as a required input in `stage_interaction_map.md`; enforcement staged for next pass.
3. **Human-facing artifacts are buried in machine dirs.** Findings live in `output/` and
   `data/` (script substrate). → **Fix:** `findings/` and `notes/` human-facing views added to
   every workspace; bridged from the substrate without moving it.

## Where agents may duplicate work

Multiple specialists legitimately find the same root cause from different angles (Beanstalk:
the migration-replay bug was found by `access_control`, `behavioral_state_analysis`, and
`cross_chain`). This is **desired redundancy** for confidence — the dedup stage links them
(`cross_agent_refs`) rather than treating it as waste. The risk is the opposite (below).

## Where findings over-merge

`tools/report_generator.py` deduplicates by collapsing findings too aggressively. In the
Beanstalk eval it merged 70 raw findings → 44, folding two **distinct** oracle bugs (OR-001
Chainlink inversion vs OR-002 LibUsdOracle wstETH branch) into one. → **Fix:** merge only on
root-cause + function + exploit-path + invariant + impact-mechanism match; otherwise keep both
and link. Regression fixture enforces it. See `dedup_and_merge_policy.md`.

## Where false clearances happen

The schema *intends* "route uncertain findings to verification, never silently clear." But
agents (especially `protocol_context`) still wrote confident "works as designed" conclusions —
clearing 5 real Beanstalk bugs (#377 Invariable, #461 quickSort, #307 multi-sunrise, #332
fundsSafu, #142 bridge). → **Fix:** clearing safety-net code now requires a written
attacker-path **disproof**; absent that, emit an `unresolved_invariant` finding routed to the
human queue. Enforced in `validate_agent_output.py`. See `zero_trust_triage_policy.md`.

## Where API calls are required (and deterministic replacements)

24 scripts call `claude-sonnet-4-6` directly — separate API spend and the exact failure that
halted the Beanstalk eval mid-run (`synthesize_compound_findings`, `triage_findings`,
`multi_pass_confirm` all crashed on a missing key). Full disposition table in
`api_dependency_audit.md`. Strategy: **skill-in-session** — deterministic pre-processor builds
a context bundle, a Claude Code skill reasons inside this session (normal subscription, no key),
a deterministic writer validates the output to schema. `triage` is converted as the flagship
pattern. A follow-up **zero-API hardening pass** then wired the `llm_runtime.py` guard into
**every** API script (`require_llm`) and added `optional_llm` skip-and-continue for the 2.5/3/3.5
enhancers — so a keyless `run_pipeline.sh full` now completes through the pause (triage via the
`/triage` skill, then `./run_pipeline.sh review-gate`). A regression guard
(`scripts/check_no_bare_anthropic.py`) prevents new bare `anthropic.Anthropic()` constructions.
True skill-in-session conversion of the remaining reasoning stages is still staged.

## What to do first / what NOT to touch yet

**First (this pass):** backup → 8 docs → workspace layout + migration (dry-run gated) → intake
+ context → API guard + triage skill → clearance gate → dedup fix → verify.

**Not yet (staged):** true skill-in-session conversion of the remaining reasoning stages — they are
now all *guarded* (skip-or-stop cleanly with no key), but only `triage` reasons in-session, so the
rest still need a key to add their value; relocating `output/`/`data/` machine artifacts (would
touch ~50 scripts); re-architecting the deep-analysis intake scripts. No new live audit is run as
part of this work.
