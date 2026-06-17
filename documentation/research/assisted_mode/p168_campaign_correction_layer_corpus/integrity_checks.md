# P168 integrity checks

| Artifact | Baseline | Post-P168 | Result |
|---|---|---|---|
| campaign ledger — existing 9 rows (`head -9`) | `22c48087…` | `22c48087…` | **byte-identical** (H14–H17 appended rows 10–13; no rewrite) |
| campaign ledger row count | 9 | 13 | append-only +4 (H14–H17) |
| prediction_log.jsonl lines | 4 | 8 | append-only +4 (H14–H17 predictions) |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** (no harness → no sidecar row) |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| readiness file | `ff8243c4…` | `ff8243c4…` | **byte-identical** |
| production `generate_scope_inventory.py` | `9088a59a…` | `9088a59a…` | **byte-identical** |
| campaign tool `option_a_campaign.py` | (P167) | unchanged this phase | **no new tooling** (used as-is) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Hygiene-filtered selection: protocol_src only; all 4 rows carry `candidate_signal_source=protocol_src`.
- `sandbox_check.py` CLEAN before reading each candidate. **0 harnesses built** (all SOURCE_REFUTED; never forced).
- Un-wired: `grep option_a_campaign|p168 run_pipeline.sh config/agent_policy.json` → empty.
- No `submission_ready`/`routing_allowed` set true; `fabrication_rate = 0/13`. No detector / routing / severity /
  submission-policy / prompt / corpus / sidecar-schema / production change.
