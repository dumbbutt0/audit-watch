# decent-2024-01-holdout — SCORECARD

Freeze hash: e4f4d7ddc8f36d30a49c5dc010654c4d9987c123fa8ded40879301305eaa807b (recorded before reveal).
Sealed-key hash: 2eafbdf52cb3d1f8. Reveal AFTER freeze. Awarded: 4 High + 5 Medium = 9.

## Awarded-finding scoring
| Awarded | Sev | My candidate | Class | Credit |
|---|---|---|---|---|
| H-01 DcntEth router can be set by anyone | High | D-C1 (exact) | DIRECT_HIT | 1.0 |
| H-02 missing min-gas check via LayerZero → dst exec fails | High | — | MISSED | 0 |
| H-03 DecentBridgeExecutor.execute failure → funds to random addr | High | D-M2 (same fn + failed-call refund path; I framed as stuck/grief, not random-addr) | PARTIAL_HIT | 0.5 |
| H-04 lose cross-chain tx if dst router lacks WETH reserves | High | D-L1 (looked at reserve check, flagged off-by-one not the loss) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-01 permanent loss if swap data outdated | Medium | — | MISSED | 0 |
| M-02 bypass fees via DecentEthRouter.bridgeWithPayload direct call | Medium | D-H2/D-M1 (fee-bypass area, wrong entrypoint) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-03 missing access control UTB.receiveFromBridge | Medium | D-H2 (exact) | DIRECT_HIT | 1.0 |
| M-04 loss due to fixed fee calc (Stargate bps) | Medium | — | MISSED | 0 |
| M-05 refunded ETH stuck at DecentBridgeAdapter | Medium | — | MISSED | 0 |

## System-finding scoring (precision)
D-C1→AWARDED_EQUIVALENT(H-01); D-H2→AWARDED_EQUIVALENT(M-03); D-M2→AWARDED_EQUIVALENT(H-03 partial);
D-L1→PLAUSIBLE(H-04 area); D-M1→PLAUSIBLE(=L-02 low, deadline/sig); D-H1 (UniSwapper public swap fns)→
PLAUSIBLE (not awarded; defensible but swapper holds no idle funds in practice); D-L2→BENIGN.
False positives: 0.

## Metrics
- High recall: strict (DIRECT) 1/4 = 25%; credited 1.75/4 = 44%.
- Medium recall: strict 1/5 = 20%; credited 1.25/5 = 25%.
- Weighted recall (H=3,M=1; denom 17): numerator 6.5 → **38.2%**.
- Precision: 0 FP across 7 system findings; 3 AWARDED_EQUIVALENT + 3 PLAUSIBLE + 1 BENIGN.
- Coverage completeness: 100% in-scope read (52/52 critical READ_FULL). Gate would PASS (no block).
- Candidates preserved by depth gate: n/a (no rejections forced).
- Advisory lens contribution: 0 (all 3 lenses 0 candidates).
- Time: single-session full read. Proof conversion attempted: 0 (BLOCKED_BY_BUILD).

## Miss attribution (one root cause each)
- H-02 → **Cross-chain** (LayerZero min-gas semantics)
- M-01 → **Reasoning depth** (stale postBridge swap-data window)
- M-04 → **Economic invariant** (fixed-bps fee vs actual bridge fee)
- M-05 → **Cross-chain** (native refund routed to adapter, stuck)

## Note
Training-data confound: H-01 (setRouter) is a widely-publicized Decent finding; LLM prior knowledge may
have aided recall here. Recorded for the aggregate honesty discussion.
