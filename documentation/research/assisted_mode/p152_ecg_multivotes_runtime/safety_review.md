# P152 — Safety Review

## Hard constraints — all honored
- One fresh candidate, distinct mechanism class, not noya/blackhole/centrifuge/velodrome(/decent), `duplicate_unknown`
  (ecg holdout, no answer key). ✓
- Real-contract harness (real abstract `ERC20MultiVotes` inherited unmodified); corrected/expected-behavior +
  matched control + vulnerable reference included. ✓
- No production source edit — `ERC20MultiVotes.sol` byte-identical (18475 bytes); shim/ref/mocks in the test. ✓
- No harness-logic / prompt / detector / gate / routing / severity / corpus / symlink change (no `P152` ref in
  `value_provenance_eval_harness.py`). ✓
- **Corpus + prompt baseline byte-for-byte unchanged** — H4 is a sidecar **runtime-only** row, not in
  `corpus.jsonl`; `integrity.prompt_corpus_unchanged: true`; `totals` == P138 baseline; test
  `test_ecg_row_does_not_perturb_prompt_metrics`. ✓
- PoC isolated in `audits/ecg-2023-12-holdout/pocs/p152/`. ✓
- All rows `routing_allowed=false` + `submission_ready=false` (incl. H4 + the backfilled conversion rows). ✓
- Conversion schema added **data-only** (new H4 row + backfill on H1/H2/H3); no logic change. ✓
- Active `output/` symlink unchanged (`quantamm-2024-12-eval`); un-wired (grep-clean); P130–P151 untouched. ✓
- Not biased toward confirmation — the result followed the runtime (refuted); `duplicate_unknown` (no novelty). ✓

## Integrity / state
2 research-only artifacts changed (`runtime_status.jsonl`: +H4 row + conversion backfill on H1/H2/H3; the test:
+3) + the ecg `pocs/p152/` harness. No production source / harness-logic change. Full pytest 1673 passed
(1670 + 3) / 2 pre-existing deep_solidity snapshot fails / 4 skipped. Temp `lib/`/`out/` removed post-run. Writes
confined to `output_research/`, the holdout `pocs/p152/`, `tests/research/`, and the deliverables. No external docs.
