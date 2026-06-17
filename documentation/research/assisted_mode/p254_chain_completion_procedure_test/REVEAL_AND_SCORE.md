# P254 — Phase 4: Reveal & score

## Freeze integrity (recorded AFTER the three pre-reveal freezes, BEFORE the key was opened)
The sealed key was opened only after these hashes were computed:
- `BASE_HUNT_FREEZE.md`   sha256 `2983bee06430d536…`
- `SELECTED_LOCI.md`      sha256 `bad10f234dd0b192…`
- `PROCEDURE_OUTPUTS.md`  sha256 `d36be8ca11db4826…`

## Reveal source
`audits/loopfi-2024-07-holdout/reports/` is **empty** — loopfi has no local answer key (consistent with P147's
"no local answer key" note). Reveal was therefore done **post-freeze** against the public Code4rena report and
the verified `code-423n4/2024-07-loopfi-findings` GitHub issues (same post-freeze WebFetch method as P250). The
contest awarded **15 High + 39 Medium** unique findings. Relevant verified awarded issues:

| issue | sev | locus | awarded mechanism |
|---|---|---|---|
| **#399** | **High** | `CDPVault.liquidatePosition` | `takeCollateral = repayAmount/discountedPrice` ignores the penalty (should be `(repayAmount−penalty)/…`); debt reduced by `repayAmount·penalty` → **profitable self-liquidation drains protocol/lenders** |
| #296 / #218 | Medium | AuraVault deposit/mint/withdraw/redeem | functions don't account for **unclaimed rewards** → share mispricing |
| #521 | Medium | `AuraVault._chainlinkSpot`/feeds | Chainlink `updatedAt` not validated → stale price |
| #215 / #174 | Med | AuraVault deposit/mint; claim | slippage; missing `_setupRole` → claim DOS |
| #87 | Med | `PositionAction.onCreditFlashLoan` residual | leftover tokens after `auxSwap` are **stuck in the contract** (stranded, not stolen) |
| #228 / #382 | Med | `StakingLPEth` MIN_SHARES | donation/`_checkMinShares` abuse → DoS / last-withdrawer locked |

## Per-locus classification (frozen procedure output vs awarded truth)

### L2 — `CDPVault.liquidatePosition` → **AWARDED_EQUIVALENT (High, #399)** ✅
Pre-frozen routine output (IDC + STS): *"collateral-out (`repayAmount/liqDiscount`) − debt-down
(`repayAmount·liqPenalty`) > 0 … the discount is pure liquidator profit … loser = borrower (and pool, via
induced bad debt)."* Awarded #399 root cause: *"the collateral sent to the caller does not incorporate the
penalty … while debt reduction uses `repayAmount·liquidationPenalty`, collateral uses the full `repayAmount` …
enabling profitable self-liquidations that drain protocol and lender funds."* **Same root cause + same impact.**
Base tag was `BASE_BORN_INCOMPLETE` ("asymmetry noticed; exploit not computed") → the **routine completed it**
(IDC computed the profit direction / self-liquidation; STS gave the worsening-health repeat path). This is a
genuine **procedure-completed-not-base** recovery of an awarded **High**.

### L1 — `AuraVault.claim` → **SAME_AREA_WRONG_MECHANISM**
Routine completed a *plausible* chain (caller-chosen `amounts[]` extract `claimerIncentive` on the full balance
+ locker over-pay). The awarded AuraVault findings are a **different** mechanism: unclaimed-rewards share
mispricing (#296/#218), oracle staleness (#521), slippage (#215), role-DOS (#174). My claim-amounts chain is
**not** an awarded finding. (Note: my **deselected** base candidate B-3 — AuraVault oracle staleness — matches
awarded #521, but B-3 was excluded from the routine, so it earns the routine no credit.)

### L3 — `SwapAction`/`PositionAction` residual → **SAME_AREA_WRONG_MECHANISM**
Routine status was **REFUTED** (CCIT: per-proxy isolation ⇒ no cross-principal theft). That theft-refutation is
*correct* — no awarded residual-**theft** finding exists. But the **awarded** residual bug (#87) is **stuck/
stranded leftover tokens** after `auxSwap` — a mechanism the routine's TSE asked about ("stranded?") but
answered benignly. Right code, wrong mechanism; the routine **missed** the awarded stranded-funds framing.

### L4 — `StakingLPEth` → **SAME_AREA_WRONG_MECHANISM**
Routine picked the **cooldownEnd reset** (correctly bounded by AAS to a self-inflicted Low — no FP). The awarded
StakingLPEth bugs (#228/#382) are the **MIN_SHARES donation / DoS** mechanism — which was visible in the code
(`_checkMinShares`) but not birthed as a candidate. Right contract, wrong mechanism.

## Metrics
| metric | value |
|---|---|
| loci selected | 4 (L1–L4) |
| chains the routine completed/partial (pre-reveal) | 3 PARTIAL_CHAIN + 1 REFUTED |
| **AWARDED_EQUIVALENT** | **1 (L2, High #399)** |
| PARTIAL_AWARD | 0 |
| SAME_AREA_WRONG_MECHANISM | 3 (L1, L3, L4) |
| BENIGN / FALSE_POSITIVE | 0 severe FP (L3 refute + L4 down-rate were correct restraint) |
| procedure-completed-not-base recoveries | **1 (L2)** |
| awarded-mechanism selection rate | **1/4** (3/4 engaged the right code but completed a non-awarded mechanism) |
| time / burden per locus | ~5–10 min manual reasoning; manageable |
| recovered anything base missed? | **Yes — L2 (the routine completed an awarded High the base left as a bare asymmetry observation)** |

## Honest reading
The routine produced its **first genuine blind completion in the whole arc** (P250/P252 had zero): at L2 the
IDC+STS operations turned a base "asymmetry observed" candidate into the awarded High #399's exact
profitable-self-liquidation chain. That literally clears the user's strong-pass threshold (≥1 AWARDED_EQUIVALENT,
0 severe FP, manageable, not base-completed). **However**, the same run shows the routine's weak point: on 3 of 4
loci it engaged the correct awarded code but **completed the wrong mechanism** — refuting the actual awarded bug
(L3 stranded funds), or selecting a non-awarded mechanism (L1 claim-amounts, L4 cooldown-reset) while the real
awarded mechanism (L4 MIN_SHARES) sat visible. The routine can complete *a* chain; it does **not reliably select
the awarded chain blind**. On the one win, the base candidate had already 90% identified the asymmetry, so the
routine's marginal contribution — real — was the profit/exploit computation, not the observation.
