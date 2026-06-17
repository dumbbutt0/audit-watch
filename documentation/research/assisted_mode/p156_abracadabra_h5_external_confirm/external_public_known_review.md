# P156 — Gate 1: External Public-Known / Duplicate Review

## Question
Is the H5 mechanism — *an expired lock keeps the boosted reward weight until operator-gated
`processExpiredLocks`, redistributing rewards from honest stakers* — a public-known duplicate of a
Code4rena `2024-03-abracadabra-money` finding (or any public report)?

## Corpus reviewed (public)
The complete **20 awarded findings** (4 High + 16 Medium) of the C4 report, the C4 report page, the M-05
issue, and targeted web searches (see search_log.md).

| Finding | Contract | Mechanism | Same as H5? |
|---|---|---|---|
| H-01..H-04 | MagicLP / oracle / BlastOnboarding | TWAP exploit, rounding, deposit loss, oracle manip | No (not LockingMultiRewards) |
| M-05 | LockingMultiRewards | tokens locked longer than intended (missing deadline / `nextUnlockTime` epoch rounding) | No — about *unlock timing*, not boost-after-expiry |
| M-07 | LockingMultiRewards | reward-**rate precision loss** (reward/remaining-time rounding), shared loss | No — precision, **not** boost multiplier / expired locks |
| M-14 | LockingMultiRewards | cannot support native USDB/WETH | No |
| M-15 | LockingMultiRewards | Blast gas-yield mode not configured | No (config/QA) |
| M-16, others | MagicLP/Router/Factory/Onboarding | various | No |

## Result
No awarded finding (and none surfaced in the QA/Low set or issue search) describes expired-lock **boost
retention**, **reward redistribution to expired lockers**, or **balanceOf/totalSupply counting expired
locked balances as boosted**. Wardens *did* examine LockingMultiRewards reward accounting (M-07 precision)
and lock timing (M-05) — yet none reported the H5 mechanism.

## Important context (not a duplicate, but reduces novelty weight)
The contract is "Based from Convex CvxLockerV2 / Curve MultiRewards / Ellipsis EpsStaker" (NatSpec :11-13).
The lock-boost + lazy operator/keeper expiry design is a **public, well-known pattern**; H5 is a consequence
of that public design applied to this contract's reward accounting.

## Classification: **public_known_but_not_duplicate**
The contract and its reward accounting are publicly audited (multiple awarded findings), and the design
lineage is public — but **no public duplicate of H5's specific mechanism was found**. Not
`novelty_clear_external_reasonable_search`: the full ~200-issue raw submission set + complete QA report were
not line-by-line exhausted, so a non-awarded (dup/QA/invalid) submission cannot be 100% excluded. Not
`duplicate_found_*`: nothing matching was located. H5's **distinct angle** vs the public set = the
reward-fairness consequence of *expired-but-unprocessed* boosted weight (orthogonal to M-05 timing and M-07
precision).
