# P202 — integrity precheck

## START hashes (md5sum first-8)
| artifact | START | expected | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |
| `scripts/validate_decent_pc.py` (new harness) | `b1f62452` | (record) | n/a |

No production artifact is run or modified (deep_trace/checker recorded for discipline only).

## Seal status
`audits/decent-2024-01-holdout/_sealed_answer_key/report.md` — present and **unopened** at precheck (4H/5M from PCS
count-only). Opened in full only at scoring (Step 6), after FREEZE 1 + FREEZE 2.

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact.

## PCS preambles NOT persisted
`positive_control_screening/screening_outputs/{decent,munchables,vultisig}.json` verified to contain **tallies +
category tags + coarse domain notes only** — no finding titles, no finding-ID→mechanism mappings, no loci. The PCS
screening subagents' free-text reasoning preambles were **not written to any deliverable**.

## Contamination caveat (see CONTAMINATION_MITIGATION.md)
The orchestrator was **transiently exposed** to decent High file/mechanism hints during PCS. Mitigation: the refined
gate calibration is authored by a **fresh cold-start firewall subagent**, NOT the orchestrator. The orchestrator
performs only source-only sampling (broad) and post-freeze scoring (legitimately answer-aware).

## END re-check
Recorded in `integrity_checks.md` — START==END required for the four production artifacts.
