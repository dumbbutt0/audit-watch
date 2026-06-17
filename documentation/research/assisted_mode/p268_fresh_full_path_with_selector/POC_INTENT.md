# P268 — POC_INTENT (Phase 8)

Exploit claims for the mechanisms sent to PoC. The mechanism hypotheses + falsifiers were committed PRE-CODE in
`outputs/p268_poc_queue.json` + RANKING_OUTPUTS + SELECTOR_OUTPUTS (all written before any PoC code); this file
consolidates them. No answer key consulted.

## C2-M1 — first-depositor share-inflation (PRIMARY; selector-preserved)
- **Target:** `Vault.deposit` / solady `ERC4626` share math (no `_decimalsOffset` override in Karak's Vault).
- **Root cause:** `totalAssets()` = `asset.balanceOf(this)` (donatable) + virtual shares with **offset 0** (only +1
  protection) ⇒ a seeded 1-wei share + a donation ≈2× the victim deposit makes `convertToShares(victimAssets)` round
  to 0.
- **Attacker model:** fresh EOA; no privilege; permissionless `deposit`.
- **Setup:** clone+init Vault (MockToken). Attacker deposits 1 wei, donates `D` assets directly, victim deposits `V`.
- **Steps / expected delta:** victim shares = 0 for `V` assets; victim redeemable = 0; victim's `V` joins the pool
  backing other holders.
- **Victim/gainer:** victim loses `V`; gainer = existing share (attacker, partially — virtual share caps profit).
- **Assertion:** `victimShares == 0` and `convertToAssets(0) == 0` and vault holds ≥ donation+victim.
- **Refutation condition (pre-stated):** solady `_useVirtualShares()` default + a nonzero `_decimalsOffset` would
  neutralize it. **Resolved by PoC:** virtual shares ARE on but offset is 0 (Karak doesn't override) → insufficient →
  inflation confirmed.

## C1-M1 — permissionless finishRedeem / finish-time spot conversion (selector-preserved)
- **Target:** `Vault.startRedeem`/`finishRedeem`. **Root cause hypothesis:** finish-time spot `convertToAssets`
  enables payout manipulation. **Assertion:** quiet-path round-trip returns ~deposit; permissionless finisher gains 0.
- **Refutation condition:** assets go to a fixed beneficiary and slashing-during-queue is intended → by-design.
  **Resolved by PoC:** quiet path safe; finisher gains nothing → NO_CHAIN/by-design.

## C1-M2 — startRedeem self-approval (easy rival)
- **Assertion:** `startRedeem` reverts without `allowance[staker][vault]`. Low-impact UX/griefing. (Included to show
  what the raw pre-P267 path would have PoC'd instead.)

## Negative control — SlasherLib.requestSlashing
- Expected benign (Core/operator-gated). No PoC needed beyond noting the access gate.

Frozen alongside the PoC sources (hashes in POC_RESULTS).
