# P156 — Search Log (external + local)

External search/fetch is available in this environment (WebSearch/WebFetch confirmed working). The
Code4rena `2024-03-abracadabra-money` contest is public.

## External queries / fetches
| # | Action | Target | Key result |
|---|---|---|---|
| 1 | WebSearch | "Code4rena 2024-03 Abracadabra LockingMultiRewards findings report" | Located the findings repo + C4 report page; 20 findings (4 H / 16 M). |
| 2 | WebFetch | `raw.githubusercontent.com/.../2024-03-abracadabra-money-findings/main/report.md` (LockingMultiRewards findings + the 3 H5 patterns) | Only M-05 ties to LockingMultiRewards in that read; **none** of the 3 H5 patterns (expired-lock boost retention / reward redistribution / balanceOf counting expired-as-boosted) present. |
| 3 | WebFetch | same raw report.md (complete H/M TOC) | H-01..H-04 = MagicLP TWAP / rounding / BlastOnboarding / oracle (no LockingMultiRewards). M-01..M-12 captured. |
| 4 | WebFetch | same raw report.md (M-13..M-16 + M-07 locus + any processExpiredLocks finding) | M-07 = LockingMultiRewards reward-**rate precision loss**, explicitly **not** boost/expired locks. No finding (any severity) on processExpiredLocks / expired-lock boost retention. |
| 5 | WebFetch | `code4rena.com/reports/2024-03-abracadabra-money` (M-13..M-16 titles + LockingMultiRewards/boost mentions) | M-13 = MagicLP `_GeneralIntegrate` precision; M-14 = staking native USDB/WETH support; M-15 = LockingMultiRewards Blast gas-yield config; M-16 = bootstrap grief. None = expired-lock boost retention. |
| 6 | WebSearch | "...findings issue LockingMultiRewards expired lock boost multiplier reward processExpiredLocks" | Confirmed the Gelato-keeper fact ("locks released by a Gelato task offchain"); no issue surfaced describing the H5 mechanism. |

### Complete awarded finding set (20)
- **High (4):** H-01 MagicLP TWAP exploit · H-02 MagicLP rounding / I-invariant · H-03 BlastOnboarding deposit loss · H-04 oracle price manipulation. *(None touch LockingMultiRewards.)*
- **Medium (16):** the **LockingMultiRewards-touching** ones are **M-05** (extended lock duration / missing deadline), **M-07** (reward-**rate precision loss**), **M-14** (cannot support native USDB/WETH), **M-15** (Blast gas-yield config). The rest are MagicLP/Router/Factory/Onboarding/oracle.
- **No awarded finding** (H, M, or the QA/Low set surfaced) describes **expired-lock boost retention**,
  **reward redistribution to expired lockers**, or **balanceOf/totalSupply counting expired locked balances
  as boosted** — the H5 mechanism.

## Local re-cross-check (P155 repeat)
`findings/{raw,validated}`, `notes/`, `reports/`, `data/` empty; `output/deep_pass/*` only enumerate
LockingMultiRewards functions for coverage (no H5 finding); `MEMORY.md` records only M-10 (MagicLpAggregator)
from prior abracadabra phases; sidecar = the H5 row only.

## Residual limit (honest)
The awarded/grouped C4 report + the C4 report page were reviewed exhaustively for the 20 awarded findings.
The **full ~200-issue raw submission set and the complete QA/Low report were not line-by-line exhausted**, so
a non-awarded (dup/QA/invalid) warden submission of this mechanism cannot be 100% excluded → classification
stays `public_known_but_not_duplicate`, not `novelty_clear`.

## Sources
- C4 report: https://github.com/code-423n4/2024-03-abracadabra-money-findings/blob/main/report.md
- C4 report page: https://code4rena.com/reports/2024-03-abracadabra-money
- M-05 issue #225: https://github.com/code-423n4/2024-03-abracadabra-money-findings/issues/225
- Contest repo: https://github.com/code-423n4/2024-03-abracadabra-money
