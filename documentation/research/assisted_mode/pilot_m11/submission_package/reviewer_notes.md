# Reviewer notes — M-11 `maxSellPercent` self-purchase bypass (INTERNAL)

> **Positioning (internal, not for the report body):** this is an **assisted-mode** result. A human supplied the
> candidate invariant ("a holder must not be able to exceed `maxSellPercent` of their original allocation via
> sale/listing/claim state transitions or accounting paths"); the mechanism was then traced from source and
> reproduced with an executable PoC. **This is not an autonomous/blind discovery** and should not be presented
> as one. Keep this caveat in internal records; the `submission_draft.md` body is deliberately platform-neutral.

## Why the issue is real
Every claim maps to a concrete source line or a passing PoC assertion — nothing is inferred from an external
report or known-issues list:
- `SecondSwap_Marketplace._validatePurchase` (387-404) gates only `status`, `msg.sender != _referral`,
  whitelist, and amount bounds. There is **no `buyer != seller`** check.
- `SecondSwap_VestingManager.completePurchase` (161-164) does `allocations[buyer][vesting].bought += amount`
  unconditionally on every purchase.
- `SecondSwap_VestingManager.listVesting` (121-140) computes
  `sellLimit = bought + maxSellPercent*(currentAlloc + sold - bought)/BASE` and enforces
  `require(sold <= sellLimit)`.

## Why self-purchase matters
A holder is allowed to buy their own public listing. That single fact turns `completePurchase` into a way for a
holder to credit **their own** `bought` counter at will — the buyer and the beneficiary of `bought += amount` are
the same address the holder controls.

## Why this bypasses `maxSellPercent`
`bought` is added to `sellLimit` at **100%**, while the capped portion is taken over
`(currentAlloc + sold - bought)`. Across list → self-buy cycles that quantity stays equal to the holder's
original allocation `A` (listing moves tokens out and decreases `currentAlloc`; the self-purchase returns them
and increases `bought` by the same amount, so the difference is invariant). Net effect: each self-purchase raises
`sellLimit` one-for-one with the amount cycled, so the cap that should bind `sold` to `maxSellPercent * A / BASE`
no longer binds. The cap is enforced against an attacker-inflatable counter, not against the original schedule.

## Why the PoC proves the exploit path
`test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent` runs the real in-scope contracts and asserts, in
order: (1) **baseline** — a list above `A/5` reverts `"cannot list more than max sell percent"`, so the cap is
genuinely enforced pre-exploit; (2) the holder's `spotPurchase` of its own listing **succeeds**; (3) `bought`
increased by the self-purchased amount; (4) a subsequent listing beyond the original cap now **passes**; (5)
after five cycles cumulative `sold == A` (the full allocation, 5× the 20% cap); (6) a separate `externalBuyer`
buys the final tranche and receives real vested tokens while the holder receives currency. The progression is
mechanical, not a single lucky path.

## Why Medium is the conservative call
The PoC proves a holder can sell **more than the intended cap, up to their full locked allocation**, for the cost
of marketplace fees. It does **not** prove theft of third-party funds, protocol insolvency, or loss beyond the
holder's own (already-owned) allocation. So the demonstrated impact is a defeat of a protocol restriction with
economic consequence (uncontrolled secondary-market dumping of locked tokens) → **Medium**. Do not escalate
unless a reviewer independently source-proves broader loss (e.g. price/oracle dependence, or third-party fund
impact). The program's own severity matrix may re-tier this; that is a human decision.

## Why this is not accounting noise
- It is **permanent and repeatable**, not a transient rounding artifact: the cap stays defeated for the rest of
  the vesting, and the holder can keep cycling.
- It is **cheap** (fees only) and **deterministic**.
- The minimal one-line guard (`require(msg.sender != listing.seller, ...)`) was added and the patch test
  (`test_M11_Patch_SelfPurchaseReverts`) confirms self-purchase then reverts while a genuine third-party purchase
  still works — i.e. the behavior is a real, fixable control gap, not a measurement quirk.

## What a triager should run
From the local clone (`/tmp/p97-secondswap` or equivalent, contracts at commit `6693d9e4`):
1. Vulnerable: `forge test --match-test test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent -vv` → PASS.
2. Patch: add `require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");` in `_validatePurchase`,
   then `forge test --match-test test_M11_Patch_SelfPurchaseReverts -vv` → PASS; restore the source.
3. Confirm `SecondSwap_Marketplace.sol` sha256 (first 14) `80573b863544a3` before and after.

## Remaining assumptions / open items (human-owned)
- The vesting plan is `sellable` with `maxSellPercent > 0` (PoC uses the contract default 20%).
- The attack costs marketplace fees per cycle; rational when the value of liquidating the locked allocation
  exceeds those fees.
- The PoC is a **local fixture** with mock tokens (no fork) — it demonstrates contract logic, not a specific live
  deployment.
- **Scope confirmation** and **duplicate / publicly-known** checks are NOT done — a human must clear both before
  any submission. Program-specific severity tiering and final wording are also human decisions.
