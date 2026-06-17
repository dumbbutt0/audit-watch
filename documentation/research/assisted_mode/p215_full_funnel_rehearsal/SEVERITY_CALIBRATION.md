# P215 — SEVERITY CALIBRATION

| candidate | P215 calibrated | official | direction |
|-----------|-----------------|----------|-----------|
| ZETA-04 (=H-13) | Medium (triage) / needs_harness (L3) | **High** | **UNDER by 1** |
| ZETA-11 (=H-10) | Medium (triage) / needs_harness (L3) | **High** | **UNDER by 1** |
| ZETA-03 (=QA[09]) | Low (triage) | QA/Low | **MATCH** |
| ZETA-02 (=QA[05]) | Low (triage) | QA/Low | **MATCH** |
| ZETA-07 (non-awarded) | Low | (not awarded) | n/a (correctly low) |
| ZETA-12 (non-awarded) | Medium | (not awarded; QA-class) | mild over (Medium vs QA) |
| All other Highs (ZETA-01/05/06/08/10) | needs_harness/medium (blocked) | (no official match) | no over-High |

## Headline
- **SEVERITY_OVER = 0.** No candidate was rated above its official severity (ZETA-12 is the only mild over, Medium vs
  QA, for a non-awarded item).
- **SEVERITY_UNDER = 2.** Both genuine in-scope Solidity Highs (H-13 pause-DoS, H-10 Trident-DoS) were found but rated
  **Medium**. **Both are DoS/availability-class** — exactly the family P212 flagged as prone to under-rating.

## Does the P214 DoS carve-out fix these? (No — and that is informative)
The P214 deterministic core-path DoS carve-out (flag-on) upgrades Medium→High only with all 10 criteria, including
`executed_l3_harness`, `permissionless_or_normal_user_trigger`, and `no_trusted_admin_prereq`.
- **H-13 (ZETA-04):** trigger requires the contracts to be **paused** (an admin/operational state) and a CCTX in flight
  → `no_trusted_admin_prereq` and `permissionless_or_normal_user_trigger` are **false**, and no harness was executed
  → carve-out correctly does **not** fire. The under-rating here is from (a) no harness and (b) the triage Medium floor,
  not from a carve-out gap.
- **H-10 (ZETA-11):** a deterministic *unconditional* revert of a core swap path — this is the **closest** the contest
  offers to the carve-out's target shape. But P215 (i) identified the wrong mechanism and (ii) built no executed
  harness, so `executed_l3_harness=false` → blocked. **Had a harness been built proving the deterministic revert of a
  permissionless core swap, the carve-out is exactly the mechanism that would have lifted it to High.**

## Calibration takeaway
The over-rating guard is solid (0 false-Highs across two live rehearsals: P212 SOPH + P215 ZetaChain). The recurring
weakness is **under-rating DoS/availability Highs**, and the carve-out only helps once an **executed harness** exists
for a **permissionless, non-admin** deterministic core-path failure. P215's gap was upstream of the carve-out: harness
effort + triage severity floor for DoS.
