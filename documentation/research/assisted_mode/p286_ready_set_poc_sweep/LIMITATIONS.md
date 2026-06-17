# P286 — LIMITATIONS

1. **Tier-C faithful reproduction**, not a live-chain or full-contract exploit. It reproduces the verbatim recipient
   control-flow + minimal mocks (ERC20/VotingEscrow/AVM); it does not run the real RewardsDistributor with its full
   dependency closure (a heavier optional follow-up). The reward computation `_claim(...)` is mocked to a fixed amount —
   the bug is in the recipient selection, which is reproduced verbatim.
2. **Scope = the two trustworthy READYs only.** No new candidates, no tuning, no remap. L2Governor is a regression re-run
   (already PASS_SUPPORTED).
3. **Eval/advisory, not production.** No production authority / submission / final severity / confirmed dashboard. The
   PoC proves the mechanism for supervised-eval recall, not a submission package.
4. **AVM-managed-lock precondition.** The misroute requires an AVM-managed lock (NFT held by the AVM while the original
   owner differs) with an expired, non-permanent lock (the direct-transfer branch). This matches the M-04 scope; locks
   not under AVM management are unaffected (shown by the control).
5. **Single-target proof.** This is one awarded relationship-error bug carried end-to-end; generalization must be checked
   on a fresh blind target (the planned next move), not inferred from this one PoC.
