# P292 — REPAIR_BACKLOG

## Admission — DONE
Distinct internal reward/accounting/share/index loci are now admitted past coverage duplicate-class dedup, bounded, with
0 false READY and stable diversity. The P291 admission residual is closed.

## The new binding residual — Lens 3 cannot lift the admitted loci (priority 1, next phase)
All 3 admitted internal loci reach Lens 3 but get NEEDS_VALUE_FLOW_EVIDENCE (NO_REFERENCE). Cause: the reward-index logic
is NOT span-local-visible (e.g. `_increaseUserShare` has share/stake terms but no in-span rewardIndex/userIndex/claim
terms; the accumulator update lives in a callee / non-standard naming). **Next repair (lens/gate)**:
- Lens 3 over the P283 trace path (detect the reward-index init in a resolved callee), OR
- broaden Lens 3's user-index/global-index term set to match more accounting conventions (e.g. `userShare`/`totalShares`
  + a `+=` to a per-user share without an index checkpoint), with refutation to keep FP=0.
FP risk: MED (broadening index terms). Priority 1.

## Secondary
- Depth-1 internal expansion only (P291): reward-index init sometimes sits 2 hops in (public→_stake→_increaseUserShare).
  Depth-2 expansion with tighter caps. Priority 2.
- Caps (≤2/class, ≤5/contest) are conservative; revisit only if a target needs more. Priority 3.
