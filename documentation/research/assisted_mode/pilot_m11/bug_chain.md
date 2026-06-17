# M-11 maxSellPercent self-purchase bypass — executable bug chain

**Subject:** code4rena 2024-12-secondswap @ `6693d9e4` · **Status:** REPRODUCED (executable Foundry PoC).
**Not blind discovery** — invariant human-supplied (assisted-mode pilot); mechanism source-derived, then proven
executably. Test run on the real in-scope contracts (`/tmp/p97-secondswap`, `SecondSwap_Marketplace.sol`
sha256(first14) `80573b863544a3` = P97 frozen).

## Test
- File: `M11SelfPurchasePoC.t.sol` (`test/audit/` in the clone).
- Vulnerable: `forge test --match-test test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent -vv` → **PASS**.
- Patch: apply `require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");` in
  `_validatePurchase`, then `forge test --match-test test_M11_Patch_SelfPurchaseReverts -vv` → **PASS** (source then restored, hash re-verified).

## L1 — Entry (unprivileged)
A single `holder` with an original locked vesting allocation `A` (maxSellPercent = 2000 = 20%, so the intended
cap is `A/5`). Acts as both seller and buyer; only needs payment-currency for marketplace fees. Entrypoints:
`Marketplace.listVesting` + `Marketplace.spotPurchase` (both permissionless).

## L2 — State flip (named storage)
1. **Baseline cap holds:** `holder` lists `A/5` (`allocations[holder][sv].sold = A/5`). A further list of `+1`
   reverts `"SS_VestingManager: cannot list more than max sell percent"` — the cap is enforced.
2. **Self-purchase allowed:** `holder` calls `spotPurchase` on its OWN listing. `_validatePurchase`
   (`SecondSwap_Marketplace.sol:387-404`) has no `buyer != seller` check, so it succeeds.
3. **`bought` inflates:** `completePurchase` (`SecondSwap_VestingManager.sol:161-164`) credits
   `allocations[holder][sv].bought += A/5` unconditionally, and returns the tokens to `holder`.
4. **`sellLimit` grows:** next `listVesting` computes
   `sellLimit = bought + maxSellPercent*(currentAlloc + sold - bought)/BASE`
   (`SecondSwap_VestingManager.sol:121-140`). `bought` enters at 100% while `(currentAlloc+sold-bought)` stays
   `= A`, so `sellLimit` rises by `A/5` each self-purchase cycle. After cycle *k*, `sellLimit = (k+1)·A/5`.

## L3 — Outcome (proven in test output)
Five list→self-buy cycles drive cumulative `allocations[holder][sv].sold` to `A` — the **entire** locked
allocation, **5× the intended 20% cap** — with every `listVesting` passing `require(sold <= sellLimit)`. The
final tranche is bought by a distinct `externalBuyer`, who receives real vested tokens (`sv.available(externalBuyer) > 0`)
while `holder` receives currency: value genuinely exits the cap. Total attacker cost = marketplace fees only
(the self-purchase principal returns to the holder, who is also the seller).

## Impact
Medium — the protocol's core maxSellPercent restriction on locked allocations is bypassable by any holder for
fee cost; a holder can dump their full locked allocation onto the secondary market regardless of the cap. No
direct theft of third-party funds → not escalated to High (severity gate kept Medium, no FP).

## Fix
Reject self-purchase: `require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");` in
`_validatePurchase` (validated above — self-purchase reverts, third-party purchase unaffected). A complete fix
should also reconsider crediting `bought` at 100% into `sellLimit` for marketplace-internal transfers.

## Honesty notes
- Invariant supplied by a human (assisted-mode); this PoC proves *reproduction*, not autonomous discovery.
- No answer-key wording used — the chain is derived from the cited in-scope source lines and proven executably.
- Not submitted; submission stays human-gated (scope/duplicate/severity review pending).
