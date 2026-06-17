# P246 — Aggregate Results

Weights: High=3, Medium=1. Credit: DIRECT_HIT=1.0, PARTIAL_HIT / SAME_ROOT_CAUSE=0.5,
SAME_AREA_WRONG_MECHANISM=0.25, MISSED=0. "Strict" = DIRECT_HIT only.

## Per-contest summary
| Contest | Arch | Awarded (H/M) | weighted denom | credited num | **weighted recall** | strict | coverage | gate |
|---|---|---|---|---|---|---|---|---|
| decent | cross-chain/NFT | 4H/5M | 17 | 6.5 | **38.2%** | 25% | 100% | PASS |
| vultisig | ILO/Uniswap-vesting | 3H/3M | 12 | 7.75 | **64.6%** | 50% | 100% | PASS |
| kleidi | Safe/timelock (hardened) | 0H/3M | 3 | 0.25 | **8.3%** | 0% | 100% | PASS |
| centrifuge | RWA/cross-chain 4626 | 0H/8M | 8 | 0.75 | **9.4%** | 0% | ~45% | BLOCK |
| munchables | GameFi/staking | 2H/4M | 10 | 4.5 | **45.0%** | 30% | ~17% | BLOCK |
| badger | lending/CDP (hardened, large) | 0H/2M | 2 | 0 | **0%** | 0% | ~1% | BLOCK |
| **TOTAL** | | **9H/25M** | **52** | **19.75** | **38.0%** | **25%** | — | 3 PASS / 3 BLOCK |

## Aggregate metrics
- **Overall weighted recall: 38.0% credited / 25.0% strict (direct-hit only).** Denominator = 52 weighted
  points (9 High×3 + 25 Med×1 = 27 + 25).
- **Overall High recall:** 9 Highs awarded; **4 DIRECT (44%)**, credited 5.5/9 = **61%** (decent H-01,
  vultisig H-01 & H-03, munchables H-02 direct; partials on decent H-03/H-04, munchables H-01).
- **Overall Medium recall:** 25 Mediums; 2 DIRECT (8%), credited ~6.25/25 = **25%**.
- **Precision / FP rate:** **0 hard false positives** submitted as findings across all 6 contests. System
  findings were AWARDED_EQUIVALENT, PLAUSIBLE (real but un-awarded/QA), or BENIGN. The 3 advisory lenses
  produced **0 true contributions** and only 2 benign advisory candidates (kleidi create-time) all phase —
  FP rate ≈ 0%.
- **Proof conversion attempted: 0/6** — universally BLOCKED_BY_BUILD (no vendored foundry deps in fresh
  workspaces). No PoCs produced.

## Recall by architecture
| Architecture | weighted recall | note |
|---|---|---|
| ILO/vesting (vultisig) | 64.6% | best — small, self-contained, clear High logic |
| GameFi/staking (munchables) | 45.0% | awarded bugs clustered in read managers |
| cross-chain/NFT (decent) | 38.2% | caught top High + 1 Med directly |
| RWA/cross-chain 4626 (centrifuge) | 9.4% | coverage-bound (gateway/token/restriction unread) |
| Safe/timelock hardened (kleidi) | 8.3% | depth-bound (subtle logic/DoS) |
| lending/CDP large (badger) | 0% | coverage-bound (gate BLOCK) |

## Recall by contest size (the dominant signal)
| Size band | contests | weighted recall | gate |
|---|---|---|---|
| Small/fully-readable (≤3.3k LOC) | decent, vultisig, kleidi | **45.3%** (14.5/32) | all PASS |
| Medium/large (coverage-incomplete) | centrifuge, munchables, badger | **26.3%** (5.25/20) | all BLOCK |
Fully-readable contests recover ~45% weighted; contests too large to fully read in one pass recover ~26%
(and would be BLOCKED from triage). **Size/coverage is the strongest determinant of recall** — consistent
with P241/P243.

## Recall by bug family (credited)
| Family | recovered / awarded (approx) | note |
|---|---|---|
| Access control / missing-auth (setRouter, receiveFromBridge, whitelist) | strong | decent H-01, M-03; vultisig H-02 |
| Vault/share & fee accounting | medium | vultisig H-01 direct; centrifuge M-05/M-07 partial |
| Lock/time-validation logic | strong | munchables H-02 direct; H-01 partial |
| Price/launch manipulation (DEX) | strong | vultisig H-03 direct |
| Cross-chain message/gas/refund | weak | decent H-02/M-05 missed; centrifuge M-01 missed |
| Oracle freshness / round-id | weak | not awarded where found (badger); none recovered |
| Permit/signature | weak | centrifuge M-02/M-03 missed |
| Governance/admin (timelock, pausers) | weak | kleidi M-01/M-03, centrifuge M-06 missed |
| Rounding-direction / precision | weak-partial | centrifuge M-07 partial |
| DoS/griefing | weak | kleidi M-01, munchables H-01 (partial), centrifuge M-04 |

## Recall with vs without advisory lenses (P237/P238/P242)
- **Without lenses (base hunt):** the entire credited 19.75 numerator came from the base hunt.
- **With lenses:** lenses added **0** awarded recovery across all 6 contests (safe-mgmt 0×6, hostile-token
  0×6, create-time 0 useful + 2 benign on kleidi). **Lens contribution to competitive recall = 0** on this
  corpus — consistent with P239/P240/P241 (lens domains are rare; these contests were out-of-domain). The
  lenses also added no false positives (0 FP), so they are recall-neutral / precision-safe here.

## Key honesty caveats (carried into READINESS_ASSESSMENT)
1. **Training-data confound:** all 6 are public C4 contests; as an LLM I may have prior exposure to their
   findings → recall here is an **upper bound** vs a truly-unseen contest.
2. **Coverage ceiling:** 3/6 were coverage-incomplete; the headline 38% blends full-coverage (~45%) and
   coverage-bound (~26%) regimes.
3. **Partial-credit dependence:** strict direct-hit weighted recall is **25%**; the 38% relies on partial
   credit for same-root/same-area candidates.
4. **No proof:** 0 PoCs (BLOCKED_BY_BUILD) — Highs are unproven, which real submission would require.
5. **n=6, high variance** (0%–65% range).
