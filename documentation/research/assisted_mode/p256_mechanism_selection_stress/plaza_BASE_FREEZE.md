# plaza — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue. Sealed key not read. Subtle-accounting/state loci only.

## Generation basis
- Surface: `audits/plaza-finance-2024-12-fresh/output/coverage_manifest.json` (~136 in-scope fns).
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <plaza manifest> --out .../outputs/plaza_*_checkpoint.json --quiet` (invariants re-verified: emits_findings:false, 0 concluded).
- Base read: `_src/plaza-evm/src/Pool.sol` (create/redeem/getCreateAmount/getRedeemAmount/startAuction/transferReserveToAuction), `BondToken.sol`, `Auction.sol`.

## Checkpoint records (advisory)
accounting 44 recs: Pool._create/_redeem/simulate*/setFee, BalancerRouter, PoolFactory, PreDeposit.claim, Auction.endAuction, BondToken.{mint,burn,updateIndexedUserAssets} (A4 19/A2 9/A1 8/A3 5/A5 3). state-transition 31: Auction.{bid,removeExcessBids,claimBid,endAuction,claimRefund}, Pool.{create,_create,redeem,_redeem,transferReserveToAuction,setFee}, PreDeposit.{deposit,claim}, Distributor.claim (S4 18/S3 7/S1 6).

## Frozen base candidate set (subtle, multi-mechanism)
| id | sev(blind) | locus | observed |
|---|---|---|---|
| **B1** | High? | `Pool.getCreateAmount`/`getRedeemAmount` collateral-level pricing | create uses **current** collateralLevel; redeem-BOND recomputes collateralLevel with **post-redemption** supply `(bondSupply-depositAmount)`; branch flips at `COLLATERAL_THRESHOLD`; bond redeem extra-capped by `marketRate` |
| **B2** | Med? | `Pool.simulateCreate`/`simulateRedeem` time-fee | `poolReserves -= poolReserves*fee*(block.timestamp-lastFeeClaimTime)/(PRECISION*YEAR)` subtracted in **pricing** only; actual transfers use the **full** reserve balance; `lastFeeClaimTime` reset only by `claimFees` |
| **B3** | Med? | `Pool.startAuction`/`transferReserveToAuction` coupon | `couponAmountToDistribute = totalSupply*sharesPerToken` snapshot at auction start; bonds mint/burn during period; `poolSaleLimit` bounds reserve sale |

### Checkpoint-hit suspicious loci, no candidate
| locus | why |
|---|---|
| BalancerRouter join/exit | wrapper routing; no subtle divergence on blind read |

## Three-way tag
| id | tag |
|---|---|
| B1 | BASE_BORN_INCOMPLETE (pricing basis seen; exploit/winner not computed) |
| B2 | BASE_BORN_INCOMPLETE (fee-in-pricing-not-balance seen; reconciliation not traced) |
| B3 | BASE_BORN_INCOMPLETE (coupon snapshot seen; over/under-distribution not traced) |
| (none) | BASE_COMPLETED_CHAIN: 0 |

**FREEZE:** final before gate/reveal. Hash in plaza_REVEAL_AND_SCORE.md before key opened.
