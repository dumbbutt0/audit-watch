# P252 — Setup & Frozen-System Attestation

Controlled forward-blind A/B experiment: does enabling the accounting + state-transition checkpoints produce
real recall lift on unseen code, vs a P245-only baseline?

## Target (per spec criteria; selection delegated to me)
`salty-2024-01-holdout` — Salty.IO AMM + staking + DAO governance. **Unseen** (no findings/revealed/local
key); not in P249/P250/P251 dev set, not P246/P240/P241, not reNFT/spectra. Medium (6.9k LOC). Chosen as the
**richest available state-transition surface** (governance proposals/votes, staking unstake state machine,
reward cooldowns) → the fairest in-domain test for the state-transition checkpoint (P250 failed precisely
because spectra had no in-domain awards). Not a pure accounting vault.
- **Coverage honesty:** 371 in-scope / 254 critical. The state-transition core was read in full (Staking,
  StakingRewards, SaltRewards, Proposals, DAO). P245 is enabled IDENTICALLY in both arms, so coverage scope
  does not bias the A/B delta. Answer key web-fetched (Code4rena 2024-01) only AFTER both arms freeze.

## Frozen system (no edits; forbidden files byte-identical)
`c1af70e1` dashboard_sync · `c095c426` deep_trace · `2a15169a` min_confirm_gate · `afc481c9` confirm_gate ·
`ae55eb80` validate_p208. Active audit `size-credit-2024-06-blind` unchanged (checkpoints run via `--manifest`).

## Two arms (frozen before reveal)
- **Arm A (baseline):** P245 enabled; accounting + state-transition checkpoints DISABLED. Genuine unaided
  hunt → base candidates. Frozen + hashed BEFORE any checkpoint runs (keeps the baseline uncontaminated).
- **Arm B (checkpoints):** P245 + accounting (`accounting_checkpoint_audit.py`) + state-transition
  (`state_transition_checkpoint_audit.py`) enabled. Arm B = Arm A ∪ checkpoint-forced candidates, each tagged
  NEW (absent from Arm A) or REINFORCED.

## Honesty (critical, per spec)
Success = ONLY awarded-equivalent exploit chains the checkpoint **creates or completes on unseen code** — NOT
replay recovery, candidate count, or question count. Same-LLM-both-arms contamination is stated: Arm A is a
genuine best-effort baseline frozen before checkpoints; CHECKPOINT_ONLY requires the awarded finding to be
absent from the frozen Arm A. salty is public → absolute recall is an upper bound; the A/B delta is the
confound-lighter signal. A null/negative result (B/C) will be reported honestly.
