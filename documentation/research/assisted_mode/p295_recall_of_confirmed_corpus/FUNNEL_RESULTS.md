# P295 — FUNNEL_RESULTS

Measurable subset (locally-answer-keyed). Confirmation = real forge exploit PASS (L1+L2+L3). FP=0 by construction.

## Aggregate (full_local denominators: kelp+ecg+salty+beanstalk)
- awarded **29** · surfaced **25** · confirmed **4**
- **recall_of_surfaced = 0.862** (the open-recall ceiling)
- **recall_of_confirmed = 0.138** (the metric driven toward 1.0)
- confirmation_yield_on_surfaced = 0.16
- **total loci confirmed by execution = 6** (incl. blackhole partial_local: ['blackhole-2025-05-eval:M-04', 'blackhole-2025-05-eval:L2Gov'])
- **confirmed_false_positive_count = 0**

## Per audit

| audit | denom | awarded | surfaced | confirmed | recall_surf | recall_conf | confirmed loci |
|---|---|---|---|---|---|---|---|
| kelp-2023-11-holdout | full_local | 5 | 4 | 1 | 0.8 | 0.2 | H-01 |
| ecg-2023-12-holdout | full_local | 6 | 6 | 1 | 1.0 | 0.167 | H-04 |
| salty-2024-01-holdout | full_local | 6 | 3 | 2 | 0.5 | 0.333 | H-02,H-04 |
| blackhole-2025-05-eval | partial_local | 2 | 2 | 2 | 1.0 | None | M-04,L2Gov |
| beanstalk-2024-05 | full_local | 12 | 12 | 0 | 1.0 | 0.0 | - |

## The gap to 100% is CONFIRMATION, not surfacing
- recall_of_surfaced **0.862** vs recall_of_confirmed **0.138**: open recall surfaces most awarded loci; only those with a passing PoC are confirmed.
- backlog: **21 surfaced-but-unconfirmed** (PoC worklist for the verification-agent loop) + **4 missed** (surfacing worklist).

## Climb this phase
- P294 confirmed 2 loci; P295 wired 4 (blackhole claim_many, salty _increaseUserShare H-02/H-04, kelp H-01, L2Governor) and built a NET-NEW confirmation: **ecg H-04 SurplusGuildMinter.stake** (incomplete same-block-only loss guard) → confirmed_by_execution. Total confirmed loci = 6.
- The refutation control (salty Pools.deposit) stays refuted_by_execution → not confirmed.
