# P210 — Dark implementation of the L3 HIGH readiness gate (default-off feature flag)

## Context
P209 chose the layered wiring design: enforce L3 only in the human submission-readiness overlay
(`submission_readiness_review.py`) + read-only dashboard display, with discovery/`deep_trace`/`min_confirm_gate`/
`confirm_gate`/routing untouched. P210 implements it **behind a default-off flag `AUDITWATCH_L3_READINESS=1`** so
flag-off behavior is output-equivalent to today. Still non-submitting, advisory/readiness-only, human review mandatory.

## Recon done (read-only) — exact integration surface
- `scripts/submission_readiness_review.py` (247 lines, hash `b435a635`): research-only/append-only overlay; never
  flips `submission_ready`/`routing_allowed`. Hook points: `READINESS_STATES` (set), `_facts(candidate_id)`,
  `evaluate(answers, facts)->(eligible,failed[])` (the checklist gate; called by `record_review` for
  `ready_for_submission_package`), `detail_overlay(candidate_id)` (display block). Severity target available via
  `answers["severity_recommendation"]` (q6; `_SEVERITIES`={High,Medium,Low,QA,no_security_impact}).
- `scripts/validate_p208_l3_readiness.py` (hash `7e148e18`): `decide(rec)` is PURE (no side effects; module only sets
  path constants; `__main__`-guarded) → safely importable. Handles missing fields via `.get` → empty record fails
  closed (high_promotion_allowed=false). HUMAN_OVERRIDE without rationale → already blocked by `decide()`.
- `scripts/dashboard.py` (hash `1eb4e278`, ~L398): builds per-finding dict incl. display-only `submission_ready`.
- Tests: `tests/research/test_submission_readiness.py` exists; pytest layout under `tests/`.

## Strict scope
No change to `deep_trace.md` / `min_confirm_gate.py` / `confirm_gate.py` behavior; no routing; no submit; no
auto-promote/demote; no historical-artifact rewrite; no candidate-selection or canonical-severity change; L3 stays
advisory/readiness-only. Flag-off MUST be output-equivalent to pre-P210.

## Implementation (all L3 code paths wrapped in a flag guard)
**`scripts/submission_readiness_review.py`** (the only behavior change; every addition inside `if _l3_enabled():`):
1. `import os` (if absent); `def _l3_enabled(): return os.environ.get("AUDITWATCH_L3_READINESS") in ("1","true","True")`.
   `L3_DIR = ROOT/"output_research/l3_readiness"`.
2. Add `"blocked_by_missing_l3_poc"` to `READINESS_STATES` (+ a `DISPLAY_SUBMISSION_STATUS` entry, e.g. "BLOCKED_L3").
   (Set membership addition is inert default-off; nothing emits it unless flag on.)
3. `_load_l3_record(candidate_id)` → reads `L3_DIR/<id>.json`; missing/parse-error → `None` (fail-closed handled next).
4. `l3_evaluate(l3_record, severity_target)` (PURE, testable): if `severity_target` not in {High, Critical} →
   `{"applies": False}`; else run `decide(l3_record or {})` (lazy `import validate_p208_l3_readiness`), return
   `{applies, high_promotion_allowed, high_promotion_blocker, l3_status, poc_tier, calibrated_severity_after_l3,
   l3_blocker_codes, human_override_required, human_override_reason, l3_evidence_summary, research_only:true,
   routing_allowed:false}`. Empty/None record → fails closed.
5. Add `"candidate_id": candidate_id` to `_facts()` return (inert default-off).
6. In `evaluate()`: after existing checks, `if _l3_enabled():` compute target from `answers["severity_recommendation"]`;
   if High/Critical and L3 not allowed → `failed.append("blocked_by_missing_l3_poc: <blocker>")`. Flag-off: untouched.
7. In `detail_overlay()`: `if _l3_enabled():` add `out["l3"] = l3_evaluate(_load_l3_record(id), target)`. Flag-off: untouched.

**`scripts/dashboard.py`**: `if os.environ.get("AUDITWATCH_L3_READINESS"):` add a read-only `"l3"` field per finding
(threat ceiling, l3_status, high_promotion_allowed, blocker, poc_path/command, human_override status) via the helper.
No submit/promote/demote controls. Flag-off: byte-identical.

## Deliverables (under `documentation/research/assisted_mode/p210_l3_dark_wiring/`)
`P210_PLAN.md` · `INTEGRITY_PRECHECK.md` · `IMPLEMENTATION_NOTES.md` · `FEATURE_FLAG_BEHAVIOR.md` ·
`SUBMISSION_READINESS_INTEGRATION.md` · `DASHBOARD_READONLY_PANEL.md` · `TEST_FIXTURES.md` · `TEST_RESULTS.md` ·
`BACKTEST_RESULTS.md` · `NO_SUBMIT_GUARD.md` · `P210_RECOMMENDATION.md` · `metrics.json` · `integrity_checks.md`.
Code: edits to `submission_readiness_review.py` + `dashboard.py`; new `tests/research/test_l3_readiness.py`;
fixtures under the p210 dir (reuse P208 backtest/regression records + 2 new human-override cases).

## Tests / fixtures
Fixtures (L3 records): decent H-01 (High+PASS→clear), vultisig H-01 (High+PASS→clear), decent M-03 & vultisig M-03
(High-ceiling+FAIL→blocked), static-High-no-PoC→blocked_by_missing_l3_poc, malformed/empty on High→fail-closed,
Medium-without-L3→not blocked, human-override+reason→allowed+marked, human-override-without-reason→blocked.
Run: existing `test_submission_readiness.py` (flag-off regression must stay green) + new `test_l3_readiness.py`
(flag-on fixtures) + a parity test (decide() over P208 fixtures == P208 expected) + no-submit guard test (L3 paths
never set submission_ready/routing_allowed true, never import/call a router/submit fn) + flag-off equivalence test
(evaluate()/detail_overlay() identical with flag unset; no `l3` key, no new blocker).

## Backtest
Re-run `python scripts/validate_p208_l3_readiness.py backtest` (10/10, 0 false-allow/0 false-block) AND the same 10
records through `l3_evaluate()` (flag-on) → identical allow/block; 0 dashboard mismatches; 0 submission/routing side
effects.

## Decision space
`L3_DARK_WIRING_READY` (flag default-off & flag-off output-equivalent; flag-on blocks High-without-L3 only; Medium
unaffected; malformed-High fail-closed; override-needs-reason; no min_confirm/confirm_gate/deep_trace/routing change;
no submit side effects; all tests + backtest green; production prompt/gate/ledger hashes byte-identical START==END) ·
`L3_DARK_WIRING_PARTIAL` · `L3_DARK_WIRING_FAILED_REGRESSION` · `L3_DARK_WIRING_BLOCKED` · `INVALID_RUN`.
**Expected:** `L3_DARK_WIRING_READY`.

## Acceptance criteria
Flag default-off; flag-off unchanged; L3 affects only High/Critical submission readiness; Medium unaffected; no
discovery/min_confirm/confirm_gate change; no submit/route/promote side effects; dashboard read-only; P204/P207/P208
fixtures classify correctly; malformed-High fails closed; human override requires written reason; `deep_trace.md`
`ef93a6c2`/`validate_deep_pass_mechanisms.py` `5d2a97f9`/`eval_locus_resolver.py` `3b0b2c02`/`min_confirm_gate.py`
`41dd3c96`/`confirm_gate.py` `4fadfc5f`/ledger `fc446040` byte-identical START==END; `submission_readiness_review.py`
+ `dashboard.py` change (recorded START→END); JSON valid; `api_free=true` unchanged.

## Verification
`AUDITWATCH_L3_READINESS` unset → `pytest tests/research/test_submission_readiness.py` green + `detail_overlay`/
`evaluate` outputs identical to pre-change (no `l3` key/blocker). Flag set → `pytest tests/research/test_l3_readiness.py`
green; High+no-L3 → `blocked_by_missing_l3_poc`; High+PASS → clears; Medium → unaffected; malformed-High → blocked;
override-no-reason → blocked. P208 backtest 10/10. No-submit guard test green. Production gate/prompt/ledger hashes
unchanged at END.

## Follow-on (NOT this phase)
Enabling the flag in a real audit + cost model for L2/L3 harness authoring (auto-scaffold vs human) = a later human
decision. Deep-pass recall + oracle track remain separate.
