# P212 Stage 2 — answer-key scorecard (sophon, sealed key opened after user approval)

Official awarded (Sherlock judging; folder = final judged severity): **1 High + 4 Medium** (+204 invalid).

| official | sev | mechanism | my candidate / coverage | score | severity |
|---|---|---|---|---|---|
| **003-H** | **High** | `stETH.transferFrom` delivers 1-2 wei less → `depositStEth`→`_stEthTOwstEth` `wrap(_amount)` reverts (contract holds amount-1) | **SOPH-03** (confirmed + harnessed, exact path L473-481/_stEthTOwstEth) | **HIT** | I rated **Medium** → **UNDER-RATED (High)** |
| 001-M | Medium | `setStartBlock()` doesn't update existing pools' `lastRewardBlock` | sf-07 examined `setStartBlock`, **rejected** the real bug | **MISS** (examined-but-rejected) | — |
| 002-M | Medium | `depositEth`→weETH treats Etherfi `eETH` **shares** as actual amount (same class as stETH) | sf-05 examined `_eethTOweEth`, **rejected** as "exact" | **MISS / ADJACENT** (eETH variant of my SOPH-03 class) | — |
| 004-M | Medium | empty pool (lpSupply==0) after start still holds `allocPoint` in `totalAllocPoint` → dilutes other pools | adjacent to SOPH-04/sf-06 dilution themes; not the empty-pool mechanism | **MISS / ADJACENT** | — |
| 005-M | Medium | ETH deposits don't set a referral account → protocol loses Etherfi/Lido referral rewards | not surfaced (no referral surface) | **MISS** | — |

## My non-awarded candidates (false-positive check)
| candidate | my verdict | in official set? | outcome |
|---|---|---|---|
| SOPH-01 withdraw boost conservation | REFUTED (harness: conservation holds) | no | **correct true-negative** |
| SOPH-02 accPointsPerShare scaling | REFUTED (harness: view==settled) | no | **correct true-negative** |
| SOPH-04 boost denominator dilution | NEEDS_HARNESS / likely by-design (not promoted) | no | correct (not promoted) |
| SOPH-05/06/07 (privileged) | blocked (admin-prereq) | no (Sherlock invalidates admin-input) | correct (not promoted) |

## Tallies
- **HIT 1** (003-H, the only High) · PARTIAL/ADJACENT 2 (002-M, 004-M) · MISS 2 (001-M, 005-M) · **FALSE_POSITIVE 0**.
- **Recall: 1/5 awarded (20%); found the #1 High.** Confirmed-finding precision: 1/1.
- Severity on the hit: **under-rated by one level** (Medium vs official High).
