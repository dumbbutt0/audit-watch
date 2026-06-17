# P240 — Answer key (revealed AFTER freeze)

**Source:** local sealed `_sealed_answer_key/report.md` (Code4rena PoolTogether 2024-03, contest 332; report
`306ec830…`). Opened only after the freeze marker (FROZEN_HUNT.md hashes predate this file).
**Awarded:** 9 unique — **1 HIGH + 8 MEDIUM** (+7 Low/QA, 10 gas). 6 in-scope contracts, 648 LOC.

## Awarded findings + mapping to my BASE blind set
| ID | Sev | Title | My base candidate | Result |
|---|---|---|---|---|
| H-01 | High | `claimYieldFeeShares` partial claim forfeits remaining `yieldFeeBalance` (`-= _yieldFeeBalance`) | **PT-01** | **DIRECT HIT** (predicted Medium → under-rated; awarded High) |
| M-01 | Med | Winner steals claimer fees / forces gas via `beforeClaimPrize` hook re-entering `Claimer.claimPrizes` | **PT-04** | **PARTIAL** (hook-griefing family + "force claimer to pay gas" impact; missed the exact fee-steal-via-reenter mechanism) |
| M-02 | Med | `_maxYieldVaultWithdraw` uses `convertToAssets` (approx; EIP-4626) | — | MISS |
| M-03 | Med | `maxDeposit` uses `yieldVault.maxDeposit` but deposit uses `mint` (EIP-4626) | — | MISS |
| M-04 | Med | No slippage protection in `withdraw`/`redeem` (yield-vault loss) | — | MISS (noted the fns, not the slippage angle) |
| M-05 | Med | `yieldFeeBalance` unclaimable after `transferTokensOut` (TWAB supply limit) | (PT-05 adjacent) | MISS |
| M-06 | Med | Funds locked: `_withdraw` raw `.transfer` returns false on lossy ERC4626 redeem → assets stranded | **PT-02** | **DIRECT HIT** |
| M-07 | Med | `maxDeposit` ignores produced fees → `yieldFeeRecipient` can't claim (TWAB limit) | (PT-05 adjacent) | MISS |
| M-08 | Med | `depositWithPermit` incompatible with DAI permit signature | — | MISS |

## Lens applicability to the awarded set (the P240 question)
- **Safe-management lens:** no Gnosis-Safe guard anywhere → 0 awarded findings in domain. Correctly silent.
- **Hostile-token settlement lens:** the only hostile-token-flavored award is **M-06** — but it is on the
  **immutable single `_asset`** of an ERC4626 vault, which the lens *deliberately excludes* (attacker/order-SELECTED
  token required; single-asset vaults are out of scope to keep precision — see P239). So the lens by-design does NOT
  cover M-06; the **base stack caught it (PT-02)**. The remaining awards are accounting / EIP-4626 / hook-reentrancy
  / DAI-permit — all outside both lens domains.
- **Net: 0 awarded findings were in either lens's domain → lens contribution is structurally 0 on this target.**
