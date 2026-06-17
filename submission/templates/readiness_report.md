<!--
readiness_report.md — reference layout for the internal gate verdict report.

This is the human-readable shape that submission/gates/render.py produces from a
gate verdict. It is the INTERNAL document (decision record), not the artifact
sent to a bounty program. Fields in {{...}} are filled by render_readiness_report().
-->

# Submission Readiness — {{finding_id}}

**Title:** {{title}}

**Status:** `{{recommended_status}}`
<!-- one of: DO_NOT_SUBMIT | NEEDS_MORE_PROOF | READY_FOR_HUMAN_REVIEW | READY_TO_SUBMIT_AFTER_APPROVAL -->

**Human approval required:** YES (the layer never auto-submits)

## Blockers (DO_NOT_SUBMIT)
<!-- one bullet per FAIL gate; absent if none -->

## Needs more proof
<!-- one bullet per NEEDS_PROOF gate; absent if none -->

## Warnings (human review)
<!-- one bullet per WARN gate; absent if none -->

## Per-gate results

| # | Gate | Verdict | Reason |
|---|------|---------|--------|
| 1 | scope | ... | ... |
| 2 | attacker_reachability | ... | ... |
| 3 | impact_severity | ... | ... |
| 4 | poc | ... | ... |
| 5 | duplicate_known_issue | ... | ... |
| 6 | evidence_completeness | ... | ... |
| 7 | invalidation_defense | ... | ... |
| 8 | human_approval | ... | ... |

_Evaluated at {{evaluated_at}}._
