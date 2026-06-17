# P270 — DIAGNOSIS (Phase 10)

Full path on a fresh zero-exposure external contest (wise-lending, 2024-02; 5H+17M; public findings; training-confound
disclosed), with BOTH selection fixes (P267 selector + P269 impact-first triage) enabled.

## Counts
- target awarded: 5 High + 17 Medium.
- advisory candidates emitted: 24 (guard PASS; recall-delta 19/24 = 79%).
- selector decisions: KEEP_BOTH ×3 (preserved all high-impact M1s), REFUTE_M1_FIRST ×1 (unsupported NFT drama).
- triage selections: **3 SELECT_FOR_PARTIAL_RUNTIME** (Pendle-share, liquidation, bad-debt — all heavy, all routed);
  unsupported drama DEFER_LOW_IMPACT; easy rivals KEEP_AS_CONTROL.
- heavy/partial candidates selected: 3/3 (none de-scoped for fixture difficulty).
- PoCs attempted: 1 (C-pp) · passed: 1 (refuted its mechanism) · C-liq/C-bd not run (NEEDS_MORE_RUNTIME).
- **exact awarded mechanisms recovered: 0** · strong: 0 · **family-level: 2 (C-liq→H-04, C-bd→H-03)** · same-area-
  wrong: 0 · non-awarded true positives: 0 · false positives: 0 · **severe concluded/reportable FP: 0**.

## Did the two fixes work? — YES, and they steered onto awarded loci
- **Selector (P267):** preserved all three high-impact mechanisms (KEEP_BOTH); refute-firsted the unsupported drama.
- **Triage (P269):** routed all three high-impact award-class subsystems as SELECT_FOR_PARTIAL_RUNTIME — **including
  the heavy ones** (needs_fork/snapshot_scaffolding) it would have de-scoped pre-P269. Two of the three routed loci
  (bad-debt, liquidation) are the **exact loci of awarded Highs H-03 and H-04.** This is the first time the selection
  layers land the PoC queue on awarded loci — the P266→P268 selection failures are resolved on fresh data.

## Why 0 exact recovery (the bottleneck, one more stage down)
1. **Completion precision:** the pre-reveal mechanism hypotheses for C-liq/C-bd were **family-level** (right subsystem
   + locus + bug family) but did not pin the exact root cause (H-04's private-vs-public collateral split; H-03's
   partial-liquidation global-vs-position bad-debt deduction).
2. **PoC harness weight:** confirming those exact mechanisms needs the **full WiseLending stack** (deposit→borrow→
   price-drop→liquidate / →insolvency→bad-debt) — the two candidates were correctly *routed* PARTIAL_RUNTIME but the
   full-stack PoC was **not built in scope** (NEEDS_MORE_RUNTIME). The one PoC that was harness-feasible (C-pp Pendle-
   share) *refuted* its (non-awarded) mechanism — a true negative.

## Per-stage localization
- Recall: ✅ surfaced the award subsystems (bad-debt/liquidation/Pendle in narrow+delta).
- Selector: ✅ preserved high-impact mechanisms.
- **Triage: ✅ routed the award-class subsystems (incl. heavy) onto awarded loci H-03/H-04** — the P268 fix, validated.
- Completion: ⚠️ family-level (not exact) on the two awarded loci.
- **PoC harness: ❌ the binding gap** — full-stack PoC for a heavy lending protocol not built; the awarded-locus
  candidates stayed NEEDS_MORE_RUNTIME.
- Gate: ✅ conservative; 0 severe concluded/reportable FP; C-pp correctly REFUTED.

## Comparison vs P266 / P268 / earlier
| phase | selection lands on awarded locus? | exact recovery |
|---|---|---|
| P266 phi | awarded locus surfaced, mis-RANKED | 0 (RANKING_GAP) |
| P268 karak | award subsystem surfaced, TRIAGE de-scoped | 0 (TRIAGE_GAP) |
| **P270 wise** | **YES — triage routed onto awarded loci H-03/H-04** | **0 — family-level; PoC harness-blocked** |
The selection bottlenecks (ranking P266, triage P268) are now BOTH fixed and the routing lands on awarded loci. The
frontier moved to **completion-precision + PoC-harness depth on heavy protocols**.

## Bottleneck (exactly one): **F — POC_HARNESS_GAP**
The award-class loci were routed (selection works), but turning the family-level locus hits into exact, PoC-confirmed
mechanisms was blocked by full-stack PoC harness weight (NEEDS_MORE_RUNTIME on H-03/H-04). Completion-precision
(family vs exact) is the secondary contributor.
