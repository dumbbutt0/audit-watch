# P156 — Duplicate / Public-Known Classification

**novelty_status = `public_known_but_not_duplicate`**

| Field | Value |
|---|---|
| Exact duplicate found? | No |
| Materially-equivalent duplicate found? | No |
| Public-known area? | Yes — LockingMultiRewards publicly audited (C4 2024-03), reward accounting examined (M-07), design "Based from Convex CvxLockerV2 / Curve" |
| Distinct angle of H5 | The reward-fairness consequence of an **expired-but-unprocessed boosted lock** (orthogonal to M-05 lock-timing and M-07 reward-rate precision) |
| Adjacent public findings | M-05 (lock duration), M-07 (reward precision), M-14 (native token), M-15 (gas yield) — all LockingMultiRewards, none = H5 |
| Pattern lineage | Convex CvxLockerV2 / Curve MultiRewards / Ellipsis EpsStaker (public) |
| Residual / limit | Full ~200-issue raw submission set + complete QA report not line-by-line exhausted → cannot 100%-exclude a non-awarded/QA submission → not `novelty_clear` |

This supersedes the P155 `duplicate_unknown / cannot_assess_locally`: an external reasonable search of the
**awarded** corpus was completed and found no duplicate, but the public-pattern lineage and the
non-exhaustive raw-issue review keep it at `public_known_but_not_duplicate` rather than a clean novelty
claim. Per project rule, novelty is **not** asserted beyond what the search supports.
