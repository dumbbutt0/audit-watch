# P273 — BACKTEST_RESULTS

Router run per contest (each = one candidate set; coverage budget per-run). Fixtures
(`outputs/p273_backtest_fixtures.json`) carry source-derivable signal text; award labels (the `_awarded_class` notes)
score outcomes only — never fed to the router. Per-contest outputs `outputs/_out_<contest>.json`. Guard PASS, 0
violations on every run.

| contest | selected_classes | awarded-class candidate routed? | classification |
|---|---|---|---|
| **init** (P272) | ORDER_VALIDATION · ACCOUNTING · FRONT_RUNNING_MEV | **YES** — `init_fillorder` (ORDER_VALIDATION) + `init_callback` (FRONT_RUNNING_MEV) SELECTED | **ROUTED_AWARDED_CLASS** (the P272 monoculture broken) |
| **wise** (P270) | ACCOUNTING · SHARE_ROUNDING | YES — `wise_baddebt` + `wise_liq` SELECT_HEAVY | ROUTED_AWARDED_CLASS (accounting preserved) |
| **karak** (P268) | STATE_MACHINE_LIFECYCLE · SHARE_ROUNDING | YES — `karak_slashing` + `karak_snapshot` SELECT_HEAVY | ROUTED_AWARDED_CLASS/LOCUS (slashing/snapshot) |
| **phi** (P266) | DOS_LIVENESS · REWARDS_CLAIMS | YES — `phi_gasdos` (DOS_LIVENESS) SELECTED, not only the skim | ROUTED_AWARDED_CLASS (DoS/liveness) |
| **benddao** (P263) | ACCOUNTING · DOS_LIVENESS | YES — `bd_yield` (DOS_LIVENESS) SELECTED | ROUTED_AWARDED_CLASS (yield/liveness) |
| **negctrl** | ACCOUNTING · SHARE_ROUNDING | n/a | **NEGATIVE_CONTROL_PASSED** — `nc_gated_admin` (ACCESS_CONTROL signal=5, the HIGHEST) → **COVERAGE_DEFER_LOW_SIGNAL** (impact_supported=false → anti-drama blocked it); did NOT monopolize/route on label |

## The headline (the P272 fix)
**init: the order/access/front-running award class is now routed** — `init_fillorder` (ORDER_VALIDATION) and
`init_callback` (FRONT_RUNNING_MEV) are SELECTED alongside accounting, instead of P272's 3-accounting monoculture. The
anti-monoculture rule forced cross-class representation.

## Success criteria (all met)
- Init order/access/front-running/DoS class routed → ✅.
- ≥2 prior awarded-class cases preserved → ✅ (Wise accounting, Karak slashing/snapshot, Phi DoS, BendDAO yield — 4).
- Accounting class NOT degraded/suppressed → ✅ (Wise + BendDAO accounting routed; init accounting still repped).
- Negative controls acceptable → ✅ (the highest-signal access-control candidate was NOT routed because
  `impact_supported=false`; anti-drama held — no gated-admin monoculture).
- Advisory guard 0 violations · malformed/missing input → exit 2 (verified).

## Honest limits
- Karak "slashing" classified as STATE_MACHINE_LIFECYCLE (via snapshot/status/transition keywords; "slash" isn't a
  keyword) — the candidate is correctly routed, but the class *label* is approximate (the awarded subsystem is routed,
  which is the coverage goal).
- "Routed" = the awarded CLASS gets a representative into the P269 handoff — not that the exact awarded mechanism is
  recovered (that's downstream completion/PoC). Coverage fixes the objective-mismatch routing, not recovery itself.
- Signals are operator/heuristic-assigned; a mis-signalled candidate misclassifies. Backtest necessary-not-sufficient
  (hand-encoded from frozen reveals); the real proof is a fresh full-path run (P274).
