# P144 — Attack-Path Hypotheses

## Nature of the bug
This is a **protocol-correctness defect**, not an attacker-controlled primitive. Routes are maintainer-set; an
external actor cannot configure or select a route. So the "attack" is **opportunistic value extraction once a
divergent ≥2-hop route exists** (which is an intended configuration), plus the systematic harm of a wrong vault
NAV.

## Path 1 — Opportunistic redeem against an over-valued position (strongest)
- **Prereq:** protocol has configured a ≥2-hop `priceRoute` for some holding token where hop i≥1 (`asset→sources[i]`)
  prices higher than the correct `quotingToken→sources[i]` ⇒ TVL over-stated.
- **Attacker assets:** vault shares (buy/deposit normally beforehand).
- **Functions:** `previewRedeem`/redeem path (`AccountingManager.sol:344`, consuming `totalAssets`=`TVL`).
- **State transition:** over-stated TVL → share price too high → redeem returns more base assets than fair.
- **Value movement:** excess assets to the redeemer; loss spread across remaining shareholders.
- **PoC coverage:** P143 proves the **oracle delta only**; the share-mint/redeem extraction is **NOT** PoC'd.
- **Missing proof:** a live divergent ≥2-hop route on a material token; an end-to-end deposit→skew→redeem test
  showing net gain > gas; bounding the extractable amount.

## Path 2 — Mint excess shares against an under-valued position
- Symmetric: a ≥2-hop route under-stating a token's value depresses TVL → `previewDeposit` mints too many shares;
  attacker later redeems at corrected/true value. Same prereqs and same missing proof; direction reversed.

## Path 3 — Distorted NAV / fees / deposit-limit (systemic, lower direct-theft)
- Wrong TVL also mis-states profit (`:577-583`) → performance-fee shares (`:483-484`) and the deposit limit
  (`:211`). Harm is dilution/accounting distortion rather than a single-tx theft.

## Path 4 — Swap slippage check skew
- `GenericSwapAndBridgeHandler:110` uses `getValue` for a slippage/min-out check on a maintainer-initiated swap; a
  skewed value could let an unfavorable swap pass. Requires the swap to route through a mis-priced pair; indirect.

## Honest assessment
A credible, user-triggerable loss path **exists and is source-supported** (Path 1/2 via the 4626 share price),
**conditioned** on a divergent ≥2-hop route being configured. The end-to-end economic exploit is **not yet
proven** — only the oracle mis-valuation is runtime-confirmed. So impact is *plausible and source-supported*, not
*demonstrated*.
