# P178 — Structured Dependency Evidence Capture (production change #3)

## Problem (from P176→P177)
P177 made guarded-downstream precise (prose-only/incomplete → advisory; only complete structured metadata
resolving an in-scope unproven guard hard-routes) — but **almost nothing produced complete structured metadata**,
so the now-precise rule went dormant (P177 replay: 0 precise guarded-downstream blocks on zaros/revert-lend).

## Fix
A deterministic extractor converts clear prose + manifest into RESOLVED structured dependency facts at
clear-time and bridges them onto the legacy fields P177's `classify_clear` already consumes — so a resolved
in-scope unreviewed dependency becomes block-eligible under the **unchanged** P177 rule. RESOLVE-OR-NOTHING:
a candidate becomes structured metadata only if it (1) is identifier-shaped (camelCase / underscore / explicit
`name(` call), (2) is not a generic category word, and (3) resolves to a manifest artifact. Generic prose
("guarded downstream", "protected by invariant", "oracle") resolves to nothing → stays advisory.

| clear prose | extractor | routing (P177, unchanged) |
|---|---|---|
| "guarded downstream" / "protected by invariant" / "the oracle prevents this" | no resolved dependency | advisory |
| "clamped by `_guardQuantAMMWeights`" (in-scope, unreviewed) | resolved → structured-complete | block → deep-pass |
| "validated by `ensureNoNavOps`" (in-scope, reviewed) | resolved → proven | allow |

## Code changed
- New `scripts/dependency_metadata.py`: `extract_dependency_metadata()` (canonical 4 fields + bridged legacy
  fields when resolved; fail-open; reuses `dcu.resolve_dependency_status`/`_bare`/`build_manifest_name_index` +
  `GENERIC_DEP_NAME_TOKENS`) and `validate_dependency_metadata()`.
- New `scripts/validate_dependency_metadata.py`: read-only capture report.
- `scripts/coverage_sweep_write.py` + `scripts/deep_pass_write.py`: before `classify_clear`, auto-capture
  resolved facts into the clear when missing (additive, fail-open) and persist the canonical 4 on the
  disposition. **`dependency_clear_utils.py` routing logic is untouched** — P178 only supplies data.
- `prompts/coverage_sweep.md` + `.claude/skills/coverage-sweep/SKILL.md`: require the canonical 4 fields and
  **reject generic dependency names** (must name a real artifact).
- New tests `tests/coverage/test_dependency_metadata.py`.

## Measurement (read-only — `measure_capture.py`, existing legacy clears)
| corpus | dep-based clears | name/scope/status coverage | structured-complete | prose-only (advisory) | routing preview (P177) |
|---|--:|--:|--:|--:|---|
| zaros | 237 / 471 | 35.0% | 83 | 154 | block 83 · advisory 154 |
| revert-lend | 30 / 102 | 0.0% | 0 | 30 | advisory 30 |

**Interpretation:** on legacy prose-written clears, the extractor recovers **83 genuine in-scope dependency
artifacts** on zaros that were previously dormant prose — reviving guarded-downstream from **0 precise blocks
(P177) → 83 precise, fact-based blocks**, each naming a real in-scope unreviewed artifact (17.6% of all clears,
vs P176's 50% blunt flood at 96% off-target). The 154 generic-prose clears correctly stay advisory.
revert-lend's prose names descriptive concepts, not manifest functions → 0 auto-resolve (only prompt-driven
future clears will populate it).

## Success criteria — status (honest)
- `dependency_name`/`scope`/`status` coverage **>80%** and structured>prose are targets for **newly generated**
  (prompt-driven) clears; **not** met on legacy corpora (35% zaros / 0% revert-lend) because those predate the
  P178 prompt. Validated for the future path via: (a) the strengthened prompt, (b) the synthetic
  prompt-shaped-clear tests (`test_dependency_metadata.py`), (c) the deterministic auto-extraction floor above.
  This limitation was stated and accepted at plan time (can't be proven without a fresh agent run).
- RESOLVE-OR-NOTHING verified: generic/unresolvable prose → advisory (zaros 154, revert-lend 30); only resolved
  real artifacts become structured (zaros 83).

## Boundaries
No new family/selector; F1, math_estimator, severity, submission, readiness, answer keys, corpora untouched.
**Routing semantics unchanged** (`classify_clear`/`dependency_route_decision` not edited in P178). Extractor is
fail-open and never blocks; `fabrication_rate=0` (dependency_evidence = a real manifest source span; routing
only re-surfaces for review). Old dispositions not mutated (measurement read-only).
