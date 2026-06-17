# P244 — Final Recommendation & Verdict

## Verdict (exactly one)

# A — BUILD_COVERAGE_REASONING_GATE_NOW

## Why
`P241_MISS_REPLAY.md` shows the gate is **addressable against 74% of the frozen system's missed weighted recall**
(coverage 61% + reasoning 13%) and **realistically recovers ~35–46 weighted points** — lifting P241 weighted recall
from ~12% to ~49–58%. That recovery is dominated by the **coverage half**, which is:
- the **largest** lever (P243-measured 61% of misses, > 2× all detector families combined),
- **mechanical** (force the unread surface to be read before triage — read ≠ detect, but unread = guaranteed miss),
- **cheap and low-risk**, because it is a *minimal delta* over machinery that already hard-blocks the review gate:
  one `read_state` field (Δ-A1) + one critical-item READ_FULL blocking rule (Δ-A2) on
  `coverage_completeness_gate.py`, behind a default-off policy flag, honoring the existing
  `AUDITWATCH_COVERAGE_OVERRIDE`.

The **reasoning half** (Δ-C/Δ-D) is a smaller, diffuse, but **recall-protective** add that generalizes an existing
pattern (`triage_write.py` no-silent-clear) to sensitive-area rejections — it cannot degrade precision (it only
reroutes weak rejections to the existing human queue, never fabricates findings), so it is build-now by virtue of
being cheap and safe, even though its yield is softer.

This is the direct, measured execution of P243's recommendation ("operate at full coverage; reasoning depth second;
do not build more detector families") — turned into an enforceable gate rather than an aspiration. P241 proved that
discipline *without* a gate fails (the misses were coverage-bound precisely because nothing forced the full read).

## Ranked recommendation (by measured weighted-recall gain)
1. **Δ-A1 read_state + Δ-A2 critical-item READ_FULL gate** (option #3 — extend the existing CLI coverage gate).
   Highest ROI (~31–39 wt), lowest risk. Default-off flag; validate on `nextgen-2023-10` per `VALIDATION_PLAN.md`
   before any default-on.
2. **Δ-D anti-shallow-rejection reroute + Δ-C completeness predicate** (option #4 — extend `triage_write.py`
   no-silent-clear to the sensitive-area list). Recall-protective (~4–7 wt), shares the critical-item classifier with
   #1, so cheaper built together.
3. **Δ-B lifecycle flow matrix** (Step-0 deep-analysis output, reusing existing schemas). MED priority — sharpens the
   reasoning half; not required for the coverage win.
4. **Δ-A3 first-class architectural `role` enum** on the manifest. LOW priority — Δ-A2's tag-based predicate already
   works; do this only if per-role coverage reporting precision demands it.

## Explicit scope boundary
P244 ends here, at **spec + verdict + validation design**. Verdict A means *the next phase should build the gate* —
it does **not** mean P244 builds it. Per the phase's Part F ("Do not implement unless explicitly approved") and the
established arc, building options #3+#4 is a **separate, explicitly-approved** phase. That build must:
- keep the new gate rule **default-off** until the `VALIDATION_PLAN.md` run confirms recall-up / time-bounded;
- make **zero** severity-policy / routing / dashboard-behavior / detector / taxonomy changes;
- keep the five forbidden files byte-identical (`deep_trace.md` is *read* as the reasoning-discipline model, never
  edited);
- keep #4 recall-protective only (reroute to `human_review_queue.jsonl`, never auto-create/auto-submit).

## Honest limits (carried from `P241_MISS_REPLAY.md`)
- **Read ≠ detect**: coverage recovery is anchored on a single fully-read P241 target (kelp 3/5 ≈ 60%); the realized
  rate on diamond/lib-heavy targets is unmeasured until validation.
- **Reasoning yield is the softest number**: Δ-C/Δ-D force completed chains or human routing, not guaranteed insight.
- **26% of misses stay out of reach** (oracle / reward-emission / permit / create-time) — these need detector
  families, not this gate; only oracle-freshness (J) has high generalization, and create-time (B) is already built
  (P242-A, un-wired). The gate is deliberately a *coverage + discipline* instrument, not a knowledge instrument.

## Bottom line
Build the coverage gate now (Δ-A1/A2) as the highest-ROI move in the program, paired with the cheap recall-protective
reasoning reroute (Δ-C/Δ-D); validate on nextgen before default-on; defer Δ-B/Δ-A3. This converts the P243 finding
("coverage is dominant") into the first *enforced* mechanism that makes the system read its full surface before it
triages — the single change most likely to move recall.
