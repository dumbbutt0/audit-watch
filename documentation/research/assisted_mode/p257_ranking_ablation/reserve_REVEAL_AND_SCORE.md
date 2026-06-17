# reserve — Reveal & score — EXCLUDED (precheck-contaminated)

Reserve is **excluded from scoring**: the REVEAL_AVAILABILITY_PRECHECK availability search returned reserve's
awarded Medium titles (M-01 DAO-fee distribution, M-02 RSR seizure, M-05 StRSR era, M-06 canceled withdrawal,
M-07 traceEnd) at planning time. A freeze-before-reveal mechanism-selection test would be hindsight-tainted, so no
loci were selected, no mechanism gate / ranking ablation / completion was run, and **no scoring is produced** for
reserve. Its checkpoint records (frozen, un-scored) are in `reserve_BASE_FREEZE.md` for provenance only.

**Reveal source (for the record, not used for blind scoring):** `code-423n4/2024-07-reserve-findings` (public).

**Lesson → refined precheck:** verify reveal *existence* (repo/URL landing) without issuing award-content
("High/Medium findings") searches. reserve cost P257 a second scored contest; P257 therefore rests on notional (n=1).
