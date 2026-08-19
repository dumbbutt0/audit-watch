# YO Protocol — Immunefi bug bounty — audit conclusion

**Target:** YO Protocol (Immunefi $10k; Base yield-optimizer vaults). In-scope: yoETH/yoBTC/yoUSD vault proxies + yoVaults impl (0xfd62..c713) + YOGateway (proxy+impl). Verified source via Etherscan V2 chainid 8453 (solc 0.8.28). KYC+PoC. Live May-2025.
**Method (LIVE-STATE-FIRST):** before any deep read, cast-read the in-scope vaults' live state. **PASSED** — yoUSD ≈ $11.5M (USDC), yoETH ≈ 4,822 WETH (~$15M+), yoBTC ≈ 112 cbBTC (~$10M+) → ~$35M+ real TVL, all funded + active. So a bug here would be genuinely exploitable + payable (not a dormant deployment). Then deep-read the custom core (yoVault 431L + YoGateway 136L), focusing on the PERMISSIONLESS surface.

## Verdict: honest negative — well-built async-ERC4626

### yoVault — no permissionless theft/insolvency/freeze
Async-redeem ERC4626: totalAssets = asset.balanceOf(vault) + aggregatedUnderlyingBalances (oracle-reported, requiresAuth, once/block, ±1% else auto-pause); withdraw/redeem revert (UseRequestRedeem); requestRedeem → instant if idle≥assetsWithFee else escrow shares + record pending[receiver]; fulfillRedeem/cancelRedeem operator-only.
- First-depositor/inflation/donation: SAFE (+1 virtual offset; donation is pro-rata loss to the donor at $35M TVL).
- deposit→instant-redeem round-trip: SAFE (double-floor + both fees Ceil against the round-tripper → break-even-or-lossy).
- Instant-redeem (assetsWithFee=super.previewRedeem gross): SAFE — pays the floored fair value of the burned shares, fee taken FROM it (not added), never overpays.
- Pending accounting (receiver-keyed): SAFE — an attacker escrows their OWN shares + funds their OWN pending = gift, not theft; escrow drops balanceOf so no double-spend; totalPendingAssets only raises the idle reservation (can't make _getAvailableBalance over-report).
- Fee math (_feeOnTotal/_feeOnRaw, Ceil): SAFE — always rounds toward the protocol; dust = self-harm.
- The only value-extraction residual (instant-redeem at a stale oracle price during an off-chain strategy loss) is **OOS** (oracle staleness, not a pure code bug; ±1%/update + auto-pause; operator-paced).
- All fund-moving levers (manage / onUnderlyingBalanceUpdate / fulfillRedeem / cancelRedeem / pause / update*) are `requiresAuth` = operator/oracle-trusted → OOS (centralization explicitly excluded).

### YoGateway — clean thin router
deposit → vault.deposit(assets,receiver) with minSharesOut; redeem → pull shares, vault.requestRedeem(shares, receiver, address(this)) with minAssetsOut; nonReentrant; registry-allowlisted vaults; correctly routes assets/pending to the end `receiver`. No theft path.

## Submission
**Nothing submitted (honest negative).** The vault + gateway are well-constructed; the only residuals are operator/oracle-trust = OOS. **But the live-state-first filter did its job** — this was a genuinely live, funded ($35M+), in-my-edge target, so a high-confidence clean negative (no effort wasted on a dormant deployment, unlike Autonolas/IPOR/Cronos). The async-4626 design is solid.
