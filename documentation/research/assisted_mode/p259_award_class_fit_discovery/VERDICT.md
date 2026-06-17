# P259 — VERDICT

## Bottleneck: LOCUS_SELECTION_GAP
## Verdict: NEEDS_MORE_HELDOUT  (build-direction recommendation: DISCOVERY[locus-prioritization + Pass-2 shapes] + TOP2 RANKING)

### What happened
P259 removed P258's two confounds — **award-class-fit target screen** + **fuller per-issue reveal** — and added
**two-pass discovery** (7 families + 8 shape-generator templates), blind, on hybra (clean) + sentiment
(disclosed-contaminated). The award-class-fit screen **worked**: both contests' headline awards are
**subtle_accounting_state** (hybra gHYBR first-depositor share-inflation; sentiment #613 bad-debt share-inflation)
— not astaria's mechanical class. And the **Pass-2 shape vocabulary generated the exact award classes** (T8
share-price/inflation matched both headlines; T7 solvency matched sentiment bad-debt).

**But 0 awarded mechanisms were cleanly SELECTED+COMPLETED pre-reveal**, because the failure moved one step
upstream of shape-discovery: **locus selection**. hybra's headline award sat on `GrowthHYBR.deposit` — a
**checkpoint hit I did not select** (I picked VotingEscrow/GaugeManager); sentiment's bad-debt share-inflation was
the **right shape (T8) placed at the wrong locus** (S-L1 not S-L2). So the shapes were right; the loci were wrong.

### Why this bottleneck (LOCUS_SELECTION_GAP)
- **Not TARGET_FIT_GAP:** the screen delivered subtle-accounting awards (confound removed).
- **Not (pure) MECHANISM_DISCOVERY_GAP:** Pass-2 generated the awarded shape classes (T8/T7) — P258's "discovery
  dominates / wrong shapes" is **revised**: the shapes are adequate.
- **Not MECHANISM_RANKING_GAP alone:** B/C elevated the right shape families when present (ranking is downstream).
- **LOCUS_SELECTION_GAP** best fits: the award-carrying loci weren't subjected to the (working) shape discovery,
  or the shape was applied at the wrong locus.

### Why NEEDS_MORE_HELDOUT (formal) — and the real build-direction
- **Formal:** the build threshold (≥2 scored contests **and ≥2 selected-locus awarded mechanisms cleanly
  selected**) is **not met** (0 clean SELECTED+COMPLETED; 1 of 2 contests contaminated; reveal search-level-plus).
  So the formal verdict is NEEDS_MORE_HELDOUT, not a build.
- **But the corpus is exhausted** — "more held-out" is not available without **acquiring fresh unseen contests**.
  So the actionable build-direction, given the now-refined diagnosis, is:
  **BUILD_DISCOVERY_PLUS_TOP2_RANKING_HARNESS, where the DISCOVERY module is a LOCUS-PRIORITIZATION + Pass-2
  shape-application tool** (not a new shape vocabulary, and not pure ranking): take the checkpoint-hit loci, force
  the 8 shape-generator templates on the *highest-value* loci (the ones locus-selection currently skips, e.g.
  first-depositor/deposit, bad-debt, queue), then apply B/C ranking. Validate it on **freshly acquired** unseen
  award-class-fit contests (the spent corpus can't serve another clean blind round).

### Arc synthesis (P256→P259)
- enumerated → ranking gap, B/C fix it (P256 plaza, P257 #886).
- not-enumerated → P258 said discovery dominates.
- **P259 refines:** with award-class-fit + shape-generators, **shape discovery is adequate**; the binding gap is
  **locus selection** (which functions to deep-enumerate) + downstream ranking. ⇒ the harness is
  **locus-prioritization + shape-application (discovery) feeding B/C ranking + the validated five completion ops.**

### Honest caveats
n=2 (1 contaminated/asterisked); search-level-plus reveal (hybra split/merge mechanisms unverified); 0 clean
SELECTED+COMPLETED; sentiment SuperPool awards partly compliance/config (residual target-fit noise); corpus
exhausted. No softening — A/B/C 0-selected reported plainly; the positive (shapes match award classes) is reported
as direction, not as a met build threshold.
