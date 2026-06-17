# P143 — Runtime Model

Deterministic per-pair price oracle: `getValue(from,to,amount) = amount * priceWad[from][to] / 1e18`.

## Tokens
- `A` (0xA1) start asset · `B` (0xB2) first intermediate · `C` (0xC3) second intermediate · `D` (0xD4) final base.

## Route & prices (wad multipliers)
`priceRoutes[A][D] = [B, C]`; amount = 1e18 (1 A).

| pair | price (wad) | role |
|---|---|---|
| A→B | 2 | hop i=0 (legitimately uses A) |
| A→C | 10 | the **static-asset** hop the loop wrongly takes at i=1 |
| B→C | 3 | the **loop-carried** hop it *should* take at i=1 |
| C→D | 1 | final hop |

## Expected arithmetic
- **Vulnerable (real contract):** 1·(A→B=2)=2 → static (A→C=10)=20 → (C→D=1)=**20**.
- **Corrected (loop-carried):** 1·(A→B=2)=2 → (B→C=3)=6 → (C→D=1)=**6**.
- **Delta:** 20 − 6 = 14e18; **ratio 20/6 = 3.33×** over-valuation.

## Controls
- **Single-hop** (`route=[B]`, base C): loop runs only i=0 (uses A correctly) → real == corrected == 6.
- **Equal-per-hop-price** (static hop price == loop-carried hop price): divergence vanishes → real == corrected,
  isolating the cause to *differing* per-hop oracle paths, not the multi-hop structure itself.
