# P197 integrity checks (documentation + selection only)

Hashes are md5sum first-8. P197 wrote only its deliverable dir (4 docs). No code, config, prompt, detector,
routing, answer-key, corpus, or disposition change; no model runs; **no sealed answer key unsealed**.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` (P194) | `3b0b2c02` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| all `_sealed_answer_key/` dirs (centrifuge/badger/kleidi + others) | unread, unchanged (seals intact) |
| corpora / answer keys / dispositions / manifests / configs | unchanged |
| P183–P196 deliverables | unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / honesty
- Corpus selection is from a **read-only survey** (answer-key path, source file+LOC counts, `_sealed_answer_key`
  presence, `findings_deep_trace` count). Sealed answer-key finding counts are kept `UNKNOWN` — not opened, not
  inferred as fact (richness inferred from protocol type, flagged as a caveat).
- No production routing/conduct change. `fabrication_rate=0`. All P197 JSON validates.

## Deliverables
`SUBARC_CLOSEOUT.md`, `fresh_corpus_shortlist.json`, `P197_RECOMMENDATION.md`, `integrity_checks.md`.
