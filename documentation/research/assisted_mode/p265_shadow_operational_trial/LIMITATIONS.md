# P265 — LIMITATIONS

1. **Scored metrics are retrospective/contaminated except benddao.** Only benddao (P263, public findings,
   training-confound accepted) is a clean scored anchor (n=1). 9 contests are scored-contaminated (awards seen in
   P254–259 reveals/training), 1 is leak-contaminated (reserve), 2 are unscored (concrete, monetrix — private
   findings). #3/#4/#5 are therefore optimistic/retrospective and are NOT pooled as rates. The deterministic
   metrics (#1/#6/#8) and the #2/#7 proxy do not depend on award knowledge and are valid across all 13.

2. **Exact-mechanism recovery is unproven** — the central caveat. benddao reached **0 exact-mechanism / 1
   family-level PARTIAL** (H-08, T5). The trial proves *locus recall* (the harness forces award-carrying loci that
   the narrow path skips), not *mechanism recovery*. Locus recall ≠ exact recovery. This is exactly the boundary the
   operator drew: shadow recall engine = ready; production authority = not until exact mechanism is proven repeatedly.

3. **The harness does not run completion.** completion_status/refutation_status are `null` by design; #4 PARTIAL/
   COMPLETED at the harness level is 0. The single PARTIAL credited (benddao H-08) came from P263's *manual*
   downstream B/C + five-op run, not from the shadow harness. Completion remains a manual/downstream step.

4. **#2/#7 are proxies, not a human study.** They apply a transparent rubric (recall-delta ∩ award-fit family ∩
   evidence-marker) deterministically. They measure *triage-worthy recall*, not realized *recovery yield*; the
   rubric counts a lead useful on structure, not on award conversion (which P254–263 show is partial).

5. **Recall-delta over-counts vs a real auditor's baseline.** "Narrow baseline" is P260 top-5; a skilled human
   auditor's implicit baseline is wider, so 72.7% recall-delta overstates the delta against a strong human. It is
   the right control vs the *old pre-P262 narrow path*, not vs an expert.

6. **No PoCs, no severity, no on-chain validation.** Nothing here is a confirmed finding. "0 concluded/reportable
   FP" is by construction (guard), not a measured precision of the underlying mechanism hypotheses.

7. **Mechanism breadth is hidden behind caps.** 12/13 contests truncated at the 30-mech cap; the operator sees a
   bounded slice. Raising caps would raise burden, not necessarily recovery — a tuning question for a later phase,
   explicitly out of scope here (no tuning during the trial).

8. **Corpus is largely the same contests the modules were developed/backtested against.** The trial demonstrates
   *generalization of behavior* (runs clean, bounded, 0 FP, recall-delta consistent across 13 architectures) but is
   not a fresh-contest recovery proof. That is P266's job.
