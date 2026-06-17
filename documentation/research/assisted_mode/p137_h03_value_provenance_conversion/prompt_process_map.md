# P137 — Prompt / Process Map

`prompts/deep_pass_value_provenance.md` (research-only deep-pass specialist):
- **Input:** ONE function-scoped bundle (candidate body + 1–2 callee bodies; optional KB precedents at rung c2).
- **Process:** bounded loop ROUTE → PLAN → TRACE (validated_subject vs mutated_subject, identity/quantity
  source, loop-carried vs stale variable, divergence_point) → CRITIC (try to disprove; needs a cited evidence
  line) → DECIDE → REPRO_HINT.
- **Output labels:** `finding` (high) | `likely_exploitable` (medium) | `strong_clear` | `needs_human` — maps to
  PROMPT_HIT/PARTIAL/ADJACENT/MISS/NEEDS_CONTEXT.
- **Evidence rules:** no hallucinated recall (every finding cites a real line); no silent clear (uncertainty →
  needs_human); don't trust comments over code; research-only (sets family/shape/confidence + a hypothesis, never
  severity/exploitability/submission/disposition).
- **Function-scoped:** yes — exactly one candidate per bundle. Prepared in-pipeline by `deep_pass_prepare.py`;
  here the bundle was assembled manually (read-only) to control blindness, equivalent to a c1 (no-KB) bundle.
