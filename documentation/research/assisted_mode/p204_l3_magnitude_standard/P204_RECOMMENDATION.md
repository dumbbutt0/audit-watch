# P204 — recommendation

## Final decision: `L3_STANDARD_PROMISING`
The harness-grade L3 realized-impact standard achieved — for the first time in the campaign — **clean two-sided
separation** on decent, via **executable Foundry harnesses** over real decent contracts (only external deps mocked;
production source byte-identical; 5/5 tests pass).

### Results vs the L3_STANDARD_PROMISING criteria
- ✅ **H-01 remains High via executable material impact** — permissionless attacker minted 1,000,000 ether unbacked
  DcntEth (`setRouter`→`mint`); control proves the hijack is the required lever.
- ✅ **M-03 demoted** — under source-valid honest custody, no attacker tx realizes material theft (cannot pull a
  victim's approved funds; cannot drain UTB treasury; only self-funded routing) → MEDIUM_OR_LOWER. The realized
  impact matches the C4 Medium (fee/signature/unauthorized-call class).
- ✅ **≥1 P203 false-High removed** — decent-06 demoted (no drain without an unsourced residual balance); decent-12
  routed to NEEDS_HARNESS (no source-valid path to redeemable dcntEth).
- ✅ **No source-proven genuine High wrongly demoted** (H-01 kept; H-02/03/04 are recall-misses, untouched).
- ✅ **Production files unchanged** (decent source tree `623aedd6` START==END).

### The decisive advance
P200→P203 showed static gates cannot separate worst-case capability from realized impact (P203: an independent
source reviewer still rated M-03's arbitrary-call capability High). P204 shows **an executable realized-impact
standard does separate them**: the EVM, under honest custody, refuses to move material value for M-03/decent-06,
while it does for H-01. HIGH-bucket precision on decent goes 6→1 (1/6 → 1/1) with **0 genuine-High loss**.

### Recommended next (each needs explicit go — NOT actioned here)
1. **Generalize + 2nd-corpus validate the L3 standard before any wiring.** One corpus (decent) is a strong signal,
   not a production warrant. Re-run the harness-grade HIGH standard on another corpus with contract-level Highs
   (e.g. vultisig — PCS flagged 2 qualifying contract-Highs) to test generalization.
2. **Define the operational form**: L3 is a *gate on HIGH promotion that requires a passing PoC/harness* — this is
   the project's existing **Level-3 PoC standard** (`L1 entry / L2 state-flip / L3 outcome`) applied as the severity
   bar. Spec how candidates get a harness (auto-scaffold vs human) and the cost budget; do **not** wire until
   generalization holds.
3. **Build the decent-12 liquidity harness** to convert its NEEDS_HARNESS into a definite verdict (close the one
   source-argument-only gap).
4. **Deep-pass recall** (H-02/03/04 recall-misses) and the **oracle track** remain separate.

### Cross-arc synthesis (frontier resolved in principle)
P200 demotion-partial · P201 demotion-clean/confirmation-untestable · P202 confirmation-works/demotion-regresses ·
P203 static-precondition-can't-fix (capability vs realized-impact) · **P204 executable realized-impact standard
separates them (H-01 High, M-03/06 demoted, 12 harness).** The Medium severity-calibration frontier — open since
P186 — now has a working principle: **HIGH requires a passing realized-impact PoC, not static capability.** Remaining
work is **generalization + operationalization**, not a new idea.

## Acceptance criteria — met
L3 standard pre-specified (brief) + encoded as assertions before result interpretation ✓ · harnesses source-valid,
**no production contract edited** (real source imported byte-identically; only external deps mocked) ✓ · H-01 and
M-03 both tested ✓ · capability separated from realized impact via measured value/control delta ✓ · v2 vs L3 scored
separately ✓ · no production files modified ✓ · JSON valid ✓ · production hashes byte-identical START==END ✓.
