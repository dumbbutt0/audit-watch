# Swan / Dria 2024-10 — Strict Full-Audit Eval Plan

## Eval identity
- **Eval name:** Swan / Dria 2024-10 Strict Full-Audit Eval
- **Workspace:** `audits/swan-dria-2024-10-strict-eval/`
- **Target repository:** `github.com/Cyfrin/2024-10-swan-dria`
- **Pinned commit:** `c8686b199daadcef3161980022e12b66a5304f8e` (HEAD resolved via `git ls-remote`;
  confirmed against contest scope in Phase 1/2)
- **Platform / contest:** CodeHawks `2024-10-swan-dria`
- **Start timestamp (UTC):** 2026-05-31T15:02:50Z
- **Active audit switched at:** 2026-05-31T15:02:37Z
- **Purpose:** Fresh blind generalization eval — does the mature Audit-Watch pipeline transfer to a new
  AI-agent-marketplace / LLM-oracle-coordinator protocol (beyond Beanstalk / Zaros / QuantAMM)?

## Answer key — POST-FREEZE ONLY
- URL (do NOT open until after freeze): `https://codehawks.cyfrin.io/c/2024-10-swan-dria`
- **Decision (with user):** the answer key is fetched via **WebFetch** of the CodeHawks contest page
  **after** the Phase 5 freeze manifest is written. It will NOT be read or inferred during Phases 0–6.
- No selected/validated submission material is accessed before freeze.

## Audit-Watch system state
- **Git commit:** N/A — the Audit-Watch repo is **not under version control** (`git rev-parse` fails).
- **File-state fingerprint** (sha256 over `sha256sum` of `scripts/ config/ run_pipeline.sh`, recorded
  at eval start): `a62cb70c860bd14ec5bffb310516f11ff60fa2017093cf6c7bdf4a633813453d`
  (stored in `output/_system_fingerprint.txt`).
- **runtime_policy:** `api_free = true` (in-session skills only; no Anthropic API calls).
- **API-free status:** preserved for the entire eval. No external Anthropic API at any phase. The only
  network use is the target `git clone` (target source, not answer key) and the post-freeze WebFetch
  of the answer key.

## Strict full-audit configuration
- **Environment:** `AUDITWATCH_FULL_AUDIT=1` exported for every pipeline stage.
- **`config/agent_policy.json → coverage_policy` (verified active at eval start):**
  - `require_dependency_clear_metadata: true`
  - `dependency_clear_strict: false`
  - `dependency_clear_strict_full_audit: true`  ← activated by `AUDITWATCH_FULL_AUDIT=1`
  - `require_math_estimator_proof: true`
  - `math_estimator_strict: false`
  - `math_estimator_strict_full_audit: true`  ← activated by `AUDITWATCH_FULL_AUDIT=1`
  - `mode: full_enumeration_first`, `require_minimal_pass_for_all_in_scope_items: true`
  - `deep_pass_attack_surface_score_min: 3`, `high_score_strong_clear: true`, `high_score_threshold: 3`
  - `review_gate_blocks_{unassigned,unexamined,unevidenced_clears}: true`
  - `allow_examined_without_disposition: false`
- **`active_mode: deep`** (full specialist pass). PoCs available but **not required for eval scoring**.
- **`multi_pass`:** enabled, passes_high=3, passes_critical=5, confirmation_threshold=0.6.
- **Effective routing** (`scripts/coverage_sweep_write.py` / `scripts/deep_pass_write.py`): with
  `AUDITWATCH_FULL_AUDIT=1`, `dep_strict` and `math_strict` evaluate true, so a blocking
  dependency-based clear or proofless math-estimator clear is downgraded to `assigned/deep` with
  `assigned_agent="dependency_review"` / `"math_estimator_review"` instead of clearing.

## Core dependency-clear rule
A clear may NOT rely on a downstream guard, estimator, oracle, math rule, invariant, lifecycle check,
or access-control dependency unless that dependency is itself finding-linked, deeply reviewed, strongly
cleared with evidence, or explicitly out of scope. Forbidden unsupported clears (e.g. "safe because
guarded downstream", "validated later", "oracle prevents this", "consensus handles it", "lifecycle
prevents this", "only phase logic", "handled by scoring function") route to `needs_deep_pass` /
`dependency_review`.

## Core math-estimator proof rule
A math-heavy scoring / variance / consensus / nonce / proof-of-work / fee / ranking / selection
function may NOT be cleared merely because NatSpec matches code. A strong clear requires: intended
formula · implemented formula · input domain · output domain · scaling/precision · rounding ·
signedness · bounds/guards · edge cases · independent re-derivation · evidence spans. Absent
independent re-derivation → route to `needs_deep_pass` / `math_estimator_review`.

## Swan/Dria mandatory high-attention surfaces (Phase 4)
Marketplace/listing · Oracle/LLM coordinator · Consensus/validator · Nonce/PoW · Phase/lifecycle ·
Fees/accounting. None may be strong-cleared by pointing to an unreviewed dependency or NatSpec=code
agreement; each must be covered by a finding or an evidence-anchored deep clear.

## Pacing
Execute Phases 0–6, then **PAUSE and report at the freeze boundary**. Phases 7–12 (answer-key access
and scoring) resume only on explicit user go.

## Hard rules
No answer-key access before freeze · no submission inspection before freeze · no mutation of frozen
artifacts after freeze · no new features/lenses/prompts/gates mid-eval (stop on hard tooling crash) ·
no score-chasing tuning · no answer-key knowledge editing findings · no external Anthropic API /
preserve api-free · no submissions · PoCs not required for scoring.

## Prior baselines (context for Phase 9)
- QuantAMM strict full-audit: 17 HIT · 7 PARTIAL · 5 ADJACENT · 15 MISS · 0 FP · useful 24/44.
- This is the first Swan/Dria run; no prior Swan/Dria baseline exists.
