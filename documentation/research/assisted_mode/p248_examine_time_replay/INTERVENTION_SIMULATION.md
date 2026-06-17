# P248 — Phase D: Intervention Simulation

Replay each miss as if each checkpoint existed. A checkpoint recovers findings in its operation cluster (it
both births the candidate and completes the chain — see Phase C). Scored over the reasoning denom (31 wt).
"Gross" = a perfect checkpoint reaching the whole cluster; "Net headroom" = gross − weighted already credited
in P246; "Expected" = net × realization rate (read≠detect + training-confound discount, per P247).

| Checkpoint | Cluster gross wt | Already credited | Net headroom | Realization | **Weighted recovered (expected)** | **Recovery % (of 31)** |
|---|---|---|---|---|---|---|
| **Accounting** | 5 | 1.0 | 4.0 | ~0.70 | **~2.8** | **9.0%** |
| **Permission** | 5 | 2.0 | 3.0 | ~0.70 | **~2.1** | **6.8%** |
| **Cross-contract** | 9 | 1.5 | 7.5 | ~0.50 | **~3.75** | **12.1%** |
| **State-transition** (incl lifecycle) | 10 | 1.75 | 8.25 | ~0.55 | **~4.5** | **14.5%** |
| (Economic — not in the 4) | 2 | 0.25 | 1.75 | ~0.40 | ~0.7 | 2.3% |

Findings each checkpoint recovers (cluster members):
- **Accounting:** kleidi M-02, centrifuge M-05, centrifuge M-07, munchables M-03, munchables M-04 (5 Med).
- **Permission:** decent M-02, **vultisig H-02 (High)**, centrifuge M-04 (1 High + 2 Med).
- **Cross-contract:** **decent H-02, H-03 (High)**, decent M-01, decent M-05, centrifuge M-02 (2 High + 3 Med).
- **State-transition:** **decent H-04, munchables H-01 (High)**, kleidi M-01, kleidi M-03, munchables M-01,
  vultisig M-03 (2 High + 4 Med).

## Notes
- **Absolute recovery ranking:** state-transition (~4.5) > cross-contract (~3.75) > accounting (~2.8) >
  permission (~2.1). The two highest-absolute checkpoints carry **all 4** of the reasoning Highs that are
  recoverable by these four checkpoints (decent H-02/H-03/H-04, munchables H-01); permission carries the
  fifth (vultisig H-02).
- **Realization caveat:** rates are judgement, not measurement; cross-contract is discounted hardest
  (cross-chain/external-protocol semantics are the least reliably reproduced). The gross-vs-expected gap is
  the uncertainty; a forward blind run is the only way to confirm.
- Recovery over the FULL P246 denom (52): state-transition ~8.7%, cross-contract ~7.2%, accounting ~5.4%,
  permission ~4.0%.
