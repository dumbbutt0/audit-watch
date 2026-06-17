# P274 — SELECTOR_OUTPUTS (Phase 3, frozen P267)

Frozen `mechanism_pairwise_selector.py` (`b0623b8c88752059`) over 3 B/C top-2 pairs built from BLIND gondi source
reading (dimensions are source-derived, NOT award labels). Input `outputs/selector_pairs.json`; output
`outputs/selector_decisions.json` (+ `.md`). Guard: **0 violations**.

## Pairs and decisions
| slot | M1 (high-impact) | M2 (easier rival) | M1 ti | M2 ti | gap | anti-easy | outcome |
|---|---|---|---|---|---|---|---|
| accounting | `distribute_tranche_split` | `pool_redeem_rounding` | 9 | 2 | 7 | **yes** | **KEEP_BOTH** |
| order | `offer_validation` | `mergeTranches_grief` | 9 | 3 | 6 | **yes** | **KEEP_BOTH** |
| auction/state | `settleWithBuyout_auth` | `withdrawalqueue_liveness` | 9 | 9 | 0 | no | **KEEP_BOTH** |

## Reading
- The two pairs with a material impact gap (accounting, order) raised the **anti-easy-PoC flag** — the lower-impact
  rival (dust rounding, merge griefing) is easier to PoC, and the selector refused to drop the high-impact mechanism
  for it. This is the P266 trap held open by design.
- The auction/state pair is near-equal terminal impact, both plausible → KEEP_BOTH.
- Net effect: **all 6 mechanisms survive Phase 3** into the coverage stage; no high-impact mechanism is pruned for
  being expensive to prove. Advisory contract stamped (severity null, all promotion flags false,
  `ADVISORY_SELECTOR_DECISION`).

Next: Phase 4 — frozen P273 award-class coverage router.
