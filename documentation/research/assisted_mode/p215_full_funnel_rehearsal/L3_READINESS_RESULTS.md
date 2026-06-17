# P215 — L3 READINESS RESULTS (AUDITWATCH_L3_READINESS=1, in-process)

Per-candidate records at `output_research/l3_readiness/ZETA-*.json` (schema = p208 L3_READINESS_SCHEMA.json).
Verdicts via the **real wired** `submission_readiness_review.l3_evaluate` (which calls `validate_p208.decide`).

| ID | ceiling | l3_status | attacker | calibrated_after_l3 | high_allowed | blocker |
|----|---------|-----------|----------|---------------------|--------------|---------|
| ZETA-03 | Critical | NOT_ATTEMPTED | privileged | medium | **False** | blocked_by_missing_l3_poc |
| ZETA-01 | High | NEEDS_HARNESS | conditional | needs_harness_for_severity | **False** | blocked_by_missing_l3_poc |
| ZETA-04 | High | NEEDS_HARNESS | conditional | needs_harness_for_severity | **False** | blocked_by_missing_l3_poc |
| ZETA-05 | High | NEEDS_HARNESS | privileged | needs_harness_for_severity | **False** | blocked_by_missing_l3_poc |
| ZETA-06 | High | NEEDS_HARNESS | conditional | needs_harness_for_severity | **False** | blocked_by_missing_l3_poc |
| ZETA-08 | High | NOT_ATTEMPTED | privileged | medium | **False** | blocked_by_missing_l3_poc |
| ZETA-10 | High | NEEDS_HARNESS | permissionless | needs_harness_for_severity | **False** | blocked_by_missing_l3_poc |
| ZETA-11 | High | NEEDS_HARNESS | conditional | needs_harness_for_severity | **False** | blocked_by_missing_l3_poc |
| ZETA-07 | Medium | PASS (executed) | conditional | (n/a — Medium not gated) | n/a | applies=False |

**0 / 8 High-or-Critical candidates promoted to High.** This is the over-rating guard doing its job in a bounded
first pass with no executed realized-impact PoCs (mirrors P212 stage-1: "0/N High-ready without an executed PoC").

## Key distinctions (so we don't mislabel at scoring)
- **Blocked ≠ L3 under-rating.** Every High here is blocked because **no executed PoC was built** (NEEDS_HARNESS /
  NOT_ATTEMPTED), not because L3 mapped a *proven* High down. If scoring shows some are genuine official Highs, that is a
  **recall/effort gap** (we didn't harness them), not the P212-class L3 under-rating bug.
- **DoS carve-out (P214) not triggered:** no candidate is a deterministic, permissionless, executed core-path DoS
  (ZETA-11 has a DoS facet but is conditional + unexecuted). `dos_carveout_applied=false` for all.
- **Privileged calibration:** ZETA-03/05/08 are privileged/centralization → correctly blocked from High independent of
  harness.
- **Flag-off equivalence:** `l3_evaluate` called directly still computes a verdict, but the FLAG gates whether it is
  applied inside `submission_readiness_review.evaluate()/detail_overlay()`; production hashes unchanged.
