# P275 — SELECTOR_OUTPUTS (Phase 3, frozen P267)

Frozen `mechanism_pairwise_selector.py` (`b0623b8c88752059`) over 3 B/C pairs from BLIND Katana-V3 source. Input
`outputs/selector_pairs.json`; output `outputs/selector_decisions.json` (`63eb68b8e688df02`). Guard: **0 violations**.

| slot | M1 (high-impact) | M2 (easy rival) | gap | anti-easy | outcome |
|---|---|---|---|---|---|
| access | `pool_swap_txorigin_auth` | `beacon_constructor` | 8 | yes | **SELECT_M1** |
| share/math | `pool_mint_burn_conservation` | `migrate_dust` | 7 | yes | **KEEP_BOTH** |
| order | `router_swap_auth` | `npm_mint_auth` | 0 | no | **KEEP_BOTH** |

## Reading
- The access pair dropped the trivial beacon constructor and kept the high-impact `tx.origin`-auth mechanism
  (SELECT_M1, anti-easy raised). The share/math pair kept both (anti-easy: dust rival is easier). The order pair is
  near-equal → KEEP_BOTH. No high-impact mechanism pruned for being expensive. Advisory contract stamped.

Next: Phase 4 — frozen P273 coverage router.
