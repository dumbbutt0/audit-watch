# P265 — OPERATOR_USEFULNESS (metrics #2 and #7)

These are **proxies**, applied via a transparent deterministic rubric (in `p265_aggregate.py`) so the numbers are
reproducible — NOT a human time-and-motion study. They estimate operator burden/value; they do not measure it live.

## Rubric — "worth human review" (metric #2)
A candidate is counted worth-review iff ALL three hold:
1. **recall-delta** — forced beyond the narrow top-5 (P260 rank ≥5 or null). (A narrow-baseline lead is "already
   obvious"; it adds nothing the old path wouldn't surface.)
2. **award-class-fit template family** — carries T1/T2/T5/T7/T8 (external-dep DoS / redemption coupling / liveness /
   solvency / share-price-inflation) — the families that actually carried awards across P254–P263.
3. **checkpoint evidence-marker hit** — `checkpoint_hit_evidence_marker` in its inclusion reasons (a real
   accounting/state checkpoint signal, not merely a name-keyword match).

## Minutes per useful lead (metric #7)
`(#candidates × 4 min triage each) ÷ #worth-review`. 4 min/candidate = read the ≤5 mechanism hypotheses + the
falsification questions per advisory candidate (the harness hands these over ready-formed).

## Results
- **#2 pooled: 33.3%** (72/216) worth review. Per contest 0% (basin) → 67% (ethos).
- **#7 pooled: 12.0 min** per useful lead.
- **Spread is informative:** subtle-accounting-rich targets score high-value/low-burden (ethos 67%/6.0min,
  sentiment 63%/6.4, notional 56%/7.1, concrete 50%/8.0, astaria 50%/8.0). Math/typo-class targets score
  low (basin 0% — its awards are T9 mechanical bugs the base read already births, which the rubric correctly
  discounts as not-worth-extra-review). Cross-liquidation-heavy targets sit mid (reserve 9%/46min, bakerfi 12%/34min).
- **benddao (clean anchor): 24% worth / 17 min/lead** — 4 of 17 advisory candidates are recall-delta subtle-family
  evidence-marked leads; among them the yield-staking loci that carry the awarded Highs.

## Honest reading
- As a **shadow recall engine** the burden is manageable: ~16 candidates/audit, ~1/3 genuinely worth a look,
  ~12 min to surface a useful subtle-family lead, and the harness pre-writes the mechanism questions. An operator
  can run it alongside a normal audit without it dominating attention.
- The proxy is generous in one direction (it counts a lead "useful" on structure, not on whether it *converts* to
  an awarded mechanism — and P254–P263 show conversion is partial). So #2/#7 measure *triage-worthy recall*, not
  *recovery yield*. Recovery yield (exact-mechanism #5) is benddao=0 exact / 1 family-level → the real bound.
