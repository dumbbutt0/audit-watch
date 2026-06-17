# concrete — Phase 2: Mechanism Selection Gate (PRE-REVEAL, FROZEN)

3 subtle loci (all BASE_BORN_INCOMPLETE; ≥3 mechanisms each). p242-exposed families excluded.
8-dim scores H/M/L.

---
## C-L1 — `WithdrawalQueue.prepareWithdrawal` finalize/claim state semantics
**No-hindsight lock:** selected for the queue's claimable-state invariant (when is a request payable); signal =
ST S2/S4 on prepareWithdrawal; base saw the finalize guard direction + strict availability check; remained
incomplete = which of several state-semantic errors is the awarded one.
Mechanisms (3):
- **M1 finalization-direction inversion** — `if (_requestId < lastFinalizedRequestId) revert` permits preparing/claiming requests with `requestId > lastFinalizedRequestId` (i.e. **not yet finalized**), and reverts only on older ones ⇒ claim an unfinalized (unbacked) withdrawal ⇒ premature fund release. [ctrl H · delta H · v/g H · comparand H(lastFinalizedRequestId exists for exactly this) · term H · amp H · simpl M · award H]
- **M2 strict-availability off-by-one** — claim body runs only if `_avaliableAssets > amount` (strict) ⇒ an exact-match (`==`) withdrawal is never processed, `claimed` never set ⇒ funds stranded / griefing. [ctrl M · delta M · v/g M · comparand M · term M · amp L · simpl M · award M]
- **M3 no partial fill** — if `_avaliableAssets < amount`, nothing happens and the request persists unclaimed with no progress ⇒ head-of-line blocking. [ctrl M · delta L · v/g M · comparand L · term M · amp L · simpl L · award L]
- `SELECTED_MECHANISM`: **M1 finalization-direction inversion (claim unfinalized request)**. `RUNNER_UP`: **M2 strict-availability off-by-one strand**. `REFUTED`/demoted: M3.
- `AWARDED_LIKENESS_REASON`: claiming a not-yet-finalized withdrawal is a direct premature-release / fund-loss shape; `lastFinalizedRequestId` is the exact comparand showing intended behavior.
- `WHY_SELECTED_OVER_RUNNER_UP`: M1 is attacker-controllable + extractable (High) vs M2's griefing/strand (Med); M1's comparand is unambiguous.
- `WHAT_WOULD_FALSIFY`: if the vault only ever calls prepareWithdrawal with `_requestId <= lastFinalizedRequestId` (caller-enforced) so the inverted guard is unreachable, M1 is void → falls to M2.

## C-L2 — `Vault.takeFees` HWM + protocol/performance fee
**No-hindsight lock:** selected for fee-accrual correctness (dilution + HWM timing); signal = A1/A3 on
accruedProtocolFee + fee mint; base saw HWM set from pre-mint shareValue + time-based protocol fee; remained
incomplete = winner/loser + magnitude.
Mechanisms (3):
- **M1 protocol fee on totalAssets including unrealized/idle** — `accruedProtocolFee = totalAssets*Δt*rate` charged via share mint regardless of profit ⇒ depositors diluted continuously even with flat/negative performance. [ctrl M · delta H · v/g H · comparand M · term H · amp H · simpl M · award M]
- **M2 HWM update-timing** — `highWaterMark = convertToAssets(1e18)` set from shareValue computed **before** fee shares are minted; after dilution actual shareValue is lower ⇒ HWM set too high ⇒ subsequent performance fees undercharged (protocol loses) OR mis-set enabling repeated fee. [ctrl L · delta M · v/g M · comparand M · term M · amp M · simpl M · award M]
- **M3 fee-share dilution rounding** — `feeInShare = totalFee.mulDiv(supply, _totalAssets - totalFee)` ⇒ `_totalAssets - totalFee` denominator inflates feeInShare; edge when totalFee≈totalAssets. [ctrl L · delta M · v/g M · comparand L · term M · amp M · simpl L · award M]
- `SELECTED_MECHANISM`: **M1 protocol fee on full totalAssets via share-mint dilution (charged without gains)**. `RUNNER_UP`: **M2 HWM pre-mint timing**. `REFUTED`/demoted: M3.
- `AWARDED_LIKENESS_REASON`: management/protocol fee minted as shares on total (idle) assets, diluting depositors, is a recognized fee-accounting award shape.
- `WHY_SELECTED_OVER_RUNNER_UP`: M1 has clear continuous value-delta + victim (all depositors) + amplification; M2's direction/magnitude is ambiguous.
- `WHAT_WOULD_FALSIFY`: if protocol fee rate is 0 / governance-bounded to negligible, or fee mint is offset elsewhere, M1 is void.

## C-L3 — `Vault._withdrawStrategyFunds` allocation withdraw
**No-hindsight lock:** selected for the multi-strategy withdrawal accounting; signal = A4/A5 on
_withdrawStrategyFunds; base saw the diff-vs-amount_ basis mismatch + Ceil; remained incomplete = net effect.
Mechanisms (3):
- **M1 diff-vs-amount_ basis mismatch** — revert-guard checks `diff.mulDiv(allocation,…)` (diff = amount-float) but the actual withdraw uses `amount_.mulDiv(allocation,…)` (full amount) ⇒ when `float>0` the vault withdraws ~`amount_` from strategies **plus** ignores float ⇒ over-withdrawal / wrong receiver amount / leftover. [ctrl M · delta M · v/g M · comparand H(diff is the intended basis) · term M · amp M · simpl M · award M]
- **M2 Ceil per-strategy over-withdraw dust** — `Math.Rounding.Ceil` on each strategy's share ⇒ Σ amountToWithdraw > amount_ ⇒ systematic small over-withdrawal drained over many calls. [ctrl M · delta M · v/g M · comparand M · term M · amp H(repeat) · simpl M · award M]
- **M3 allocation-proportional loss realization** — withdrawing proportionally across strategies realizes strategy slippage/loss onto the withdrawing user (or remaining holders). [ctrl L · delta M · v/g M · comparand L · term M · amp M · simpl L · award M]
- `SELECTED_MECHANISM`: **M1 diff-vs-amount_ basis mismatch (over-withdraw when float>0)**. `RUNNER_UP`: **M2 Ceil dust over-withdraw**. `REFUTED`/demoted: M3.
- `AWARDED_LIKENESS_REASON`: a guard computed on one basis (diff) while the action uses another (amount_) is a precise accounting-mismatch shape.
- `WHY_SELECTED_OVER_RUNNER_UP`: M1 has the strongest comparand (the guard itself uses `diff`, revealing intent) and a larger per-call delta than M2's dust.
- `WHAT_WOULD_FALSIFY`: if allocations always sum to 100% AND float is always 0 in the else-branch (amount_>float ⇒ float< amount_, but float can be >0), making amount_≈diff, M1's delta shrinks to dust → falls to M2.

**FREEZE:** selections final before completion + reveal.
