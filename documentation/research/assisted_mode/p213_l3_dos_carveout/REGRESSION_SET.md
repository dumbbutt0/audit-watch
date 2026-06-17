# P213 — regression set (regression_cases.json)

10 fixtures, each = a P208 base record (→ `old_label` via `decide()`) + a 10-field `carveout` block + `expected`.

| id | role | base (old) | carve-out | expected |
|---|---|---|---|---|
| SOPH-03 | **positive** | dos/FAIL → medium | ALL 10 true | **high** |
| decent-M-03 | neg (auth-bypass) | auth_only/FAIL → medium | not DoS/no-revert | medium |
| decent-06 | neg (false High) | other/FAIL → medium | no DoS proof | medium |
| decent-12 | neg (needs harness) | NEEDS_HARNESS → needs_harness | no executed proof | needs_harness_for_severity |
| vultisig-M-03 | neg (cap-bypass) | bounded_local/FAIL → medium | not core-path/not DoS | medium |
| munchables-DoS | neg (screened DoS High, no harness) | dos/NEEDS_HARNESS → needs_harness | **no deterministic_l3_proof + no control** | needs_harness_for_severity |
| generic-static-high-no-poc | neg | NOT_ATTEMPTED → needs_harness | no proof | needs_harness_for_severity |
| generic-dos-no-core-path | neg | dos/FAIL → medium | **core_path=false** | medium |
| precision-no-magnitude | neg | precision/NOT_ATTEMPTED → needs_harness | no proof | needs_harness_for_severity |
| source-refuted | neg | refut/FAIL → invalid | (all 10 true) → **never upgraded** | invalid |

Positive proves the fix; negatives prove no over-HIGH regression (incl. the munchables-DoS and source-refuted guards).
