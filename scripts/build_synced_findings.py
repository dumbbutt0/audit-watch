#!/usr/bin/env python3
"""build_synced_findings.py — P216 generator, RETIRED in P217 to a thin shim over the generic wrapper.

The real extraction + richer field population now lives in scripts/sync_hunt_findings.py (P217). This shim simply
invokes that wrapper with the P215 ZetaChain arguments so there is a SINGLE extraction code path and no stale
lower-fidelity generator can downgrade the mirror. Kept for backward compatibility (existing references / muscle memory).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_hunt_findings  # noqa: E402

P215_ARGS = [
    "--phase", "P215",
    "--audit", "zetachain-2023-10-holdout",
    "--workspace", "documentation/research/assisted_mode/p215_full_funnel_rehearsal",
    "--l3-dir", "output_research/l3_readiness",
    "--dry-run-queue", "output_research/dry_run_submission_queue",
    "--write",
]

if __name__ == "__main__":
    # pass through extra flags (e.g. --dry-run, --strict, --replace-phase-records); default = P215 write.
    extra = [a for a in sys.argv[1:]]
    argv = P215_ARGS + extra if extra else P215_ARGS
    raise SystemExit(sync_hunt_findings.main(argv))
