# P195 — Deep-pass selection-consistency validation (read-only)

Burden-of-proof check before any production selection change. **Read-only**, deterministic, no model runs.

## Decision: `EXECUTION_BUDGET_IS_THE_REAL_LEVER` → **do NOT open P196 (selection-by-score fix)**
The proposed selection-order change has a **maximum recall gain of 0** in the available evidence: the budgeted
deep-pass **executed 0 items in every eval run**, so reordering the queue cannot change what runs. The burden of
proof for a selection-order production change is **not met**. The only conceivable lever is deep-pass **execution
budget** — and that is itself likely an eval-config artifact (`strict / full_audit` waived the deep pass), which
must be confirmed against production behaviour before any change.

## Premise correction (decisive)
P192's "revert-lend has score inversions" rested on reading `assigned_pass=='deep'` as "deep-run". It is not:
- `deep_pass_budget_summary.json` → revert-lend `queued 63 / executed 0 / rate 0.0`; panoptic `154 / 0 / 0.0`;
  `executed_deep_passes = 0` for **all five** corpora.
- `assigned_pass=='deep'` is a **tier/cluster assignment label** — revert-lend has 106 deep-assigned dispositions
  with **0 `finding_refs`**. The actual deep-trace outputs (`findings_deep_trace`, 2–5/corpus) come from a
  different path.
So P192's "inversions" compared the queue `score` against the **tier/cluster assignment axis** — two different,
by-design dimensions — and **nothing executed via either**. Selection *order* is moot at 0% execution.

## The six questions
1. **How many inversions exist?** **6, revert-lend only** under the assignment-signal (a queued function
   out-scoring a deep-*assigned* one); **0** under the execution-signal (deep-pass executed 0). panoptic 0,
   zaros/ark have no deep tier.
2. **How many touch awarded loci?** **0** under the execution-signal. Even under the assignment-signal the
   "inversions" are an axis-mismatch artifact (queue-score vs tier-assignment), not awarded-locus starvation.
3. **How many unresolved would enter deep-pass under score-consistent selection?** **8 (UPPER BOUND)** — revert-lend
   3 (M-03, M-06, M-25), panoptic 5 (H-02, H-03, M-03, M-07, M-18). **But this is execution-driven, not
   order-driven:** for panoptic N (deep-assigned)=153 ≥ the queue size, so "top-N" already includes everything —
   reordering changes nothing. The 8 would only materialise if the deep pass **executed** (it executed 0).
4. **Max possible recall gain?** From the **proposed selection-order fix: 0** (reordering is moot at 0% execution
   and N≥queue-size). From a *different* change (actually executing the deep pass + score-ordering): **≤ 8 awarded
   loci *reaching* deep-pass** — an upper bound on deep-pass **entry**, **not** catches (catching still depends on
   the P183–P188 adjudication stack).
5. **Is the gain concentrated in revert-lend only?** Assignment-signal inversions: **revert-lend only**.
   Counterfactual execution-gain: revert-lend (3) + panoptic (5) — but that is execution-driven, and panoptic was
   `CONSISTENT` in P192. zaros/ark have no deep tier.
6. **Intentional heuristic or accidental inconsistency?** **INTENTIONAL by design + budget-gated.** The deep tier
   is assigned by a documented **tier (2/3/4/6) × cluster × specialist** policy with explicit skip reasons and
   `waived` flags (`skipped_deep_passes_with_reason.json`); it is not score-ordered because it is not meant to be,
   and the execution budget waived it entirely (`execution_rate 0.0`). It is not an accidental score inconsistency.

## Measurement-signal correction (and its bounded impact)
`assigned_pass=='deep'` ≠ executed. P190/P192/P194 used it as a "deep-run" signal, so their "deep-run" / `DEEP_PASS_GAP`
/ `REACHED_DEEP_PASS` attributions should be read as **"assigned-to-deep-tier"**, consistent with `execution_rate=0`
(i.e. almost everything "routed to deep" was budget-waived). This **does not affect P189's adjudication results**
(P189 force-ran deep-trace on each surface) nor the P183–P188 adjudication conclusions. It does mean P190's funnel
"deep-pass" stage measured *assignment*, not *execution* — a labeling correction, not a reversal of the upstream
finding.

## Recommendation
- **P196 (production selection-by-score fix): NOT warranted.** Max gain from it is 0; the inversions are an
  axis-mismatch artifact at 0% execution.
- The real open question is **deep-pass execution budget** (it ran 0/63 and 0/154 under strict/full-audit eval).
  Before any change: confirm whether **production** actually executes deep passes (these eval runs waived them) —
  if production also executes ~0, that is the lever; if production executes normally and only the eval harness
  waived, then there is no production problem here at all. Either way it needs its own read-only validation, not a
  selection-order change.

## Honesty / limits
- Max-gain numbers are upper bounds on deep-pass **entry**, never catches. `fabrication_rate=0`; every count cites
  its artifact (`deep_pass_budget_summary`, `skipped_deep_passes_with_reason`, queue score, `assigned_pass`,
  `findings_deep_trace`). Both signal readings reported. The counterfactual presupposes execution>0, which did not
  occur. n is small and revert-lend/panoptic-specific.
