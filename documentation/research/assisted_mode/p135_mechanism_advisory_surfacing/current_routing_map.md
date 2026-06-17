# P135 — Current Routing Map

## How findings reach review today
- **review_gate.md** — `scripts/generate_review_gate.py`, CONFIRMED findings only (parses `[x] CONFIRMED` triage
  markdown). No advisory/context section.
- **human_review_queue.jsonl** — `scripts/human_review_classifier.py`, from triage submit/poc_required when ≥2
  criteria fire. Fields: finding_id, triage_status, recommended_severity, ice, human_review_reasons/score,
  priority_score.
- **merged_findings.json** — candidates with `id`, `location{file,function,lines}`, `manifest_refs`.

## What gets surfaced today vs dropped
| Detector | Status | Reaches review? |
|---|---|---|
| connector_position_accounting | advisory (advisory_escalation_gate) | only in **strict-full-audit** |
| arithmetic_conservation | advisory (advisory_escalation_gate) | only in **strict-full-audit** |
| units_invariant | **report-only** | **no** (report written, never surfaced) |
| semantic_tvl_completeness | **research-only / un-wired** | **no** |
| registry_position_lifecycle | **research-only** | **no** |

⇒ In a normal run, the detector hits that recover the P133 MISS (units H-01, CPA H-13, AC H-14) are computed but
**don't reach the standard review surface**.

## Where advisory evidence should attach (P135)
- **Primary (safe):** a new audit-local artifact `output/mechanism_advisory_context.json` — isolated, clearly
  advisory_only / routing_allowed:false, consumable by review without touching submission.
- **Secondary (gated):** append **review_context** entries to `data/triage/human_review_queue.jsonl` (only when
  `mechanism_advisory_standalone_queue=true`), each `advisory_only:true`, `finding_id:null`, no severity.
- **Attach to candidate** when a `merged_findings.json` item matches contract+function+file (sets
  `related_candidate_id`); noya has no merged_findings → standalone.

## Where NOT to attach
- **Not** into the CONFIRMED list of review_gate.md, submission packages, severity, or any submit path. Advisory
  evidence must never be mistakable for a confirmed finding (mirrors the existing `advisory_escalation_gate`
  "never converts advisory to finding" rule).
