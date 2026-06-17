# P219 — ZETA RESYNC RESULTS (REPLAY_MODE via the P218 hook)

`run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace …/p215_full_funnel_rehearsal`
→ **exit 0**: wrapper emitted 12 (12 updated / 0 new), completion guard **PASS** (reader+card checks), metrics written.

- 12 records regenerated, no duplicate ids, same `zetachain-2023-10:P215:` prefix.
- Idempotent: re-run byte-identical (`c7166e71…`).
- Safety: 12/12 pass validate_synced + safety_ok; submission_ready/routing_allowed false; severity recorded-or-HUMAN_PENDING.
- Evidence DEPTH (8 H5-parity dims): **0/96 → 48/96** populated, all artifact-backed (ZETA-07 8/8).
- 21-field aggregate completeness unchanged at 90% (those fields were already populated in P217; P219 adds depth on
  dimensions the legacy scorer didn't track — non-cosmetic).
- REPLAY_MODE: reused frozen P215 candidates/merged/triage/L3/harness/dry-run-queue/confirm; only evidence extraction
  re-run. No blind discovery, no new harness, no Zeta source change.
