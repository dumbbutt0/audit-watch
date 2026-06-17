# P211 — failure cases & honest limitations

1. **Not a full-discovery replay.** decent has no `output/` pipeline artifacts, so discovery/min_confirm/confirm_gate
   were not re-run; P211 rehearses the L3-relevant wired surface (readiness → dashboard → package). Those upstream
   gates were validated in P209/P210 and are unchanged here.
2. **`final_submission_pack.py` not modified.** The package rehearsal is an "equivalent" assembly (existing fields +
   L3 overlay). Rendering L3 inside the packer is a noted follow-up, not done (keeps the packer hash-stable).
3. **`record_review` write path used a monkeypatched `_unified_keys`** so rehearsal ids are accepted without a live
   audit; the canonical-flag invariants still held (no `submission_ready`/`routing_allowed` flip). Rehearsal rows were
   removed from the shared research ledger afterward.
4. **DEC-STATIC is synthetic** (a High-ceiling candidate with no PoC) to exercise fail-closed; the other two map to
   real awarded decent findings.
5. **Critical caveat carried from P210:** the overlay's q6 vocabulary excludes "Critical"; L3 gates {High,Critical}
   at the policy level but Critical is independently un-submittable via the checklist today (unchanged).
6. **Flag is process-local.** Enabled only in the rehearsal process env; never persisted to `config/`.
