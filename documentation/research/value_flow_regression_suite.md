# Value-Flow Standing Regression Suite

Research-only. The chain's REVIEW_ONLY output is trusted **only when this suite is green**. Runner:
`documentation/evals/blind_mechanism_discovery/run_p52.py` (engine + P45 + P47 + P49 + P52, byte-identical). Any red check
→ `REGRESSION_FAILURE` (block outputs). Verified green at P60/P61.

| # | subject | expectation | current |
|---|---|---|---|
| 1 | A1 LoopFi | `tokenScale` + `penalty` must ADVANCE | 2 ✓ |
| 2 | A2 Blackhole | `recipient` must ADVANCE | 1 ✓ |
| 3 | BakerFi NC | must ABSTAIN | 0 ✓ |
| 4 | Sentiment V2 | missing-cap / interface / getter noise BLOCKED | 0 ✓ |
| 5 | TraitForge `DevFund.claim` | omitted-term DEMOTED | 0 ✓ |
| 6 | Reserve | RoundingMode/FLOOR + view-status noise DEMOTED | 0 ✓ |
| 7 | LamboWin | native-ETH fee sink RECOGNIZED (`_sellQuote`/`_buyQuote` demoted) | 0 ✓ |
| 8 | SecondSwap | `referralFeeCost` PRESERVED as PARTIAL | 1 ✓ |
| 9 | Basin / Plaza / Notional / Concrete / Ramses / Phi | no noisy advances | 0 ✓ |

## Meaning of each check (the failure class it pins)
1–2: positive anchors — the chain must still surface the genuine value-flow mechanisms (no over-tightening).
3: negative control — must abstain on a benign getter pair.
4: P44/P45 family-noise class (missing_cap on token primitives / interface getters).
5: P46/P47 ERC20 intermediate-aggregate dataflow false-omitted-term class.
6: P48/P49 bound-vocabulary collision (RoundingMode.FLOOR) + view-getter design-absence class.
7: P51/P52 native-ETH value-sink class.
8: the one genuine fresh PARTIAL must not regress.
9: clean-abstain subjects must not gain noisy advances.

## Operating rule
Run this suite (a) before any batch of REVIEW_ONLY output, and (b) after any change anywhere in `scripts/` (hash drift
check). Green = outputs trustworthy as review candidates. Red = `REGRESSION_FAILURE`, investigate before trusting output.
