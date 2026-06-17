# P283 — IMPLEMENTATION_NOTES

## Files changed (allow-list only)
| File | Change |
|---|---|
| `scripts/research/cross_function_value_tracer.py` | NEW — bounded tracer (`build_index`, `trace`, `_resolve`, `_callee_names`, `_has_external_dynamic`, `_body`). |
| `config/research_cross_function_value_tracer.json` | NEW — bounds + call-skip names + trace statuses. |
| `scripts/research/source_span_guard_extractor.py` | `strip_comments()` applied in `detect()`; `_DIV_BEFORE_MUL` now excludes `**` exponent. |
| `scripts/research/completion_evidence_deriver.py` | imports tracer; builds `trace_index`; attaches `enriched["trace_evidence"]` when in-span scan has no anomaly. |
| `scripts/research/poc_readiness_evidence_gate.py` | value-class D3 lift condition also accepts a cross-function `TRACE_FOUND` + anomaly + HIGH/MEDIUM; summary carries `trace_status` / `trace_value_flow_confidence`. |

## Resolution policy (`_resolve`)
Prefer a same-contract match; else a **unique** match anywhere (library/inherited); else `None` (ambiguous or absent →
fail-closed). This keeps resolution deterministic and conservative — we never guess between two same-named callees.

## Comment-stripping (correctness requirement)
`strip_comments()` removes `// line` and `/* block */` comments before ANY guard/state/value/anomaly detection. The
pre-plan scan flagged 4 "div-before-mul" callees in SiloVault/PanopticPool that were ALL comments (math notes like
`// T * (C - L) = G`). Without stripping these become false MEDIUM anomalies → false READY. Stripping only removes false
flags; P282's div-before-mul on real code is unchanged, so P282's 0-lift result and tests are unaffected.

## `**` exponent exclusion (correctness; found during the P283 audit)
The original `_DIV_BEFORE_MUL = /[^;\n]*\*` matched `/ 2 ** 64` (fixed-point Q64 scaling) because the `*` of `**` looked
like a multiplication. New pattern `/[^;\n]*(?<!\*)\*(?!\*)` requires the final `*` to be a *real* multiplication, not
part of `**`. Effect on the remap: PanopticPool `_burnOptions` (which had passed the value-flow gate on the false
`_getPremia /2**64` anomaly and landed at NEEDS_MORE_EVIDENCE) correctly fell back to NEEDS_VALUE_FLOW_EVIDENCE — a
**precision gain of 1**, not a lift. Like comment-stripping, this can only remove false flags.

## Back-compat
The tracer/comment-strip/exponent-exclusion change outcomes only when a real (non-comment, non-exponent) cross-function
anomaly is present. Synthetic P279–P282 fixtures have no such case, so all 72 prior tests stay green. The deriver
attaches `trace_evidence` only when the in-span scan found NO anomaly and a real `item` is present, so prior gate
behavior (D1 guard precedence, declaration-only, in-span anomaly) is untouched.

## No hash-pin cascade
No test pins the extractor/deriver/gate or their configs. FROZEN modules (P260/P262/P264/P267/P269/P271/P273 router
code+config) and the forbidden 5 are byte-identical (asserted in test_p283 + verification).
