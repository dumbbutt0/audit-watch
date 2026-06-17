# P254 — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

**This is the frozen base-workflow analogue for P254, not an ad hoc manual hunt.** It reproduces what the base
workflow produces: a frozen candidate/suspicious-locus set, the checkpoint records, rankings, the exact
generation basis, and a three-way state tag per item. Frozen and hashed before any locus selection or reveal.
The sealed answer key (`audits/loopfi-2024-07-holdout/reports/`) was **not** read at this point.

## 4. Generation basis (exact command/path)
- **Surface enumeration:** `audits/loopfi-2024-07-holdout/output/coverage_manifest.json` (399 in-scope function
  items; ROOT-relative paths resolve; `source_span` present).
- **Checkpoint records (isolated, advisory):**
  - `python scripts/accounting_checkpoint_audit.py --manifest audits/loopfi-2024-07-holdout/output/coverage_manifest.json --out documentation/research/assisted_mode/p254_chain_completion_procedure_test/outputs/loopfi_accounting_checkpoint.json --quiet`
  - `python scripts/state_transition_checkpoint_audit.py --manifest <same manifest> --out documentation/research/assisted_mode/p254_chain_completion_procedure_test/outputs/loopfi_state_transition_checkpoint.json --quiet`
- **Base candidate set:** isolated/manual blind read of the loopfi core (the P250/P252 forward-blind method) over
  the contracts the checkpoints + architecture flagged: CDPVault, AuraVault, StakingLPEth, PositionAction/
  SwapAction/PoolAction, PoolV3, Flashlender, quotas. Source read directly under `.../contracts/src/`. **The
  base candidate set is the isolated/manual analogue of the frozen base workflow** — comparable to the original
  procedure, not an ad hoc hunt.

## 2. Checkpoint records (advisory inputs — invariants re-verified)
Both outputs: `emits_findings:false`, `concludes_vulnerability:false`, `output_type:reasoning_records`, **0
records carrying severity/concluded** (asserted in-script + re-checked).

| checkpoint | question-records | distinct loci | by-family |
|---|---|---|---|
| accounting | 188 | 126 | A5 idx 60 · A4 shared-depletion 45 · A1 rounding 35 · A3 double-count 34 · A2 conservation 14 |
| state-transition | 50 | 37 | S1 reset/overwrite 19 · S4 branch-not-traced 15 · S2 growable-loop 8 · S3 dual-state 8 |

Core-contract loci the checkpoints fired on (the ones that informed base reading): CDPVault.{deposit,withdraw,
borrow,repay,modifyCollateralAndDebt,liquidatePosition,liquidatePositionBadDebt,calcDecrease} ·
AuraVault.{_convertToShares,_convertToAssets,claim,previewReward,_previewReward,_previewMining} ·
StakingLPEth.{cooldownAssets,cooldownShares} · PoolV3.{deposit,mint,withdraw,redeem,_convertToShares,...} ·
Flashlender.{flashLoan,creditFlashLoan} · SwapAction.{swap,transferAndSwap} · PoolAction.{exit,_pendleExit} ·
PositionAction4626._onIncreaseLever · PoolQuotaKeeperV3.{updateRates,quotedTokens}.

## 1. Frozen base candidate / suspicious-locus set
(severity = blind pre-reveal guess; mechanism = what the base read observed)

| id | sev(blind) | locus | mechanism observed (base) | checkpoint signal |
|---|---|---|---|---|
| **B-1** | Medium | `StakingLPEth.cooldownAssets/cooldownShares` (L104–126) | Each call **overwrites** `cooldowns[msg.sender].cooldownEnd = block.timestamp + cooldownDuration` while `underlyingAmount += assets`. A user mid-cooldown who adds more **resets the whole cooldown** later → funds already cooling are re-locked. | ST S1 reset/overwrite |
| **B-2** | High | `AuraVault.claim` (L280–310) | Caller passes `amounts[0]` (BAL) / `amounts[1]` (AURA) **arbitrarily**; contract pays `amounts[0]` BAL + `amounts[1]` AURA to `msg.sender`, charging `amountIn` WETH computed from the same caller-chosen amounts via oracle. No check that `amounts ≤ actually earned`. | acct A1/A4 on claim/_previewReward |
| **B-3** | Medium | `AuraVault._chainlinkSpot` (L365–379) / `_getAuraSpot` (L381–391) | Chainlink `latestRoundData()` consumed with **no staleness / round-completeness / min-answer** validation (only `price>0` for BAL; none for ETH). Stale/zero feed skews `_previewReward` pricing. | (oracle; not a checkpoint family) |
| **B-4** | High | `CDPVault.liquidatePosition` (L509–574) | Liquidator chooses `repayAmount`; `takeCollateral = repayAmount/discountedPrice`, `deltaDebt = repayAmount·liquidationPenalty`, `penalty = repayAmount·(WAD−penalty)`. Debt reduced by `deltaDebt` while cash and collateral flows use `repayAmount`/`penalty` — penalty/debt-reduction asymmetry; liquidator-controlled. | acct A3 double-count / A4 depletion |
| **B-5** | Medium | `SwapAction.swap` (L139–141) + `PositionAction` residuals (L468–485, L609) / `pendleJoin` (L343) | EXACT_OUT leftover `limit − retAmount` of `assetIn` is sent to **caller-controlled `recipient`**; `pendleJoin` uses `balanceOf(address(this))` (full proxy balance). Residual / other-principal funds can route to an attacker-chosen address across the action layer. | acct A4 depletion / A5 idx on swap |

### Checkpoint-hit suspicious loci with **no** base candidate born
| locus | checkpoint | why no candidate |
|---|---|---|
| `PoolV3.{deposit,mint,withdraw,redeem,_convertToShares,_convertToAssets}` | acct A1/A2/A4 | standard Gearbox-style ERC4626 rounding; no specific divergence seen on blind read |
| `Flashlender.{flashLoan,creditFlashLoan}` | acct A2 conservation | fee/repay conservation looked intact on blind read |
| `PoolQuotaKeeperV3.{updateRates,quotedTokens}` | ST S2 growable-loop | bounded by governance-added quota tokens; no attacker path seen |

## 3. Ranking (strength × signal, pre-reveal)
1. **B-2** AuraVault.claim (High; AAS — caller-chosen reward amounts; strongest blind candidate)
2. **B-4** CDPVault.liquidatePosition (High; AAS+IDC — liquidator-chosen repay, penalty accounting)
3. **B-5** SwapAction/PositionAction residual recipient (Medium-High; CCIT)
4. **B-1** StakingLPEth cooldown reset (Medium; STS)
5. **B-3** AuraVault oracle staleness (Medium; oracle — near-complete chain already)

## 5. Three-way state tag per item (set BEFORE the routine, BEFORE reveal)
This tag is what the five-operation routine's contribution is measured against.

| id | tag | base chain state (pre-routine) |
|---|---|---|
| B-1 | **BASE_BORN_INCOMPLETE** | mechanism seen (cooldown reset); not chained to who-loses/amplification/terminal-state |
| B-2 | **BASE_BORN_INCOMPLETE** | "amounts unvalidated" observed; **not** chained to a concrete attacker profit / drain sequence |
| B-3 | **BASE_BORN_INCOMPLETE (near-complete)** | stale-oracle → mispricing is a known generic chain; impact direction not pinned |
| B-4 | **BASE_BORN_INCOMPLETE** | penalty/deltaDebt asymmetry noticed; who-gains/loses + exact exploit not computed |
| B-5 | **BASE_BORN_INCOMPLETE** | residual-to-recipient seen; cross-principal victim path not traced |
| PoolV3 / Flashlender / quotas loci | **CHECKPOINT_HIT_SUSPICIOUS_LOCUS** | checkpoint fired; no base candidate born |
| (none) | **BASE_COMPLETED_CHAIN** | base completed **0** full chains — consistent with the program thesis (births candidates, doesn't complete) |

---
**FREEZE:** the above is final and recorded before locus selection and before reveal.
Freeze hash recorded in REVEAL_AND_SCORE.md (computed after this file + SELECTED_LOCI.md + PROCEDURE_OUTPUTS.md
are written, before the key is opened).
