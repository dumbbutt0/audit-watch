# AC-001 — RESCUER role can drain GM marketToken / poolToken (deployed vault value) via rescueFunds — only the USDC asset is protected

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** Improper Access Control
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=Deployed reserve stolen; _totalValueLocked deflated so every subsequent _convertToAssets payout to honest lockers is reduced. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:617`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`

## Description

CarthaVault.rescueFunds(token,recipient,amount) is gated only by Roles.RESCUER and blocks a transfer only when token == $.asset (the USDC accounting asset). However the vault's deployed value lives in OTHER tokens: $.marketToken (the 0xMarkets/GM market token minted when deployToPool sends USDC into the GM deposit vault) and $.poolToken. _totalValueLocked() = USDC balanceOf(this) + _gmValueInUsdc($), and _gmValueInUsdc prices the GM position via PoolDeployLib using poolToken/marketToken. A RESCUER can call rescueFunds(marketToken, attacker, fullBalance) (or poolToken) and transfer the entire GM-deployed position out of the vault. Because rescueFunds only excludes the USDC asset, the actual deployed reserves are rescuable. This both (a) directly removes real value backing user shares and (b) silently lowers _gmValueInUsdc -> _totalValueLocked, deflating sharePrice and every subsequent _convertToAssets payout (release / forceExit / processQueuedWithdrawals) for honest users. This confirms deep-analysis DT-002. RESCUER is a privileged role (not permissionless), so impact is bounded by trust in that key, but the guard is mis-scoped: the developer clearly intended rescueFunds to NOT touch vault value (it blocks the asset), yet the value-bearing GM tokens are left fully rescuable. Same mis-scope is absent on the parent (parent holds no GM tokens directly), so this is child-vault specific.

## Impact

A compromised or malicious RESCUER drains the GM marketToken/poolToken (the deployed reserve), removing the value backing user shares and deflating sharePrice for all remaining lockers; user redemptions then pay out a fraction of their principal.

## Attack path (Intent / Technique / Evasion)

- **Intent:** As the RESCUER, transfer the vault's entire GM marketToken / poolToken balance to an attacker address, stealing the deployed reserve and deflating the share price for honest lockers.
- **Technique:** Call CarthaVault.rescueFunds($.marketToken, attacker, IERC20(marketToken).balanceOf(vault)). The token != $.asset check at line 619 passes (marketToken is not the USDC asset), recipient/amount checks pass, and SafeERC20.safeTransfer(line 623) ships the full GM position out. The GM value is no longer in the vault, so _gmValueInUsdc and _totalValueLocked drop accordingly.
- **Evasion:** rescueFunds is meant to recover only stray non-vault tokens and explicitly blocks token == $.asset (line 619). The gap: the vault's REAL value backing shares is held in marketToken/poolToken, not in the USDC asset, and those are not on the block-list, so the value-rescue protection is incomplete.

## Reachability / follow-up

reachable: RESCUER calls rescueFunds(marketToken,...). no_privileged_keys: NO — requires RESCUER. state_before_after: GM balance -> attacker; TVL collapses. why_guards_fail: only asset is blocked. scope_match: privileged value-at-risk.

## Triage reasoning

CarthaVault.rescueFunds blocks only token==$.asset (USDC); the GM marketToken/poolToken (deployed vault value) is not the asset, so RESCUER can transfer the entire deployed GM position out. Mis-scoped guard. Privileged (RESCUER = emergency multisig) so trust-bounded, but it defeats the 'recover non-vault tokens only' intent; fix by also blocking marketToken/poolToken.
