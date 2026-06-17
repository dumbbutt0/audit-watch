# Silo Finance (Silo Vaults) — Scope Reconstruction (blind, pre-answer-key)

**Source:** repo `scope.txt` + `out_of_scope.txt` + `README.md` only. `4naly3er-report.md`, `audits/`,
`discord-export/`, `coverage/`, `lcov.info` quarantined to `/tmp/silo-QUARANTINE-DO-NOT-READ/` (not read/intaken).
No report-page access.

- Repo `code-423n4/2025-03-silo-finance` @ `1732f3e…`; solc `0.8.28`, EVM cancun, Foundry. ~1,697 nSLOC in scope.
- **SiloVault = a MetaMorpho/MorphoVault ERC4626 fork** over Silo isolated lending markets, **plus a novel
  vault incentives/reward layer**. Imports openzeppelin5 ERC4626/ERC20Permit/Ownable2Step/Multicall + morpho-blue.

## In scope (key impl files)
| File | nSLOC | Role |
|---|---|---|
| `SiloVault.sol` | 554 | ERC4626 vault fork: deposit/mint/withdraw/redeem, totalAssets, fee accrual, market caps + withdraw/supply queue reallocation, **reward-notification hooks on share transfer/mint/burn** |
| `IdleVault.sol` | 33 | idle ERC4626 for unallocated capital |
| `PublicAllocator.sol` | 90 | permissionless reallocation (fees, flow caps) |
| `VaultIncentivesModule.sol` | 106 | wires claiming-logics + notification receivers to the vault |
| `SiloIncentivesControllerCL.sol` | — | claiming-logic adapter |
| `SiloIncentivesController.sol` | 78 | reward controller (immediate distribution) |
| `BaseIncentivesController.sol` | 159 | core reward index/accrual mechanics |
| `DistributionManager.sol` | 162 | reward distribution math (index, emissions) |
| libs: `SiloVaultActionsLib, PendingLib, ConstantsLib, ErrorsLib, EventsLib` | | actions/timelock/constants |

## Roles
Owner · Curator · Allocator · Guardian (MetaMorpho role model; Ownable2Step; pending-timelock changes via PendingLib).

## OUT OF SCOPE (per README weird-ERC20 table) — must NOT be scored HIT; flagging ≠ FP
**Fee-on-transfer, rebasing/airdrop balance changes, approval-race/reset, pausable, upgradeable, flash-mint,
blocklists, high-decimals(>18), multiple-token-address** — all OUT OF SCOPE. Also: everything in
`4naly3er-report.md` (automated). **⇒ the 6 awarded Mediums are NOT token-weirdness** — they live in the
**vault-accounting + reward/incentives** logic (the Silo-novel layer over audited MetaMorpho).

## Where the bugs almost certainly are (focus the deep-read)
1. **Reward accrual ordering vs share supply changes** — does the vault notify the IncentivesController/update
   the reward index BEFORE vs AFTER `_mint`/`_burn`/`transfer` changes `totalSupply`/balances? A wrong order =
   stolen/mis-accrued rewards (Silo's delta from MetaMorpho).
2. **feeShares minting order** — fee shares minted before/after reward accrual → fee recipient gets/dilutes rewards.
3. **transfer/transferFrom side-effects** — share transfers must move reward entitlement; missing notification = loss.
4. **Market cap (maxDeposit) / reallocation / market removal** — PublicAllocator flow caps, withdraw-queue removal.
5. **4626 rounding / donation / inflation / zero-share** on deposit/mint/withdraw/redeem.
6. **DistributionManager index math precision**; **claiming-logic** (CL) adapter correctness.

## Specialist → focus mapping
erc4626_vault_accounting (SiloVault 4626 + feeShares + caps + rounding) · reward-accounting (incentives layer —
applied manually, not a pipeline surface) · reentrancy_callback (transfer→notification, external 4626 target
calls) · token_integration (only the IN-scope token behaviors; FoT/rebasing/approval-race are OUT of scope) ·
access_control_init (roles, factory init, pending-timelock) · math_precision (reward index, share rounding) ·
logic/economic_attack (reallocation, market removal, reward theft). oracle_liquidation + transformer_external_call
= no surface in the vault scope → per-specialist waiver (recall-risk).
