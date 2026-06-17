# P244 — Part E: P241 Miss-Replay Calibration

**Method.** For every P241 awarded finding the frozen system missed, replay it against the gate spec'd in
`COVERAGE_REASONING_GATE_SPEC.md` and assign **exactly one** label:

- **recovered-by-coverage-gate** — the relevant code was never read; Part-A Δ-A2 (critical-item READ_FULL before
  triage) would have forced it to be read, and a competent full read recovers this *class* of bug.
- **recovered-by-lifecycle-matrix** — the code was reachable but no structured flow row forced reasoning about it;
  Part-B Δ-B would have created the row.
- **recovered-by-reasoning-checklist** — the code was read but the exploit/defense chain was abandoned; Part-C/D
  Δ-C/Δ-D would have blocked the shallow dismissal and forced (or human-routed) the completed chain.
- **still-missed** — recovery needs *domain/family knowledge the gate does not add* (oracle-freshness, reward/emission,
  permit-binding, create-time-reentrancy). The gate may force the read, but reading alone doesn't detect these.

**Inputs (no re-audit).** P243 attribution table (`../p243_miss_roi_audit/MISS_ROI_AUDIT.md`) + P241 per-contest
SCORECARDs. Weights High=3, Med=1. Replay is done at the **P243 category level** (reusing its recorded per-category
tallies verbatim) so no raw counts drift from the recorded ground truth.

**Honesty rule (critical).** The coverage gate forces *reading*, not *detecting*. P243's own counterfactual anchored
the realized recovery rate on the one fully-read P241 target (**kelp recovered 3/5 ≈ 60%**). So "recovered-by-coverage-
gate" means *the gate removes the binding constraint (unread surface) and a ~60–75% full-read recovery rate applies* —
NOT a guaranteed catch. Family-bound misses are labeled still-missed even where coverage would force the read, because
P243 judged a full read alone insufficient for that class (the gate adds no domain knowledge — see the plan's honest
limit).

---

## E.1 Replay by P243 recovery category

| P243 cat | Recovery family | Raw (H/M) | Wt | Which P241 misses | P244 label | Gate delta that fires |
|---|---|---|---|---|---|---|
| **K** | Diamond/facet coverage | 7H / 9M | **30** | dittoeth — all (unread facets) | **recovered-by-coverage-gate** | Δ-A2 (facets are critical items → READ_FULL) + Δ-A1 read_state |
| **A** | Full-surface coverage | 4H / 10M | **22** | nextgen Minter/Core (H-04,M-01..M-12 subset) + predy trade/reallocation libs (H-02,H-03,H-04,M-02,M-03,M-05,M-07) | **recovered-by-coverage-gate** | Δ-A2 critical-item READ_FULL + Δ-B lifecycle rows for create/mint/settle/reallocate |
| **L** | Reasoning depth (read-but-missed) | 2H / 5M | **11** | kelp H-02 (transfers-before-mint ordering), M-01 (migration share); nextgen H-02 (==endTime), M-05, M-07, M-10, M-11 | **recovered-by-reasoning-checklist / lifecycle-matrix** (partial) | Δ-C state-timeline + Δ-D anti-shallow reroute; Δ-B mint/settle flow rows |
| **J** | Oracle freshness/validity | 2H / 3M | **9** | kelp H-01 (heartbeat/deviation); predy H-01, M-01, M-04 (Chainlink stale), M-08 | **still-missed** (coverage forces the read; detection needs the oracle family) | — (Δ-D oracle-freshness depth record raises odds, no guarantee) |
| **I** | Reward/emission accounting | 1H / 6M | **9** | fenix all (ve(3,3) gauge/emission/index) | **still-missed** (family-bound; coverage forces the read) | — (gauge contracts barely read → Δ-A2 forces read, but ve(3,3) detection needs the family) |
| **B** | Create-time reentrancy | 1H / 0M | **3** | nextgen H-01 (mint callback before counter) | **still-missed by the gate** (already covered by the *built, un-wired* P242 Family A detector, not the gate) | — |
| **F** | Permit/signature binding | 0H / 1M | **1** | nextgen M-06 (artist sig forgery) | **still-missed** (family-bound) | — |
| **TOTAL** | | **17H / 34M** | **85** | | | |

---

## E.2 Weighted tally

| Replay label | Weighted | Share of missed (85) | Realized (apply ~60–75% read-recovery to coverage; ~40–60% to reasoning) |
|---|---|---|---|
| recovered-by-coverage-gate (A + K) | **52** | **61%** | **~31–39 wt** |
| recovered-by-reasoning-checklist / lifecycle (L) | **11** | **13%** | **~4–7 wt** |
| **gate-addressable subtotal** | **63** | **74%** | **~35–46 wt** |
| still-missed — family/domain (J + I + B + F) | **22** | **26%** | 0 from the gate (needs a detector family; B already built as P242-A, un-wired) |

**Counterfactual recall (P241, weighted denom 97), consistent with P243:**

| Scenario | Weighted recall |
|---|---|
| Current frozen system (this benchmark's bounded reads) | ~12% |
| + coverage gate (Δ-A1/A2, full-surface + facet READ_FULL) | **~45–53%** |
| + lifecycle matrix + reasoning checklist (Δ-B/C/D) | **~49–58%** |
| + best future detector family (J oracle freshness, *not part of this gate*) | ~57–62% |

The coverage half of the gate is the dominant, mechanical lever (matches P243's +31…+39 wt). The reasoning half is a
real but smaller and **diffuse** add (no single flip; it forces completed chains / human routing rather than
guaranteeing the insight) — exactly the L=13% "read-but-missed" bucket.

---

## E.3 Honest limits of this replay
1. **Read ≠ detect.** Every "recovered-by-coverage-gate" is contingent on the ~60% full-read recovery rate observed on
   the *single* fully-read P241 target (kelp). It is the best available anchor but n=1; the true realized rate on
   dittoeth's diamond / predy's libs is unknown until the validation run (`VALIDATION_PLAN.md`).
2. **dittoeth caveat.** Its 16 awards are classified at theme level (the contest report is >10 MB and was not fully
   read in P241); they are attributed as a group to unread facets (coverage-bound) — high-confidence on the *category*,
   lower-confidence on per-finding mapping.
3. **Reasoning-checklist yield is the softest number.** Δ-C/Δ-D *force* a completed chain or a human reroute; they do
   not manufacture the missing insight. The ~40–60% applied to L is a judgement, not a measurement — the validation
   run measures "shallow rejections prevented," not "insights guaranteed."
4. **Family-bound misses (26%) are explicitly out of scope for the gate** — recovering J/I/F needs detector families
   (only oracle-freshness J has high generalization per P243); B (create-time) is already built (P242-A, un-wired).
   This is the deliberate honest limit: the gate is a *coverage + discipline* instrument, not a knowledge instrument.

**Bottom line:** the gate is *addressable* against 74% of missed weighted recall and *realistically recovers ~35–46
wt* (≈ lifting P241 weighted recall from ~12% to ~49–58%), with the coverage half carrying almost all of it. This is
the measured basis for the verdict in `RECOMMENDATION.md`.
