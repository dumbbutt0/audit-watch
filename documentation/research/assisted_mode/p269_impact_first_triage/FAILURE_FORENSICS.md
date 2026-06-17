# P269 — FAILURE_FORENSICS

The P268 triage failure, from frozen scored artifacts (P268 REVEAL_AND_SCORE / P268_DIAGNOSIS). No new answer keys.

## What happened in P268
- **Recall surfaced the award subsystem.** karak's 20 advisory candidates included the NativeVault/slashing/snapshot
  loci where all 9 awards live: `NativeVault._startSnapshot` (narrow #2), `NativeVault.validateSnapshotProofs`
  (recall-delta #7), `NativeVault.withdrawableWei` (#8), `SlasherLib.finalizeSlashing` (#11), `cancelSlashing` (#12),
  plus narrow withdrawal-credential loci. So locus recall was **not** the gap.
- **Triage de-scoped it.** The P268 PoC queue's `skipped_high_ranked` recorded: *"NativeVault.validateWithdrawalCredentials/
  finishWithdrawal + BeaconProofs/Merkle … needs beacon-chain proof fixtures → heavy PoC harness; deferred to keep the
  first selector-in-loop run on the self-contained ERC20 Vault subsystem."* Triage chose the **easier** subsystem.
- **The easier candidates were non-awarded.** The routed ERC20 Vault candidates: C2-M1 first-depositor inflation
  (PoC-confirmed REAL but **not awarded**), C1 finishRedeem (by-design), C1-M2 approval-revert (UX). Real work,
  zero awarded recovery.
- **Result:** 0 exact recovery, even though the selector preserved the high-impact Vault mechanisms — because the
  *awarded* subsystem was never routed into PoC.

## Why triage de-scoped it (the bias)
PoC-feasibility was used as the **primary** routing signal: "self-contained ERC20 Vault is easy to harness;
NativeVault needs beacon fixtures → skip." This is the same easy-proof bias P267 fixed inside mechanism selection,
now at candidate-selection-for-PoC. The de-scope reason ("needs beacon fixtures") is a **harness-weight** statement,
not an infeasibility statement.

## What impact signals should have forced NativeVault/slashing/snapshot in
- **Award-class fit:** slashing + snapshot/checkpoint corruption + state-machine terminal failure are top award
  classes — exactly the impact families that should dominate routing.
- **Subsystem clustering:** ≥5 high-risk candidates clustered in NativeVault/slashing/snapshot → at least one
  representative should have been routed.
- **Recall-delta:** `validateSnapshotProofs`/`finalizeSlashing`/`cancelSlashing` were recall-delta (narrow baseline
  skips them) → higher routing priority, not lower.
- **Terminality:** locked ETH (H-01), snapshot DoS (H-03/M-02), slash miscalc (M-03) are permanent/systemic — far
  above a one-off royalty-style skim.

## Was a partial-runtime harness feasible?
Yes. Even without full beacon-chain proof fixtures, a **PARTIAL_RUNTIME** test of the slashing/snapshot accounting
(e.g. asserting the double-reduction of `totalAssets` in the slash+snapshot path, or the convertToAssets >
totalRestakedETH rounding) is constructible by mocking the proof inputs and exercising the accounting math directly.
So the correct P268 routing was `SELECT_FOR_PARTIAL_RUNTIME` / `SELECT_FOR_MANUAL_HARNESS_DESIGN` — **HEAVY_POC_REQUIRED,
not DEFER**. "Needs beacon fixtures" is a harness-weight flag, not an infeasibility.

## The fix P269 must encode
Impact-first ranking with PoC-feasibility demoted to a constraint; an anti-easy-PoC hard rule; subsystem-clustering
representation; and a HEAVY_POC_REQUIRED / PARTIAL_RUNTIME route so heavy-but-feasible award subsystems are carried,
not dropped. DEFER_INFEASIBLE reserved for genuine infeasibility (no source / no mockable dep / no exploit path / no
falsifiable assertion).
