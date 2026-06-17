# P192 integrity checks (read-only resolution + selection audit)

Hashes are md5sum first-8. P192 wrote only its deliverable dir + `scripts/validate_p192.py`. No production /
prompt / detector / routing / scoring / answer-key / corpus / disposition / manifest edits.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| P190 `loss_funnel.json` / P191 `discovery_resolution_audit.json` (read-only inputs) | `a65d8c88` / `83fe9831` |
| each corpus manifest / candidate_queue / dispositions / deep-trace / answer-key / eval_findings | read-only, unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / evidence discipline
- `scripts/validate_p192.py` reads P190/P191 outputs + corpus artifacts and writes only the P192 JSON
  deliverables. No model runs; no corpus/answer-key/disposition/manifest mutation.
- **Every recovered match cites an artifact**: Tier-0 manifest id; Tier-1 the normalized form; Tier-2 the difflib
  pair within the resolved contract; Tier-3 the exact field (`answer_key.title/alt_titles` or
  `eval_findings.match_terms`) that contained the manifest function name. Tiers never cross-contract except via an
  explicit artifact alias.
- Unknowns kept `UNKNOWN`: Tier-4 `UNRESOLVABLE` (27); Question-B `UNKNOWN_no_deep_pass_executed` for zaros/ark.
- `fabrication_rate=0`. All P192 JSON validates.

## Scope notes (also in the report)
- Question A ladder run over all 114 unresolved findings; metrics focus on the 59 P190 `DISCOVERY_GAP` rows.
- Question B restricted to `kind=function` (the `assigned_pass='deep'` tag also marks constants/immutables — that
  confound is excluded). Genuine only for revert-lend (INCONSISTENT) + panoptic (CONSISTENT).
- Tier-2 fuzzy + Tier-3 alias are candidate-grade recoveries, reported apart from the 2 exact/normalized.

## Deliverables
`locus_resolution_audit.json`, `selection_consistency.json`, `metrics.json`, `P192_REPORT.md`,
`integrity_checks.md`.
