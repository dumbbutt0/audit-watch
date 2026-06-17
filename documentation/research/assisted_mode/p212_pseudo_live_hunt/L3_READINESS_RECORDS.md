# P212 — L3 readiness records (flag-on overlay results)

Records at `output_research/l3_readiness/SOPH-0{1..5}.json`. Readiness overlay run with `AUDITWATCH_L3_READINESS=1`.
No executed harness was built within first-hunt scope, so every High-ceiling candidate is correctly blocked.

| candidate | attacker | l3_status | high_promotion_allowed | calibrated | blocker |
|---|---|---|---|---|---|
| SOPH-01 | permissionless | NEEDS_HARNESS | **false** | needs_harness_for_severity | blocked_by_missing_l3_poc |
| SOPH-02 | permissionless | NEEDS_HARNESS | **false** | needs_harness_for_severity | blocked_by_missing_l3_poc |
| SOPH-03 | permissionless | NEEDS_HARNESS | **false** | needs_harness_for_severity | blocked_by_missing_l3_poc |
| SOPH-04 | permissionless | NEEDS_HARNESS | **false** | needs_harness_for_severity | blocked_by_missing_l3_poc |
| SOPH-05 | privileged | NOT_ATTEMPTED | **false** | medium | blocked_by_missing_l3_poc |

**Result: 0 candidates High-submission-ready.** The L3 gate prevented any over-rated HIGH from reaching submission
readiness. Promotion path for any of these: build an executed L2/L3 harness proving material impact (then PASS), or a
written human override — both require human review. SOPH-06/07 are Medium-ceiling (privileged) → not High targets.
