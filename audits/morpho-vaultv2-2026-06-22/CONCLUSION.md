# Morpho Vault V2 (gate delta) — Immunefi bug bounty — audit conclusion

**Target:** Morpho (Immunefi, Vault V2 periphery up to $1.5M; Crit = theft/insolvency/permanent-freezing). Repo github.com/morpho-org/vault-v2 @ d9c2266.
**Method: DIFF-THE-AUDIT.** Vault V2 core is audited through **Dec-2025** (Spearbit ×3, Zellic, ChainSecurity, Blackthorn, Certora — all in repo `audits/`). The live HEAD is actively developed; computing the src delta since 2025-12-16 (post last audit) isolated the **only unaudited in-scope code**: the periphery **whitelist GATES**, added/rewritten **June-2026** (the `multi-whitelister-gates` / `receive-shares-gate` / `send-assets-gate` line of work). Focused the entire pass on that ~200-LOC delta + its VaultV2 enforcement instead of re-auditing the verified core.

## The delta = the new whitelist gates
- `src/periphery/WhitelistReceiveSharesGate.sol` (95) — implements `canReceiveShares` (gates deposit `onBehalf` + share transfers-in + fee-share mint).
- `src/periphery/WhitelistSendAssetsGate.sol` (108) — implements `canSendAssets` (gates deposit `msg.sender`; vault comment: "not critical, cannot block users' funds").
- Both: `roleSetter` → `isWhitelister[]` → `isWhitelisted[]`; plus `setIsWhitelistedWithSig` (EIP-712 signed whitelisting) + a self-`delegatecall` `multicall`.
- VaultV2 enforcement: enter()=canReceiveShares(onBehalf)+canSendAssets(msg.sender); exit()=canSendShares+canReceiveAssets; transfer()=canSendShares+canReceiveShares.

## Verdict: clean — delta holds (honest negative)
- **No permanent-freeze (Critical) via these gates:** they implement only `canReceiveShares` + `canSendAssets` — the two NON-freeze gates. `exit()`/redeem never calls `canReceiveShares`, so assets stay recoverable; the freeze-capable slots (`sendSharesGate`/`receiveAssetsGate`) are NOT these contracts. `canReceiveShares` is a non-reverting pure mapping read (can't gas-grief/brick). The only revert-capable method (`canSendAssets` → `IIntermediary(account).initiator()`) is wired ONLY to the deposit path (VaultV2:778) — confined, recoverable, non-critical. Un-whitelisting blocking a transfer-back-then-withdraw is the **documented compliance tradeoff** executed by a **trusted whitelister** (OOS centralization).
- **No whitelist bypass:** EIP-712 domain binds chainid+`address(this)` (no cross-chain/cross-gate replay); nonce `nonces[whitelister][account]++` is consumed *inside* the signed hash + the bool is signed (no true/false or malleability replay); `ecrecover(0)` guarded; `isWhitelister[recovered]` checked at execution (removed whitelister's pre-signed msgs invalid); deadline enforced. The intermediary path needs a whitelister to register `isIntermediary`, and even a full send-assets bypass still requires `canReceiveShares(onBehalf)` to get shares. `multicall` self-delegatecall preserves msg.sender (no escalation). Two-tier role auth complete.
- `FeeWrapperDeployer` predates the delta (Jan-2026), atomic config, no permissionless fund-loss.

## Submission
**Nothing submitted.** The diff-the-audit method efficiently isolated the unaudited delta (the June-2026 gates) and a zero-trust pass found it well-built (no theft / permanent-freeze / bypass). Honest negative — but a high-confidence, efficiently-scoped one (the audited core was correctly out of focus).
