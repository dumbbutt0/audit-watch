# Phase 92 — Deep-pass depth-trace v3 (localized-mechanism concrete tracing)

Repairs the recurring **conversion-depth** miss (P90-B's dominant `deep_pass` fix-owner bucket) after a
suspicious mechanism has already been localized. No fresh blind eval; no machinery change; the severity gate
stays frozen at `193abf9f`.

## Why
P91 was a SAFETY-ONLY PASS: discipline held (0 severity FP), but conversion was 0. The near-miss was **M-02** —
the system *localized* the calldata index/length mechanism and flagged `NEEDS_CONTEXT`, but never traced
`length = endIndex - startIndex` (missing `+1`) to its concrete revert (a checked param that fills all its
bytes slices one byte short → hash mismatch → the whitelisted call reverts). The gap: after localization, the
deep pass stopped at a generic abstain instead of tracing the arithmetic to a concrete pass/revert.

## What shipped (all add-only; v1/v2 prompts intact)
- **`prompts/deep_pass_depth_trace_v3.md`** — composes on v2. After v2 §1/§2 localize a mechanism, v3 mandates a
  5-step concrete trace (**Inputs → State-before → Operation → State-after → Concrete-outcome**) before any
  `NEEDS_CONTEXT`/harmless/Low conclusion, with the structured output schema and the target miss classes.
- **`scripts/investigation/localized_depth_trace.py`** — advisory, un-wired `evaluate(trace)` that validates
  trace completeness and recommends a verdict, downgrading to **`INSUFFICIENT_TRACE`** when the trace was not
  actually performed. Mirrors the P90-C `maximal_consequence_check` pattern. Never sets severity, never calls
  or changes `severity_impact_gate`, never converts a REJECT into a finding, never routes.
- **`config/localized_depth_trace.json`** — required trace fields, the NEEDS_CONTEXT gating rule, target miss
  classes.
- **`tests/investigation/test_localized_depth_trace.py`** — 15 tests (7 anchors + gating).
- this doc.

## When `NEEDS_CONTEXT` is allowed (the core fix)
`NEEDS_CONTEXT` is honored **only** if the trace reached a *specific* unknown external dependency/fixture/
runtime value AND all of `{named_dependency, missing_value, next_step}` are filled AND
`operation_trace`+`boundary_cases` were actually attempted. Otherwise the check returns `INSUFFICIENT_TRACE`
("trace the operation, or name the specific missing dependency + next step"). A bare "needs more context" is
rejected. Likewise a `REJECT` (harmless/bounded/Low) is honored **only** with a boundary-case + state-after
trace — a generic "looks standard" is rejected.

**Reject-first is preserved, not weakened:** a *traced* bounded/self-correcting outcome is still a valid
`REJECT` — anchor 6 (P85 `updateTaxRate`: eventual self-correction, no concrete consequence) is honored, and
the depth check never forces a positive verdict.

## Regression anchors (all pass)
| Anchor | Trace | Verdict |
|---|---|---|
| P91 M-02 calldata `endIndex-startIndex` | full-width param → slice short → revert | **PASS** |
| P91 M-02 bare abstain | no named dependency | **INSUFFICIENT_TRACE** |
| P89 H-05 public index mutation | corrupt index → later sell reverts | **PASS** |
| P89 M-07 sell-lock reset | third-party action, involuntary distinguished | **PASS** |
| P87 H-01 counter-scope | global `_tokenIds` vs per-gen → brick | **PASS** |
| P85 H-05 dirty flag | never reset → permanent reward loss | **PASS** |
| P85 updateTaxRate | bounded, self-corrects, no concrete | **REJECT (honored)** |
| P81e H-01 fee-routing | `collect(max)` → order-dependent loss | **PASS** |
| generic harmless / incomplete / missing-next-step | — | **INSUFFICIENT_TRACE** |

## Integrity
- `severity_impact_gate.py` **unchanged** (`193abf9f`); deep_pass / hygiene / lens / funnel / handoff_generator /
  maximal_consequence_check byte-identical (the new module is additive).
- No frozen-artifact mutation; no historical re-score; no production wiring (`localized_depth_trace` un-wired).

## Next
P93 = fresh sealed-key blind run using the P91 selection policy + the v3 depth trace, ideally on a
higher-density subject with findings in low-scoring contracts, to test whether conversion improves while holding
0 severity FP.
