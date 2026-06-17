# P221 — Severity invariance (the safety gate)

The reachability taxonomy is **display/evidence only**. It must not move severity. Proof:

## decide() is byte-identical before and after
`validate_p208_l3_readiness.decide()` reads `attacker_model`, `l3_status`, `impact_class`, the material-delta fields,
`production_source_modified`, `dependency_mocks`, and the control — **never** `reachability_class` or any of the new
structured attacker fields. The L3 records' `attacker_model` enums were left unchanged; only additive reachability
fields were added.

| ID | attacker_model (unchanged) | reachability_class (new) | calibrated_severity | high_promotion_allowed |
|----|----------------------------|--------------------------|---------------------|------------------------|
| ZETA-04 | privileged_only | TRUSTED_SYSTEM_ACTOR_REACHABLE | medium (before & after) | false (before & after) |
| ZETA-10 | permissionless | UNPRIVILEGED_REACHABLE | invalid (before & after) | false (before & after) |
| ZETA-11 | unknown | REACHABILITY_UNKNOWN | medium (before & after) | false (before & after) |

Baseline captured pre-edit: ZETA-04 medium/False, ZETA-10 invalid/False, ZETA-11 medium/False. Post-edit `decide()`
output matches exactly (asserted by `test_severity_invariance` and `test_reachability_not_an_attacker_model_value`).

## Why `PROGRAM_ACCEPTED_ACTOR_REACHABLE` does not leak severity
It is a reachability *label*, not an `attacker_model` value. Assigning it never sets
`attacker_model="program_accepted"`, so it cannot satisfy `decide()`'s High-promotion gate. The class taxonomy and the
severity enum are deliberately separate namespaces; `test_reachability_not_an_attacker_model_value` asserts no class
string ever appears in an `attacker_model` field.

## Net
Richer, honest reachability evidence on the card; **zero** change to calibrated severity or High-promotion. No
candidate was promoted; ZETA-04 stays Medium with the privileged-TSS-trigger blocker. Human judgment on whether a
TSS-gated availability bug should be escalated remains exactly where it was (the P220 RECOMMENDATION open item).
