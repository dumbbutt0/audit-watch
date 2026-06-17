# P189 integrity checks (read-only cross-corpus measurement)

Hashes are md5sum first-8. P189 wrote only new files under its deliverable dir + `scripts/validate_p189.py`.
No production / prompt / detector / answer-key / corpus / disposition edits.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` — used read-only inside blind prompts, not edited |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` — not edited |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Corpus inputs (read-only — recorded baseline, never written by P189)
| Artifact | md5 |
|---|---|
| zaros answer key | `24ad4ebd` |
| zaros match matrix | `56b0c155` |
| revert-lend match matrix | `3f6888a1` |
| panoptic match matrix | `71549033` |
| ark answer key | `0494c2fb` |

## Firewall (the decontamination guarantee)
- 13 blind prompts frozen BEFORE scoring; token-scan = zero finding-IDs / `answer key` / phase text (the only
  `awarded` hits are the production prompt's own generic menu wording, identical to P186).
- Blind selector = **Sonnet** (different from campaign Opus), each given ONLY its frozen prompt and instructed to
  read no other file.
- 13 raw outputs preserved verbatim in `raw_outputs/`; token-scan = **zero answer-key IDs cited** → blind
  confirmed at the output level.
- Scored answer-aware only AFTER all outputs frozen; **no backfill**; misses (incl. sibling-trace) recorded
  honestly. `fabrication_rate=0`.

## Read-only / honesty
- `scripts/validate_p189.py` recomputes the miss denominators from the corpora and reads the frozen outputs; it
  writes only the three P189 JSON deliverables. Corpus answer keys / match matrices / dispositions unchanged.
- before-rate = 0 by construction (denominator = misses); n≈4/corpus is an architecture-level signal, not a
  precise recall figure; Sonnet is same-vendor (residual caveat); 2 zaros items are sibling-traced (disclosed).
- All P189 JSON validates. 13 blind prompts + 13 raw outputs present.
