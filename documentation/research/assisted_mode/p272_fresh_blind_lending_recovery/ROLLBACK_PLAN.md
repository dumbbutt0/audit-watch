# P272 — ROLLBACK_PLAN

Additive and isolated.

## Creates (all removable)
- `documentation/research/assisted_mode/p272_fresh_blind_lending_recovery/` (docs + outputs).
- `pocs/p272/` (isolated foundry PoCs).
- `tests/research/test_p272_fresh_blind_lending_recovery.py`.
- `/tmp/p272_fresh/init` (fresh source clone — transient, outside repo tree).
- Memory: `project_phase272_*.md` + one MEMORY.md line.

## Must NOT have changed (verify on rollback)
- Frozen modules + configs byte-identical: P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c`
  · P269 `63c88d02` (+ configs). The P271 checklist file unchanged (applied read-only).
- 5 forbidden files byte-identical.
- Active audit symlink `output → audits/size-credit-2024-06-blind/output`. `audits/` untouched.
- No production/contest source mutated (init source in `/tmp` only).

## Procedure
1. `rm -rf documentation/research/assisted_mode/p272_fresh_blind_lending_recovery pocs/p272
   tests/research/test_p272_fresh_blind_lending_recovery.py /tmp/p272_fresh`.
2. Delete `memory/project_phase272_*.md` + its MEMORY.md line.
3. `sha256sum` re-check frozen + forbidden; confirm `output` symlink.
4. `pytest tests/research/` (P271..P260) green.

## Abort path (verdict G)
Any frozen-module/forbidden change, production-authority leak, award-content leak before Phase-9 freeze, or
active-audit switch → record `G — ABORTED_SAFETY_OR_CONTAMINATION`, run rollback. No partial reportable output.
