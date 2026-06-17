# API-Free Pipeline

Audit-Watch can run the full eval-critical path (`analyze → /ite-audit → full → review_gate`) with
**no Anthropic API calls** — every LLM reasoning stage runs in-session via Claude Code
skills/agents/tools, bracketed by deterministic prepare/write scripts. This removes both the cost
and the reproducibility problem of leaning on a key during evals.

## The switch

`config/runtime_policy.json`:
```json
{ "api_free": true }
```
`scripts/llm_runtime.py::api_free_mode()` reads this. When true, `llm_available()` returns **False**
even if `ANTHROPIC_API_KEY` is set, and both `require_llm()` and `optional_llm()` take the
skill route instead of constructing an Anthropic client. `AUDIT_WATCH_API_FREE=0` env overrides the
config to temporarily re-enable the API. The key in `.env` is also commented out (belt-and-suspenders).

Guard: `scripts/check_api_free.py` asserts every eval-critical stage in `SKILL_MAP` has a skill route
or skips cleanly (so nothing hard-stops). A `PreToolUse(Bash)` hook
(`scripts/hooks/block_api_scripts.py`) blocks direct invocation of deprecated API-only scripts and
points to the credit-free route.

## The triplet pattern

Each converted stage is three pieces (reference impl: triage):

| Piece | Role | API? |
|---|---|---|
| `scripts/<stage>_prepare.py` | deterministic — build a bundle from disk artifacts | none |
| `.claude/skills/<stage>/SKILL.md` | in-session reasoning → writes canonical artifacts / `_decisions.json` | none (runs in Claude Code) |
| `scripts/<stage>_write.py` | deterministic — validate + finalize, never silent | none |

## Stage → route map

| Stage | Route | Status |
|---|---|---|
| Step 0 deep analysis | `/deep-analysis` (`deep_analysis_prepare.py` → skill → `deep_analysis_write.py`) | **converted (P0)** |
| Step 2 specialists | `/ite-audit` + `agents/*.md` (read source + MCP tools) | already in-session |
| Step 2.5 cross-agent | `optional_llm` skip (deterministic merge carries) | clean-skip; `/synthesis` planned P1 |
| Step 3 compound synth | `optional_llm` skip | clean-skip; `/synthesis` planned P1 |
| Step 3.5 multi-pass confirm | `optional_llm` skip | clean-skip; `/confirm` real conversion planned P1 |
| Step 4 triage | `/triage` (`triage_prepare.py` → skill → `triage_write.py`) | already converted |
| Step 5 severity/dupe/exploitability/judge/reference-diff | — | **deferred P1** (off the review_gate path) |
| PoC generation | — | **deferred P2** |
| FP autopsy | — | **deferred P2** |

MCP tools (`kb-search`, `onchain-context`, `immunefi-audit-competitions`) are credit-free and used by
the in-session skills/agents.

## API-free run flow

```
./run_pipeline.sh analyze <contract>      # scope + sandbox + static + deep_analysis_prepare → PAUSE
/deep-analysis                            # (Claude Code) writes invariants / interactions / threads / deep-trace findings
./run_pipeline.sh analyze-resume <contract>  # validate Step 0 → brief → defense → context pack
/ite-audit                                # Step 2 specialists (parallel, in-session)
./run_pipeline.sh full                    # 2.5/3/3.5 skip cleanly → gates → triage_prepare → PAUSE
/triage                                   # (Claude Code) re-derive ICE, write decisions
python scripts/triage_write.py            # canonical triage buckets
./run_pipeline.sh review-gate             # PoC queue + review_gate.md → PAUSE
```

Hooks keep the flow on-track: the **SessionStart** banner shows the stage→skill preflight and any
`⏸ skill pending` cue; the **Stop** hook (`next_skill_reminder.py`) reminds which `/skill` is next
when the pipeline is parked at a pause.

## Verifying api-free

```
python scripts/check_api_free.py          # critical path safe (exit 0)
python scripts/llm_runtime.py             # preflight: every stage "use /skill" or "SKIP optional"
python scripts/llm_runtime.py --have-key  # exit 1 (no API path)
```
