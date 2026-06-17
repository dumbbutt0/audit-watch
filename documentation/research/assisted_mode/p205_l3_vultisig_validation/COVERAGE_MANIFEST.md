# P205 — coverage manifest + pre-registered blind sample (vultisig-2024-06)

Source-only, read-only. vultisig = Uniswap-V3 ILO launchpad, solc 0.7.6, `src/` (ILOPool 469 LOC, ILOManager 208,
base/* libs). Awarded (count-only): **3 High / 3 Medium**.

## Severity-relevant surfaces (from source)
- **ILOPool**: `buy` (raise/deposit, fund custody), `claim` (vested claim + fee distribution, V3-position),
  `launch` (OnlyManager, creates V3 liquidity), `claimRefund`/`claimProjectRefund` (refund custody / permanent-lock).
- **ILOManager**: `initialize`, `initILOPool` (onlyProjectAdmin), `launch`, `claimRefund`, `setPlatformFee`/`setFeeTaker`.
- **Access/whitelist**: `ILOWhitelist` (batchWhitelist/remove/setOpenToAll/isWhitelisted, onlyProjectAdmin).
- **Vesting**: `ILOVest` (_unlockedLiquidity/_claimableLiquidity/_validate*).
- **V3 interaction**: `LiquidityManagement` (addLiquidity + `uniswapV3MintCallback`).

## Pre-registered blind sample (8 surfaces) — frozen BEFORE the blind run
| id | file · function(s) | category |
|---|---|---|
| v-01 | ILOPool.buy | fund-custody / raise accounting |
| v-02 | ILOPool.claim | fee/vesting accounting (V3 position) |
| v-03 | ILOPool.launch | launch / liquidity / DoS |
| v-04 | ILOPool.claimRefund / claimProjectRefund | refund custody / permanent-lock |
| v-05 | ILOManager.initialize / initILOPool | init / access-control |
| v-06 | ILOManager.launch / claimRefund / setPlatformFee / setFeeTaker | manager control / fees |
| v-07 | base/ILOWhitelist | access-control / whitelist |
| v-08 | base/LiquidityManagement | V3 mint callback / payment |

Coverage: fund-custody (v-01,v-04) · fee/vesting (v-02) · launch/DoS (v-03,v-06) · access-control (v-05,v-06,v-07) ·
V3 callback/payment (v-08). Bounded sample → out-of-sample signal.
