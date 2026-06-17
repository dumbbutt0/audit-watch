# P240 — Frozen submission drafts (predictions, pre-reveal)

Frozen BEFORE opening the answer key. Base-stack only; advisory lenses contributed 0.

| ID | Predicted severity | Predicted impact | Confidence | Evidence depth | Source |
|---|---|---|---|---|---|
| PT-01 | Medium | yield-fee recipient forfeits accrued fees on a partial claim (balance zeroed, fewer shares minted) | High (clear logic bug) | L1 (static; harness BLOCKED_BY_BUILD) | base |
| PT-04 | Medium | malicious/reverting winner hook griefs the claimer (claim reverts) | Medium | L1 (static) | base |
| PT-02 | Low/Med | non-standard asset returning false burns shares without paying out | Medium | L1 (static) | base |
| PT-03 | Low | yield buffer may be unfunded for non-standard assets on deploy | Medium | L1 (static) | base |
| PT-05 | Low | liquidation/yield-fee rounding edge | Speculative | L1 (static) | base |

No submission draft is harness-backed (build blocked); all are static reasoning. None originated from the advisory
lenses (both emitted 0 on this single-asset, non-Safe target).
