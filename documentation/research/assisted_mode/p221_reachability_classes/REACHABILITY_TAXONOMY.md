# P221 — Reachability class taxonomy

A **display/evidence** label on the dashboard card, decoupled from the `attacker_model` severity enum. It gives every
candidate an honest reachability bucket instead of forcing the binary unprivileged-or-unknown collapse.

| Class | Meaning | Example |
|-------|---------|---------|
| `UNPRIVILEGED_REACHABLE` | Any EOA can reach it through a permissionless entrypoint | H5; ZETA-10 (getEthFromZeta entry) |
| `PROGRAM_ACCEPTED_ACTOR_REACHABLE` | Reachable by a program-accepted caller (severity-eligible for High) | (none in this corpus) |
| `TRUSTED_SYSTEM_ACTOR_REACHABLE` | Reachable only via a trusted *system* actor (TSS / cross-chain executor / FUNGIBLE_MODULE) | ZETA-04 (`onlyTssAddress` onReceive) |
| `PRIVILEGED_ONLY_REACHABLE` | Reachable only by an admin/owner-type privileged role | ZETA-05 (derived) |
| `COMPROMISE_REQUIRED` | Requires compromising a trusted actor/key | — |
| `REACHABILITY_UNKNOWN` | Not source-confirmable / depends on external state | ZETA-11 (theft via external Trident factory) |

## Derivation (deterministic, artifact-backed)
1. If the L3 record sets `reachability_class` explicitly → use it (e.g. a TSS gate → `TRUSTED_SYSTEM_ACTOR_REACHABLE`).
2. Else map the L3 `attacker_model`: `permissionless→UNPRIVILEGED_REACHABLE`,
   `program_accepted→PROGRAM_ACCEPTED_ACTOR_REACHABLE`, `privileged_only|privileged|trusted_admin→PRIVILEGED_ONLY_REACHABLE`,
   `compromise_required→COMPROMISE_REQUIRED`, anything else → `REACHABILITY_UNKNOWN`.
3. Else fall back to the register `attacker_model`, else the binary unprivileged heuristic.

## Why a third bucket matters
`TRUSTED_SYSTEM_ACTOR_REACHABLE` ≠ `UNPRIVILEGED_REACHABLE` (not an H5-style clean attacker story) and ≠
`PRIVILEGED_ONLY_REACHABLE` (the TSS is the protocol's own message executor, not an admin) and ≠ `MISSING_EVIDENCE`
(the boundary is *known*). ZETA-04 sits exactly here: a real pause-bypass whose trigger is the TSS, so the card can
state the boundary clearly (`privilege_required: TSS caller`, `self_remediation: none for users`) instead of leaving
four fields blank.

## Hard separation from severity
`reachability_class` is **never** read by `validate_p208_l3_readiness.decide()`; it is not an `attacker_model` value.
`attacker_model` enums are unchanged, so calibrated severity and High-promotion are byte-identical (SEVERITY_INVARIANCE.md).
`PROGRAM_ACCEPTED_ACTOR_REACHABLE` is a label only — assigning it does not set `attacker_model="program_accepted"`.
