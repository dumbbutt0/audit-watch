# P262 — VERDICT

## A — RECALL_FIX_READY_FOR_FRESH_PROOF
(meaning: the one-shot recall fix demonstrably closes the P259 early-pruning leak on the frozen backtest with a
clean FP-guard, so it is ready for a fresh end-to-end proof — NOT a claim of live validation.)

### Why A
- **The leak is fixed:** all 6 subtle-accounting skipped award-locus areas (hybra GrowthHYBR.deposit, sentiment
  rebalanceBadDebt, notional _accrueFees, plaza _create, bakerfi harvest, loopfi liquidatePosition) are now
  FORCED_INTO_SWEEP — shape discovery reaches them BEFORE narrow selection. T7/T8 share/debt/solvency loci are no
  longer skipped.
- **Basin-style math recall restored:** T9 forces decodeWellData + calcReserveAtRatio* into the sweep (4/4), the
  P258/P260 math/units gap.
- **Zero concluded/reportable FP preserved:** advisory-only; runtime-asserted no severity/concluded/reportable/
  submission; promotion-gated. Output bounded on every contest (caps enforced; truncation recorded).
- **Zero production changes:** reuses (does not modify) the P260 module + checkpoints; forbidden files byte-identical.

### Not B/C/D
- Not C (NOT_USEFUL): it recovers the exact skipped award-locus class the arc has chased.
- Not D (constraint violation): no production edits; FP-guard holds; active audit unchanged.
- Not B as headline (though caveats are real — sibling-locus misses, T1-vs-fee template precision, cap truncation,
  T9 recall-not-precision): A means "ready for the fresh PROOF," which is the correct next gate, not "validated."

### Required next step
Fresh end-to-end proof (P263-style): fresh contest → recall sweep → B/C ranking → five ops → freeze → reveal →
score. As in P261, this needs a fresh target whose findings are publicly retrievable (monetrix reveal still
deferred). Do NOT claim recall is "restored" until a fresh scored run confirms an awarded locus survives
sweep→ranking→completion.

### Honest caveats
Backtest necessary-not-sufficient; sibling-locus residual misses; caps can truncate; T9 trades precision for recall;
"0 concluded/reportable FP" (by construction) ≠ true 0-FP at the candidate stage.
