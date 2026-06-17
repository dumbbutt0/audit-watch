# P270 — ROLLBACK_PLAN

Additive and isolated; rollback fully restores the pre-P270 state.

## Creates (all removable)
- `documentation/research/assisted_mode/p270_fresh_full_path_selector_triage/` (docs + outputs).
- `pocs/p270/` (isolated foundry PoCs).
- `tests/research/test_p270_fresh_full_path_selector_triage.py`.
- `/tmp/p270_fresh/wise` (fresh source clone — outside repo working tree; transient).
- Memory: `project_phase270_*.md` + one MEMORY.md line.

## Must NOT have changed (verify on rollback)
- Frozen modules + configs byte-identical: P260 `d6b494bc`/`c61da091` · P262 `a48336275f`/`62e860199` · P264
  `85f9cbe6`/`e9b74687` · P267 `b0623b8c`/`9dab060d` · P269 `63c88d02`/`7c174b5d`.
- 5 forbidden files byte-identical (dashboard_sync, deep_trace, min_confirm_gate, confirm_gate, validate_p208).
- `scripts/dashboard.py`, `dashboard/*.html`, canonical finding records — untouched (advisory surface standalone).
- Active audit symlink `output → audits/size-credit-2024-06-blind/output`.
- `audits/` untouched (wise lives only in `/tmp`).

## Procedure
1. `rm -rf documentation/research/assisted_mode/p270_fresh_full_path_selector_triage pocs/p270
   tests/research/test_p270_fresh_full_path_selector_triage.py /tmp/p270_fresh`.
2. Delete `memory/project_phase270_*.md` + its MEMORY.md line.
3. `sha256sum` re-check frozen + forbidden; confirm `output` symlink target.
4. `pytest tests/research/` (P269..P260 + checkpoints) green.

## Abort path (verdict G)
Any promoted/confirmed/reportable/severity field on a candidate, or award-content leak before the Phase-9 freeze →
stop, record `G — ABORTED_SAFETY_OR_CONTAMINATION`, exclude the artifact, run rollback. No partial reportable output.
