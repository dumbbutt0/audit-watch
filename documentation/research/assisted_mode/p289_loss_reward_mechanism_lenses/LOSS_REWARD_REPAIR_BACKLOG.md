# P289 — LOSS_REWARD_REPAIR_BACKLOG

## Lifted
- SurplusGuildMinter.stake (H-04) → READY via Lens 1. Next: a Tier-C PoC in a future sweep (intent recorded:
  `outputs/poc_intent_surplusguildminter_stake.json`).

## Still-blocked ECG awarded loci (precise, source-backed reasons → next repairs)
| awarded | locus | block reason | next repair | FP risk | prio |
|---|---|---|---|---|---|
| H-03 | LendingTerm.onBid | non-value class + D1 refute; Lens 2 needs the global-accumulator loss write which lives in a callee | extend Lens 2 over the P283 trace path (bad-debt write in a resolved callee) + allow UNKNOWN→ACCOUNTING reclass | MED | 1 |
| H-02 | ERC20RebaseDistributor.transfer | Lens 4 REFUTED (both-side materialization) — the theft is a subtler rebase share-accounting flaw | rebase-share-accounting sub-lens (share-price vs balance materialization ordering) | MED-HIGH | 2 |
| H-01 | ProfitManager.claimGaugeRewards | exact fn not surfaced (claimRewards surfaced); Lens 3 needs the per-user index init site | recall: surface claimGaugeRewards; Lens 3 over the accrual helper | MED | 3 |
| M-02 | RateLimitedMinter.mint | surfaced advisory, not queued | selection/queue (not a lens issue) | LOW | 4 |

## Lens hygiene
- Lens 4 marginally matched hybra GaugeCL.withdraw (held, 0 FP) — tighten to require a real transfer-hook/from-to move,
  not a withdraw. Prio 2.
- Lenses 2 & 3 fired nowhere in this sample (no FP, but unproven on a positive) — exercise them on a future target with
  a confirmed contagion / index-init award before crediting generalization.
