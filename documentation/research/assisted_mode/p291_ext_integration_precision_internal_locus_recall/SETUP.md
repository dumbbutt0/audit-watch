# P291 — SETUP

**Phase:** P291 — EXTERNAL_INTEGRATION Precision + Internal-Locus Recall Repair (supervised; two tight repairs;
production authority WITHHELD). RESEARCH-ONLY · ADVISORY · default-off · fail-closed.

## What this phase is
Repairs the two failure modes P290 localized on salty (blind): (A) a generic EXTERNAL_INTEGRATION class-template READY
(`Pools.deposit`, PoC-refuted), and (B) the reward-index lens starved because internal awarded loci
(`StakingRewards._increaseUserShare`) were never surfaced. No new broad lenses; no scaleout.

## Components
- **A**: `completion_evidence_deriver.py` gains a source-backed `integration_deviation_evidence` detector;
  `poc_readiness_evidence_gate.py` gains a fail-closed block + `NEEDS_INTEGRATION_DEVIATION_EVIDENCE` status; deriver
  config gains integration-deviation signal terms. EXTERNAL_INTEGRATION lifts ONLY with a concrete source-backed
  deviation.
- **B**: `recall_first_harness.py` gains a bounded internal-locus expansion post-pass (config caps) that surfaces
  class-relevant internal callees of surfaced public candidates as `internal_locus` advisory candidates.

## Standing constraints
Research/advisory only; no production authority/submission/severity/reportable/confirmed; no production/contest source
edits; active audit `size-credit-2024-06-blind` symlink unchanged; no target/award hard-coding; forbidden 5 + do-not-edit
frozen modules byte-identical (cascade pins bumped/excluded per the P289 precedent).
