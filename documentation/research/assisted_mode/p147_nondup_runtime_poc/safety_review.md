# P147 — Safety Review

## Hard constraints — all honored
1. No submission. ✓
2. Not submission-ready (`submission_ready=false`). ✓
3. No detector logic changed. ✓
4. No severity logic changed (no severity assigned; severity deferred to human review). ✓
5. No submission logic changed. ✓
6. No production contract changed — real `UserEscrow.sol` byte-identical (2330 bytes); mocks/controls in the test
   only. ✓
7. No new detector. ✓
8. No auto-confirm of severity. ✓ (`runtime_confirmed` = mechanism evidence; intent/severity → human)
9. `runtime_status` separate from `submission_status`. ✓
10. `runtime_status` recorded separately (research sidecar + panel + P147 deliverable). ✓
11. **Prompt scorecard baseline byte-for-byte unchanged** — the holdout item is a **runtime-only** sidecar row,
    NOT in `corpus.jsonl`; `build_runtime_panel` surfaces it without touching `per_arch`/`totals`/`runs`
    (`integrity.prompt_corpus_unchanged: true`; test `test_runtime_only_does_not_perturb_prompt_metrics`). ✓
12. Honest filtering — design-intended paths (loopfi `claimFromConverter`/`getReward`) classified as **controls**,
    not bugs; `duplicate_status=duplicate_unknown` (no novelty/award claim); intent caveat flagged. ✓
13. Active audit + temp artifacts — no audit switched (holdout read by path; forge ran in its pocs dir); `output/`
    symlink still `quantamm-2024-12-eval`; temp `lib/`/`out/` removed post-run. ✓

## Research invariants
- Every panel row (incl. the runtime-only one) is forced `routing_allowed=false` / `submission_ready=false`
  (`integrity.routing_allowed_all_false` / `submission_ready_all_false` = true).
- Harness stays un-wired: `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty.
- All harness outputs carry the four research flags + `routing_allowed:false`.

## Integrity / state
4 research-only file groups changed (`value_provenance_eval_harness.py`, `runtime_status.jsonl`, the test, the
holdout `pocs/p147/`); no production source touched. Full pytest 1661 passed (1657 + 4) / 2 pre-existing
deep_solidity snapshot fails / 4 skipped. Writes confined to `output_research/`, the holdout `pocs/p147/`,
`tests/research/`, and the deliverables.
