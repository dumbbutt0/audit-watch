# reserve — EXCLUDED FROM SCORING (precheck-contaminated)

Reserve was selected (approved) and its checkpoints were run isolated (recorded below), but during the
REVEAL_AVAILABILITY_PRECHECK the availability **search returned awarded Medium titles** (M-01 DAO-fee
distribution, M-02 RSR seizure, M-05 StRSR era, M-06 canceled withdrawal, M-07 traceEnd). Per the no-hindsight
rule, a freeze-before-reveal mechanism-**selection** test on reserve would be contaminated, so reserve is
**EXCLUDED from blind scoring** and contributes 0 scored loci. Recorded here for provenance + the refined precheck
rule (verify reveal *existence* without fetching award *content*).

## Checkpoint records (run isolated; advisory only; UN-SCORED)
- `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest audits/reserve-2024-07-fresh/output/coverage_manifest.json --out .../outputs/reserve_*_checkpoint.json --quiet` (invariants re-verified: emits_findings:false, 0 concluded).
- accounting 139: RTokenP1 {redeemCustom,redeemTo,issueTo}, StRSRP1 {cancelUnstake,unstake,stake,withdraw,_mint,_burn},
  BackingManagerP1 {forwardRevenue,rebalance,settleTrade}, BasketHandlerP1 {quoteCustomRedemption}, DistributorP1
  {setDistributions,distribute} (A5 55/A4 23/A2 21/A1 20/A3 20). state-transition 41: RTokenP1.redeemCustom,
  BasketHandlerP1 {setPrimeBasket,setBackupConfig}, Auth pause/unpause, BackingManagerP1.settleTrade (S3 17/S4 13/S2 9/S1 2).

No selected loci, no mechanism gate, no completion, no scoring for reserve — the blind test integrity is void here.
