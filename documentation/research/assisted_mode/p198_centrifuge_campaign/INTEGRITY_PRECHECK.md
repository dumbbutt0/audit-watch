# P198 — integrity precheck (START)

md5sum first-8, recorded before the campaign:
| artifact | hash | expected |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | ef93a6c2 ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | 5d2a97f9 ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | 3b0b2c02 ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | e23c5bc9 ✓ |

Seal status: `audits/centrifuge-2023-09-holdout/_sealed_answer_key/_FIREWALL_SEAL.txt` present ("SEALED — do not
open until queues frozen."); answer-key `data/` and `report.md` **unread** at precheck. END-of-run re-check
recorded in `integrity_checks.md` (all four byte-identical; seal files unchanged).
