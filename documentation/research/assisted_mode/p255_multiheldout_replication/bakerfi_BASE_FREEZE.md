# bakerfi — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue. Sealed key not read. Disclosed-exposed areas (create-time reentrancy; ERC4626
share-accounting, p242) avoided — loci taken from the leverage/flashloan/oracle surface instead.

## Generation basis (exact command/path)
- Surface: `audits/bakerfi-2024-05-holdout/output/coverage_manifest.json` (167 in-scope fns).
- Checkpoints: `python scripts/accounting_checkpoint_audit.py --manifest audits/bakerfi-2024-05-holdout/output/coverage_manifest.json --out .../outputs/bakerfi_accounting_checkpoint.json --quiet` (+ state_transition). Invariants re-verified.
- Base read: `core/Vault.sol` (rebalance), `core/strategies/StrategyLeverage.sol` (onFlashLoan/harvest/_getPosition/_undeploy), oracle usage.

## Checkpoint records (advisory)
accounting 21 recs: Vault.{rebalance×3, deposit×3, withdraw×3, convertToShares/Assets} (A1/A2), StrategyLeverage.{_repayAndWithdraw×2, onFlashLoan, harvest, _undeploy, _supplyBorrow} (A2/A4), PythOracle.getAndUpdatePrice. state-transition: 0.

## Frozen base candidate set
| id | sev(blind) | locus | mechanism observed | checkpoint |
|---|---|---|---|---|
| **B1** | Med/High | `StrategyLeverage._getPosition` (L453–460) | staleness gate uses **OR**: reverts iff `priceMaxAge>0 AND ethStale AND collStale`; so **one** fresh feed suffices → a stale collateral (or eth) price is tolerated and used in valuation | (oracle) |
| **B2** | Low/Med | `StrategyLeverage.harvest` (L387–419) | `balanceChange` (P&L) is only set when `deltaDebt == 0`; a harvest that triggers `_adjustDebt` (deltaDebt≠0) updates `_deployedAmount` but reports **0** P&L → no perf-fee + silent value change. `deltaDebt` also algebraically cancels in `newDeployedAmount` | A2 on harvest |
| **B3** | Low/Med | `StrategyLeverage._undeploy` (L482–526) | `_pendingAmount` read at L517 but "not cleared to save gas" → stale `_pendingAmount` could be reused if a later path reads it before a fresh set | A2/A4 |

### Checkpoint-hit suspicious loci with no base candidate
| locus | checkpoint | why no candidate |
|---|---|---|
| `StrategyLeverage.onFlashLoan` | A2/A4 | callback auth is **correct** (msg.sender==lender, initiator==this, token==WETH) → refuted as candidate |
| `Vault.deposit`/`withdraw`/`convertTo*` | A1/A2 | ERC4626-share area — **excluded** (p242 prior exposure) |
| `PythOracle.getAndUpdatePrice` | A1 | not read in depth this pass |

## Ranking (pre-reveal)
1. **B1** _getPosition staleness OR-logic 2. **B2** harvest P&L-only-when-deltaDebt==0 3. **B3** _undeploy stale _pendingAmount

## Three-way state tag
| id | tag | base chain state |
|---|---|---|
| B1 | BASE_BORN_INCOMPLETE | OR-vs-AND seen; depends on whether getSafeLatestPrice already reverts; exploit/impact not computed |
| B2 | BASE_BORN_INCOMPLETE | P&L-gap seen; who-loses + amplification not computed |
| B3 | BASE_BORN_INCOMPLETE | not-cleared comment seen; concrete stale-reuse path not traced |
| onFlashLoan | CHECKPOINT_HIT_SUSPICIOUS_LOCUS | fired; auth correct → no candidate |
| Vault ERC4626 | (excluded — prior exposure) | — |
| (none) | BASE_COMPLETED_CHAIN | base completed 0 full chains |

**FREEZE:** final before selection/reveal. Hash recorded in bakerfi_REVEAL_AND_SCORE.md before key opened.
