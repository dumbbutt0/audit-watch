# notional — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue. Sealed key not read (Sherlock judging repo not opened). Subtle loci only;
p242 Family-A/B excluded.

## Generation basis
- Surface: `audits/notional-exponent-2025-06-fresh/output/coverage_manifest.json` (~290 in-scope fns).
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <notional manifest> --out .../outputs/notional_*_checkpoint.json --quiet` (invariants re-verified: emits_findings:false, 0 concluded).
- Base read: `_src/notional-v4/src/AbstractYieldStrategy.sol` (convert*, price, effectiveSupply, fees, mint/burn,
  initiateWithdraw/escrow, _accrueFees/_calculateAdditionalFeesInYieldToken, _update), `rewards/AbstractRewardManager.sol`.

## Checkpoint records (advisory)
accounting 117: AbstractYieldStrategy {_withdraw,_mintSharesGivenAssets,_burnShares,convert*,mintShares,burnShares,
redeemNative,initiateWithdraw,collectFees}, AbstractRewardManager {_claimVaultRewards,updateAccountRewards},
AbstractLPOracle._calculateLPTokenValue (A1 39/A4 33/A3 20/A2 16/A5 9). state-transition 35: AbstractRewardManager
{updateRewardToken,updateAccountRewards}, AbstractLendingRouter.migratePosition, AbstractYieldStrategy
{collectFees,_accrueFees,redeemNative} (S1 22/S4 6/S3 6/S2 1).

## Frozen base candidate set (subtle, multi-mechanism)
| id | sev(blind) | locus | observed |
|---|---|---|---|
| **B1** | Med/High? | `AbstractYieldStrategy` conversion + effectiveSupply/escrow | `convertSharesToYieldToken`/`convertYieldTokenToShares` use `(_yieldTokenBalance() - feesAccrued() + VIRTUAL_YIELD_TOKENS)` over `effectiveSupply() = totalSupply - escrowedShares + VIRTUAL_SHARES`; escrowed shares' yield tokens stay in balance but shares leave effectiveSupply |
| **B2** | Med? | `AbstractYieldStrategy` fee accrual | `_calculateAdditionalFeesInYieldToken` = continuous exp-decay (Taylor) on `_yieldTokenBalance()-s_accruedFees`; `_accrueFees` must precede mint/burn; `collectFees` deletes `s_accruedFeesInYieldToken` |
| **B3** | Med? | `AbstractYieldStrategy` escrow + withdraw-request state | `initiateWithdraw` escrows `s_escrowedShares += sharesHeld` after converting; `mintShares`/`preLiquidation` gated by `_isWithdrawRequestPending`; transient `t_CurrentAccount` valuation |

### Checkpoint-hit suspicious loci, no candidate
| locus | why |
|---|---|
| AbstractLPOracle._calculateLPTokenValue | LP oracle valuation; needs DEX-specifics not read this pass |
| Vault deposit/mint convert (Family-B-like) | excluded (p242 prior exposure) |

## Three-way tag
| id | tag |
|---|---|
| B1 | BASE_BORN_INCOMPLETE (conversion/escrow basis seen; winner/loser not computed) |
| B2 | BASE_BORN_INCOMPLETE (exp-decay fee + accrue-before-op seen; drift/extraction not traced) |
| B3 | BASE_BORN_INCOMPLETE (escrow + withdraw-request + transient valuation seen; manipulation not traced) |
| (none) | BASE_COMPLETED_CHAIN: 0 |

**FREEZE:** final before selection/reveal. Hash in notional_REVEAL_AND_SCORE.md before key opened.
