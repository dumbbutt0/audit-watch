# P190 integrity checks (read-only upstream funnel analysis)

Hashes are md5sum first-8. P190 wrote only its deliverable dir + `scripts/validate_p190.py`. No production /
prompt / detector / routing / answer-key / corpus / disposition / manifest edits.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| zaros `coverage_manifest.json` / `coverage_dispositions.json` | `ca2e69c6` / `5f76e9fc` (read-only) |
| P189 deliverable `metrics.json` | unchanged (read-only) |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / evidence discipline
- `scripts/validate_p190.py` reads each corpus's answer key, match matrix, coverage_manifest, candidate_queue,
  coverage_dispositions, findings_deep_trace + the 13 frozen P189 outcomes; it writes only the P190 JSON
  deliverables. No corpus/answer-key/disposition/manifest mutation.
- **Every per-finding label carries its artifact evidence** in `loss_funnel.json` (stageA/B/C outcomes,
  awarded_manifest_id, queue score, P189 outcome). Insufficient evidence → `NEEDS_EVIDENCE`, never inferred
  (10 rows, 8.8%).
- `fabrication_rate=0`. All P190 JSON validates.

## Known measurement caveats (also in the report)
- DISCOVERY_GAP is split in `metrics.discovery_breakdown`: genuine NOT_DISCOVERED = 8 (7.0%) vs
  DISCOVERED_CONTRACT_ONLY = 50 (43.9%, locus-noise-prone). The matching-robust headline is the loss-phase split
  (87.7% upstream of deep-pass).
- Stages D–F resolved only via the 13 P189 re-adjudications; the rest of the post-deep slice is `NEEDS_EVIDENCE`.
- A `contracts_of()` parsing fix was applied during the run (bare-identifier `affected` like "V3Vault" now treated
  as a contract) after revert-lend initially mis-scored 27/27 DISCOVERY_GAP; the corrected run cross-checks against
  P189 (revert-lend ≈19 findings reach queue, consistent with P189's 17 deep-run-misses).
