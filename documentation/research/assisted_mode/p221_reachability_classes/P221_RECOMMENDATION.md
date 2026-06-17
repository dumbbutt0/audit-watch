# P221 — Recommendation

**Decision: `REACHABILITY_TAXONOMY_READY`.** The dashboard now has a third reachability bucket for trusted-system /
TSS-gated paths. ZETA-04's card no longer shows four "unknown" fields — it states the boundary honestly
(`privilege_required: TSS caller (onlyTssAddress)`, `operator_or_keeper_dependency: TSS / cross-chain message executor`,
`self_remediation: none for users`, `reachability_class: TRUSTED_SYSTEM_ACTOR_REACHABLE`,
`reachability_verdict: trusted-system actor reachable; not unprivileged`). Severity is provably unchanged.

## What this fixes (the user's diagnosis, implemented)
- The schema was treating reachability too narrowly (unprivileged-attacker **or** missing-evidence). The six-class
  taxonomy adds the missing middle, so a valid issue with a privileged/trusted-system boundary is shown as such
  instead of half-blank.
- Reachability and impact are now visibly **decoupled**: ZETA-10 is `UNPRIVILEGED_REACHABLE` (the entry is
  permissionless and reentrancy is reachable) even though its theft impact is refuted — two separate axes, two
  separate fields.

## Safety
- `reachability_class` is display/evidence only; `decide()` (severity) is byte-identical and untouched
  (`validate_p208_l3_readiness.py` unchanged). No candidate promoted. `dashboard_sync.py` unchanged. All forbidden
  files byte-identical. HARD RULE preserved: granular fields populate only from L3 artifacts, else stay explicit
  `unknown`.

## Open items (human decision — unchanged by P221)
1. **Severity floor for TSS-gated availability.** ZETA-04 is now *described* precisely as trusted-system reachable,
   but it is still calibrated Medium (the answer key rates H-13 High). The taxonomy makes the boundary legible for a
   human reviewer; it deliberately does not move severity. Escalation remains a `HUMAN_OVERRIDE`-with-rationale call.
2. **Per-source adapters.** Curated non-ZETA cards (vultisig/munchables/…) get a derived class from `attacker_model`;
   richer granular fields would need those corpora to record the structured reachability fields (as the ZETA L3
   records now do).
3. **`PROGRAM_ACCEPTED_ACTOR_REACHABLE`** has no example in this corpus yet; it exists so a genuinely
   program-accepted actor can be labeled without conflating it with the severity enum.

## ARC
…P218 enforced hook → P219 evidence DEPTH (extraction) → P220 evidence GENERATION (3 executed harnesses) →
P221 reachability TAXONOMY (third bucket for trusted-system paths; ZETA-04 card complete; severity invariant).
