# P295 — SETUP

**Phase:** Corpus-wide open recall — measure recall-of-confirmed toward 100% (measurable subset, surfacing-first).
Research-only, advisory, production authority WITHHELD.

## Scope (chosen via AskUserQuestion)
- Measure & drive on the **locally-answer-keyed subset** (strict-eval answer keys are sealed):
  kelp/ecg/salty (locus-level `reveal_score.json`), blackhole (p286/p281 loci), beanstalk (ground_truth, finding-level).
- **Surfacing-first:** establish recall-of-surfaced (the ceiling the verifier could ever confirm) before chasing
  recall-of-confirmed (can't confirm an un-surfaced bug).

## New files only (zero edits to existing modules → no hash cascade)
- `scripts/research/recall_of_confirmed_corpus.py` — the funnel harness.
- `config/research_recall_corpus_map.json` — subset audits + awarded-locus → poc-dir map + reveal/ground_truth paths.
- `poc_manifest.json` added to `pocs/p287/kelp/...` and `pocs/p281`; new climb PoC `pocs/p295/ecg_stake/`.
- minor L1/L2 strengthening of the p287 + p281 exploit tests (faithful named before/after + attacker prank).
- `tests/research/test_p295_recall_of_confirmed_corpus.py` + this docs dir.

## Reused (byte-identical)
P294 `executed_poc_verifier.py` (the FP oracle), forge 1.5.1, the reused PoC scripts, forbidden 5.
Answer keys (`reveal_score.json` / `ground_truth.jsonl` / `match_matrix.json`) are READ-ONLY.

## Reproduce
`python3 scripts/research/recall_of_confirmed_corpus.py` (runs the verifier over the mapped poc dirs via real forge).
