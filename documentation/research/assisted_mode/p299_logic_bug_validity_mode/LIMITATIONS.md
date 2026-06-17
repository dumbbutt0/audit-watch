# P299 — LIMITATIONS

- **Differential trust model.** A logic confirmation rests on the author-declared corrected-control genuinely
  representing the FIXED behavior (same trust model as the exploit/refutation split + Tier-C faithfulness). The
  verifier checks both tests PASS + the map exists; it cannot fully prove the control is the "correct" reference. The
  fidelity/human-review tier (P297) covers the residual; confirmed_by_logic_differential is MEDIUM-confidence.
- **L2 dropped for logic mode.** For value-correctness bugs there is no before/after state flip; the divergence is the
  named-value evidence. This is correct for getters/loops/accounting but means a logic confirmation does not assert a
  storage flip (it asserts a divergent computed value).
- **Demonstrated on 3 loci.** The 3 beanstalk logic loci from P298; the mode generalizes to any logic/correctness bug
  with a faithful bug + corrected-control differential, but breadth is unproven beyond these.
- **Cumulative recall counts loci, not the full 81-public denominator.** 20 confirmed loci across the arc + beanstalk
  is the executed-validity tally; it is not a recall-of-81 figure.
