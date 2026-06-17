# P137 — Routing Recommendation

The blind `deep_pass_value_provenance` pass discovered H-03 from source (PROMPT_HIT) and was specific on a clean
control. Recommended routing for the H-03 / multi-hop-value-loop class:

## Recommended: surface as advisory deep-pass recommendation → human_review_queue (advisory_only)
- Keep the P136 `deep_pass_router` recommendation (`recommended_prompt: deep_pass_value_provenance`) for the
  oracle/value-loop class. When that signal fires, **the operator runs the prompt** (or it is run in the deep
  pass) and the structured `finding`/`needs_human` output is attached to the advisory review_context and the
  `human_review_queue` as **advisory_only / submission_ready=false / requires_human_review=true** — exactly the
  P135/P136 surfacing channel. No change to severity/submission/gates.
- The prompt's `finding` is **review evidence**, not a confirmed finding: a human + a PoC/runtime check must
  confirm the ≥2-hop precondition and that the per-pair oracles differ before any severity/submission.

## Not recommended (now)
- **No new static detector.** A regex/AST detector can't reliably catch "stale loop-carried variable in a value
  path"; the prompt does. Building one risks overfitting to this single shape.
- **No auto-confirm / auto-queue-as-finding.** n is tiny (1 blind HIT, 1 aided HIT, 1 clean clear, 1 needs_human);
  promote to automated queue-as-finding only after the prompt repeatedly succeeds on a larger blind value-
  provenance corpus with a measured low FP rate.
- **Never** promote prompt output to confirmed/submission-ready from reasoning alone.

## Why this is safe
- Specificity check passed (clean `convertCToL` → strong_clear; single-hop oracle → needs_human, no false
  finding) → low over-flag risk for advisory surfacing.
- The prompt is research-only by construction (sets family/shape/confidence + a hypothesis, never severity/
  submission), so its output cannot bypass the human + PoC gates.
