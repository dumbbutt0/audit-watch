# P274 — SETUP (Fresh Full-Path Test With Award-Class Coverage Enabled — BLIND)

**RESEARCH-ONLY · BLIND application test, NOT a build.** First blind run with ALL selection fixes active together:
P267 selector + P273 award-class coverage + P269 impact-first triage + P271 checklist, on a diverse multi-class
target. Tests whether coverage closes the P272 "valid non-awarded TP" mismatch (recover an AWARDED mechanism).

## Full chain
P260 -> P262 -> P264 harness -> advisory dashboard -> P267 selector -> P273 coverage router -> P269 triage (per
represented class) -> B/C + five-op completion (P271 checklist for accounting; class-specific questions for access/
order/front-run/DoS) -> full/partial-runtime PoC -> pre-reveal gate -> reveal + score.

## Target
`code-423n4/2024-04-gondi` (P2P NFT lending; multi-class). Source-only clone /tmp/p274_fresh/gondi (never audits/).
Answer key `2024-04-gondi-findings` PUBLIC, sealed until Phase 10. See TARGET_SCREEN.md.

## Frozen modules (verified unchanged; byte-identical -- NO tuning)
P260 d6b494bc / c61da091 · P262 a48336275f / 62e860199 · P264 85f9cbe6 / e9b74687 · P267 b0623b8c / 9dab060d ·
P269 63c88d02 / 7c174b5d · P273 b87e3d22 / 3fbc476e. P271 LENDING_COMPLETION_CHECKLIST applied READ-ONLY.
Forbidden 5: dashboard_sync c1af70e1 · deep_trace c095c426 · min_confirm_gate 2a15169a · confirm_gate afc481c9 ·
validate_p208 ae55eb80. Active audit output -> audits/size-credit-2024-06-blind/output.

## Safety
Blind (answer key sealed until full pre-reveal set frozen+hashed; no answer-key content drives candidates/dimensions/
completion). No production authority / auto-submission / severity / reportable / submission-ready / confirmed. No
production/contest source edits; PoCs isolated under pocs/p274/.
