# P158 — Integrity Checks

| Claim | Verification | Result |
|---|---|---|
| Production source unchanged | no `audits/**/contracts/**` edits | ✓ |
| Value-provenance sidecar unchanged | `runtime_status.jsonl` not edited (H6 had no runtime PoC) | ✓ `491da8c1…` (H1–H5 byte-identical) |
| Value-provenance harness logic unchanged | `value_provenance_eval_harness.py` not edited | ✓ |
| Prompt baseline / detectors / gates / routing / severity / submission / selection code | not touched | ✓ |
| Corpus unchanged | `frozen_corpus.json` | ✓ `60089ff5…` |
| Panel/scorecard prompt metrics unchanged | `scorecard.json` | ✓ `70f4c44d…` |
| Active audit symlink unchanged | `readlink output` | ✓ `audits/quantamm-2024-12-eval/output` |
| New campaign tool un-wired | `grep option_a_campaign run_pipeline.sh config/agent_policy.json` | ✓ empty |
| value_provenance harness still un-wired | `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` | ✓ empty |
| Ledger never asserts authority | every row forced `research_only=true / routing_allowed=false / submission_ready=false` | ✓ |
| Sealed answer key not opened | `_sealed_answer_key/` untouched | ✓ |
| No PoC deployed/run | no `pocs/p158/` created | ✓ (runtime not_run) |

## Files added (research/docs only — none production)
- `scripts/research/option_a_campaign.py` (tiny, un-wired) · `output_research/option_a_campaign/ledger.jsonl`
  (H5 backfill + H6) · `tests/research/test_option_a_campaign.py` (4 tests) ·
  `documentation/research/assisted_mode/p158_pooltogether_prizevault_erc4626/*`.

## Tests
- New campaign tests: **4 passed**.
- Full `pytest`: expected **1687 prior + 4 new = 1691 passed / 2 pre-existing deep_solidity snapshot fails /
  4 skipped** (no production/test baseline change). Recorded in the closeout.
