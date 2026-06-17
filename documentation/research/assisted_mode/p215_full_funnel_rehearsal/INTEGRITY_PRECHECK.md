# P215 — INTEGRITY PRECHECK (START hashes)

**Captured:** 2026-06-06, before any run step. md5 first-8 (file) / first-12 (trees & seal).

## Production code & config (must be byte-identical START==END)

| File | START hash |
|------|-----------|
| `prompts/deep_trace.md` | `ef93a6c2` |
| `scripts/min_confirm_gate.py` | `41dd3c96` |
| `scripts/confirm_gate.py` | `4fadfc5f` |
| `scripts/submission_readiness_review.py` | `e4960878` |
| `scripts/dashboard.py` | `197ac4d5` |
| `scripts/validate_p208_l3_readiness.py` | `fe37e6ad` |
| `documentation/.../p208_l3_high_policy_dryrun/L3_READINESS_SCHEMA.json` | `415d3eeb` |
| `scripts/final_submission_pack.py` | `57cba16d` |
| `scripts/audit_manager.py` | `1fca3bcb` |
| `scripts/audit_context.py` | `38f31838` |
| `scripts/triage_write.py` | `3c16f0d4` |
| `config/runtime_policy.json` | `bea43487` |
| `config/agent_policy.json` | `c65957b8` |
| `data/fp_autopsies/rejection_rules.jsonl` | `598f9318` |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |

The first 7 hashes match the post-P214 production state recorded in memory (deep_trace `ef93a6c2`,
min_confirm `41dd3c96`, confirm_gate `4fadfc5f`, submission_readiness `e4960878`, dashboard `197ac4d5`,
validate_p208 `fe37e6ad`, schema `415d3eeb`). The campaign ledger reads `e23c5bc9` — this differs from the
older P214-era recorded value, i.e. it was appended between phases by other work. **P215 will not touch it;**
END must equal this P215 START value (`e23c5bc9`).

## Target (rehearsal corpus) — recorded for tamper-evidence

| Item | START value |
|------|-------------|
| In-scope source tree `audits/zetachain-2023-10-holdout/contracts/**/*.sol` (37 files) | `5a215a698e1a` |
| Sealed answer-key dir top-level listing | `77caf9cfbeb0` |
| Sealed `report.md` content md5 (marker only, **not read**) | `5cf9c263d432` (401033 B) |
| `config/active_audit.json` (to restore) | audit_id = `quantamm-2024-12-eval`, switched_at `2026-06-04T19:11:51Z` |
| Source commit (from sealed-key git log line) | `be8cdbf` "Report for 2023-11-zetachain" |

## Holdout working-substrate START snapshot (expected to grow; pre-staged blind bundles must be preserved)
`output/coverage_manifest.json` `7850867f…`; 34 pre-staged blind deep_pass bundles
`output/deep_pass/_bundles/dp_0000..dp_0033.json` + `index.json` `9ffa6f72…`; `candidate_queue.json` `17710f1a…`;
`candidate_queue_bridge_recall.json`. `data/triage/` empty at START. These bundle hashes are recorded in the
run log; P215 **adds** `findings_deep_trace.json`, `merged_findings.json`, triage buckets, gate outputs — it does
**not** overwrite the pre-staged blind bundles.

## Core in-scope build facts
- Solc **0.8.7** for core EVM+ZEVM (`ERC20Custody`, `ZetaConnector*`, `ZetaInteractor`, `ZRC20`, `SystemContract`).
- `WZETA.sol` legacy `^0.4.18` (WETH-style).
- Framework: foundry (per `meta.json`).
