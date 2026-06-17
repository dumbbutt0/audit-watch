# hybra — Phase 3: Two-pass mechanism discovery (PRE-REVEAL, FROZEN)
Pass 1 = 7 families (A-G). Pass 2 = 8 shape-generator templates (T1-T8). Discovery only — no completion.

## H-L1 multiSplit
**Pass 1:**
- M1 (A) permanentLockBalance desync — permanent veNFT split: original burned but `permanentLockBalance` not
  decremented while N new permanent NFTs add nothing → global permanent balance overstated/understated → voting-power/supply desync. ctrl M; delta H; comparand=merge adjusts it; terminality H.
- M2 (A/B) proportional rounding dust — `orig*w_i/totalWeight` floors each → sum<orig → ve supply silently shrinks. ctrl M; delta L-M.
- M3 (G) checkpoint ordering — _checkpoint(original→0) then per-NFT checkpoints; slope/bias drift. ctrl L.
**Pass 2 (templates):**
- T4 migration/conversion-residue: permanent flag + locktime carried to N NFTs across the split "domain" without
  global permanentLockBalance reconciliation = **same as M1 but framed as conversion residue** (strong). 
- T8 share-price/inflation: can split+merge round-trip mint voting power (sum of split voting powers > original due
  to per-NFT rounding/bias) → **voting-power inflation**. ctrl M; delta H; **NEW vs Pass 1** (round-trip convexity).
- T5 state-machine liveness: burned original tokenId reuse / dangling approvals. ctrl L.

## H-L2 merge
**Pass 1:** M1 (A) permanent edge mis-add; M2 (G) checkpoint.
**Pass 2:** T6 cross-tx-drift: merge then split round-trip drifts permanentLockBalance (pairs with H-L1 T8);
T4 conversion-residue on merge of permanent+permanent.

## H-L3 GaugeManager._distribute
**Pass 1:** M1 (A) reward double-count across period; M2 (G) stale period index.
**Pass 2:** T1 external-dependency: a gauge/bribe external call blocks distribution (liveness DoS); T6 cross-epoch
reward drift if distribute skipped a period.

**FREEZE.** Pass 2 added: H-L1 T8 voting-power inflation round-trip (new), H-L2 T6 round-trip drift, H-L3 T1 DoS.
