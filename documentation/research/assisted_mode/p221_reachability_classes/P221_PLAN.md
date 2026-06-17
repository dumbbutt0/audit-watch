# P221 — Reachability taxonomy: a third bucket for trusted-system / TSS-gated paths

**Problem.** The H5 gold-standard card has a clean attacker story (unprivileged user, no privilege, no victim action,
no self-remediation). ZETA-04 is a real bug of a *different evidence class*: `onReceive` is `onlyTssAddress`, so the
pause-bypass is proven through the TSS caller, not an unprivileged path. The card couldn't say that: reachability
rendering was binary (`finding_detail.py` `unpriv = "unprivileged" in rv`), collapsing `privilege_required`,
`victim_action_required`, `self_remediation`, and `attacker` to `unknown` for any non-unprivileged path. ZETA-04's
live card showed four "unknown" fields — a missing taxonomy bucket, not missing evidence.

**Fix (schema/rendering, not a harness).** Add explicit reachability classes so trusted-system paths populate
honestly. **Display/evidence only — severity never moves**: `decide()` keys off the L3 `attacker_model` enum, never
reachability; `attacker_model` enums are left unchanged.

**Taxonomy:** `UNPRIVILEGED_REACHABLE` · `PROGRAM_ACCEPTED_ACTOR_REACHABLE` · `TRUSTED_SYSTEM_ACTOR_REACHABLE` ·
`PRIVILEGED_ONLY_REACHABLE` · `COMPROMISE_REQUIRED` · `REACHABILITY_UNKNOWN`. Derived from `attacker_model`,
overridable by an explicit `reachability_class` in the L3 record.

**Footprint (additive, 2-file — the P219 pattern; `dashboard_sync.py` UNCHANGED):**
- `sync_hunt_findings.py`: `_REACH_CLASS` map; in `build_bundle` compute `reachability_class` + extract structured
  attacker fields (`privilege_required`, `victim_action_required`, `operator_or_keeper_dependency`,
  `self_remediation`, `attacker_controls`, `attacker_does_not_control`) with provenance; prefer an L3-recorded
  `reachability_verdict`; extend `CARD_INJECT`.
- `finding_detail.py`: attacker_model block prefers inline fields + renders `reachability_class`; harden `unpriv`
  so the literal "not unprivileged" doesn't trip it; keep the binary heuristic as fallback.
- L3 records ZETA-04/10/11: additive reachability fields (artifact source for the granular card fields).

**Decision: REACHABILITY_TAXONOMY_READY.** See SEVERITY_INVARIANCE.md, BEFORE_AFTER_CARDS.md, TEST_RESULTS.md.
