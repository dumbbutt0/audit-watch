# P170 integrity checks

| Artifact | Baseline | Post-P170 | Result |
|---|---|---|---|
| campaign ledger — existing 17 rows (`head -17`) | `124015459d…` | `124015459d…` | **byte-identical** (H22–H24 appended rows 18–20) |
| campaign ledger row count | 17 | 20 | append-only +3 (H22–H24) |
| prediction_log.jsonl lines | 12 | 15 | append-only +3 |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** (no harness) |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| readiness file | `ff8243c4…` | unchanged | **byte-identical** |
| production `generate_scope_inventory.py` | `9088a59a…` | `9088a59a…` | **byte-identical** |
| campaign tool `option_a_campaign.py` | (P169) | unchanged this phase | **no code change** |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- **No code change this phase** (P169 already added `bug_family`). All 3 rows carry
  `candidate_signal_source=protocol_src` + `bug_family`.
- `sandbox_check.py` CLEAN before reading each source. **0 harnesses built** (all refuted; never forced).
- Un-wired; no `submission_ready`/`routing_allowed` true; `fabrication_rate = 0/20`. No routing/severity/
  submission-policy/detector/prompt/corpus/sidecar-schema/production change.
