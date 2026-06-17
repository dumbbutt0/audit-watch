# P212 — SOPH-03 under-rating analysis

| | value |
|---|---|
| Official (Sherlock 003-H) | **High** (escalation accepted: "asset loss or deposit DoS → high") |
| System (P212) | **Medium** |
| Harness | EXECUTED deterministic DoS: `depositStEth(100e18)` reverts under realistic stETH 1-wei share-rounding; honest-stETH control succeeds |

## Why the old L3 mapping demoted it
`decide()` severity branch: SOPH-03's record was `l3_status=FAIL` (FAIL meant "no THEFT under the theft-centric High
bar") + `impact_class=dos`. Both branches map to `medium`:
- `elif l3=="FAIL": cal = "invalid" if refut else "medium"` → medium.
- `elif ic in (dos,griefing,precision,bounded_local,auth_only): cal="medium"`.
**Root flaw:** the mapping conflates *no-theft* with *not-High* and treats ALL DoS as Medium. It has no notion of a
**deterministic, no-workaround DoS of a core supported path**, which a venue rates High.

## Why the venue treats it High
- It bricks a **core supported deposit path** (`depositStEth`) for an entire class of users (stETH holders).
- It is **deterministic** (stETH always share-rounds 1-2 wei) and **unavoidable** by normal users; **no workaround**
  for depositing held stETH.
- Source-valid (documented Lido stETH behavior; cited precedent). Permissionless / normal-user-triggered. No admin
  prereq. This is "core protocol functionality broken" → High by Sherlock criteria.

## What separates SOPH-03 from ordinary griefing/DoS (→ the carve-out)
Deterministic (not probabilistic) · core supported entry path (not a peripheral/optional fn) · affects a class of
users (not one self-inflicted edge) · no workaround · permissionless/normal-user · no admin prereq · executed L3 proof
with a control. Ordinary DoS lacks several of these (recoverable, optional, single-user, has a workaround, or
unharnessed) → stays Medium. These are exactly the 10 carve-out criteria (L3_DOS_CARVEOUT_RULE.md).
