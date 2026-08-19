# Ethena — Immunefi bug bounty — audit conclusion

**Target:** Ethena (Immunefi, $3M max, KYC + PoC, live since Apr-2024, last scope update May 28 2026).
**Scope:** 9 deployed contracts on Ethereum (verified source fetched via Etherscan V2):
USDe · **EthenaMinting V2** (0xe349…62D3) · StakedUSDe/StakedUSDeV2 · USDeSilo · SingleAdminAccessControl · EthenaLPStaking · StakingRewardsDistributor · ENA. ~1,500 LOC Ethena-authored + OZ 4.9.
**Focus (per "most recent updates"):** the **EthenaMinting V2 delta** (V2 = 404-line rewrite vs V1) — EIP-1271 sig support, stablecoin price-delta minting, per-asset + global per-block caps, benefactor→beneficiary whitelist, packed uint128/uint120 order fields — plus the newer staking batch (StakingRewardsDistributor, EthenaLPStaking).
**Method:** api-free deep pipeline (analyze → deep-analysis) + 2 focused specialist deep-reads (V2 minting; staking/vault/rewards) + manual code confirmation + dedup (Immunefi reports MCP + scope rules).

## Verdict: no novel submittable finding

Ethena is exhaustively audited and the bounty is 2+ years live. Every candidate is a correctness nit, a MINTER-trust design item, or a known/OOS property.

### Candidates assessed

| Candidate | Severity | Disposition |
|---|---|---|
| **Cooldown-silo blacklist bypass** — `StakedUSDeV2.unstake()` (StakedUSDeV2.sol:80-92) + `USDeSilo.withdraw()` (USDeSilo.sol:27) have **no `FULL_RESTRICTED_STAKER_ROLE` check**; USDe parked in the silo before a blacklist escapes both the freeze and `redistributeLockedAmount` (which only burns remaining sUSDe shares). | — | **OOS + likely known.** Bypasses a centralization/compliance control (Ethena lists "centralization risk impacts" as OOS); the user withdraws *their own* funds → not theft-of-others / insolvency / permanent-freezing. 2-yr-live audited contract. Not payable. |
| **EIP-712 typehash field widths swapped** — `ORDER_TYPE` declares `uint128 expiry, uint120 nonce` but the struct is `uint120 expiry; uint128 nonce` (EthenaMinting.sol:36-38 vs IEthenaMinting.sol:48-49). | Low | Correctness/interop only. On-chain self-consistent (same constant both sides; abi.encode 32-byte-pads). No theft. |
| **Nonce bitmap truncates high 64 bits** — `verifyNonce` does `uint64(nonce)>>8` (EthenaMinting.sol:562), so `Order.nonce`'s upper 64 bits are ignored. | Low | **Fail-closed** (collisions revert `InvalidNonce`, never replay). Reduces usable nonce space to 2^64; can only cause spurious rejects, not double-mint. |
| **Stablecoin mint price guard is nominal, not market** — `verifyStablesLimit` (EthenaMinting.sol:570-599) bounds USDe to within `stablesDeltaLimit` bps of decimal-normalized collateral *amount*, with **no oracle**; a depegged whitelisted STABLE could be minted ~1:1. | (design) | **MINTER_ROLE-gated** — Ethena's backend prices and co-submits every mint; admin sets STABLE assets + delta. Intended trust model, not independently exploitable. |
| Cooldown timer reset on repeated cooldown (StakedUSDeV2.sol:101/114) + LP unstake reset (EthenaLPStaking.sol:142) | Low | Self-grief only (keyed by msg.sender); same class graded Low across the reports archive (Plume). |

### Verified safe (honest negatives)
- **EIP-1271 path**: exact magic-value check, view/staticcall (no reentrancy), benefactor must be admin-whitelisted (hostile 1271 wallet can't self-enroll); OZ ECDSA blocks low-s malleability.
- **Mint route/custody**: all destinations gated to whitelisted custodians, ratios sum to 10000, `_transferCollateral` conserves amount exactly (dust → last custodian).
- **Per-asset vs global block caps**: incremented atomically, consistent; uint128 amounts can't silently wrap the checks.
- **sUSDe ERC4626**: unvested-reward sandwich mitigated (`totalAssets = balance − getUnvestedAmount`, `StillVesting` guard); donation/first-depositor double-guarded (`MIN_SHARES=1e18` + OZ 4.9 virtual offset).
- **StakingRewardsDistributor / EthenaLPStaking**: operator/owner-gated, `_checkInvariant` after every mutation, `rescueTokens` can't touch staked assets/USDe.
- **SingleAdminAccessControl**: sound two-step admin, admin role protected from generic grant/revoke. **ENA**: mint onlyOwner, 1/yr, ≤10% inflation.

## Submission
**Nothing submitted.** No novel, in-scope, reachable fund-loss bug. The freshest surface (EthenaMinting V2) yielded only correctness nits + a MINTER-gated design item; the one substantive property (cooldown-silo blacklist bypass) is OOS (centralization control) and near-certainly known.
