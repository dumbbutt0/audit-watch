# P201 — corpus viability (zetachain-2023-10-holdout)

## Verdict: VIABLE for the testable refinements
- **14 High / 34 Medium** (count-only unseal) — strongest High count of any fresh corpus → best power for
  genuine-High preservation **and** secondary-High preservation (the P200 folding failure).
- Fresh: not used in P186/P189/P198/P199 derivation or P200 scoring.
- 18 core `.sol` / 2444 LOC, omnichain bridge.

## Class coverage (what P201 can / cannot test here)
| gate class | coverage on zetachain | testable? |
|---|---|---|
| A theft/insolvency/permanent-loss | custody withdraw, connector lock/mint, ZRC20/WZETA value-flow | ✓ strong |
| B oracle/price-feed | **none** (oracle surfaces = 0) | ✗ **carved out — UNVALIDATED_OUT_OF_SAMPLE** |
| C precision/rounding | ZRC20 gas-fee math, ZetaTokenConsumer swap amounts | ~ light |
| D DoS/griefing | pause, cross-chain message handling, supply caps | ✓ |
| E auth/privileged transition | onlyTSS / onlyTSSUpdater / onlyFungible / interactor verification / setters | ✓ strong |
| F secondary-High preservation | multi-mechanism surfaces (connector send+onReceive+onRevert; ZRC20 withdraw+gasfee) | ✓ |

## Caveats (carried into scoring)
- **Oracle (B) not testable** — no oracle findings. Oracle stays design-only; no production-validated claim. (→ P202/P203.)
- **Precision (C) lightly testable** — zetachain is precision-thin (≈2 precision surfaces); precision result will be
  directional, not strong.
- Cross-chain bridge → classes **A / D / E** are the best-tested; the strongest evidence will be there.
- Bounded ~18-surface sample → out-of-sample **signal**, not full recall (as in P200). Mechanism-matched subset
  size determines power; recorded at scoring.
