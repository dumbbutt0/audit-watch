# P271 — ROLLBACK_PLAN

Additive and isolated.

## Creates (all removable)
- `documentation/research/assisted_mode/p271_lending_runtime_scaffold/` (docs + outputs).
- `pocs/p271/wise/` (isolated foundry scaffold + 2 PoC tests; wise_src is a read-only copy).
- `tests/research/test_p271_lending_runtime_scaffold.py`.
- Memory: `project_phase271_*.md` + one MEMORY.md line.

## Must NOT have changed (verify on rollback)
- Frozen modules + configs byte-identical: P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c`
  · P269 `63c88d02` (+ configs).
- 5 forbidden files byte-identical (dashboard_sync, deep_trace, min_confirm_gate, confirm_gate, validate_p208).
- Active audit symlink `output → audits/size-credit-2024-06-blind/output`. `audits/` untouched.
- No production/contest source mutated (Wise source copied read-only).

## Procedure
1. `rm -rf documentation/research/assisted_mode/p271_lending_runtime_scaffold pocs/p271
   tests/research/test_p271_lending_runtime_scaffold.py`.
2. Delete `memory/project_phase271_*.md` + its MEMORY.md line.
3. `sha256sum` re-check frozen + forbidden; confirm `output` symlink.
4. `pytest tests/research/` (P270..P260) green.

## Abort path (verdict D)
Any frozen-module/forbidden-file change, production-authority leak, or active-audit switch → record `D —
ABORTED_CONSTRAINT_VIOLATION`, run rollback.
