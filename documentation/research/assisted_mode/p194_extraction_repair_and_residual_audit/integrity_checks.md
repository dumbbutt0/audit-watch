# P194 integrity checks (eval-harness repair + residual audit)

Hashes are md5sum first-8. P194 added a new **eval-harness** module + tests + read-only validation + docs. No
production / prompt / detector / routing / severity / dashboard change; no answer-key / corpus / disposition /
manifest mutation.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| zaros answer key | `24ad4ebd` (unchanged) |
| revert-lend answer key | `ff124c6e` (unchanged) |
| per-audit `build_answer_key.py` snapshot | `7f2af8ed` (NOT rewritten) |
| corpus manifests / dispositions / deep-trace | read-only, unchanged |
| P190–P193 deliverables | unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## New code (eval-harness only)
- `scripts/eval_locus_resolver.py` — carries `EVAL_HARNESS_ONLY=True` / `ROUTES_IN_PRODUCTION=False`.
  **Un-wired:** `grep "eval_locus_resolver"` across `run_pipeline.sh` / `scripts/` (non-self) / `prompts/` /
  `agents/` / `config/` returns only the module, its test, and `validate_p194.py`. It sets no severity, routes
  nothing, mutates nothing, mints no findings.
- `tests/eval/test_eval_locus_resolver.py` — 9 cases, all green (direct/alt_title/normalization, generic-token
  rejection, ambiguous multi-match no-autoselect, contract-constrained, no-fuzzy-auto, match-term-verbatim,
  flags).
- `scripts/validate_p194.py` — read-only before/after + residual audit.

## Read-only / honesty discipline
- Every recovery cites the exact answer-key field. AMBIGUOUS never auto-selects; get/set/fuzzy → REVIEW_GATED.
- Residual `TRUE_COVERAGE_GAP=0` is **artifact-confirmable**, established by **source inspection** that refuted the
  9 initial candidates (contracts/events/state-vars). 5 residual kept `NEEDS_HUMAN_MAPPING` (`UNKNOWN`, not
  inferred). `fabrication_rate=0`.
- Tests: `tests/eval` 9 + `tests/deep_solidity` adjudication 10 + checker 8 = 27 passed (no regression). All P194
  JSON validates.

## Deliverables
`EXTRACTION_REPAIR_REPORT.md`, `before_after_resolution.json`, `residual_source_audit.json`,
`automation_decisions.json`, `integrity_checks.md` + `scripts/eval_locus_resolver.py` +
`tests/eval/test_eval_locus_resolver.py` + `scripts/validate_p194.py`.
