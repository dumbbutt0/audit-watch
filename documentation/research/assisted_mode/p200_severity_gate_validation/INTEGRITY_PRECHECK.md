# P200 — integrity precheck

## START hashes (md5sum first-8) — recorded before any P200 action
| artifact | START | expected (P199 END) | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |

All four byte-identical to the P199 END state → no drift since P199.

## Seal status (badger-2024-06-holdout)
- `audits/badger-2024-06-holdout/_sealed_answer_key/` present and **unopened** at precheck:
  `report.md` (48820 bytes), `data/` (56 submissions), `README.md` (7229 bytes — contest overview, NOT read at
  precheck). Treated as sealed until the documented controlled unseal (Step 2 = count-only; Step 6 = full).
- The `report.md` finding bodies are not read until **after both freezes** (Step 6).

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact, unchanged.

## Corpus (source, NOT sealed)
`badger-2024-06-holdout` eBTC core: **32 `.sol` / 9377 LOC** in scope (excluding `Dependencies/`, test, mock,
interface). Substantial, severity-rich CDP system → suitable to test High-vs-Medium separation.

## END re-check
Recorded in `integrity_checks.md` at phase close — must show START==END for all four artifacts.
