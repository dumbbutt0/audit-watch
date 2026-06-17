# P221 — ZETA-04 card: before → after

The motivating case. Live `attacker_model` block from `finding_detail.load_unified_detail("funnel:ZETA-04")`.

## Before (four "unknown" fields — the missing-bucket problem)
```
attacker:                       conditional — requires a specific protocol state/precondition
controls:                       []
does_not_control:               []
privilege_required:             unknown
victim_action_required:         unknown
operator_or_keeper_dependency:  unknown
self_remediation:               unknown
reachability_verdict:           uncertain (confirm gate)
```

## After (trusted-system bucket populated, honestly)
```
attacker:                       conditional — requires a specific protocol state/precondition
controls:                       ["not the direct caller under honest assumptions; the path triggers via
                                 TSS-delivered inbound or a trusted-system failure"]
does_not_control:               ["onlyTssAddress authorization under honest assumptions (would require TSS
                                 compromise or trusted-system failure)"]
privilege_required:             TSS caller (onlyTssAddress)
victim_action_required:         no (inbound cross-chain message flow; no direct victim action)
operator_or_keeper_dependency:  TSS / cross-chain message executor
self_remediation:               none for users (pause/unpause is pauser-controlled)
reachability_class:             TRUSTED_SYSTEM_ACTOR_REACHABLE
reachability_verdict:           trusted-system actor reachable; not unprivileged
```
Safety unchanged: `submission_ready=false`, `routing_allowed=false`; 15/15 sections render.

## The other two harnessed candidates (reachability decoupled from impact)
| ID | reachability_class | privilege_required | note |
|----|--------------------|--------------------|------|
| ZETA-10 | `UNPRIVILEGED_REACHABLE` | no (permissionless getEthFromZeta entrypoint) | reentrancy *is* reachable; theft refuted (l3 FAIL) — reachability and impact are separate axes |
| ZETA-11 | `REACHABILITY_UNKNOWN` | unknown (depends on external Trident factory policy) | DoS is a missing-pool state, not attacker-triggered; theft mechanism not source-confirmable |

## Non-target candidates (dashboard-wide, additive)
Every candidate now carries a derived `reachability_class` (e.g. ZETA-05 → `PRIVILEGED_ONLY_REACHABLE`,
ZETA-01 → `REACHABILITY_UNKNOWN`). Their granular fields (`privilege_required`, …) stay explicit `unknown` because no
L3 record supplies them — HARD RULE preserved (no fabrication). The curated non-ZETA cards (vultisig/munchables/…)
are unaffected; the binary unprivileged fallback still renders them as before.
