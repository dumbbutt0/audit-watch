# P290 — EVIDENCE_AND_READY_GATE (blind, salty)

Ran deriver (P279/P282/P283/P284 + **P289 lenses**) + gate (P281/P285). severe FP=0, guard PASS.
status_tally: **READY 1 · NEEDS_VALUE_FLOW_EVIDENCE 3 · NEEDS_STATE_MACHINE_EVIDENCE 1 · INLINE_GUARD_REFUTED 5.**

## P289 lens result: **0 lens firings** across all 10 candidates
No loss_on_stake / bad_debt_contagion / reward_index_init / share_transfer_theft lens matched on any salty candidate —
including the staking/rewards loci (StakingRewards.claimAllRewards, Airdrop.allowClaiming) and the collateral/liquidation
loci. The lens multi-signal coupling (verb + state-term + per-user/global write + path-term, in-span) was not satisfied
in these candidates' own spans (the loss/index/checkpoint state lives in callees or separate accounting contracts). **The
P289 lenses did NOT generalize to salty.**

## The one READY — Pools.deposit (EXTERNAL_INTEGRATION) — NOT lens-driven, NOT source-faithful
Reached READY via the pre-existing **P279 EXTERNAL_INTEGRATION class template** (attacker MEDIUM / impact HIGH / victim
MEDIUM; invariant_delta = NO_REFERENCE; generic assertion "a crafted external/callback response leaves Pools state
inconsistent"). **Source (pre-reveal, in-scope):**
```
function deposit(IERC20 token, uint256 amount) external nonReentrant {
    require(amount > PoolUtils.DUST, "Deposit amount too small");
    _userDeposits[msg.sender][token] += amount;
    token.safeTransferFrom(msg.sender, address(this), amount);   // standard pull; only the comment notes fee-tokens
    emit TokenDeposit(...);
}
```
This is a `nonReentrant` deposit with a standard `safeTransferFrom` and **no external callback** — the template's
"crafted callback" mechanism is **speculative / not source-faithful**. This is a P279-template precision miss, not a
P289-lens result, surfaced blind.

## Other candidates (precise blocks)
3 NEEDS_VALUE_FLOW (claimAllRewards, withdrawCollateralAndClaim, depositLiquidityAndIncreaseShare — value-flow present,
no source-backed deviation/lens), 1 NEEDS_STATE_MACHINE (Pools.withdraw), 5 INLINE_GUARD_REFUTED (real guards: Upkeep.
step2, Airdrop.allowClaiming, liquidateUser, USDS.mintTo, DAOConfig admin). severe FP=0.
