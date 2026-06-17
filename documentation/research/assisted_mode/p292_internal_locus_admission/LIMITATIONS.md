# P292 — LIMITATIONS

1. **Admission ≠ lift.** P292 closes admission (internal loci now reach Lens 3), but the admitted loci do NOT lift —
   Lens 3 returns NO_REFERENCE because the reward-index logic is not span-local-visible. The end-to-end reward-index
   READY needs a lens/gate refinement (cross-function reward-index detection or broader index terms), a separate phase.
2. **Span-local lens.** Lens 3 reads the candidate's own span; reward-index init in a callee (public→_stake→
   _increaseUserShare) is invisible. Depth-1 internal expansion + span-local Lens 3 = the gap.
3. **Bounded by design.** ≤2/class, ≤5/contest, appended pool. On a target with many distinct internal loci, some
   eligible ones may be capped out (DEFERRED_INTERNAL_LOCUS_CAP).
4. **Queue-layer only.** The router's COVERAGE_DEFER_DUPLICATE_CLASS still fires; the exception re-admits in the queue.
   The router is byte-identical (no internal_locus in its input).
5. **Supervised, advisory, not production.** salty/ECG/silo used as eval; no target/award constants; no production
   authority/submission/severity. No new full PoC (no internal locus reached READY).
