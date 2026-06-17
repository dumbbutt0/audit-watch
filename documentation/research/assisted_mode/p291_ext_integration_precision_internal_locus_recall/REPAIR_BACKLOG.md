# P291 — REPAIR_BACKLOG

## Part A (EXTERNAL_INTEGRATION) — essentially complete
- Auto-detect covers low-level call / callback / reentrancy-ordering. Structural bases (fee-on-transfer/adapter/create2/
  cross-contract) require explicit evidence by design (auto-detecting fee-on-transfer would re-flag whitelist-mitigated
  deposits). Next (optional): a fee-on-transfer sub-detector that ALSO checks for a whitelist/fee-exclusion guard before
  flagging — only if a target needs auto fee-on-transfer. FP risk MED. Priority 3.

## Part B (internal-locus recall) — HALF DONE; the binding residual
- **Internal locus surfaced at advisory but dropped by P273 `COVERAGE_DEFER_DUPLICATE_CLASS` before the validation
  queue/Lens 3.** The reward-index awarded locus (`_increaseUserShare`) competes for the SHARE_ROUNDING class slot and
  loses to a same-class sibling. **Next repair (priority 1, separate phase — P273/P278 are do-not-edit in P291)**: give
  internal-locus candidates a reserved validation-queue slot, OR allow a distinct-locus same-class internal candidate
  past coverage duplicate-class dedup (it is a different function, not a true duplicate). FP risk LOW (advisory; the gate
  still must prove it). This is the path to Lens 3 actually firing on the reward-index bug.
- Secondary: depth-1 only (callees of public entries). Reward-index init bugs sometimes sit 2 hops in (public→_stake→
  _increaseUserShare). Next: depth-2 internal expansion with tighter caps. FP risk MED. Priority 2.

## Cross-cutting
- The internal-locus expansion competes for the harness `max_swept_loci_json` cap (25) with base candidates; on dense
  targets internal loci may be truncated. Consider a reserved internal-locus sub-cap. Priority 2.
