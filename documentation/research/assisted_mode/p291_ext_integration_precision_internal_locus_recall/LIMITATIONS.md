# P291 — LIMITATIONS

1. **Part B is half-done end-to-end.** Internal-locus recall surfaces the awarded `_increaseUserShare` at the advisory
   layer (the P290 gap is fixed there), but the P273 coverage router's duplicate-class dedup drops it before the
   validation queue, so Lens 3 never receives it. Closing the end-to-end reward-index path needs a coverage/queue change
   (P273/P278), which is do-not-edit in P291 → deferred to a separate phase.
2. **Part A auto-detect is conservative.** Fee-on-transfer/adapter/create2/cross-contract deviations require EXPLICIT
   operator evidence (auto-flagging fee-on-transfer would re-introduce the whitelist-mitigated Pools.deposit false READY).
   So a fresh target whose EXTERNAL_INTEGRATION bug is auto-only fee-on-transfer would be held at
   NEEDS_INTEGRATION_DEVIATION_EVIDENCE (correctly fail-closed, but a recall gap for that sub-class).
3. **Internal expansion is depth-1, bounded.** Callees two hops in (public→_stake→_increaseUserShare) are not surfaced;
   caps (≤3/entry, ≤15/contest) and the harness JSON cap (25) can truncate on dense targets.
4. **Heavy frozen-pin cascade.** Editing the P264 harness cascaded 20+ byte-identical pins (all hash-only, 0 behavioral);
   future edits to deeply-pinned modules carry the same cost.
5. **Supervised, advisory, not production.** salty/ECG used as eval only; no target/award constants; no production
   authority/submission/severity. Only a deviation-detector + a recall expansion; no new full PoC this phase.
