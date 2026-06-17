# P298 — SETUP

**Phase:** First end-to-end eval against a LOCAL answer key — beanstalk-2024-05. Research-only, advisory, authority
WITHHELD. Three axes: **answer-key recall/precision**, **novelty**, **executed-PoC validity**.

## Framing (honest)
- **Discovery is PRE-EXISTING** (44 merged findings + static.json from the prior eval2/beanstalk_finale run). This
  evals the existing output with the CURRENT stack; it is NOT a fresh blind discovery.
- **Answer key = 81 public findings** (`evals/beanstalk_finale/match_matrix.json`, scored by the prior eval2 semantic
  judge) + `ground_truth.jsonl` (12 platform_confirmed accepted). **Read-only — used only to score.**
- **Validity** (user-resolved): finish the chain with a Tier-C executed PoC where faithfully mockable; evidence-bundle
  + `needs_execution` (NOT confirmed) for the entangled tail; tractable batch this run. confirmed = executed PASS only.
- No active-audit switch; eval artifacts under this dir + PoCs under `pocs/p298/`; symlink stays at size-credit.

## New files (no existing module edited → zero cascade)
`scripts/research/beanstalk_eval_score.py` (answer-key scorecard) · `beanstalk_eval_novelty.py` (KB sim) ·
`beanstalk_eval_validity.py` (P294-verifier judge over pocs/p298 + evidence-bundles) ·
`config/research_beanstalk_eval.json` (paths + 12 validity targets w/ build_mode) · `pocs/p298/*` (5 Tier-C PoCs) ·
test + docs + outputs. Reuses P294 `executed_poc_verifier`, the kb-search + immunefi MCPs (both verified live).

## Reproduce
`beanstalk_eval_novelty.py` → `beanstalk_eval_validity.py` → `beanstalk_eval_score.py`.
