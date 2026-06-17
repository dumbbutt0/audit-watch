# P205 — recommendation

## Decision: `L3_STANDARD_PARTIAL`

Second-corpus validation of the P204 L3 realized-impact HIGH standard on vultisig-2024-06 is **partial**:

- ✅ **L3 demotion side generalizes and was EXECUTED on a 2nd corpus.** v-07 (real `src/base/ILOWhitelist`, forge
  2/2 PASS under solc 0.7.6): an access-bypass capability that requires the admin role and moves no funds →
  `MEDIUM_OR_LOWER`. This is the same capability→demote logic L3 applied to decent's M-03/decent-06 in P204.
- ✅ **The over-HIGH skew the standard is meant to fix reproduces here** (blind 7/8 ≥HIGH; awarded-Medium M-03
  over-rated to HIGH) — consistent with P199/P198 on a 3rd architecture.
- ⚠️ **The L3 HIGH-confirmation (positive-control) side is `HARNESS_INCONCLUSIVE` on vultisig.** Every awarded src/
  High is in ILOPool/ILOManager, gated behind a solc-0.7.6 OZ-3.4 + v3-core/v3-periphery dependency web with no
  locally-vendored compatible deps. The HIGH-confirmation side was already executed on decent (P204, PASS).
- ⚠️ **The executed negative control does not map to an awarded finding** (v-07 is the by-design ILO whitelist, not
  awarded H-02 in the hardhat `Whitelist.sol`). No awarded High was wrongly demoted; no false-High was created.

**Why not VALIDATED:** the decision space requires ≥1 genuine awarded High *preserved by an executable material-impact
harness*; that harness was not built on vultisig (compile obstacle). **Why not FAILED:** no false-High and no
false-demotion of an awarded High occurred; the demotion mechanism executed cleanly.

## What this means for the campaign
The L3 principle (HIGH = executed realized material impact, not static capability) now has: a clean two-sided proof
on **decent** (P204) + an executed **demotion** generalization on **vultisig** (P205) + the over-HIGH skew confirmed
on a 3rd architecture. The remaining generalization gap is a **positive-control High confirmed by harness on a 2nd
corpus** — blocked here only by toolchain dependency assembly, not by the standard itself.

## Next (NOT this phase; no production wiring yet)
1. **Finish the vultisig positive control** to convert PARTIAL→VALIDATED: assemble a solc-0.7.6 V3 harness env
   (forge-install OZ 3.4.x + Uniswap v3-core/v3-periphery, or vendor the canonical 0.7.6 files) and build
   **M-03 cap-bypass (negative, awarded Medium)** + **H-01 claim-fee-loss (positive, awarded High)**. M-03 is the
   higher-value, more tractable target (buy() needs no live pool).
2. **OR** pick a 2nd positive-control corpus with a lighter dependency web (no V3/0.7.6 entanglement) to get the
   positive-control harness cheaply.
3. Only after a positive-control High is harness-confirmed on a 2nd corpus → consider operationalizing the L3 HIGH
   bar (require a passing L1/L2/L3 PoC for HIGH promotion). Deep-pass recall + oracle track remain separate.

## Guardrails honored
Production prompt/checker/resolver/ledger untouched (`ef93a6c2`/`5d2a97f9`/`3b0b2c02` byte-identical START==END);
vultisig src tree `d9489e47` unchanged; `realsrc/` byte-identical; key opened read-only only post-FREEZE-1; blind
firewall clean; harness artifacts isolated under `pocs/`; fabrication_rate=0.
