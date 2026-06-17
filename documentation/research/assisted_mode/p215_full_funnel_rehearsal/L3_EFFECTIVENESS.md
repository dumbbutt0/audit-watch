# P215 — L3 EFFECTIVENESS

## What L3 did (flag on)
- **0 / 8** High/Critical candidates promoted to High (all `blocked_by_missing_l3_poc`); **0 false-Highs**.
- **1 executed L3 PASS** (ZETA-07, real ZRC20) — calibrated **Medium** (privileged precondition), correctly **not**
  promoted to High.
- Privileged/centralization candidates (ZETA-03/05/08) blocked from High independent of harness — matches official
  QA[09] (centralization, not High).
- DoS carve-out (P214) evaluated, **applied to none** (no permissionless, admin-free, executed deterministic core-path
  DoS among the candidates).

## Scored against the answer key
- **Precision: excellent.** Nothing P215 promoted was an over-rated High; the one fully-ready item (ZETA-07) is a
  genuine low. 0 false-Highs (consistent with P212).
- **The two real Solidity Highs (H-13, H-10) were BLOCKED as `needs_harness`, not promoted.** Important distinction:
  this is **not L3 under-rating** (L3 never mapped a *proven* High down). It is the **fail-closed default** doing its
  job on candidates with **no executed PoC**. The miss-as-High is a **recall/effort gap** (no harness built), compounded
  by a triage Medium floor — not an L3 mapping error.
- **Where L3 needs help:** L3 alone cannot recover a real High that lacks a PoC — it can only refuse to over-rate it.
  Surfacing genuine DoS Highs requires (a) harness effort on `needs_harness` High-ceiling candidates and (b) the P214
  carve-out, which itself needs an executed harness for a permissionless/admin-free deterministic core-path DoS.

## Verdict
L3 effectiveness on P215: **precision strong (0 false-Highs), recall-neutral.** It correctly blocked every unproven
High and the one executed item was a true low. It did not (and by design cannot) rescue the two genuine Highs that were
never harnessed.
