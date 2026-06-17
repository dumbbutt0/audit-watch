# P292 — EVIDENCE_AUDIT

## _increaseUserShare (the target) — ADMITTED, reaches Lens 3, precise block
- Admission decision correct? Yes — ADMITTED_INTERNAL_LOCUS_EXCEPTION (internal_locus + reached from
  Liquidity._depositLiquidityAndIncreaseShare + source_span + SHARE_ROUNDING class + share signal + distinct fn).
- Reaches Lens 3? Yes — now in the queue → evidence package → deriver → Lens 3.
- Lens 3 lift? No — invariant_delta NO_REFERENCE → NEEDS_VALUE_FLOW_EVIDENCE. Audited cause: `_increaseUserShare` has
  share/stake terms but NO in-span rewardIndex/userIndex/claim terms (Lens 3's reward_index_init signals); the index
  accounting is in a callee / non-standard naming → Lens 3 correctly returns None (no false READY). Precise block.

## ADMITTED_INTERNAL_LOCUS_EXCEPTION candidates (3, all audited)
salty `_increaseUserShare`, ECG `updateTotalRebasingShares`, silo `_convertToSharesWithTotalsSafe`: all real internal
share/reward/accounting functions with state writes, reached from surfaced public entries (call paths real), class-
relevant. Exceptions justified (distinct functions, eligible classes, within caps). All → NEEDS_VALUE_FLOW_EVIDENCE
(Lens 3 received, did not fire). 0 false READY.

## DEFERRED_DUPLICATE_CLASS sample (5) — default dedup preserved
Non-internal same-class duplicates remain deferred (unchanged behavior) — the exception only applies to internal_locus
candidates. ✓

## Normal primary admissions (5) — unaffected
Base handoff-queue candidates admitted as ADMITTED_PRIMARY_CLASS; their statuses unchanged from pre-P292. ✓

## Regressions
Pools.deposit NEEDS_INTEGRATION_DEVIATION_EVIDENCE (P291 held) · ECG H-04 stake READY · kelp H-01 READY · blackhole
claim_many READY · L2Governor READY. All correct, no over-demotion, no false READY. ✓

## Anti-monoculture / noise
Max class fraction ≤0.27 on all 8 audits; ≤1 internal admission/audit; caps never hit; no monoculture guard triggered.
No over-admission, no hallucinated call paths. ✓

## Tally
internal loci admitted 3 (incl. the awarded `_increaseUserShare`) · all reach Lens 3 · 0 lift (precise NEEDS_VALUE_FLOW)
· 0 false READY · 0 over-admission · severe FP=0 · regressions stable.
