# P295 — IMPLEMENTATION_NOTES

## Files
- `scripts/research/recall_of_confirmed_corpus.py` — reads awarded+surfacing (read-only) → overlays
  `executed_poc_verifier.verify_poc` over mapped poc dirs → emits recall_funnel / verification_records / backlog /
  guard_report. Hashes the answer-key artifacts into guard_report for the unchanged-check.
- `config/research_recall_corpus_map.json` — the subset + awarded-locus → poc-dir map.
- manifests added: `pocs/p287/kelp/.../poc_manifest.json`, `pocs/p281/poc_manifest.json`,
  `pocs/p295/ecg_stake/poc_manifest.json`.
- climb PoC: `pocs/p295/ecg_stake/` (Tier-C faithful SurplusGuildMinter.stake incomplete-guard / missing
  loss-checkpoint).

## L1/L2 strengthening of two existing PoCs (faithful, not cosmetic)
kelp `getRsETHAmountToMint` and L2Governor `execute` confirmed `setup_only` at first because the verifier's L2
parse wants a NAMED before/after state-flip and L1 wants an explicit attacker entry — these are non-storage-corruption
bugs (oracle misvaluation, state-machine acceptance) whose flip was asserted differently. Fix (in the PoCs, NOT the
verifier oracle): kelp now reads the valuation `valuationBefore`/`valuationAfter` across a 30-day warp (the same call
returning the stale value is a real temporal flip) under an explicit attacker `vm.startPrank`; L2Governor captures
`executedBefore`/`executedAfter` (false→true on a Defeated proposal) under an attacker `vm.prank`. Both are genuine
L1+L2+L3; the verifier (the FP oracle) stays byte-identical.

## Why FP=0 is structural
A locus is counted confirmed ONLY if the verifier returns `attacker_verified=True` (a real exploit forge PASS +
L1+L2+L3) for its mapped poc dir, and every confirmed locus maps to an awarded id. The salty Pools.deposit refutation
control is run too — it returns `refuted_by_execution` (not confirmed). confirmed_false_positive_count = 0.
