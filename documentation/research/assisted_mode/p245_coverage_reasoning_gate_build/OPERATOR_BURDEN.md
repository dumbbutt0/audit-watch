# P245 — Operator Burden

The gate is recall-protective, so it necessarily asks the operator to do more before triage. This
document quantifies how much, and why it stays manageable.

## #3 coverage read-completeness
- **What the operator must do (only when enabled):** set a `read_state` on each in-scope CRITICAL item —
  `READ_FULL` once read, or one of the justified states (`NOT_IN_SCOPE` / `GENERATED_INTERFACE_ONLY` +
  reason / `DUPLICATE_WRAPPER` + `duplicate_of` / `BLOCKED_BY_*` + reason + `read_block_ack`). One CLI
  call: `update_coverage_disposition.py --id <mid> --read-state READ_FULL`.
- **How big is the critical set?** On nextgen: **92 of 122 in-scope items (75%)**. That is high — but it is
  the actual security surface (entrypoints, privileged setters, mint/burn/auction, randomizers). The
  FP-control choice (read-only getters excluded) keeps it from being 122/122; the ~30 non-critical items
  only ever warn, never block.
- **Why it is bounded, not busywork:** the operator was *already supposed* to read these to clear them; the
  gate just makes "I cleared it" and "I read it" the same assertion. The `BLOCKED_BY_*` + ack states give
  an honest, low-friction escape for genuinely unreadable surface (no build, missing source) so the gate
  degrades gracefully instead of forcing impossible reads. `AUDITWATCH_COVERAGE_OVERRIDE=1` remains.
- **Failure mode watched:** if the critical predicate flagged getters/trivial items, the set would explode
  and the gate would over-block. It does not (validated: plain `public view` getter → not critical; 0 false
  blocks on nextgen).

## #4 rejection depth-record
- **What the operator must do (only when enabled):** for a rejection that touches a sensitive area, fill a
  6-field depth record (`source_anchors`, `defense_anchors`, `attacker_path`, `impact_path`,
  `state_timeline`, `defense_fully_covers_reason`). A genuine dismissal already has most of this ("guarded
  by `onlyOwner` at X.sol:42, attacker can't reach it because …").
- **How often does it fire?** Only on `rejected` decisions whose text/area matches the 11-area list — not
  on submits, downgrades, merges, or non-sensitive rejections (validated: QA gas rejection unaffected).
- **It never blocks the pipeline** — it reroutes to the existing `human_review_queue.jsonl` (recall
  protection), so the cost is "a human looks again," not "the run halts."
- **Busywork guard:** the gate only triggers when a record is *incomplete*; a complete record passes
  silently (DT-002). So the burden is proportional to under-justified sensitive-area rejections — exactly
  the population we want a second look at.

## Net assessment
Manageable. The burden lands on (a) reading the real security surface before clearing it and (b) justifying
sensitive-area rejections — both of which are the work that *should* already happen and whose absence
caused the P241 misses. Both halves are default-off, overridable, and degrade gracefully. → no
stop-condition triggered (not over-blocking on normal items; not noisy; not busywork-without-payoff per
the `coverage_enforced_recall_gain` table).
