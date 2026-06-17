# P169 integrity checks

| Artifact | Baseline | Post-P169 | Result |
|---|---|---|---|
| campaign ledger — existing 13 rows (`head -13`) | `86eefe01…` | `86eefe01…` | **byte-identical** (H18–H21 appended rows 14–17) |
| campaign ledger row count | 13 | 17 | append-only +4 (H18–H21) |
| prediction_log.jsonl lines | 8 | 12 | append-only +4 |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** (no harness) |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| readiness file | `ff8243c4…` | `ff8243c4…` | **byte-identical** |
| production `generate_scope_inventory.py` | `9088a59a…` | `9088a59a…` | **byte-identical** |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Only code change: `FIELDS += "bug_family"` (additive, backward-compatible) — the minimal schema add the task
  required ("record bug_family"). No new functions / endpoints / dashboard.
- Hygiene-filtered: all 4 rows carry `candidate_signal_source=protocol_src` + a `bug_family`.
- `sandbox_check.py` CLEAN before reading each source. **0 harnesses built** (all refuted; never forced).
- Un-wired: `grep option_a_campaign|p169 run_pipeline.sh config/agent_policy.json` → empty.
- No `submission_ready`/`routing_allowed` true; `fabrication_rate = 0/17`. No routing / severity /
  submission-policy / detector / prompt / corpus / sidecar-schema / production change; no correction-layer gate.
