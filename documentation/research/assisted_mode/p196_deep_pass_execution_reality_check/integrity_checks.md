# P196 integrity checks (read-only execution reality check)

Hashes are md5sum first-8. P196 wrote only its deliverable dir + `scripts/validate_p196.py`. No production /
prompt / detector / routing / selector / config / answer-key / corpus / disposition edits; no model runs.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` (P194) | `3b0b2c02` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| `config/runtime_policy.json` | `bea43487` (read-only) |
| `config/agent_policy.json` | `c65957b8` (read-only) |
| corpus deep-pass / budget / dispositions / deep-trace artifacts | read-only, unchanged |
| P190–P195 deliverables | unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / evidence discipline
- `scripts/validate_p196.py` reads budget summaries, executed_deep_passes, findings_deep_trace,
  skipped_deep_passes_with_reason, candidate_queue, `runtime_policy.api_free`, `agent_policy.coverage_policy`
  across all ~38 audits; writes only the P196 JSON + report. No model runs; no mutation.
- **Two mechanisms reported separately** (A budgeted executor vs B in-session deep-trace), each artifact-cited.
  Unknowns stay `UNKNOWN`. `fabrication_rate=0`. All P196 JSON validates.

## Key recorded facts
- Mechanism A executed_anywhere = **false** (0 in every run/run-type).
- Mechanism B (`findings_deep_trace`) present in **11 eval runs / 51 findings**, **0** in holdout(18)/fresh(18)/bench(3)/other.
- `api_free=true`; `deep_pass_high_priority_block_strict_full_audit=true`, `waiver_discipline_strict_full_audit=true`.
- Decision: `MIXED_BEHAVIOR`; no production execution gap worth fixing; close the sub-arc.

## Deliverables
`EXECUTION_REALITY_CHECK.md`, `run_execution_matrix.json`, `skip_reason_taxonomy.json`, `metrics.json` (aux),
`integrity_checks.md` + `scripts/validate_p196.py`.
