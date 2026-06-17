# P296 — IMPLEMENTATION_NOTES

## Files
- `scripts/research/verification_agent_loop.py` — `emit` (specs) + `judge` (verifier overlay). judge() runs
  `executed_poc_verifier.verify_poc` over each `pocs/p296/<id>`, reads any `agent_report.json` as `agent_claimed`
  (advisory), requires manifest `assertion_map` for a clean confirmation, re-runs the p290 refutation control,
  computes pass = (attempted≥3 AND new_confirmations≥1 AND confirmed_FP==0), and updates the cumulative funnel
  (P295 baseline 6 + new).
- `config/research_verification_agent_loop.json` — 9-locus tractable allowlist with per-locus mechanism_hint +
  source_paths + manifest schema (incl. assertion_map) + pass_condition.
- PoCs built by spawned subagents under `pocs/p296/<audit>__<id>/` (foundry.toml + lib→pocs/p286/lib + test +
  poc_manifest.json with assertion_map + agent_report.json).

## This wave
Spawned 3 `general-purpose` subagents (clear-mechanism loci): ecg H-03 (onBid bad-debt cascade), ecg H-02
(ERC20RebaseDistributor.transfer reward theft), kelp H-02 (deposit-before-calc under-mint). All 3 wrote faithful
Tier-C PoCs that the verifier confirmed (3/3). The remaining 6 allowlisted loci are the next wave (not built this
phase — the relaxed bar is ≥3 attempted / ≥1 confirmed).

## Verifier-authoritative in practice
All 3 builders self-reported "confirmed" AND the verifier agreed (clean_confirmation=True, assertion_map present,
real logs). The judge-not-the-builder guard is proven by the synthetic test (`test_builder_claim_ignored_when_
exploit_fails`): a manifest claiming an exploit test that FAILS → verifier attacker_verified=False regardless of
agent_claimed. The assertion_map requirement is proven by `test_pass_without_assertion_map_is_unmapped`.
