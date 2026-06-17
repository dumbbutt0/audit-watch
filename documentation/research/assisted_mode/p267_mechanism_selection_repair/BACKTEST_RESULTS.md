# P267 — BACKTEST_RESULTS

Run: `mechanism_pairwise_selector.py --pairs outputs/p267_backtest_pairs.json --out outputs/p267_backtest_decisions
.json --md outputs/p267_backtest_report.md`. Guard **PASS** (0 violations). Inputs derived from frozen scored
artifacts (FAILURE_FORENSICS); award labels used only to *score* outcomes, never fed to the selector.

| case | outcome | anti-easy-PoC | gap | awarded preserved? | classification |
|---|---|---|---|---|---|
| **A — P266 Phi H-03** (skim vs gas-DoS) | **KEEP_BOTH** | **YES** | 10 | **YES** | **KEPT_AWARDED_IN_KEEP_BOTH** |
| B — P256 Plaza P-L2 (repeated-fee vs insolvency reconciliation) | KEEP_BOTH | no | 3 | YES | KEPT_AWARDED_IN_KEEP_BOTH |
| C — P256 Plaza P-L1 (basis-asym vs ≤1.2 convexity) | KEEP_BOTH | no | 3 | YES | KEPT_AWARDED_IN_KEEP_BOTH |
| D — P257 Notional N-L2 (tidy Taylor vs messy fee-dodge) | **SELECT_M2** | no | 6 | YES | **SELECTED_AWARDED** |
| E — P255 BakerFi L5 (P&L-gap vs harmless) | SELECT_M1 | (n/a) | 7 | n/a | **INCONCLUSIVE** (awarded fee-omission was NOT enumerated; selector can't recover an un-enumerated mechanism) |
| NC1 — drama-but-refuted | **REFUTE_M1_FIRST** | no | 2 | control | **NEGATIVE_CONTROL_PASSED** (did NOT pick the dramatic, refuted, privileged mechanism) |
| NC2 — two weak, no dominance | **KEEP_BOTH** | no | 0 | control | **NEGATIVE_CONTROL_PASSED** (no fabricated winner; feasibility did not decide) |

## The headline (the P266 fix)
**A — Phi H-03: KEEP_BOTH with `anti_easy_poc_flag=true`.** The awarded curator-enumeration gas-DoS (terminal_impact
10) was the higher-impact mechanism; the royalty skim (terminal_impact 0) was easier to PoC. The selector flags the
anti-easy-PoC trap and **refuses to drop the gas-DoS** — it carries BOTH into completion/PoC. Had P266 used this,
the awarded mechanism would have had a PoC attempt → a real shot at exact recovery.

## Success criteria (all met)
- P266 H-03 awarded mechanism **selected or kept** → KEEP_BOTH ✅.
- ≥1 prior runner-up awarded case improves → **B, C (KEEP_BOTH) and D (SELECT_AWARDED)** all improve ✅.
- Selector does **not** simply choose the messier/higher-drama mechanism → NC1 (REFUTE_FIRST) + NC2 (KEEP_BOTH) ✅.
- Negative controls not degraded → both PASSED ✅.
- Outputs bounded + human-reviewable ✅. Advisory guard 0 violations ✅. No production-authority paths changed ✅.

## Honest limits shown by the backtest
- **E (BakerFi)** is INCONCLUSIVE by construction: the awarded mechanism was never enumerated into the top-2, so a
  *pairwise* selector cannot recover it. P267 fixes ranking/selection, NOT discovery/enumeration.
- Every "preserved" result for A/B/C is a **KEEP_BOTH**, not an outright SELECT of the awarded mechanism. That is the
  intended, conservative win: the selector's job is to stop the awarded top-2 mechanism from being *dropped*, not to
  perfectly pick it. Whether KEEP_BOTH then yields exact recovery is the job of completion/PoC (a fresh full-path run).
- The dimension signals are operator-assigned; a mis-scored input (e.g. labeling a real DoS as `griefing_minor`)
  would mislead the selector. The selector formalizes the impact comparison; it does not independently verify it.
