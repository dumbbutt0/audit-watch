# P180 — Dependency extractor precision patch (production change #4)

## Problem (from P179)
P179 refuted P178's zaros "revival": all 83 structured guarded-downstream blocks were a **boilerplate artifact**
— 100% `dependency_name=loadLive`, mined from one out-of-scope disposition template whose `guard_or_invariant`
enumerates *"…guards/invariants identified (loadLive/loadExisting existence checks, access modifiers…)"*. The
extractor treated a near-generic storage-load helper, listed in a guard SURVEY, as a real dependency.

## Fix (tightening-only, extractor-only, no routing-semantics change)
`scripts/dependency_metadata.py` only — `dependency_clear_utils.py` (routing) untouched:
1. **Plumbing stoplist** — `loadlive`, `loadexisting`, `getlive`, `getexisting` added to `NAME_STOPLIST` (they
   are storage-load accessors, not guards; never become a `dependency_name`, mined or explicit).
2. **Boilerplate / out-of-scope skip** — `_is_boilerplate_or_survey()` returns True when prose contains a
   boilerplate phrase (`"out of contest"`, `"answer-key eligible"`/`"not answer-key"`, `"allowlist"`,
   `"light pass"`) or the cleared item is a non-logic site (`constructor` / `_authorizeUpgrade*` / `constant`).
3. **Guard-survey skip** — same helper returns True on survey markers (`"guards/invariants identified"`,
   `"guards identified"`, `"invariants identified"`, `"relevant guards"`, `"existence checks"`,
   `"access modifiers"`).
Wired at the top of `extract_dependency_metadata` (inside the fail-open `try`), **gated to prose-mining only**:
`if not disp.get("clear_depends_on") and _is_boilerplate_or_survey(...): return _neg()`. An explicit
`clear_depends_on` (genuine structured auditor input) bypasses the skip and is still honored.

## Validation (read-only replay — `validate_p180.py`, writes only its own JSON; P179 record preserved)
| | BEFORE (P179) | AFTER (P180) |
|---|--:|--:|
| zaros structured guarded-downstream blocks | 83 | **0** |
| `dependency_name=loadLive` concentration | 83 (100%) | **gone** ({}) |
| exact "precision" (common-name coincidences) | 9.6% | n/a (no blocks) |

Regression (asserted): `_guardQuantAMMWeights` still resolves; `ensureNoNavOps` still resolves (unit tests);
explicit `clear_depends_on` still honored; generic prose ("guarded downstream") still advisory.

## Tests
`tests/coverage/test_dependency_metadata.py`: +6 P180 tests (boilerplate→advisory, survey→advisory,
plumbing→advisory, real-guard-still-resolves, ensureNoNavOps-still-resolves, explicit-input-bypass). Dependency
suite 46 pass; full `tests/coverage` **177 passed, 0 failed**.

## Boundaries
Tightening-only (extractor strictly MORE advisory, never more blocking). Guardrail grep: zero
severity/routing_allowed/submission_ready/finding writes. `dependency_clear_utils.py` routing logic byte-
unchanged. No selector / severity / submission / answer-key / corpus / disposition change; no new recovery
claimed. `fabrication_rate=0`. P178 `capture_coverage.json` and P179 `metrics.json`/`precision_by_block.json`
left intact as historical pre-patch records.

## Net result of the P176→P180 arc
P176 diagnosed the instrumentation failure; P177 removed the blunt prose flood (precise routing); P178 added
structured capture (mechanism sound); P179 caught that P178's zaros payoff was a boilerplate artifact; P180
removes the artifact. Guarded-downstream is now: prose-only → advisory, boilerplate/survey/plumbing → advisory,
and only a resolved, real, in-scope, unreviewed artifact (explicit or specifically named) → block. On zaros that
currently yields **0** genuine structured blocks — an honest result: zaros's dependency clears were all
boilerplate, so there is nothing precise to re-surface there. The mechanism is ready for corpora that contain
genuine named-dependency over-clears.
