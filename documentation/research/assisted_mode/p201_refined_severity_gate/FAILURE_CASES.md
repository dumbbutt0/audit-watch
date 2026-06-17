# P201 — failure cases & limitations (described, not patched)

## A. The structural limitation: zetachain Highs are off-chain (corpus-scope failure)
The dominant "failure" is **corpus scope**, not the gate. 11/14 awarded Highs live in the off-chain Go layer
(observer/cctx/consensus/UTXO/TSS-voting) — a Solidity-source blind trace structurally cannot reach them:
- H-01 NonceVoter halt · H-02 observer internal-TX · H-03 fake ZetaReceived cctx-queue · H-04 malicious inbound
  blocks processing · H-05 disable-outbound theft · H-07 outbound DoS · H-08 tombstoned observer · H-09 unconfirmed
  UTXO griefing · H-11 confirmation race double-spend · H-12 voting-index double-spend · H-14 TSS key voting collision.
- These are not contract findings → not in scope for the severity gate under test. They neither validate nor
  invalidate it; they just aren't reachable. (This is why the matched-High set is empty.)

## B. Recall misses on the 3 contract-level Highs (deep-pass recall, not severity)
- **H-06** "zEVM cross-chain messages ignore the user-specified message" (SystemContract.depositAndCall, zeta-13):
  the blind run found *reentrancy* and *stale-amount-forwarding* instead of the *message-ignored* mechanism →
  recall miss (wrong mechanism). The severity gate never saw H-06's mechanism, so it couldn't grade it.
- **H-10** "ZetaTokenConsumerTrident swap always reverts (wrong router method)": the sample took
  ZetaTokenConsumer**UniV2** (zeta-17), not **Trident** → file not sampled. Pure coverage miss.
- **H-13** "User funds lost during CCTX due to contracts being paused": relates to the pause surfaces (zeta-02/06),
  but the blind run framed *admin pause-asymmetry* (TSS can act during pause), not the *user-fund-loss-during-cctx*
  mechanism → recall miss.
These are P183–P188 **deep-pass recall** items, independent of the severity gate.

## C. The gate's own risk: 0 HIGH_CONFIRMED (positive behavior unvalidated)
The refined reject-first gate confirmed **zero** Highs across 46 mechanisms. Every blind High-ceiling mechanism fell
into one of: admin/TSS/owner-compromise (auth, capped Medium), DoS/griefing (Medium), depends-on-unseen-cross-chain/
TSS/replay code (Harness), precision/self-inflicted (Medium), or source-refuted/latent. **On this corpus that is
plausibly correct** (the contract layer's awarded findings are Mediums; the theft-Highs are off-chain). **But it
means the gate's High-confirming path was never exercised** — we have no positive control proving the gate would
confirm a genuine permissionless contract-High rather than over-demote it. This is the single most important
caveat: P201 validated demotion, not confirmation.

## D. Correctly handled (the wins)
- **M-13** "Sender of outbound cctx set to incorrect sender → lost assets" (zeta-05/zeta-15 tx.origin attribution):
  ceiling HIGH → gate **Medium** = awarded Medium. ✓ Exact mechanism match, correct calibration.
- **M-28** "UpdateSystemContract → withdraw DoS" (zeta-11): ceiling HIGH → gate **Medium** = awarded Medium. ✓
- **M-16** "Arbitrary destination gas limit" (zeta-15 input-validation): graded Harness — acceptable (≥Medium, not a
  false-LOW) for an awarded Medium.
- **M-01 / M-09 / M-26 / M-30** (loose matches): ceiling HIGH → gate Medium = awarded Medium. ✓ direction correct.
- All admin/TSS-compromise drains (zeta-02/03/04/09/11/18) → Medium (admin-prereq cap): consistent with how
  contests typically rate centralization/key-compromise issues (not High). No awarded contract-High contradicts this.

## E. FP-side note
zeta-08 (ZetaInteractor ZERO_BYTES permissionless auth-bypass) is the strongest *permissionless* blind candidate;
it is **not** in the awarded set → a recall false-positive the gate correctly routed to Harness (not confirmed High).
Had it been confirmed High, it would have been a false High; routing to Harness was conservative-correct.

## Summary
No false-demotion of a matched awarded-High occurred (none were matched). The gate's demotion behavior is correct
on every matched contract-Medium. The unresolved risk is whether the gate over-demotes genuine permissionless
contract-Highs — untestable here because zetachain has none in-scope. A corpus with permissionless contract-level
Highs is required to close this.
