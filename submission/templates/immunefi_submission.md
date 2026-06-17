<!--
immunefi_submission.md — Immunefi-style submission template.

Fill ONLY after the readiness gate returns READY_TO_SUBMIT_AFTER_APPROVAL (or
READY_FOR_HUMAN_REVIEW that a human has cleared) AND a human has approved.

Format rules (per the house style):
- Do NOT include an internal "Quality Checklist" or "Severity Justification"
  heading in the submitted text.
- Avoid overclaims: do not write "permanently" or "all funds" unless literally
  proven. Prefer scoped, quantified statements.
- The Proof of Concept is a top-level section with a runnable command.
-->

# {{title}}

**Severity:** {{severity_claim}}

**Target asset (in scope):** {{in_scope_asset}}

## Description

{{root_cause}}

Affected contract(s): {{affected_contracts}}
Affected function(s): {{affected_functions}}

## Attack scenario

1. Attacker entrypoint: {{attacker_entrypoint}}
2. Call path:
   {{call_trace}}
3. State transition (before → after): {{state_transition}}

## Impact

- Impact category: {{impact_category}}
- Quantified delta: {{asset_delta}}
- Worst case: {{severity_justification.worst_case}}
- Realistic case: {{severity_justification.realistic_case}}
- Program impact-table mapping: {{severity_justification.program_table_mapping}}

## Proof of Concept

PoC: `{{poc_path}}` (status: {{poc_status}})

Reproduction:
{{reproduction_steps}}

<!-- paste the runnable command + the key asserted output here -->

## Recommendation

<!-- exact file + line to change, before/after snippet, one sentence on why it fixes the root cause -->
