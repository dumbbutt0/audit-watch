# Option-A campaign closeout (H5–H24)

renzo produced no reportable and no harness candidate, completing the cross-architecture sweep. **Campaign closed.**

## Funnel (H5–H24, across 8+ architectures)
- 20 candidates · **1 reportable** (H5 — abracadabra post-expiry boost retention) · **1 harness built** (H5) ·
  **19 harnesses avoided** · 7 source-refutations · 12 gate-refutations.
- **reportables per harness built = 1/1** (headline) · **prediction_accuracy 15/15** (H10–H24) ·
  **fabrication_rate = 0/20** (hard invariant held throughout).
- Architectures swept: abracadabra · pooltogether · wildcat · basin · hybra · revert-lend · silo · zaros ·
  predy · maia-talos · tokemak · renzo (+ earlier noya/blackhole/centrifuge/velodrome/decent/ecg).

## Conclusion
**Convertibles are scarce in the current corpora.** Across 15 bug families and many architectures, the
hygiene-filtered reject-first protocol produced meaningful, source-grounded refutations and exactly one
reportable — with **zero fabricated confirmations** and **zero wasted harnesses** beyond the one that converted.

**The durable asset is the tooling + calibration**, not any single finding: candidate-generation hygiene
(protocol_src only, vendored/test/mock excluded), the reject-first protocol with named failure buckets,
prediction logging + calibration (15/15), the `fabrication_rate=0` invariant, and the campaign scorecard.

**Next improvement = new corpora or new bug-family priors, NOT more dashboard/tooling.** The tooling is
sufficient; the bottleneck is the input distribution. Productive next steps:
- (a) bring fresh, unaudited / recently-deployed corpora more likely to contain live convertibles;
- (b) add new bug-family priors / signal patterns informed by recently-disclosed exploit classes.

Do **not** add more dashboard / scorecard / readiness tooling — that surface is complete.
