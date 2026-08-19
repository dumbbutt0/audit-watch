# Maple CCIP Cross-Chain Receiver — Immunefi ($500k) — audit conclusion

**Target:** Maple Finance CCIP Cross-Chain Receiver (Chainlink-CCIP bridge: EVM+SVM source chains → Ethereum receiver → Maple pool deposit/redeem of syrupUSDC, shares returned cross-chain). Repo maple-labs/maple-cross-chain-receiver; src/MapleCCIPReceiver.sol (1611) + ccip/ base. Real value flows through it.
**Method (diff-the-audit + my-edge cross-chain):** the receiver is audited TWICE — Dedaub (Nov-2025) + SigmaPrime (Jan-2026), only Lows found (all resolved) — with NO post-Jan-audit logic delta (only a rename + audit-report commit). So diff-the-audit is null; played it as "audited high-value bridge, occasional miss" on my edge (cross-chain msg auth), deduping the audited Lows.

## Verdict: honest negative — the 2-audit bridge holds
Focused cross-chain deep-read (0 findings). Why the crown jewels are safe:
- **Source authentication:** receive-path enforces `_normalizeToBytes32(message.sender) == message.universalSenderAddress` (MapleCCIPReceiver.sol:1112-1115) → every deposit credit + redemption/recovery output routes to the CCIP-VERIFIED actual source sender. No spoofing gap, no victim (credits never depend on WHICH sender; the sender always credits itself).
- **Deposit accounting:** shares credited only from CCIP-delivered `destTokenAmounts`; `_vaultDeposit` asserts exact `balanceBefore−balanceAfter == amount` → no mint-without-tokens.
- **Redemption escrow:** requestId monotonically bound to (sender+chain); execute/cancel executor-gated → no cross-user hijack/double-execute (nonReentrant).
- **Failed-message recover/retry (permissionless):** state machine single-consume (FAILED→RESOLVED before the external send, nonReentrant); recovery returns to the CACHED ORIGINAL sender (not msg.sender) → no double-send / redirection / replay.
- **EVM/SVM universal addressing:** `_bytes32ToAddress` reverts on dirty upper-12-bytes → no silent SVM→EVM truncation/mis-route (worst case = admin-config-dependent stuck escrow = OOS, not theft).
- The novel-vs-audit observation (the fork stripped Chainlink's canonical trusted-sender allowlist; the auditors only flagged the unused errors) is **not exploitable** under the protocol's documented permissionless any-sender / self-binding model — there is no privileged source contract whose authority an attacker could usurp.

## Submission
**Nothing submitted (honest negative).** A well-built, twice-audited cross-chain receiver; the self-binding sender invariant + exact-amount deposit asserts + sender-bound redemption escrow + single-consume recovery close the theft/forge/hijack/freeze vectors. diff-the-audit was null (no post-audit delta); the deep-read on my cross-chain edge confirmed the audits hold.
