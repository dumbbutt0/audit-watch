# P198 integrity checks (campaign — controlled unseal)

md5sum first-8. Production stack used **read-only**; the only seal access was the documented Centrifuge unseal.

## START == END (byte-identical)
| artifact | START | END |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` |
| `_sealed_answer_key/_FIREWALL_SEAL.txt` | `cff15409` | `cff15409` (seal files unchanged) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged |

## Controlled unseal
- Stage A (viability): count-only read of `report.md` severity headers → 0 High / 8 Medium. No titles/bodies.
- Stage B (scoring): full `report.md` read **only after** all 12 blind prompts + raw outputs were frozen and
  token-scanned. `report.md` was **read, not modified** (hashes of seal files unchanged).

## Blind firewall
- 12 frozen blind prompts (`blind_prompts/`) = `deep_trace.md` + verbatim source; token-scanned before the run →
  zero finding-IDs / answer-key / report refs (only the prompt's own generic `awarded` menu words).
- 12 raw outputs (`raw_outputs/`) preserved verbatim; token-scanned → **zero answer-key IDs cited** (blind
  confirmed). Blind model = Sonnet (read only its single prompt).
- Scorer answer-aware only post-freeze; **no backfill**; in-sample MISS (M-04) and out-of-sample misses recorded
  honestly. `fabrication_rate=0`.

## Scope
No production/detector/routing/selector/prompt/script edits; no source/corpus mutation; no answer-key mutation
(read-only). New files: the P198 deliverable dir (+ `blind_prompts/`, `raw_outputs/`, `_sample_manifest.json`,
`_scoring_table.json`) and read-only `scripts/validate_p198.py`. All P198 JSON validates.
