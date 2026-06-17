# P212 Stage 2 — recommendation

## Decision: `SEVERITY_GATE_REGRESSION`

The first pseudo-live hunt scored against the (now-opened, user-approved) Sherlock answer key. Headline:
**the system found the #1 awarded High but its L3 severity gate under-rated it to Medium.**

## Scoring vs official (1 High + 4 Medium; 204 invalid)
- **HIT 1 / FALSE_POSITIVE 0.** SOPH-03 == **003-H** (exact: stETH 1-2 wei transfer rounding → `depositStEth` reverts
  in `_stEthTOwstEth`). My harness reproduced the exact revert. **Recall 1/5; confirmed-precision 1/1.**
- **Severity:** I calibrated SOPH-03 **Medium**; Sherlock judged **High** (escalation accepted, "asset loss or
  deposit DoS → high"). **Under-rated by one level.**
- **Misses (4):** 001-M (setStartBlock—examined but rejected), 002-M (eETH share-vs-amount—same conversion family as
  SOPH-03, examined but rejected), 004-M (empty-pool allocation), 005-M (referral rewards). Bounded 8-surface hunt.
- **L3 precision:** correct — SOPH-01/02 refuted (true negatives), privileged/by-design not promoted, **0 false-Highs**.

## Why SEVERITY_GATE_REGRESSION (not the other states)
- Not `LIVE_HUNT_READY`/`_WITH_LIMITS`: the gate mis-severitied the one confirmed finding (a genuine High shown as
  Medium) — shipping that would under-report a High in a real contest.
- Not `TOO_MANY_FALSE_POSITIVES`: 0 FP.
- `NEEDS_MORE_REHEARSAL` also applies (1/5 recall) and is the secondary signal — but the **sharpest, most actionable**
  result is the severity regression, which strikes at the L3 standard itself.

## The actionable fix (the campaign lesson, inverted)
P199-P211 hardened against **over**-rating. The live test exposed the opposite: the L3 demotion rule
*"DoS/griefing → Medium unless permanent material loss/insolvency"* is **too blunt** — a **permanent DoS of a core
deposit/withdraw path with no admin prerequisite can be High**. Recommended change (research-only, re-validate before
wiring): add that carve-out to the L3 severity mapping and re-run the P208 backtest + P204/P207 controls to confirm it
doesn't reintroduce over-rating. Also add a **conversion-family sibling-parity lens** (when one share-rounding variant
hits, force-check eETH/sDAI siblings) — would have converted the 002-M near-miss.

## What went right (keep)
- End-to-end firewall held: blind discovery → harness verification → human-review pause → scoring only after approval;
  0 false positives; the top High was found and reproduced; nothing submitted/routed; production untouched.

## Status / next
- This closes P212. The L3 severity-floor regression is the input to a follow-up calibration phase (P213): add the
  permanent-core-DoS carve-out + sibling-conversion lens, re-validate on decent/vultisig/sophon, **do not wire** until
  re-validated. Recall improvement (fuller surface sweep / coverage gate) is a parallel track.
- Answer key was opened only after explicit user approval; no submission was ever made (sophon is a completed contest).
EOF
echo "wrote STAGE2_RECOMMENDATION.md"