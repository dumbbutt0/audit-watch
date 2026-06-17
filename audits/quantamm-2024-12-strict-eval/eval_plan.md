# QuantAMM 2024-12 — Strict Full-Audit Eval Plan

## Eval identity
- **Eval name:** QuantAMM 2024-12 Strict Full-Audit Eval
- **Workspace:** `audits/quantamm-2024-12-strict-eval/`
- **Target repository:** `github.com/Cyfrin/2024-12-quantamm`
- **Pinned commit:** `a775db4273eb36e7b4536c5b60207c9f17541b92`
- **Platform / contest:** CodeHawks `2024-12-quantamm`
- **Start timestamp (UTC):** 2026-05-31T04:52:17Z
- **Active audit switched at:** 2026-05-31T04:52:08Z

## Answer key — POST-FREEZE ONLY
- URL (do NOT open until after freeze): `https://codehawks.cyfrin.io/c/2024-12-quantamm/submissions?filterSelectedForReport=...&filterValidated=...&search=`
- **Decision (with user):** offline run — reuse the already-on-disk normalized answer key at
  `audits/quantamm-2024-12-eval/output/answer_key/normalized_answer_key.json` in Phase 7. The live
  URL will NOT be fetched. The answer key will NOT be read during Phases 0–6.

## Audit-Watch system state
- **Git commit:** N/A — the Audit-Watch repo is **not under version control** (`git rev-parse` fails;
  parent dirs are not repos either).
- **File-state fingerprint** (sha256 of `sha256sum` over `scripts/ config/ run_pipeline.sh`, recorded
  at eval start): `2046b3a9a871e102113b5606e1fe95ab090a62cfb2ce1e797b0662b95d0d0ae6`
- **runtime_policy:** `api_free = true` (in-session skills only; no Anthropic API calls)
- **API-free status:** preserved for the entire eval. No external APIs at any phase.

## Strict full-audit configuration
- **Environment:** `AUDITWATCH_FULL_AUDIT=1` exported for every pipeline stage.
- **`config/agent_policy.json → coverage_policy` (verified active at eval start):**
  - `require_dependency_clear_metadata: true`
  - `dependency_clear_strict: false`
  - `dependency_clear_strict_full_audit: true`
  - `mode: full_enumeration_first`, `require_minimal_pass_for_all_in_scope_items: true`
  - `deep_pass_attack_surface_score_min: 3`, `high_score_strong_clear: true`, `high_score_threshold: 3`
- **`active_mode: deep`** (full specialist pass; PoC for all High/Critical — PoCs not required for eval).
- **Effective dependency-clear rule** (from `scripts/coverage_sweep_write.py` /
  `scripts/deep_pass_write.py`): with `AUDITWATCH_FULL_AUDIT=1`, `dep_strict` evaluates true, so a
  blocking dependency-based clear is downgraded to `assigned/deep` with
  `assigned_agent="dependency_review"` and `dependency_review_required=true` instead of clearing.

## Core dependency-clear rule
A clear may NOT rely on a downstream guard, estimator, oracle, math rule, invariant, lifecycle check,
or access-control dependency unless that dependency is itself finding-linked, deeply reviewed, strongly
cleared with evidence, or explicitly out of scope. Forbidden unsupported clears (e.g. "safe because
guarded downstream", "bounded by MathGuard", "validated by `_guardQuantAMMWeights`", "handled by
estimator", "oracle prevents this", "lifecycle prevents this") route to `needs_deep_pass` /
`dependency_review`.

## Pacing
Execute Phases 0–6, then PAUSE and report at the freeze boundary. Phases 7–13 (answer-key access and
scoring) resume only on explicit user go.

## Hard rules
No answer-key access before freeze · no mutation of frozen artifacts after freeze · no new features
mid-eval (stop on hard tooling crash) · no prompt/lens/gate tuning to improve score · no answer-key
knowledge editing findings · no external APIs / preserve api-free · no submissions · PoCs not required
for scoring.

## Prior QuantAMM baseline (for Phase 9 delta)
3 HIT · 4 PARTIAL · 1 ADJACENT · 36 MISS · 0 FP · useful detection 7/44 · any-touch 8/44.
