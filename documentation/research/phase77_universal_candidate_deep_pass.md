# Phase 77 — Universal Candidate Deep-Pass v1

**Result: PASS.** Built a detector-family-agnostic investigation scaffold that turns static leads into disciplined
**investigation bundles**, never findings. A normalized `STATIC_LEAD` is walked through context → defenses → exploit path →
impact → source-falsification, and the forbidden shortcut `STATIC_LEAD → finding` is **structurally impossible** (every
progression is validated; every promotion terminal is reachable only from `SOURCE_FALSIFIED`). Research-only, REVIEW_ONLY,
**un-wired**. Parked detectors + value-flow byte-identical; 104 regression tests green.

## Objective
Re-center the project on a **lead→finding engine**: detectors/lenses generate candidate pressure (high recall at the lead
layer); the promotion layer is extremely strict (near-zero false-positive promotion). P77 builds the universal deep-pass
that enforces: static lead → context map → defense map → exploit reasoning → impact → source falsification → only then
POC_REQUIRED or READY_FOR_HUMAN_REVIEW.

## Changed / new files
| file | hash |
|---|---|
| `scripts/investigation/__init__.py` | (pkg) |
| `scripts/investigation/lead_schema.py` | `3c57f04e2f8b6332` |
| `scripts/investigation/transitions.py` | `2c00069cb49362e3` |
| `scripts/investigation/deep_pass.py` | `57c29fff73803fbc` |
| `tests/investigation/test_universal_deep_pass.py` | new (9 tests) |
| `documentation/research/_p77/<candidate>/bundle.json` ×10 + `_p77/eval_summary.json` | eval batch |
No production/value-flow/parked-detector code changed.

## Hashes before/after (unchanged frozen artifacts)
missing-auth `f9ec0bff8de53cf0` · wrong-actor `2337edc2ded25116` · signature-replay `e72b9994100d35e7` · value-flow
`697e72a7`/`5522e15f`/`aca9125a` — all **byte-identical** before and after.

## Architecture (reuses existing infrastructure)
- **State machine** (`transitions.py`): `STATIC_LEAD → CONTEXT_MAPPED → DEFENSE_TRACED → EXPLOIT_PATH_ATTEMPTED →
  IMPACT_CHECKED → SOURCE_FALSIFIED → {REJECTED|NEEDS_CONTEXT|POC_REQUIRED|READY_FOR_HUMAN_REVIEW}`. `assert_transition`
  permits only the next step or an allowed terminal off-ramp; **promotion terminals (POC_REQUIRED / READY_FOR_HUMAN_REVIEW)
  are reachable only from `SOURCE_FALSIFIED`** → every shortcut raises `ForbiddenTransition`. Forbidden promotion labels are
  rejected by `assert_no_forbidden_label`.
- **Normalizer** (`lead_schema.py`): mixed detector/lens output → one `STATIC_LEAD` (missing fields → null/unknown; no
  detector rewrite). **Refuses routed sources** (`routes_in_production`/`routed_manifest_ids`) — reusing the
  `normalize_research_findings.py` discipline.
- **Deep-pass runner** (`deep_pass.py`): deterministic, reject-first at every stage over an evidence dict (filled by an
  in-session agent / the existing `scripts/candidates/` gates in real use; by fixtures in tests). Emits the full
  investigation bundle (`defense_ledger` 16 fields × 6 classifications · `exploit_path` · `source_falsification` 10 checks
  · `final_decision`). `POC_REQUIRED` = local PoC-task permission only; `READY_FOR_HUMAN_REVIEW` = bundle ready for a human
  to review (not a submission verdict). Reuses the blueprint lifecycle (`candidate_validation_to_poc_blueprint.md`) and the
  defense-classification vocab from `gates/defense_map_gate.py`.

## Reject-first / source-falsification discipline (the value)
- DEFENSE_TRACED: any defense `blocks_candidate` → REJECTED (source-backed); any **critical** defense `unknown`/
  `source_unavailable` → NEEDS_CONTEXT (cannot promote with an unknown critical defense).
- EXPLOIT_PATH_ATTEMPTED: a written `rejection_case` is required first; no attacker sequence or no broken invariant →
  REJECTED.
- IMPACT_CHECKED: no measurable impact → REJECTED.
- SOURCE_FALSIFIED: any of 10 falsifiers True (reachability, caller-authorized, state-immutable, missing-check-in-helper,
  later-invariant-covers, intentional-by-design, hash-bound-to-mutable-state, name-confusion, out-of-scope-source,
  economically-meaningless) → REJECTED with the falsifying evidence. Only candidates that **survive** falsification with
  complete evidence reach a promotion terminal.

## Tests (9 passed) + self-test (OK)
1 missing-AC but reachable modifier → REJECTED · 2 missing-nonce but state-bound hash → REJECTED · 3 value-flow, no
blocking defense, no PoC → POC_REQUIRED · 4 multicall, final invariant covers → REJECTED · 5 missing source → NEEDS_CONTEXT
· 6 strong candidate (reachability+invariant+impact+defense ledger+falsification pass) → READY_FOR_HUMAN_REVIEW · 7 force
STATIC_LEAD→READY/POC/CONTEXT→READY → ForbiddenTransition · 8 unknown critical defense → NEEDS_CONTEXT · 9 no-wiring +
forbidden-labels-absent + routed-source refused.

## Eval batch result table (`_p77/`)
| candidate | family | decision | why |
|---|---|---|---|
| FP-AC-modifier | missing_auth | **REJECTED** | `access_control` blocks (reachable modifier) |
| FP-nonce-statebound (AI Arena claimFighters) | signature_replay | **REJECTED** | source-falsified: hash bound to mutable claimed state |
| FP-multicall-finalinv | multicall_invariant | **REJECTED** | `final_invariant_check` blocks (re-checks skipped per-call check) |
| WM-burnDyad (DYAD) | permissionless_position_reduction | **REJECTED** | intentional-by-design + economically meaningless |
| WM-deployRentalSafe (reNFT) | permissionless_factory_deploy | **REJECTED** | intentional factory self-register |
| WM-olas-checkpoint (Olas) | permissionless_state_advance | **REJECTED** | permissionless-by-design epoch advance |
| ANCHOR-phi-AC-A1 | missing_auth | **POC_REQUIRED** | survives falsification; concrete path; PoC required |
| ANCHOR-valueflow | value_flow | **READY_FOR_HUMAN_REVIEW** | full evidence + falsification pass; impact source-provable |
| FRESH-1-libgap | signature_replay | **NEEDS_CONTEXT** | critical defense (nonce guard) source-unavailable |
| FRESH-2-leadpoc | value_flow | **POC_REQUIRED** | concrete attacker path; PoC required |

Histogram: **6 REJECTED · 1 NEEDS_CONTEXT · 2 POC_REQUIRED · 1 READY_FOR_HUMAN_REVIEW**. The funnel shape (many leads →
few candidates → very few promoted, 0 false-positive promotions) matches the north star.

## False-positive analysis
All 3 known FP-shapes and all 3 prior-OVERFIT wrong-mechanism candidates were **REJECTED with source-backed reasons**
(defense-blocks or source-falsified). **0 unsupported READY_FOR_HUMAN_REVIEW; 0 direct detector→finding promotions** (the
latter is impossible by construction — promotion terminals are only reachable from `SOURCE_FALSIFIED`).

## Forbidden-transition validation
`assert_transition` raises on STATIC_LEAD→POC_REQUIRED, STATIC_LEAD→READY_FOR_HUMAN_REVIEW, CONTEXT_MAPPED→READY, and any
skip; tests 7 confirm. Forbidden promotion labels are blocked by `assert_no_forbidden_label` (test 9).

## Regression
`tests/investigation` 9 · `tests/signature_replay` 22 · `tests/access_control` 51 · `tests/candidates` 22 → **104 passed**.
Parked detectors + value-flow byte-identical. No-wiring CLEAN.

## Promotion decision
**No promotion.** P77 validated only that static leads can be converted into disciplined investigation bundles with
0 false-positive promotion. The deep-pass is research-only and un-wired.

## Recommended next
P78 eval lens pack (mixed candidate batches: anchors / NCs / wrong-mechanism traps / defense-present traps / fresh leads).
P79 agentic reasoning repair (baseline vs defense-first vs source-falsification agent, scored by the P77 categories
CLEAN_HIT/STRONG_PARTIAL/REJECT_CORRECT/ABSTAIN_CORRECT/WRONG_MECHANISM/SOURCE_FALSE/OVERFIT/HARD_FAIL). P80 PoC handoff
gate. P81 submission-readiness gate. Principle held: **broad at the lead layer, extremely strict at the promotion layer.**

## Reproduce
```
python3 scripts/investigation/deep_pass.py --self-test
~/.local/bin/pytest tests/investigation/ -q                 # 9 passed
# eval bundles + summary: documentation/research/_p77/<candidate>/bundle.json, _p77/eval_summary.json
~/.local/bin/pytest tests/signature_replay/ tests/access_control/ tests/candidates/ -q   # regression
```
