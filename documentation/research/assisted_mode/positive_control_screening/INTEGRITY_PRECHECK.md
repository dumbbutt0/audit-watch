# PCS — integrity precheck

## START hashes (md5sum first-8) — before any screening action
| artifact | START | expected | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |

No production artifact is run or modified in this phase (deep_trace/checker recorded for discipline only).

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact.

## Seal status (candidates, unopened at precheck)
- `decent-2024-01-holdout/_sealed_answer_key/report.md` — present (4H/5M)
- `munchables-2024-05-holdout/_sealed_answer_key/report.md` — present (2H/4M)
- `vultisig-2024-06-holdout/_sealed_answer_key/report.md` — present (3H/3M)

Each is opened only via a controlled **title/summary-level unseal performed by a firewall screening subagent**
(not by the orchestrator). The orchestrator never receives verbatim High titles/mechanisms/loci (see
`SCREENING_PROTOCOL.md`).

## END re-check
Recorded in `integrity_checks.md` at phase close — START==END required for the four production artifacts.
