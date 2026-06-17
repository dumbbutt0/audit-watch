# P193 integrity checks (read-only extraction-failure analysis)

Hashes are md5sum first-8. P193 wrote only its deliverable dir + `scripts/validate_p193.py`. No production /
prompt / detector / routing / extraction / answer-key / corpus / disposition / manifest / queue edits.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| P192 `locus_resolution_audit.json` (read-only input) | `462bebb3` |
| corpus manifests / candidate_queue / dispositions / deep-trace / answer-keys / eval_findings | read-only, unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / evidence discipline
- `scripts/validate_p193.py` reads P190/P192 outputs + corpus artifacts and writes only the P193 JSON
  deliverables. No model runs; no corpus/answer-key/disposition/manifest mutation.
- **Every recovery cites the exact artifact field** that contained the function name (`answer_key.title` /
  `answer_key.alt_titles` / `eval_findings.match_terms` / normalized form / difflib+prefix). Unknowns kept
  `UNKNOWN` (the 27 unresolvable). `fabrication_rate=0`. All P193 JSON validates.

## Honesty (required, mirrored in the report)
- A shrunk discovery bucket is a **measurement** correction, not recall; recovered loci are **not** newly found
  bugs. Question-B AFTER redistributes findings into routing/deep-pass buckets (the real smaller bottleneck) and
  claims no catch.
- 30/32 recoveries are zaros → alias buckets are zaros-specific; reported per-corpus.
- Tier-2/Tier-3 recoveries are candidate-grade; high-confidence (exact/normalization) is a small minority.

## Deliverables
`EXTRACTION_ANALYSIS.md`, `extraction_failure_taxonomy.json`, `before_after_metrics.json`,
`automation_candidates.json`, `integrity_checks.md`.
