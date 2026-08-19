# Submission Packs — cartha

32 findings total (22 real + 10 merged/rejected/info). Each folder has `report.md` + `sources/` (full vulnerable files).

## Real findings (recommended for submission) (22)

| ID | Severity | Category (VRT) | Title | Vulnerable files | Status |
|---|---|---|---|---|---|
| [CARTHA-SEAM-001](CARTHA-SEAM-001/report.md) | Critical | Business Logic Errors | gmValueInUsdc returns an 18-decimal USD value but is summed with 6-dec | PoolDeployLib.sol, CarthaVault.sol | poc_required |
| [DOS-001](DOS-001/report.md) | High | DoS with (Unexpected) revert | A single child vault whose GM price read reverts bricks ALL parent ope | CarthaParentVault.sol, CarthaVault.sol, PoolDeployLib.sol | poc_required |
| [DT-001](DT-001/report.md) | High | Transaction-Ordering Dependence (TOD) / Front Running | Share dilution via deposits during the async 0xM pool deploy/recall wi | PoolDeployLib.sol, CarthaVault.sol | poc_required |
| [AC-001](AC-001/report.md) | Medium | Improper Access Control | RESCUER role can drain GM marketToken / poolToken (deployed vault valu | CarthaVault.sol | submit |
| [DOS-002](DOS-002/report.md) | Medium | DoS with (Unexpected) revert | releaseFromParent / release permanently un-callable when child funds a | CarthaParentVault.sol, CarthaVault.sol | submit |
| [DOS-003](DOS-003/report.md) | Medium | DoS with (Unexpected) revert | withdraw / releaseFromParent revert when ANY single active child rever | CarthaParentVault.sol | submit |
| [DT-003](DT-003/report.md) | Medium | Business Logic Errors | removePool strands the GM-deployed portion of the parent's stake | CarthaParentVault.sol, CarthaVault.sol | submit |
| [DT-004](DT-004/report.md) | Medium | Violation of Secure Design Principles | GM-pricing inputs (oracle/reader/marketToken/dataStore) are ADMIN-sett | CarthaVault.sol, PoolDeployLib.sol | submit |
| [TI-005](TI-005/report.md) | Medium | Business Logic Errors | poolToken (valuation) and marketToken (router send/recall) are two ind | CarthaVault.sol, PoolDeployLib.sol | submit |
| [AC-002](AC-002/report.md) | Low | Improper Access Control | CarthaParentVault.executeForceExit applies an uncapped penaltyBps from | CarthaParentVault.sol | submit |
| [AR-002](AR-002/report.md) | Low | Integer Underflow | First-deposit decimal-offset exponent (18 - assetDecimals) underflow-r | CarthaVault.sol | downgraded |
| [AR-003](AR-003/report.md) | Low | Business Logic Errors | Parent _convertToShares/_convertToSharesRoundUp hardcode the 1e12 firs | CarthaParentVault.sol, CarthaVault.sol, CarthaVaultFactory.sol | downgraded |
| [DOS-005](DOS-005/report.md) | Low | DoS with (Unexpected) revert | _distributeToChildren reverts the entire lock when all weighted pools  | CarthaParentVault.sol | downgraded |
| [DT-006](DT-006/report.md) | Low | Reentrancy | No reentrancy guards; safety relies on non-callback asset + trusted ex | CarthaVault.sol, CarthaParentVault.sol | downgraded |
| [LG-002](LG-002/report.md) | Low | Improper Authentication | depositAndLock bypasses the EIP-712 signature gate entirely; the 'mine | CarthaVault.sol, CarthaParentVault.sol | downgraded |
| [LG-003](LG-003/report.md) | Low | Business Logic Errors | migratePositionShares sets position.shares = balanceOf(owner), over-at | CarthaVault.sol | downgraded |
| [LG-004](LG-004/report.md) | Low | Business Logic Errors | processAutoLocks re-locks an expired position (resets start), silently | CarthaVault.sol | downgraded |
| [OR-001](OR-001/report.md) | Low | Business Logic Errors | GM price for valuing held GM uses the DEPOSIT PnL cap (MAX_PNL_FACTOR_ | PoolDeployLib.sol, CarthaVault.sol | downgraded |
| [TI-004](TI-004/report.md) | Low | DoS with (Unexpected) revert | USDC blacklist/freeze DoS on payouts is per-iteration in batch loops ( | CarthaVault.sol, CarthaParentVault.sol | downgraded |
| [UP-003](UP-003/report.md) | Low | Other | Parent retains a DEPRECATED `positions` mapping mid-struct to preserve | CarthaParentVault.sol | submit |
| [AC-004](AC-004/report.md) | Info | Privilege Escalation | ADMIN can grant itself EJECTOR / FORCE_EXITER and bypass merkle-list i | AccessControlFacet.sol | downgraded |
| [AR-006](AR-006/report.md) | Info | Business Logic Errors | getUtilization can exceed 10000 bps (>100%) when GM loss makes TVL < t | CarthaVault.sol, CarthaParentVault.sol | downgraded |

## Merged duplicates (do not submit separately) (3)

| ID | Severity | Category (VRT) | Title | Vulnerable files | Status |
|---|---|---|---|---|---|
| [AR-001](AR-001/report.md) | High | Business Logic Errors | gmBalance * gmPrice / 1e30 truncates the GM TVL leg to 0 for small GM  | PoolDeployLib.sol, CarthaVault.sol | merged |
| [EA-001](EA-001/report.md) | High | Transaction-Ordering Dependence (TOD) / Front Running | Share dilution via deposits during the async 0xM (GMX-v2) deploy/recal | CarthaVault.sol, PoolDeployLib.sol | merged |
| [DT-005](DT-005/report.md) | Low | Improper Access Control | executeForceExit applies an uncapped penaltyBps | CarthaParentVault.sol, CarthaForceExit.sol | merged |

## Rejected — honest negatives (do not submit) (7)

| ID | Severity | Category (VRT) | Title | Vulnerable files | Status |
|---|---|---|---|---|---|
| [AC-003](AC-003/report.md) | Info | Improper Access Control | DiamondInit.init(admin) is external and unguarded but is NOT reachable | DiamondInit.sol | rejected |
| [AC-005](AC-005/report.md) | Info | Improper Authentication | EJECTOR-signed LockRequest binds owner/poolId/amount/lockDays/hotkey/t | CarthaVault.sol | rejected |
| [AR-005](AR-005/report.md) | Info | Timestamp Dependence | uint64(block.timestamp) casts on lock timestamps/cooldown/epoch are sa | CarthaVault.sol, CarthaParentVault.sol, LibDiamond.sol, PoolDeployLib.sol | rejected |
| [EA-004](EA-004/report.md) | Info | Business Logic Errors | First-depositor / inflation surface is mitigated by 1e12 virtual offse | CarthaVault.sol, CarthaParentVault.sol | rejected |
| [UP-001](UP-001/report.md) | Info | Other | erc7201 storage locations for CarthaVault / CarthaParentVault / Cartha | CarthaParentVault.sol | rejected |
| [UP-002](UP-002/report.md) | Info | Improper Access Control | UUPS _authorizeUpgrade is ADMIN-gated on both vaults and the factory;  | CarthaVault.sol | rejected |
| [UP-004](UP-004/report.md) | Info | Other | No selfdestruct, no storage-slot collision with ERC-1967 admin/impl/be | CarthaParentVault.sol | rejected |

