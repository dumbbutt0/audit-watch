# Optional platform fields — M-11 (DRAFT, NOT FINAL)

> ⚠️ **DRAFT — not final.** These are copy-ready field values for a generic submission form. Do **not** apply any
> platform-specific wording, severity matrix, or category taxonomy until a human supplies the target program's
> rules. Severity, in-scope status, and duplicate status are pending human review.

| Field | Value (draft) |
|---|---|
| **Title** | `maxSellPercent` sell-cap can be bypassed by purchasing your own listing |
| **Severity** | Medium *(candidate; subject to the program's own severity matrix)* |
| **Affected contract(s)** | `SecondSwap_Marketplace.sol`, `SecondSwap_VestingManager.sol` |
| **Affected function(s)** | `Marketplace._validatePurchase` (via `spotPurchase`); `VestingManager.completePurchase`; `VestingManager.listVesting` |
| **Commit** | `6693d9e4f03a37919a52626de64b1cadf632fd29` |
| **Summary** | `_validatePurchase` has no `buyer != seller` check, so a holder can buy their own listing. `completePurchase` then credits `bought += amount`, and `listVesting` adds `bought` at 100% into `sellLimit = bought + maxSellPercent*(currentAlloc + sold - bought)/BASE`. Repeating list → self-purchase cycles inflates `bought` and lifts `sellLimit` without bound, letting a holder sell their full locked allocation despite `maxSellPercent`. |
| **Impact** | The per-holder `maxSellPercent` cap on locked allocations is bypassable for the cost of marketplace fees; a holder can liquidate their entire locked allocation regardless of the configured cap. No third-party fund theft is claimed. |
| **PoC command** | `forge test --match-test test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent -vv` *(PASS on the pinned source; full test + evidence in this package)* |
| **Remediation** | Add `require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");` in `_validatePurchase`; and stop crediting `bought` at 100% into `sellLimit` for marketplace-internal transfers (cap sellability against the original allocation, not an inflatable counter). |

*Notes for the human filling the form:* set the platform's category/CWE per its taxonomy; confirm in-scope and
non-duplicate before submitting; re-tier severity if the program's matrix differs.
