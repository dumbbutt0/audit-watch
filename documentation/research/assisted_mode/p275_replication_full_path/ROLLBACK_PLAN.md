# P275 — ROLLBACK_PLAN

P275 is **research-only, advisory, un-wired** — nothing to roll back in production. If any artifact must be removed:

1. Delete `documentation/research/assisted_mode/p275_replication_full_path/` and `pocs/p275/` and
   `tests/research/test_p275_replication_full_path.py`.
2. Verify frozen modules/configs + P271 checklist + 5 forbidden files are byte-identical to the SETUP.md baselines
   (P275 never edited them).
3. Verify `output` symlink → `audits/size-credit-2024-06-blind/output` (P275 never touched the active audit).
4. `/tmp/p275_fresh/` (ronin source + findings) is outside the repo; delete freely.

No config flags, no routing, no gate wiring were added. No production authority was granted. No memory of an awarded
finding to retract (target had 0 awarded H/M).
