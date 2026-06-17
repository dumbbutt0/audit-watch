# idOS contracts — HackenProof bug-bounty audit notes

Auditor: Audit-Watch (Claude). Real hunt, local-only, nothing submitted (user does PoC + submission; $1 fee,
POC required, Critical SC scope). Repo `idos-network/contracts` @ `ebbae56b3bf3598dc9794032dd3df37c772cfe8d`
(master). Foundry; pragmas `^0.8.27`/`^0.8.20`; deps OZ 5.5.0 (soldeer) + forge-std. In-scope SC files (3):
`src/IDOSToken.sol`, `src/IDOSVesting.sol`, `src/IDOSNodeStaking.sol` (web/API/enclave/facesign OUT of SC toolkit).

## ENV (working)
`forge soldeer install` (OZ 5.5.0 → dependencies/); copy forge-std into lib/; stash out-of-scope CCA contracts
(BatchCaller/CCADisbursementTracker/TDEDisbursement) + script/ (need continuous-clearing-auction submodule).
Build/test: `forge build|test --use ~/.solc-select/artifacts/solc-0.8.35/solc-0.8.35` (0.8.35 satisfies pragmas;
svm 0.8.27 unfetchable). Builds clean.

## IDOSToken.sol — SOUND (honest negative)
Verbatim OZ `ERC20 + ERC20Burnable + ERC20Permit`; fixed 1B supply minted once to treasury in ctor; no further
mint, no fee/pause/blacklist; receive/fallback revert. Nothing custom → no finding.

## IDOSVesting.sol — SOUND (honest negative)
Inherits OZ `VestingWallet + VestingWalletCliff`; the `_vestingSchedule` override is **verbatim from OZ's own
documented example** (cliff guard + the OZ caveat comment). All logic = audited OZ; ctor cliff≤duration validated
by OZ's VestingWalletCliff. No finding.

## IDOSNodeStaking.sol — the only custom contract; reward MATH conserves, but 3 real issues (PoCs pass)
Epoch (1-day) staking; per-(user,node) stake; per-epoch pro-rata reward replayed via a per-user checkpoint
(`rewardAcc/userStakeAcc/totalStakeAcc`); owner slashing; 14-day unstake queue. PoCs: `test/zzz_IDOSNodeStakingPoC.t.sol`.
- **No over-draw (confirmed)**: `stakedByEpoch[i]=Σ stakeByUserByEpoch[i]` and `stakeByNode=Σ stakeByNodeByUser`
  hold ⇒ `Σ_user userStakeAcc==totalStakeAcc` ⇒ per-epoch payouts sum to `epochReward` (rounded down).
  `test_conservation_sumEqualsEpochReward` PASS (sum==1000e18). So no Critical reward-inflation drain.

### F-A (Medium) — No time-weighting → JIT reward capture / honest-staker dilution (permissionless)
`stake` credits `stakeByUserByEpoch[currentEpoch()]`, and `withdrawableReward` applies that at FULL weight in the
epoch's `rewardAcc += userStakeAcc*epochReward/totalStakeAcc` — no fraction-of-epoch weighting. So a deposit made
1 second before an epoch boundary earns the SAME epoch reward as one staked the whole epoch.
PoC `test_JIT_noTimeWeighting` PASS: alice(24h) and bob(1h) each get 500e18; bob withdraws 500 immediately.
Impact: a late-epoch staker dilutes full-epoch stakers' rewards; reward (not principal) is claimable next epoch
with no delay (only the 14-day delay applies to principal withdrawal). Real reward-distribution flaw; severity
tempered by the 14-day principal lock and that epoch-snapshot accounting is arguably a design choice.

### F-B (High, conditional on funding) — Rewards paid from the SAME balance as principal; no segregation
**Standalone write-up: `F-B_report.md`. FORK-VALIDATED on live Arbitrum One.**
The contract has NO reward-funding/accounting function (only `setEpochReward` sets a number); `withdrawReward`
(L280) transfers reward `idosToken` straight from the contract balance, which otherwise holds only staker
PRINCIPAL (in L119 `stake`, out L185 `withdrawUnstaked`). If the reward budget is not separately (out-of-band)
funded above obligations, reward claims are paid out of pooled principal first-come-first-served, and later
unstakers cannot withdraw their full stake. Contradicts NM-0731 System Overview ("rewards… without affecting the
principal stake"); NOT among NM-0731's 6 findings → novel.
- Local PoC `test_rewardClaimEatsPrincipal` PASS: 2×100 staked (bal 200), epochReward 50; alice claims 25 reward
  (bal→175); both unstake 100; alice withdraws 100 (bal→75); **bob's withdrawUnstaked REVERTS — only 75 for a 100
  obligation → exact shortfall 25 principal.**
- Fork PoC `test/zzz_IDOSNodeStaking_ForkPoC.t.sol` (2 tests PASS, `https://arb1.arbitrum.io/rpc`):
  identity asserted (code≠0, idosToken==0x68731…, EPOCH_LENGTH=1d, UNSTAKE_DELAY=14d). **LIVE posture @ epoch 144:
  balance 26,938,533.96 IDOS vs principal 26,411,601.41 → buffer 526,932.54 (~2% of principal), deficit 0** (so
  presently solvent for principal, but razor-thin & unenforced). Loss reproduced on live bytecode+token: 2 dominant
  stakers (100M each via deal), owner setEpochReward(2X) unfunded, warp 1 epoch, alice claims 88.33M reward →
  bal 138.6M; both unstake; alice withdrawUnstaked → 38.6M; **bob's 100M withdrawUnstaked REVERTS (insolvent for
  principal).** Read-only fork + local sim, no live tx.
(If the team always funds rewards ≥ obligations, no loss — but nothing enforces it; buffer is only ~2%.)

### F-C (Low/Medium) — Unbounded loops → gas-griefing/DoS that grows over time
`withdrawableReward` loops `checkpoint.epoch → currentEpoch()` — for a first-time staker checkpoint.epoch=0, so it
replays EVERY epoch since startTime (with a nested `slashesByEpoch[i].values()` loop) ⇒ after enough epochs, new
stakers' `stake()`/`withdrawReward()` exceed the block gas limit (can't join/claim). `getUserStake` (used in
`unstake`) loops ALL `slashedNodes` globally; `withdrawUnstaked` re-scans a `delete`-gapped array. Grows unbounded.

## VERDICT: IDOSToken/IDOSVesting honest negatives. IDOSNodeStaking reward MATH is conservative (no over-draw),
## but has F-A (no time-weighting/JIT, Medium), F-B (reward-from-principal/no funding segregation → principal loss
## if underfunded, High-conditional), F-C (unbounded-loop gas-DoS, Low/Med). All PoC-backed (3 tests pass).
## None is an unconditional Critical permissionless drain. Nothing submitted — user reviews/submits.
