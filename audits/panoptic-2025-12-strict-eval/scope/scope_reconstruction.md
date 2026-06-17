# Panoptic Next-Core — Scope Reconstruction (blind, pre-answer-key)

**Source of scope:** the cloned repo's `scope.txt`, `out_of_scope.txt`, `foundry.toml`, and
`README.md`. **The contest findings file (`2025_12_panoptic_v12_findings.md`) and the prior-audit
PDFs/`diff` were quarantined to `/tmp/panoptic-QUARANTINE-DO-NOT-READ/` and were NOT read or
intaken.** No report-page / answer-key access.

- Repo: `code-423n4/2025-12-panoptic` @ `fe557748210a529ae414d7c487b6514be0d9e220`
- Solidity `^0.8.24`, EVM `cancun`, Foundry, optimizer 9,999,999 runs (viaIR off in default profile).
- Built on **Uniswap V3 and V4** pools (SFPM V3 + SFPM V4 both in scope).
- Perpetual options protocol; designed to be fully collateralized & noncustodial.

## In scope (12 files, 12,796 LOC)

| File | LOC | Role (primary-focus mapping) |
|---|---|---|
| `PanopticPool.sol` | 2156 | Options engine: mint/burn/exercise, force-exercise, liquidation orchestration, premium settle |
| `RiskEngine.sol` | 2403 | Solvency/margin, `isAccountSolvent`, `getLiquidationBonus`, `exerciseCost`, IRM (PID), oracle/EMA/median |
| `CollateralTracker.sol` | 1664 | ERC4626 vault: share/debt accounting, interest accrual, commission, premium settle, liquidation settle |
| `SemiFungiblePositionManager.sol` | 1528 | V3 position engine (LP + long via burnt liquidity), ERC1155 tokenIds |
| `SemiFungiblePositionManagerV4.sol` | 1339 | V4 variant of the SFPM |
| `libraries/PanopticMath.sol` | 774 | Protocol math helpers |
| `libraries/Math.sol` | 1293 | Low-level math (mulDiv, ticks, sqrt-price) |
| `types/OraclePack.sol` | 636 | Packed oracle state (EMA/median/observations) |
| `types/TokenId.sol` | 534 | Position encoding (legs, strikes, widths) |
| `types/MarketState.sol` | 187 | Packed market/borrow-index state |
| `types/RiskParameters.sol` | 174 | Packed risk parameters |
| `types/PoolData.sol` | 108 | Packed pool data |

## Out of scope (present only as read dependencies)
Factories (`PanopticFactory`, `PanopticFactoryV4`), `base/*`, `interfaces/*`,
`libraries/{CallbackLib,Constants,EfficientHash,Errors,FeesCalc,InteractionHelper,SafeTransferLib,V4StateReader}`,
`tokens/*`, `types/{LeftRight,LiquidityChunk,Pointer,PositionBalance}`, all `script/` and `test/`.

## Constructor assumption (mandated)
RiskEngine constructor args = `10_000_000, 10_000_000, address(0), address(0)`.

## Publicly-known / ineligible (must not be scored HIT; flagging them is not an FP)
Captured in `program_scope.json → publicly_known_ineligible`. Headlines:
- **Oracle:** only **atomic** price manipulation from a normal state is valid; non-atomic / multi-block
  EMA manipulation and stale-EMA-vs-market are **out of scope**.
- **Premium/liquidation:** back-and-forth premium manipulation (if not self-profitable & no protocol
  loss), liquidator price-extraction, rounding-direction premium inflation, `settleLongPremium`
  tiny-amount avoidance, premium accumulator cap — all **known/acceptable**.
- **Share supply:** overflow/DoS that *requires* near-2^256 share supply reachable only via repeated
  protocol-loss liquidations is **invalid**.
- **Nethermind pre-contest (4):** double penalty/index update; `_getMargin` deficit masking; broken
  bonus calc from masked deficit; orphan shares in delegate→revoke. These are **publicly disclosed**
  → ineligible; if our pipeline finds them, they count as detections but **not** as awarded-AK HITs.

## Primary attack surfaces to cover (from the task brief, mapped to scope)
liquidation solvency (RiskEngine/CollateralTracker/PanopticPool) · oracle/TWAP-EMA-median
(RiskEngine/OraclePack) · collateral accounting (CollateralTracker) · share/debt accounting
(CollateralTracker ERC4626 + MarketState borrow index) · risk-engine formulas (RiskEngine
margin/bonus/IRM) · state↔price mismatch (OraclePack vs pool) · liquidation liveness (PanopticPool
liquidate path) · bad-debt propagation (protocol-loss → CollateralTracker) · force-exercise
(PanopticPool `exerciseCost`/force-exercise) · interest/rate update math (MarketState index + IRM) ·
cross-function invariants (mint/burn/settle/liquidate conservation across PanopticPool ↔
CollateralTracker ↔ RiskEngine).
