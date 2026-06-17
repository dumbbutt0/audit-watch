# P268 — ROLLBACK_PLAN

P268 is additive and isolated. Rollback fully restores the pre-P268 state.

## What P268 creates (all removable)
- `documentation/research/assisted_mode/p268_fresh_full_path_with_selector/` (docs + `outputs/`).
- `pocs/p268/` (isolated foundry PoCs).
- `tests/research/test_p268_fresh_full_path_with_selector.py`.
- `/tmp/p268_fresh/karak` (fresh source clone — outside the repo working tree; transient).
- Memory: `project_phase268_*.md` + one MEMORY.md line.

## What P268 must NOT have changed (verify intact on rollback)
- Frozen modules + configs byte-identical: P260 `d6b494bc`/`c61da091` · P262 `a48336275f`/`62e860199` · P264
  `85f9cbe6`/`e9b74687` · **P267 `b0623b8c`/`9dab060d`**.
- 5 forbidden files byte-identical (dashboard_sync, deep_trace, min_confirm_gate, confirm_gate, validate_p208).
- `scripts/dashboard.py`, `dashboard/*.html`, canonical finding records — untouched (advisory surface standalone).
- Active audit symlink `output → audits/size-credit-2024-06-blind/output` (no `switch_audit`).
- `audits/` — untouched (karak lives only in `/tmp`, never copied under `audits/`).

## Rollback procedure
1. `rm -rf documentation/research/assisted_mode/p268_fresh_full_path_with_selector pocs/p268
   tests/research/test_p268_fresh_full_path_with_selector.py /tmp/p268_fresh`.
2. Delete `memory/project_phase268_*.md` and its MEMORY.md line.
3. `sha256sum` re-check frozen + forbidden lists; confirm `output` symlink target.
4. `pytest tests/research/` (P267/P266/P265/P264/P262/P260 + checkpoints) green.

## Abort path (verdict G — safety/contamination)
If any candidate/selector decision acquires a promoted/confirmed/reportable/severity field, or award content leaks
before the Phase-11 freeze: stop, record `G — ABORTED_CONTAMINATION_OR_SAFETY` in VERDICT.md, exclude the affected
artifact, run the rollback above. No partial reportable output emitted.
