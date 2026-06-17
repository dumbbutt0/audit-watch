# P213 — repaired-mapping scorecard

`python documentation/research/assisted_mode/p213_l3_dos_carveout/validate_p213.py` → **10/10 pass, 0 regression failures.**

| id | old_label | repaired_label | expected | carve-out | pass |
|---|---|---|---|---|---|
| SOPH-03 | medium | **high** | high | ALL 10 | ✅ |
| decent-M-03 | medium | medium | medium | miss: deterministic_l3_proof, no_workaround, affects_class | ✅ |
| decent-06 | medium | medium | medium | miss: deterministic_l3_proof, no_workaround, affects_class | ✅ |
| decent-12 | needs_harness | needs_harness | needs_harness | miss: proof, source_valid, no_workaround, affects_class, control | ✅ |
| vultisig-M-03 | medium | medium | medium | miss: deterministic_l3_proof, core_path, no_workaround | ✅ |
| munchables-DoS | needs_harness | needs_harness | needs_harness | miss: deterministic_l3_proof, control_case_present | ✅ |
| generic-static-high-no-poc | needs_harness | needs_harness | needs_harness | miss: proof, source_valid, no_workaround, control | ✅ |
| generic-dos-no-core-path | medium | medium | medium | miss: core_path, no_workaround, affects_class | ✅ |
| precision-no-magnitude | needs_harness | needs_harness | needs_harness | miss: proof, no_workaround, control | ✅ |
| source-refuted | invalid | invalid | invalid | ALL 10 (but invalid never upgraded) | ✅ |

**SOPH-03 fixed (medium→high); 0 new false-Highs; 1 DoS upgraded, 2 DoS retained < High.**
