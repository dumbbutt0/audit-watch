# P240 — FREEZE MARKER (anti-hindsight gate)

**FROZEN_AT:** 2026-06-08, before opening `_sealed_answer_key/report.md`.
**Subject:** PoolTogether V5 (Code4rena 2024-03), `audits/pooltogether-2024-03-holdout` (in-place blind read).

All artifacts below were committed before the answer key was opened. The reveal/scoring phase adds NEW files only
(ANSWER_KEY_revealed.md, CONTEST_SCORECARD.md) and never edits these.

## Frozen content hashes
| Artifact | sha256 |
|---|---|
| candidates_pooltogether.md (base set) | `07d3315b3a4aaa515a93793731283fc8824e542d2ca313689da5e7e4e1434d54` |
| FROZEN_RANKINGS.json | `598c4cd7d424604053264f4f4295428d7958295cb6b2cbe5286613303620ece0` |
| FROZEN_SUBMISSIONS.md | `f1820340da0139e362a0253122f2a81aacc99aa1196925f0de5748389579084a` |
| outputs/pooltogether_safe.json (Safe lens) | `39a985f15da08d8aebb12417366641df1dc2675b4bd277ecd8cf79a565ec615d` |
| outputs/pooltogether_hostile.json (hostile lens) | `6142a4a11c606cfd789f787a0985908601a548698a39e600e12e870f9484ad8d` |

## Sealed answer key (re-verified = never opened during the hunt)
`_sealed_answer_key/report.md` = `306ec8306d0f948eeb4219a1efa9d28ba02433ad770a89f59db942824dc9dead` (matches SETUP_WITNESS).

## Frozen sets (base vs advisory — the contribution-measurement basis)
- **Base-stack candidates (5):** PT-01 (claimYieldFeeShares fee forfeit, Med) · PT-04 (prize-claim hook griefing,
  Med) · PT-02 (_withdraw raw transfer, Low/Med) · PT-03 (factory transferFrom, Low) · PT-05 (liquidation rounding,
  Low).
- **Advisory-lens candidates (0):** safe_management_coverage = 0; hostile_token_settlement = 0. (Single-asset,
  non-Safe target → out of both lens domains. 0 FP, 0 noise.)

## Frozen metrics
| Metric | Value |
|---|---|
| Base candidates | 5 |
| Advisory-lens candidates | 0 (Safe 0 + hostile 0) |
| Advisory FP | 0 |
| Advisory noise / wasted effort | 0 |
| Harness attempts | 0 (BLOCKED_BY_BUILD — no foundry deps shipped) |
| L3 confirmed | 0 |

The hunt and drafts are FROZEN. Proceed to Phase 3 (reveal + score).
