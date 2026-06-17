# ArkProject NFT Bridge — Strict Blind Eval Plan

## Identity
- Workspace: `audits/ark-project-2024-07-strict-eval/`
- Target: CodeHawks `2024-07-ark-project` · repo @ `273b7b94986d3914d5ee737c99a59ec8728b1517`
- Eval surface: **Solidity L1 only** (12 in-scope files); Cairo L2 out of tool capability (separate bucket).
- Started: 2026-05-31T17:07Z
- Audit-Watch fingerprint (sha256 over scripts/ config/ run_pipeline.sh): `60f1a65517f909b3a0350d4822f36a92a8c503fb605d91ddd45ad36d82d7a5cf`

## ANSWER KEY LOCKED
No answer-key / submissions access until the Phase-5/6 freeze is complete. `answer_key_used:false`.

## Strict config
- `AUDITWATCH_FULL_AUDIT=1` for every stage.
- api_free=true (in-session skills; no Anthropic API).
- active_mode=deep.
- coverage_policy strict keys ALL on: dependency_clear_strict_full_audit, dependency_locality_strict_full_audit,
  math_estimator_strict_full_audit, math_adversarial_proof.
- Anti-false-clear rules under test: dependency clears leaning on a NON-LOCAL guard must prove path-dominance
  (else `guard_not_path_dominant` → needs_deep_pass); math-sensitive clears need an adversarial proof
  (else `confirmatory_proof`); economic-shift routing only where naturally present.

## Pacing
Run end-to-end. The freeze (Phase 5/6) is a HARD ordering checkpoint — no answer-key access before it.
After freeze: fetch answer key, classify families, two scorecards, miss-class (Solidity-in-tool-scope only),
gate-regression notes, report.

## Hard rules
No answer-key before freeze · no submission inspection before freeze · no mutation of frozen artifacts
(before OR after answer key) · no pipeline/config/prompt/gate/taxonomy edits during the eval (measurement,
not tuning) · no Cairo hand-analysis folded into the scoring set · api-free preserved · nothing submitted ·
PoCs not required for scoring · new miss-class → document after scoring, don't patch.

## Family classification (Phase 7, post-freeze)
SOLIDITY_IN_TOOL_SCOPE · MIXED_SOLIDITY_CAIRO · CAIRO_ONLY_OUT_OF_TOOL_SCOPE · NON_CODE_OR_OUT_OF_SCOPE.
MIXED counts in-scope only if the Solidity side holds the root cause / missing guard / custody violation /
enforceable invariant; if detection requires Cairo semantics → mixed(out) or cairo-only, with explanation.

## Scorecards
- Primary: recall + precision over SOLIDITY_IN_TOOL_SCOPE (+ qualifying MIXED).
- Secondary: full-contest recall, Cairo-only separated (not blamed as Solidity misses).
