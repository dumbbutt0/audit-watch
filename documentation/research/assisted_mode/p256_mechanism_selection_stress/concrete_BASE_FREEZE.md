# concrete — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue. Sealed key not read. Subtle-accounting/state loci only. **p242-exposed families
excluded** (Family-A deposit `transferFrom`-before-`_mint` reentrancy; Family-B `max*`/`preview*` using `convertTo*`).

## Generation basis
- Surface: `audits/concrete-2024-11-fresh/output/coverage_manifest.json` (~293 in-scope fns).
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <concrete manifest> --out .../outputs/concrete_*_checkpoint.json --quiet` (invariants re-verified).
- Base read: `_src/src/vault/ConcreteMultiStrategyVault.sol` (takeFees/accruedProtocolFee/accruedPerformanceFee/_withdraw/_withdrawStrategyFunds), `_src/src/queue/WithdrawalQueue.sol`, `RewardManager.sol`.

## Checkpoint records (advisory)
accounting 106 recs: Vault.{withdraw,_withdraw,deposit,mint,redeem,_withdrawStrategyFunds,claimWithdrawal,
batchClaimWithdrawal,accruedProtocolFee,_convertTo*}, StrategyBase.harvestRewards, ClaimRouter.addRewards
(A5 36/A3 26/A1 22/A4 12/A2 10). state-transition 30: WithdrawalQueue.{prepareWithdrawal,getWithdrawalRequests},
MultiStrategyVaultHelper.addOrReplaceStrategy, registries (S2 14/S4 11/S3 5).

## Frozen base candidate set (subtle, multi-mechanism; excluded families avoided)
| id | sev(blind) | locus | observed |
|---|---|---|---|
| **B1** | High? | `WithdrawalQueue.prepareWithdrawal` | finalize/claim state semantics: guard `if (_requestId < lastFinalizedRequestId) revert` (allows requestId **>** lastFinalized = **unfinalized** to proceed); claim only if `_avaliableAssets > amount` (strict); `claimed` set only inside that branch; no partial fill |
| **B2** | Med/High? | `Vault.takeFees` / `accruedProtocolFee` / `accruedPerformanceFee` | `highWaterMark` set from `convertToAssets(1e18)` computed **before** fee shares minted; protocol fee is **time-based on totalAssets** (charged w/o gains); fee minted as shares (dilution) |
| **B3** | Med? | `Vault._withdrawStrategyFunds` | revert-guard uses `diff.mulDiv(allocation,…,Ceil)` but actual `amountToWithdraw = amount_.mulDiv(allocation,…,Ceil)` (full `amount_`, not `diff`); `Ceil` per-strategy; allocation-proportional withdraw |

### Checkpoint-hit suspicious loci, no candidate
| locus | why |
|---|---|
| Vault.deposit/mint, max*/preview* | **excluded** (p242 Family-A/B prior exposure) |
| registries (Token/Vault/Implementation) | governance-set; no attacker path on blind read |

## Three-way tag
| id | tag |
|---|---|
| B1 | BASE_BORN_INCOMPLETE (queue state semantics seen; which check is the awarded one not resolved) |
| B2 | BASE_BORN_INCOMPLETE (HWM/fee timing seen; winner/loser not computed) |
| B3 | BASE_BORN_INCOMPLETE (diff-vs-amount_ basis mismatch seen; over-withdraw impact not traced) |
| (none) | BASE_COMPLETED_CHAIN: 0 |

**FREEZE:** final before gate/reveal. Hash in concrete_REVEAL_AND_SCORE.md before key opened.
