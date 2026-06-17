# P222 — Recommendation

**Decision: `HUMAN_REVIEW_PRIORITY_READY`.** The dashboard now has a review-priority lane that surfaces real,
L3-proven, core-safety/control findings that are not auto-reportable because a program threat-model decision is
required. ZETA-04 — a CLEAN_HIT against the official awarded finding with an executed L3 PASS, blocked from
auto-High only by its `onlyTssAddress` trigger — is now shown as
`CLEAN_HIT · L3_PASS · TRUSTED_SYSTEM_ACTOR_REACHABLE · HIGH_PRIORITY_HUMAN_REVIEW`, above ordinary
Medium/noise, while remaining **not** submission-ready.

## What this fixes
- The blocker reframes from a fatal/noise-like `attacker_model=privileged_only` to the actionable
  `PROGRAM_THREAT_MODEL_DECISION_REQUIRED`. The finding is no longer buried with rejected/refuted noise.
- `submission_ready` and `human_review_priority` are made into **independent axes**: ZETA-04 is high-priority for
  a human *and* not auto-submittable at the same time.
- Reachability and impact stay decoupled (P221): ZETA-10's permissionless reentrancy path is real, but with the
  theft impact refuted by L3 it lands at LOW, not the lane.

## Safety (the whole point)
- `human_review_priority` lives in a **separate namespace** from `attacker_model`. `decide()`
  (`validate_p208_l3_readiness.py`) is byte-identical and untouched; ZETA-04/10/11 severities are unchanged
  (medium/invalid/medium, all `high_promotion_allowed=false`).
- The priority helper never sets `submission_ready`, `routing_allowed`, `high_promotion_allowed`, `attacker_model`,
  or any severity. `dashboard_sync.py` (the synced-record + safety-constant contract) is byte-identical — the
  fields ride via `CARD_INJECT`. All forbidden files byte-identical. No submit/promote controls; dashboard
  read-only; severity never browser-computed.
- The completion guard now **enforces** the invariants: priority present + valid; HIGH ⇒ `submission_ready=false`;
  HIGH_PRIORITY_HUMAN_REVIEW ⇒ `routing_allowed=false` and no silently-true high promotion.

## Acceptance — all met
ZETA-04 highlighted above noise as high-priority human review · still not auto-submission-ready · blocker
reframed to PROGRAM_THREAT_MODEL_DECISION_REQUIRED · trusted-system reachability explicit · L3 PASS + core
safety/control impact surfaced · ZETA-10 remains refuted/demoted (LOW) · H5-style unprivileged unaffected (stays
reportable through the normal path) · no submit/route/promote side effects · dashboard read-only · completion
guard passes · production hashes recorded start+end · JSON valid.

## Open items (human decision — unchanged by P222)
1. **Severity floor for TSS-gated availability.** P222 *prioritizes* ZETA-04 for human review but deliberately
   does not move its severity (still Medium; the answer key rates H-13 High). Escalation remains a
   `HUMAN_OVERRIDE`-with-rationale or DoS-carveout (P214, default-off) call.
2. **`impact_type` provenance for other corpora.** Only ZETA-04/11 carry an artifact-backed `impact_type`; the
   HIGH/MEDIUM rule simply doesn't fire elsewhere until an L3 record records one (HARD RULE — no invention). The
   four new reachability classes (KEEPER_OR_RELAYER / ADMIN_OR_OWNER / SELF_INFLICTED_ONLY / SOURCE_REFUTED) are
   defined and gate the rule, but have no example in this corpus yet.
3. **`CRITICAL_HUMAN_REVIEW`** is reserved (HIGH lane + a direct fund-loss impact); no corpus example.

## ARC
…P218 enforced hook → P219 evidence DEPTH → P220 evidence GENERATION (3 harnesses) → P221 reachability TAXONOMY
(trusted-system bucket) → **P222 human-review PRIORITY lane** (surfaces the trusted-system finding above noise;
submission-ready and human-review-priority decoupled; severity invariant).
