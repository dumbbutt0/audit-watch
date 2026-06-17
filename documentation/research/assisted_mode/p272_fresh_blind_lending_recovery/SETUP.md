# P272 — SETUP (Fresh Blind Full-Path Rerun With Lending Scaffold/Checklist)

**RESEARCH-ONLY · BLIND application test, NOT a build.** Runs the full path on a FRESH scored lending contest with
the P267 selector + P269 triage enabled AND the P271 LENDING_COMPLETION_CHECKLIST applied at completion — all
pre-reveal, NO tuning of the checklist/patterns or frozen modules during the run. Tests whether the Wise calibration
generalizes BLIND to exact/strong awarded recovery with runtime support.

## Full chain
P260 prioritizer -> P262 recall sweep -> P264 shadow harness -> standalone advisory dashboard -> P267 selector ->
P269 impact-first triage -> B/C + five-op completion (steered by the P271 LENDING_COMPLETION_CHECKLIST) ->
full/partial-runtime PoC (P271 patterns) -> pre-reveal gate -> reveal + exact-mechanism scoring.

## Target
`code-423n4/2024-01-init-capital-invitational` (money-market/leverage lending). Source-only clone at
/tmp/p272_fresh/init (isolated, never under audits/). Answer key `...-invitational-findings` (PUBLIC, sealed until
Phase 9). See TARGET_SCREEN.md (training-confound + invitational-sparsity disclosed).

## Frozen modules (verified unchanged; must stay byte-identical -- NO tuning)
P260 d6b494bc / c61da091 · P262 a48336275f / 62e860199 · P264 85f9cbe6 / e9b74687 · P267 b0623b8c / 9dab060d ·
P269 63c88d02 / 7c174b5d. The P271 LENDING_COMPLETION_CHECKLIST is applied as READ-ONLY reference.
Forbidden 5 byte-identical: dashboard_sync c1af70e1 · deep_trace c095c426 · min_confirm_gate 2a15169a ·
confirm_gate afc481c9 · validate_p208 ae55eb80. Active audit output -> audits/size-credit-2024-06-blind/output.

## Safety
Blind (answer key sealed until full pre-reveal set frozen+hashed; no answer-key content used to generate candidates /
assign selector-triage dimensions / drive completion). No production authority / auto-submission / severity /
reportable / submission-ready / confirmed. No production/contest source edits; PoCs isolated under pocs/p272/.
