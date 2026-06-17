# P273 — VERDICT

## Bottleneck addressed: AWARD_CLASS_TARGET_FIT (the P272 objective mismatch)
## Verdict: A — COVERAGE_ROUTER_READY_FOR_FRESH_FULL_PATH_TEST

### Why
P273 built a narrow, default-off, advisory award-class coverage router that repairs the P272 mismatch (impact-first
triage monopolizing the lending-accounting class and missing init's order/access/front-run/DoS awards). All A-criteria
are met on backtest (award labels used only to score, never to drive routing):
- **Init awarded class routed:** `init_fillorder` (ORDER_VALIDATION) + `init_callback` (FRONT_RUNNING_MEV) are
  SELECTED alongside accounting — the P272 3-accounting monoculture is broken by the anti-monoculture rule.
- **≥2 prior awarded-class cases preserved:** Wise (accounting), Karak (slashing/snapshot), Phi (DoS/liveness),
  BendDAO (yield/liveness) — 4 preserved.
- **Accounting NOT degraded:** Wise + BendDAO accounting routed; init accounting still represented.
- **Negative controls acceptable:** the highest-signal access-control candidate (`nc_gated_admin`, signal=5) was NOT
  routed because `impact_supported=false` — the anti-drama gate held; no gated-admin monoculture.
- **Advisory guard 0 violations**; malformed/missing input fails closed (exit 2). **P260/P262/P264/P267/P269 + P271
  checklist + 5 forbidden byte-identical.** Tests green.

### Honest bounds (no over-claim)
- **Coverage ≠ recovery.** Routing the awarded class into the P269 handoff is not the same as recovering the exact
  awarded mechanism — that's downstream (P274). P273 fixes the *objective-mismatch routing*, the specific P272 gap.
- Class assignment is heuristic (keyword signals); Karak "slashing" classed as STATE_MACHINE (approximate label, but
  the candidate is routed). Backtest is necessary-not-sufficient (hand-encoded; the blind proof is P274).
- Recall depth is upstream/unchanged: P273 routes classes whose candidates recall surfaced; the exact-locus recall
  miss (updateOrder/fillOrder) is a separate gap.

### Not B / C / D
- Not **B** (PROMISING_NEEDS_REFINEMENT): the core requirement — route Init's awarded order/access class while
  preserving the prior accounting/slashing/DoS classes and not degrading negative controls — is fully met.
- Not **C** (NOT_USEFUL): it demonstrably breaks the P272 accounting monoculture and routes the awarded class.
- Not **D** (ABORTED): research-only, advisory, un-wired, 0 production edits, frozen + forbidden byte-identical,
  active audit unchanged.

### The arc
P272 = objective mismatch (impact-first over-weighted accounting, missed order/access awards). **P273 = an award-class
coverage layer that guarantees cross-class representation before impact-first ranks within each class** — the
monoculture is broken on backtest across 5 contests + held negative controls. Required next step **P274 = full-path
rerun with the coverage router + impact triage + selector + lending checklist available** (used blind, pre-reveal),
scoring whether the "valid non-awarded bug" mismatch is closed or whether contest-award matching is inherently too
target-dependent for one policy. Production authority remains **withheld**.

### Constraints honored
Research-only / advisory / un-wired. No tuning of any frozen module or the P271 checklist: P260 `d6b494bc` · P262
`a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c` · P269 `63c88d02` byte-identical. 5 forbidden byte-identical. Active
audit `size-credit-2024-06-blind` unchanged. No answer key in router input; award labels scored outcomes only.
