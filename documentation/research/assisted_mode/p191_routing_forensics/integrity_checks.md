# P191 integrity checks (read-only routing forensics)

Hashes are md5sum first-8. P191 wrote only its deliverable dir + `scripts/validate_p191.py`. No production /
prompt / detector / routing / ranking / answer-key / corpus / disposition / manifest edits.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| P190 `loss_funnel.json` (read-only input) | `a65d8c88` |
| each corpus manifest / candidate_queue / dispositions / deep-trace / call_graph | read-only, unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / evidence discipline
- `scripts/validate_p191.py` reads P190 outputs + the corpus artifacts and writes only the P191 JSON deliverables.
  No corpus/answer-key/disposition/manifest mutation; no model runs.
- **Every conclusion cites an artifact-derived score or routing record** (queue score, attack_surface_score,
  selected_by, manifest tags/file, call_graph chain). Unknowns are kept `UNKNOWN`
  (`UNRESOLVABLE_FROM_ARTIFACTS`, shared-state-vars `UNKNOWN`, zaros risk_score≡0).
- `fabrication_rate=0`. All P191 JSON validates.

## Corrections applied during the run (recorded for honesty)
- **Starvation logic fixed:** initial version used the deep-cutoff *rank* as the budget reference and reported all
  9 "recoverable at +1." Corrected to top-N-by-score (`deep_pass_slots_used`), revealing awarded fns out-rank
  deep-run siblings → deep-pass selection is not score-ordered (selection-logic problem, not budget).
- **Discovery categories fixed:** initial "genuine_function_gap" bucket was unmatched answer-key junk tokens
  (`solidity`, `abs`, …). Reclassified into `ANSWER_KEY_RESOLUTION_NOISE` / `UNRESOLVABLE_FROM_ARTIFACTS` /
  `answer_key_naming_drift` / `inherited` — no row is asserted as a demonstrable coverage gap.

## Deliverables
`ROUTING_FORENSICS.md`, `routing_pairs.json`, `score_attribution.json`, `similarity_analysis.json`,
`discovery_resolution_audit.json`, `starvation_analysis.json`, `metrics.json`, `integrity_checks.md`.
