# P272 — VERDICT

## Bottleneck: AWARD_CLASS_TARGET_FIT (objective mismatch)
## Verdict: D — PROVES_NONAWARDED_TRUE_POSITIVES (objective mismatch / award-class targeting)

### Why
On a fresh BLIND lending target (init-capital) with the full chain + the P271 lending checklist applied pre-reveal:
- **The family→exact bridge GENERALIZED BLIND** — the headline positive. C-incentive (LiqIncentiveCalculator
  min-floor-after-max-cap) was sharpened, pre-reveal, from a recall candidate into an **exact, real-code,
  runtime-proven** mechanism (returned multiplier 3.0e18 > the 1.5e18 protocol cap; control respects the cap). The
  P271 capability is **not Wise-specific.**
- **BUT 0 awarded recovery.** init-capital's 7 awards (3H+4M) are **entirely access-control / order-validation /
  front-running / DoS in the MarginTradingHook ORDER layer** (updateOrder access control, arbitrary tokenOut,
  fillOrder front-run). The impact-first triage + the P271 LENDING checklist target the **bad-debt / liquidation /
  collateral-credit ACCOUNTING class** — so selection pursued lending-accounting loci and the **awarded access-control
  class was de-prioritized**. The one exact recovery (C-incentive) is a **non-awarded** true mechanism (config-reachable
  `min>max`). This is exactly the user's **D**: *real bug discovery ≠ contest-awarded bug matching.*

### Why D and not A / B / C
- Not **A** (exact/strong AWARDED with runtime): the exact recovery is non-awarded; 0 awarded.
- Not **B** (right loci+family, exact partial): the exact recovery is real but on a non-awarded mechanism; the awarded
  loci/class were not the ones routed.
- Not **C** (misses awarded loci → recall/triage regression): recall did partially surface the awarded MarginTradingHook
  subsystem and the chain ran coherently — this is not a recall regression but an **award-class objective mismatch**
  (impact-first/lending-accounting targeting vs an access-control/order-management award set). D names it precisely.
- Not **G**: no safety/contamination trip — 0 severe concluded/reportable FP, no award leak before the Phase-9 freeze,
  frozen modules + 5 forbidden byte-identical, active audit unchanged, contest source unmutated.

### Honest reading (the arc's real state)
The upstream chain is solid: recall + selector + triage route coherently, and **family→exact now works blind**
(C-incentive). The remaining gap is precisely the one the user predicted: **award-class targeting**. The system pursues
high-*impact* accounting classes (bad-debt/liquidation/insolvency — what impact-first triage weights), but contest
awards are not always in those classes (init-capital's were access-control/order-management). Two compounding factors:
(1) target-class fit — init-capital was chosen as a money market expecting lending-accounting awards, but its
(invitational, sparse) awards live in a peripheral order hook, which the content-safe screen cannot detect pre-reveal;
(2) impact-first triage structurally under-weights access-control/validation/front-running (low "value-at-risk
accounting" signal) even though those are common award classes.

### Required next step — P273
Address **award-class targeting / objective alignment**: broaden the impact-first triage (or add an award-class-
coverage lens) so access-control / input-validation / front-running / order-management classes are not structurally
de-prioritized vs accounting-impact classes; and/or improve pre-reveal target award-class fit. Re-run blind on ≥1
fresh target whose award class is known-broad. Production authority remains **withheld** — exact AWARDED recovery is
still unproven blind.

### Constraints honored
Blind (answer key opened only after the full pre-reveal freeze manifest was hashed; no answer-key content drove
candidates/dimensions/completion). No tuning of frozen modules or the P271 checklist during the run: P260 `d6b494bc`
· P262 `a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c` · P269 `63c88d02` byte-identical. 5 forbidden byte-identical.
Active audit `size-credit-2024-06-blind` unchanged. init source isolated in `/tmp`; contest source unmutated; PoCs
under `pocs/p272/`.
