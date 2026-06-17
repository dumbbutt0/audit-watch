<!--
code4rena_submission.md — Code4rena / Sherlock-style submission template.

Fill ONLY after the readiness gate clears the candidate AND a human approves.
Do NOT include internal sections (Quality Checklist, Summary, Severity
Justification headings) in the submitted text. Keep language factual; avoid
"permanently"/"all" overclaims unless literally proven.
-->

# {{title}}

## Lines of code

{{affected_contracts}} — {{affected_functions}}
<!-- link to the exact lines, e.g. https://github.com/.../File.sol#L150-L175 -->

## Vulnerability details

{{root_cause}}

Attack path:
1. Entrypoint: {{attacker_entrypoint}}
2. {{call_trace}}
3. State change (before → after): {{state_transition}}

## Impact

{{impact_category}} — {{asset_delta}}

Worst case: {{severity_justification.worst_case}}
Realistic case: {{severity_justification.realistic_case}}

## Proof of Concept

`{{poc_path}}` (status: {{poc_status}})

{{reproduction_steps}}

<!-- runnable command + key assertions proving L1 entry / L2 state flip / L3 outcome -->

## Tools used

<!-- e.g. Foundry, Slither, manual review -->

## Recommended mitigation

<!-- exact fix with before/after snippet -->
