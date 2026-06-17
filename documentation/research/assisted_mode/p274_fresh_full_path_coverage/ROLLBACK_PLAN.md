# P274 — ROLLBACK_PLAN
Additive and isolated.
## Creates (removable): documentation/research/assisted_mode/p274_fresh_full_path_coverage/, pocs/p274/,
tests/research/test_p274_fresh_full_path_coverage.py, /tmp/p274_fresh/gondi (transient), memory/project_phase274_*.md
+ MEMORY.md line.
## Must NOT have changed: frozen P260 d6b494bc / P262 a48336275f / P264 85f9cbe6 / P267 b0623b8c / P269 63c88d02 /
P273 b87e3d22 (+ configs) + P271 checklist; 5 forbidden (dashboard_sync c1af70e1, deep_trace c095c426,
min_confirm_gate 2a15169a, confirm_gate afc481c9, validate_p208 ae55eb80); active audit symlink ->
audits/size-credit-2024-06-blind/output; audits/ untouched; gondi source in /tmp only.
## Procedure: rm -rf the P274 dir + pocs/p274 + test + /tmp/p274_fresh; delete memory file + line; sha256 re-check
frozen+forbidden; pytest tests/research (P273..P260) green.
## Abort (verdict G): any frozen/forbidden change, production-authority leak, award-leak before Phase-10 freeze, or
active-audit switch -> record G ABORTED_SAFETY_OR_CONTAMINATION, run rollback.
