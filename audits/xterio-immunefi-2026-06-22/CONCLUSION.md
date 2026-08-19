# Xterio — Immunefi bug bounty — audit conclusion

**Target:** Xterio (Immunefi, max $80k Critical / $50k min, KYC + PoC, Solidity, multi-chain: ETH/BSC/Polygon/opBNB/Base/XterChain). Live since Jul-2024, scope last updated Apr-17-2026.
**Scope (named in-scope assets — deployed addresses, no GitHub):**
- **TokenGateway** `0x7127f0FEaEF8143241A5FaC62aC5b7be02Ef26A9` (mint/management gateway over Xterio ERC721/1155/20 tokens) — impl `0x9cbf…59ae`.
- **MarketplaceV2** `0xFC1759E75180aeE982DC08D0d6D365ebFA0296a7` (order-based NFT marketplace) — impl `0x4b62…d402`.
Both behind TransparentUpgradeableProxy, solc 0.8.9. Verified source fetched via Etherscan V2. ~1,321 LOC core (TokenGateway 384 + MarketplaceV2 937).
**Reward tiers:** Critical max $80k / min $50k (Primacy of Impact) · High max $50k / min $21k (Primacy of Impact) · **Medium flat $20k (Primacy of Rules)**. So Medium/High ARE in scope and pay well — a finding does not need to be Critical.
**Method:** sandbox check (1 benign FP — OZ ERC1155 NatSpec hex), 2 focused deep-readers (access-control on TokenGateway; logic/marketplace on MarketplaceV2).

## Verdict: honest negative — nothing submittable

### TokenGateway — no permissionless mint / freeze / seize
- Mint fns (`ERC721/1155/20_mint` + batch) gated by `onlyWithMintAccess` = `isInManagement(per-token) || operatorWhitelist || _minters[token]`. **All three branches are bootstrap-protected** — you cannot become a token's owner/`_nftManager`/minter, or an admin-whitelisted operator, without already being authorized (`addMinter`/`setManagerOf` are `onlyManagerOrGateway`; `addOperatorWhitelist`/`addManager` are `DEFAULT_ADMIN_ROLE`). The deployed whitelisted operator is MarketplaceV2, not an attacker.
- Every management/admin mutator (`setManagerOf`/`addMinter`/`setURI`/`pause`/`resetOwner`/`setGatewayOf`/`transferGatewayOwnership`) is correctly role-gated. `pause` is `onlyManagerOrGateway` → no non-manager freeze.
- The caller-supplied `_tokenContract` arbitrary-external-call surface yields no escalation: the gateway is fundless/approval-less and mint auth is re-checked per-token against the real `msg.sender` on any re-entry.
- **Low residuals (not submittable):** `setGatewayOf` doesn't clear `_minters[token]` (admin/re-migration-gated); impl lacks `_disableInitializers` (but non-UUPS, so owning the impl gives no proxy power).
- **Caveat:** the actual `BasicERC721/1155/20` token contracts are NOT in the named scope (only the gateway + interfaces). A mint bug inside a token contract would live there, not the gateway; those are separate, un-named, deployed-per-collection contracts (out of scope for this program).

### MarketplaceV2 — no theft / forge / replay
- **Signatures replay-safe:** digest binds `block.chainid` AND enforces `order.marketplaceAddress == address(this)` (no cross-chain / cross-contract replay despite multi-chain deployment); OZ 4.9 ECDSA rejects high-s / `address(0)`; EIP-1271 for contract signers. All economic fields (price/token/tokenId/payment/fees/royaltyRecipient/allowMint) are signed, and buyer+seller sign the **identical** `Order` → no underpay/redirect.
- **Fill/replay-safe:** `fills` capped by `Math.min(remaining)`, incremented before transfers (CEI), gated `< maximumFill`; ERC721 forced fill==1; cancelled/expired rejected.
- **Conservative settlement + CEI/`nonReentrant`:** payment partition sums exactly to total cost; recipients from each party's own signed metadata; fees/royalties signed by both, on-chain ERC2981 can only *lower* royalty; rounding favors payer. No arbitrary call/delegatecall; marketplace only pulls from addresses that signed a matching order. `allowMint` double-gated (seller == NFT manager AND marketplace holds gateway mint access). `_disableInitializers` present.
- **MP-001 (functionality defect — assessed NOT payable):** the native-token path in `_transferFT` (`MarketplaceV2.sol:633-663`) **ignores `from`** and funds the trade from `msg.value` (the tx sender), whereas the ERC20 path pulls `totalCost` from the signed `buyer` via allowance. Consequence: a native-token **buy/bid** order cannot be filled by a relayer or by the seller-accepting-a-bid without the **caller** paying out of pocket (`require(msg.value == totalCost)` forces it). **No involuntary victim** — nobody is debited against their will; a rational seller/relayer simply won't submit. This is a feature-doesn't-work limitation, not a security impact (no fund loss / no contract-DoS / no griefing-with-damage), so it does not map to a payable Immunefi Medium even though Medium ($20k) is in scope.

## Submission
**Nothing submitted.** Re-checked against the corrected reward tiers (Medium $20k / High $21–50k in scope, not Critical-only): the two named in-scope contracts are well-built; the only defect (MP-001) is a non-payable functionality limitation with no involuntary victim, and the TokenGateway residuals are Low/admin-dependent (centralization = OOS). Honest negative.
