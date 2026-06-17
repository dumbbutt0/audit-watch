# P155 — Gate 5: Novelty / Duplicate / Public-Known (local-only)

## Local surfaces checked
| Surface | Result |
|---|---|
| `audits/abracadabra-2024-03-holdout/findings/{raw,validated}` | **empty** |
| `…/notes`, `…/reports`, `…/data` | **empty** |
| `…/output/deep_pass/_bundles`, `_decisions.json`, `candidate_queue.json` | `LockingMultiRewards` functions (`balanceOf`, `totalSupply`, `withdrawWithRewards`) are **enumerated for coverage** (source snippets only). **No finding/decision describes the post-expiry boost-retention mechanism.** The "expired"/"boost" hits are the source code itself, not a prior identification. |
| `MEMORY.md` | abracadabra appears in **Phase 14b/14c/15** (used as a sampler/vocab **fresh holdout**). Phase 14c **read the C4 report** but recorded only **M-10 (`MagicLpAggregator._getReserves`)** — a **different contract**. No memory entry describes the H5 LockingMultiRewards expired-boost finding (other than P154/P155, which are mine). |
| sidecar `runtime_status.jsonl` | one abracadabra row = my H5 (P154). No other. |
| `data/evaluation` ground truth | no abracadabra match. |

## Material caveats (handed to the human)
1. **The contest is PUBLIC.** `meta.json` = Code4rena `2024-03-abracadabra-money`. The full findings list is
   publicly available; a prior report of this exact issue is **plausible** and must be checked externally.
   I have **no external search** here, so public-known status is **not assessable locally**.
2. **The project previously consulted this contest's report** (Phase 14c) and captured only M-10 (a
   different contract). That is *weak* evidence the H5 mechanism was not a headline finding, but it is **not
   conclusive** — Phase 14c recorded only what its sampler covered, not the full C4 finding set.
3. **The pattern is public.** The contract is "Based from … Convex CvxLockerV2 / Curve MultiRewards"
   (:11-13). Lock-boost with lazy `processExpiredLocks` expiry is a known design family; whether the
   *reward-weight-after-expiry* consequence was previously reported (here or upstream) is unknown locally.

## Classification: **duplicate_unknown** (public-known: **cannot_assess** locally)
No local duplicate of the H5 mechanism exists, but per the project rule novelty is **not** inferred from an
empty local record — especially since the contest is public and was previously consulted. `novelty_clear`
stays **unknown**; the human must run an external Code4rena/KB check before any novelty claim.
