# P288 — DISCOVERY_AND_ROUTING (blind, ecg-2023-12-holdout)

Frozen blind chain on the existing coverage_manifest (no answer-key access).

## Results
- Advisory candidates (P264 shadow): **23**.
- Coverage classes routed (P273): ACCOUNTING_LIQUIDATION_BAD_DEBT · REWARDS_CLAIMS · SHARE_ROUNDING_PRECISION ·
  STATE_MACHINE_LIFECYCLE · UNKNOWN_OTHER (5 classes — richer class spread than kelp's 3).
- Triage (P269): 6 advanced.
- Validation queue (P278): **8** candidates, 5 classes, max_class_fraction 0.25, anti-monoculture OK, 0 injected.
- Guard: PASS (advisory/research_only; no leakage).

## Validation queue (8)
SurplusGuildMinter.stake (SHARE_ROUNDING) · ERC20RebaseDistributor._burn (SHARE_ROUNDING) ·
ERC20RebaseDistributor.distribute (REWARDS) · LendingTerm.onBid (UNKNOWN) · ProfitManager.claimRewards (REWARDS) ·
LendingTerm.borrow (ACCOUNTING) · LendingTerm._borrow (ACCOUNTING) · SimplePSM.redeem (STATE_MACHINE).

The surface routed to the credit-guild core (lending terms, surplus/guild staking, rebase distribution, profit/rewards,
PSM) — a sensible attack surface for a credit protocol. No answer key consulted.
