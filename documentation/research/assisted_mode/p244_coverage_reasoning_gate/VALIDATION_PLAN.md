# P244 — Part G: Validation Plan (design only; NOT executed this phase)

**Goal.** Show that the spec'd gate (`COVERAGE_REASONING_GATE_SPEC.md`, options #3 + #4 from
`IMPLEMENTATION_OPTIONS.md`) **increases recall without exploding time**, on one concrete target, as a controlled
before/after. This is a *design*; running it belongs to the future build phase (the gate must exist first).

## G.1 Primary target — `nextgen-2023-10`
Chosen because it is the cleanest single-target demonstration of the coverage lever:
- In P241 only `AuctionDemo` was read; **MinterContract / NextGenCore / Randomizers were UNREAD** — the textbook
  coverage-bound miss set (H-01 create-time mint, H-04 phases, M-01..M-12 subset).
- It has a published answer key (already used post-freeze in P241) so recovery is scorable.
- It is large enough to exercise Δ-A2 (critical-item READ_FULL forcing the unread contracts) but small enough to fully
  read within budget — so "time overhead" is measurable, not dominated by an intractable surface.
- It hits both halves of the gate: coverage (unread Minter/Core) **and** reasoning (nextgen H-02 `==endTime` was
  *read-but-missed* in `AuctionDemo`).

**Secondary stress target — `predy-2024-05`** (optional): exercises the **`BLOCKED_BY_BUILD`** honesty state (predy
needs unvendored deps — the P228 gap). Validates that the gate degrades gracefully (records the blocker, doesn't
falsely report full coverage) rather than the recall outcome.

## G.2 Protocol — controlled before/after on the same target
1. **Arm A (control / frozen baseline).** Re-run the P241-frozen flow on nextgen with the gate **policy flag OFF**.
   Record the same bounded read P241 produced. (Equivalent to replaying the frozen scorecard.)
2. **Arm B (gate ON).** Same target, gate **policy flag ON**: Δ-A1 read_state + Δ-A2 critical-item READ_FULL block +
   Δ-D sensitive-area depth-record reroute. The gate forces MinterContract/NextGenCore/Randomizers entrypoints to
   `READ_FULL` (or an explicit justified `BLOCKED_BY_*`) before triage may begin; sensitive-area rejections (create-
   time callback, auction timing) must carry a depth record or route to the human queue.
3. Score both arms against the nextgen answer key. **Blind discipline:** the answer key is opened only *after* both
   arms' candidate sets are frozen (consistent with P235/P240/P241).

## G.3 Metrics (the six the phase requires)
| Metric | Definition | Success signal |
|---|---|---|
| **Coverage completeness** | % critical items at `READ_FULL` (or justified) | Arm B ≫ Arm A (target: Arm B ≥ 95% critical; Arm A ~ the frozen partial) |
| **Candidates generated** | count of triageable candidates | Arm B > Arm A (more surface read → more candidates), without a precision collapse |
| **Shallow rejections prevented** | sensitive-area rejections rerouted to human queue for missing depth record | > 0 in Arm B (e.g. the `==endTime` dismissal); the recall-protection signal |
| **Time overhead** | wall-clock / token cost Arm B − Arm A | bounded — target ≤ ~1.5–2× Arm A (reading 3 more contracts, not unbounded) |
| **Findings recovered** | answer-key Highs/Meds newly hit in Arm B | target: H-01 (create-time) read + at least the coverage-bound H-04 / M-subset surfaced; ≥ the ~60% full-read anchor |
| **Operator burden** | manual actions added per audit (set read_state, justify blockers, complete depth records) | qualitative: bounded to critical items + sensitive-area rejections; "should-already-exist" data |

## G.4 Pass / fail criteria
- **PASS (supports verdict A):** Arm B coverage completeness materially higher, **≥ +1 High recovered** (or its read
  forced + a depth record produced) vs Arm A, time overhead ≤ ~2×, zero new false *findings* (reroutes to human queue
  don't count as FPs — they are recall protection), operator burden judged acceptable.
- **CONDITIONAL (supports verdict B):** recall improves but time overhead or operator burden is too high to automate →
  ship as an operator checklist (option #1) instead of a hard gate.
- **FAIL (supports verdict D):** no recall gain, or precision/time damage → don't build.

## G.5 Honest caveats on the validation itself
- **n=1 target.** nextgen validates the *mechanism* (does forcing the read recover the bug?), not the population rate.
  A fuller claim needs ≥3 targets (dittoeth diamond, predy libs) — scoped as follow-up, not first validation.
- **Read ≠ detect** persists: Arm B can force MinterContract to `READ_FULL` and still miss a bug the full read should
  have caught. That outcome is itself informative — it would re-attribute that miss from *coverage-bound* to
  *reasoning-bound*, refining `P241_MISS_REPLAY.md`'s split.
- **Family-bound misses won't move** (oracle/reward/permit) — by design; the validation should not be scored against
  them.
- Validation must run on a **non-active** workspace / explicit `--manifest`/`--out`, leaving the active audit
  (`size-credit-2024-06-blind`) untouched, consistent with prior phases.
