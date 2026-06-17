# Revert Lend — Scope Reconstruction (blind, pre-answer-key)

**Source:** repo `scope.txt` + `README.md` only. The automated-findings files (`4naly3er-report.md`,
`bot-report.{md,json}`, `slither.txt`), prior `audits/` PDF, and `discord-export/` were quarantined to
`/tmp/revert-QUARANTINE-DO-NOT-READ/` and were **not** read or intaken. No report-page access.

- Repo `code-423n4/2024-03-revert-lend` @ `62ad70e6…`; solc `0.8.24`, optimizer 200, Foundry.
- Uniswap-V3-position-NFT collateral lending protocol. ~3,000 SLOC (README), ~4,401 raw lines.

## In scope (11 files)
| File | Role (focus mapping) |
|---|---|
| `V3Vault.sol` (1315) | ERC4626 lending vault: NFT collateral, loans, liquidation health checks, interest/global accounting, debt/lend limits, `onERC721Received` |
| `V3Oracle.sol` (502) | Chainlink + Uniswap-V3-TWAP position valuation; tick/rounding; **L2 sequencer** assumption |
| `InterestRateModel.sol` (102) | Interest-rate math |
| `automators/Automator.sol` (256) | Base operator/permission/fee handling for bots |
| `automators/AutoExit.sol` (245) | Bot-driven position exit |
| `transformers/AutoCompound.sol` (287) | Bot-driven fee compounding |
| `transformers/AutoRange.sol` (315) | Bot-driven range adjustment |
| `transformers/LeverageTransformer.sol` (176) | Atomic leverage/deleverage via borrow |
| `transformers/V3Utils.sol` (919) | Atomic swap + liquidity mgmt; Permit2; transformer approval flows |
| `utils/FlashloanLiquidator.sol` (110) | Atomic liquidation via UniV3 flashloan |
| `utils/Swapper.sol` (174) | Swap routing (UniversalRouter, 0x, direct pools) — crafted external calldata surface |

## Roles
Owner (Multisig+Timelock) · EmergencyAdmin (Multisig) · Operators (EOA bots for Automator actions).

## Main invariant
**Debt can never exceed lent assets** (after all loans repaid/liquidated).

## README attack ideas (where to look)
reentrancy · share calculation · price manipulation · crafted ERC-20 tokens · crafted external swap calldata.

## Publicly-known / ineligible (must NOT be scored HIT; flagging them is not an FP)
- Anything in `bot-report.md` / `4naly3er-report.md` (automated findings) — publicly known.
- Fee-on-transfer / rebasing tokens **not supported** (usage reverts) → not a valid finding class.
- Only Uniswap-V3-position ERC721 allowed as collateral.
- V3Vault is **intended** to be ERC-4626 compliant (so 4626-deviation findings may be valid if they break it).

## Specialist → focus mapping (mandatory profiles)
reentrancy (onERC721Received/transformer approvals/Swapper external calls) · access_control
(Automator operator perms, transformer approvals, owner/emergencyAdmin, init) · oracle (V3Oracle
Chainlink+TWAP tick/rounding, L2 sequencer, manipulation) · logic+economic_attack (V3Vault liquidation
health, debt/lend limits, interest/global accounting, bad-debt invariant) · erc4626 (V3Vault 4626
share/asset rounding & deposit/mint/withdraw/redeem) · arithmetic (InterestRateModel, oracle rounding,
share precision) · token_integration (Permit2/approval/callback) · flash_loan (FlashloanLiquidator).
