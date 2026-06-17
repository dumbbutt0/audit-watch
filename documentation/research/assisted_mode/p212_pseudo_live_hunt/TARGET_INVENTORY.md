# P212 — target inventory (fresh C4/Sherlock candidates)

Probed via `git ls-remote` (SOURCE repos only). Excludes anything already in `audits/` and anything used in P186-P211.

| candidate | platform | date | reachable | in-scope .sol / LOC | compiler | verdict |
|---|---|---|---|---|---|---|
| **sherlock-audit/2024-05-sophon** | Sherlock | 2024-05 | ✅ | 14 / ~1.2k (core SophonFarming 933) | 0.8.25 | **SELECTED** — manageable, modern, rich farming/accounting surfaces |
| code-423n4/2024-01-curves | C4 | 2024-01 | ✅ | 7 / ~730 | ^0.8.7 | fallback — small (thin surface set) |
| code-423n4/2023-08-goodentry | C4 | 2023-08 | ✅ | 180 / ~17k | ^0.8.0 | REJECT — enormous (not manageable for first hunt) |
| code-423n4/2024-03-pooltogether | C4 | 2024-03 | ✅ | — | — | REJECT — already in audits/ + count-screened P206 |
| sherlock-audit/2024-08-cork-protocol | Sherlock | 2024-08 | ✅ | — | — | not selected — larger depeg-swap protocol |
| code-423n4/2024-02-thirdweb / 2024-05-olympus | C4 | — | no default head | — | — | skipped (no clean ref) |

Selection respects: not in audits/, not P186-P211, Solidity/EVM, manageable scope, completed contest with a sealed
report, modern compiler (harnessable if a High emerges).
