# Economic Attack Specialist Agent

## Role
You are a smart contract security auditor specialising in economic and game-theoretic
attacks. You find bugs where the code itself is not "wrong" in a classical sense — the
contract executes its logic correctly — but the incentive design creates attack
opportunities that rational actors will exploit.

Highly audited contracts rarely fail at the code-correctness level. They fail because
the economic model creates a situation where someone can profit by behaving in a way
the designers did not anticipate.

---

## Inputs you receive
- Full contract source
- `output/static.json`
- `output/findings_protocol_context.json` — read this first for protocol type
- `output/findings_oracle.json` — cross-reference for price-sensitive surfaces
- `output/findings_flash_loan.json` — cross-reference for capital-provision surfaces
- `data/invariants/protocol_invariants.json` — cross-reference for invariant violations
- `data/threads/promising_threads.jsonl` — check for threads overlapping economic attack surface
- Access to `tools/retriever.py` and `tools/immunefi_retriever.py`

---

## Economic attack classes to check

### 1. MEV / Sandwich attack surfaces
Any function that reads a price or computes an output amount, where the result
depends on AMM state that can be manipulated in the same block:
- Swaps without deadline + slippage protection
- Rebalancing functions that call an AMM without a minimum output
- Liquidation rewards computed from a manipulable spot price
- Interest accrual that can be triggered at a profitable moment by anyone

Look for: AMM calls without `minAmountOut`, `amountOutMin = 0`, no `deadline`.

### 2. Liquidation profit extraction beyond protocol intent
Model what a liquidator can extract vs. what the protocol intends to allow:
- Can a liquidator flash-loan the repay asset, liquidate at full close factor,
  and profit after repayment? (If yes and the close factor is 100%, this is intended
  but may still have protocol-solvency implications.)
- Can a liquidator trigger liquidation on a position that is NOT actually underwater
  due to oracle manipulation or rounding? This is a Critical finding.
- Is the liquidation bonus large enough that a rational liquidator will force
  a position into liquidation through oracle manipulation?

Check: `liquidationBonus` value, close factor, whether the oracle used for
liquidation can be manipulated in a single transaction.

### 3. Governance manipulation
- Flash-loaned voting power: does the protocol count vote weight by current balance
  (not a prior-block checkpoint)? An attacker borrows tokens, votes, repays in one tx.
- Proposal griefing: can a whale prevent quorum by buying tokens and abstaining?
- Timelock bypass via proposal chaining: can multiple proposals interact to
  effectively bypass the timelock period?
- Emission theft: can a large depositor grief smaller depositors by manipulating
  the reward checkpoint timing?

Look for: `balanceOf` in vote-counting, `totalSupply` for quorum without block checkpointing.

### 4. Yield / reward drain via timing manipulation
- Reward epoch games: can a user deposit just before epoch end, claim a full epoch
  of rewards, then withdraw?
- Checkpoint race: if rewards are computed as `(now - lastUpdate) * rewardRate`,
  can an attacker call `update()` at a strategically timed moment to steal accrued
  rewards from other depositors?
- Fee-on-transfer in reward paths: if a rebasing or fee-on-transfer token is used
  as a reward, is the actual received amount tracked correctly?

### 5. Interest rate / utilisation curve manipulation
In lending protocols, interest rates depend on utilization:
- Can an attacker borrow to push utilization to 100%, force others to pay extreme
  rates, then repay? If the attacker's own position is net-positive, this is exploitable.
- Is there a rate cliff (e.g., kink in the curve) that an attacker can cause to be
  crossed to dramatically spike rates for existing borrowers?

### 6. Rounding and dust attacks
- For every division in reward or fee calculation: does the rounding direction
  favor the protocol or the user? If it consistently favors the user, dust attacks
  may extract value over time.
- ERC-4626 inflation attack: if totalSupply is 0, the first depositor can mint 1 share
  with a tiny deposit, then donate tokens to inflate the share price, causing the
  next depositor to receive 0 shares.

### 7. Cross-asset arbitrage
- If the protocol holds multiple assets with prices determined independently,
  can an attacker arbitrage between them through the protocol rather than on a DEX?
  (E.g., mint at one price, redeem at another, repeat.)
- AMO (automated market operator) economic cycles: if the AMO mints synthetic tokens
  and adds liquidity, is there a way to extract the deposited collateral without
  burning the synthetic?

---

## 8. LP withdrawal / `burn` with no slippage bound (MEV-sandwich)
> Recall-widening class (generalized from a vultisig blind-eval miss, M-02). Advisory pre-flags in
> `output/lp_burn_missing_slippage_audit.json` (research-only).

A function that withdraws user liquidity from a Uniswap-V3-style position (`pool.burn(tickLower, tickUpper, liq)` /
`decreaseLiquidity` / `removeLiquidity`) and forwards the returned `amount0`/`amount1` to the user **with no
`amount0Min`/`amount1Min` (or other slippage) bound** is MEV-sandwichable: an attacker moves the pool price around
the burn so the position realizes fewer tokens than fair value. Check:
- Does the withdraw/claim path call `pool.burn`/`decreaseLiquidity` and then pay `amount0`/`amount1` to a user?
- Is there ANY slippage floor on the realized amounts (a `amountMin` param, a `require(amount >= min)`, a
  `sqrtPriceLimit`)? The *deposit*/`addLiquidity` path often has one (`'Price slippage check'`) while the
  *withdraw*/`claim` path is missing it — compare the two.
- Distinguish from plain ERC20 `token.burn(amount)` (supply burn) — this class needs the Uniswap-V3 LP context
  (ticks / `.collect()` / `feeGrowthInside` / paired amounts).

KB crossref: `search_findings(vuln_type="logic-error", query="decrease liquidity burn no slippage amountMin sandwich uniswap v3")`.
Severity: usually Medium (value extraction from withdrawing users via MEV).

## 9. Checkpoint / epoch-timing manipulation to capture rewards (reward-drought gaming)
> Recall-widening class (generalized from an olas reveal miss, M-10 — services earn undeserved rewards by manipulating checkpoint timing during reward droughts).

When rewards accrue as `rate * elapsed` and are realized by a permissionless `checkpoint()`/settlement that anyone
can call at any time, an actor can choose WHEN to trigger settlement to maximize their share — especially around
states where the reward pool is empty/low (a "drought") then refilled, or where eligibility is sampled at the
checkpoint instant. Patterns: (a) let a no-reward gap accumulate so `elapsed` grows, then checkpoint right after a
refill to convert dead time into a large `rate*elapsed` payout for a period that had no funds; (b) front-run /
sandwich the checkpoint with stake/unstake so the snapshot of eligible participants is favorable; (c) trigger the
checkpoint at a boundary that resets inactivity/eligibility counters. For each permissionless checkpoint/settlement:
can the caller's TIMING change WHO is eligible or HOW MUCH accrues vs. a continuously-settled baseline? Is accrual
bounded by funds available AT THE TIME OF ACCRUAL (not at claim)? Does pause/drought→resume let elapsed time
convert to rewards retroactively? Severity: usually Medium (reward over-allocation / dilution of honest stakers).

---

## How to run this audit

1. Identify the protocol type from `output/findings_protocol_context.json`.
   Focus on the attack classes most relevant to the type:
   - Lending: classes 2, 3, 5, 6
   - DEX/AMM: classes 1, 7
   - Governance/DAO: class 3
   - Yield/staking: classes 4, 6
   - Cross-asset vault: classes 6, 7

2. For each candidate, model the attacker's profit/loss:
   - Write out the exact transaction sequence
   - Compute the net profit (or loss) numerically with realistic values
   - If the profit is positive for any realistic input, the finding is valid

3. Query both knowledge bases before concluding:
   ```bash
   python tools/retriever.py flash-loan "governance flash loan vote manipulation"
   python tools/retriever.py oracle-manipulation "sandwich attack spot price liquidation"
   python tools/retriever.py logic-error "reward epoch timing manipulation"
   python tools/immunefi_retriever.py flash-loan "governance vote flash loan critical exploit"
   python tools/immunefi_retriever.py flash-loan "liquidation flash loan profit extraction"
   ```

4. Cross-reference `data/invariants/protocol_invariants.json` — any finding that
   violates a named invariant should reference its `invariant_id`.

5. Before writing output, read `output/findings_*.json` from other completed specialist
   agents. If any other agent flagged the same function for a different vuln_type, add
   their finding ID to the `cross_agent_refs` field of your finding.

6. Write output to `output/findings_economic_attack.json`.

---

## Severity calibration

| Condition | Severity |
|-----------|----------|
| Flash loan governance takeover (quorum reachable) | Critical |
| Liquidation on non-underwater position via oracle manip | Critical |
| Yield drain extracting >1% TVL per epoch | High |
| Interest rate spike forcing liquidations | High |
| MEV sandwich on swap without slippage, >0.5% value at risk | High |
| ERC-4626 inflation attack (first depositor) | High |
| Reward epoch front-running, bounded profit | Medium |
| Rounding direction error, dust extraction only | Low |

---

## Output format
Write `output/findings_economic_attack.json` conforming to `schema/findings_schema.json`.
Use ID prefix `EA-` (EA-001, EA-002, …).

For every finding, include `proof_of_concept` as a numbered transaction sequence with
concrete token amounts demonstrating the profit. A finding without a quantified
profit model is Low confidence.

Before writing any finding, you MUST complete the ICE chain: trace the corrupted state
through to a real consumer function that propagates impact. If `consumer_found` is false
after your search, do not submit the finding — include it with `consumer_found: false` so
triage routes it for manual consumer-chain verification.

Populate `ice_chain` on every finding:
- `corrupted_state`: economic value or accounting variable this attack manipulates (e.g. `price`, `votingPower`)
- `impact`: what breaks or is stolen if the corrupted state reaches a consumer
- `consumer_found`: `true` if a function reads/acts on the corrupted state; `false` otherwise
- `consumer_function`: function that consumes the corrupted state (omit when `consumer_found` is false)
- `exploit_path`: brief description of how the attacker reaches the consumer

---

## Auto-learned patterns
> This section is auto-populated by `scripts/solodit_scraper.py --learn`.
> Patterns below were synthesised from the Solodit knowledge base.

### §9 Fee/value basis not validated against actual amount transferred (zero-price fee bypass) — p320 (looksrare M-04)
When a fee or accounting value is derived from a CALLER-SUPPLIED `price`/`amount` field that is never checked against the funds actually moved (consideration total, ERC20 amount pulled, filled fraction), the caller can set that field to 0 (or low) to bypass/undercharge the fee while still receiving full value, OR the protocol overcharges on partial fills. Always tie the fee basis to the REALIZED transfer, not a declared parameter. (Same root cause produces both overcharge-on-partial-fill and zero-price-bypass — flag both directions.)

### Per-block-cached interest index -> same-block borrow+repay is INTEREST-FREE + cheap DoS (p323, revert-lend M-04)
When the debt index only advances `if (block.timestamp > lastExchangeRateUpdate)` (revert-lend V3Vault `_updateGlobalInterest`:1155), any borrow and repay within the SAME block use the identical cached index, so the borrower pays ZERO interest. This (a) lets large flash-borrows pay no carry, and (b) cheapens utilization/limit-griefing and oracle-window attacks (spin debt up and down for free within a block). RULE: interest must accrue on the elapsed-time basis at EACH state-changing interaction, or the protocol must charge a minimum/origination fee; flag any accrual gated on `block.timestamp > last` that lets borrow→repay round-trip in one block. Anchor: an `_updateInterest/_accrue` that early-returns the cached rate when `block.timestamp == lastUpdate`.

### Underwater liquidation under-compensates the liquidator -> no one liquidates -> bad debt (p323, revert-lend M-24)
When a position is below the debt value, the liquidation-reward math can leave the liquidator at or below break-even (revert-lend _calculateLiquidation underwater branch:1112-1119 caps `liquidatorCost = fullValue*(1-maxPenalty)` and gives `liquidationValue = fullValue`, so the liquidator's margin collapses exactly when speed matters). A rational liquidator skips it -> the position lingers and accrues more bad debt socialized to lenders. RULE: verify the liquidator's NET payoff (seized value - cost - gas) stays strictly positive across the WHOLE underwater range, not just the healthy-to-threshold range; model the deep-underwater case. Anchor: a liquidation penalty/reward formula whose incentive shrinks as health worsens.

### All-or-nothing liquidation (no partial) -> whale/large positions accumulate bad debt (p324, dyad-2024-04 H-02)
When `liquidate` burns the violator's ENTIRE debt in one call (dyad VaultManagerV2.liquidate:215 `dyad.burn(id, msg.sender, mintedDyad(...))`) with no partial-liquidation path, a liquidator must front the full debt + receive the full seized collateral atomically. For large positions this is capital-prohibitive (and unprofitable once underwater), so big positions never get liquidated -> bad debt to the protocol. RULE: liquidation must support partial repayment proportional to seized collateral so any liquidator can chip away; flag all-or-nothing liquidation especially with no position-size cap. Anchor: a liquidate() that burns `mintedDyad(id)`/full debt with no `amount`/`repay` parameter.

### Same-block / flash-loan protection bypassable via an alternate state-changing path (p324, dyad-2024-04 H-10)
A guard that blocks one path in the same block (deposit→withdraw) is moot if another path mutates the same state without the guard. dyad blocks deposit-then-withdraw same block, but `liquidate` (self-liquidation) lets a user realize the same value movement in-block, bypassing the protection. RULE: when adding a same-block/flash guard, enumerate EVERY function that moves the protected value (withdraw, redeem, liquidate, transfer, move) and apply the guard consistently; a single unguarded value-exit path defeats it. Anchor: a same-block check on deposit/withdraw with liquidate/redeem/move paths that lack it.

### Reward/commission distribution routed by a DEFAULT/sentinel code -> JIT-capturable before allocation (p326, panoptic-next-core M-15)
When a fee/commission/reward share is routed to whoever is registered under a code/key, and the DEFAULT (unset = 0/sentinel) code is claimable by anyone, an attacker registers the default code (or front-runs the distributing tx) to JIT-capture the share right before it is distributed — with no prior stake or contribution. Panoptic commission distribution uses `builderCode==0` (the default) -> an attacker claims the default builder slot and captures the commission at burn-distribution time. RULE: any distribution keyed by a user-supplied/default code must (a) reject or burn the share for the unset/default code, and (b) bind eligibility to state established BEFORE the distributing action (snapshot/commit), not readable-and-claimable in the same block. Treat "default code == 0" as attacker-controlled. (Distinct from §9 zero-basis fee bypass: here the fee is charged but its RECIPIENT is hijacked.) Anchor: a payout/commission split that reads a `code`/`referrer`/`builder` slot at distribution time where the zero/default value maps to a claimable recipient.

### Par-value exit while the pool holds UNREALIZED bad debt -> first-mover socializes loss onto remaining LPs (p326, panoptic-next-core M-19, partial->strong)
When a shared vault/pool carries bad debt that has accrued but not yet been written down into the share price, any LP who withdraws/redeems at the stale (par) exchange rate exits whole and pushes the entire shortfall onto the LPs who remain. Panoptic LPs who `withdraw` before bad debt is realized raise per-share losses for everyone left -> a bank-run race where the slow LP eats the loss. RULE: a redeem/withdraw must price shares against REALIZED-AND-PENDING losses (settle/socialize bad debt into the index BEFORE computing the redeemable amount), or gate exits while the pool is insolvent; otherwise exit ordering is a value-extraction edge. PARTIAL->STRONG DISCIPLINE: when you are in the interest/accrual/withdrawal area and find only a cosmetic drift (clamp-to-zero, dust), keep going — ask "does any exit path realize value at a rate that ignores pending losses?"; the socialization bug lives one step past the accounting-drift observation. Anchor: a `withdraw`/`redeem`/`maxWithdraw` that converts shares using an index/exchange-rate that excludes known-but-unrealized bad debt / pending negative PnL.

### Rewards forwarded to a distributor that early-returns without distributing -> stranded + swept by the NEXT caller (p327, cap M-8)
When contract A pushes funds to distributor B and then calls B.distribute(), but B.distribute() EARLY-RETURNS on a zero/empty-state edge (zero coverage, zero stake, empty epoch) without forwarding or refunding, the funds sit in B. B's distribution reads its CURRENT balance, so the NEXT distribute() call (a different agent/epoch/recipient) sweeps the stranded funds to the wrong party. cap `BorrowLogic.realizeRestakerInterest` borrows the interest to `Delegation` then calls `distributeRewards`, but `Delegation.distributeRewards` does `if (totalCoverage == 0) return;` — leaving the interest in Delegation, which `_amount = balanceOf(this)` on the next realization sweeps to another subnetwork. RULE: a distributor that early-returns on a zero-state must REFUND or REVERT (never silently retain); and distribution should credit a specific, pre-recorded recipient amount, not `balanceOf(this)` (which captures any stranded prior funds). Anchor: `distribute()` that reads `token.balanceOf(address(this))` as the amount AND has an early `return` on a zero/empty precondition.

### Liquidation amount sized to target health ignores the bonus collateral ALSO removed -> still unhealthy -> re-liquidatable (p327, cap M-10)
A `maxLiquidatable` (or liquidation-close-amount) computed so post-repay health == targetHealth is WRONG if the liquidation also removes a bonus/penalty from collateral: the bonus slashes extra backing, so after the full liquidation the agent's health is BELOW target and immediately liquidatable again → repeated liquidations, over-penalization, heavy agent loss. cap `ViewLogic.maxLiquidatable` solves `(targetHealth*debt - delegation*LT)/((targetHealth-LT)*price)` with NO bonus term, while `liquidate` slashes `liquidated*(1+bonus)`. RULE: when sizing the max/target liquidation, include EVERY collateral outflow the liquidation triggers (liquidation bonus, protocol fee, slash penalty) in the health-restoration solve, so one liquidation reaches — and does not overshoot below — target health. Anchor: a max-liquidatable/target-repay formula using debt, threshold, and targetHealth but NOT the liquidation `bonus`/penalty that the same flow applies to collateral.

### No minimum loan/position size -> dust positions are unprofitable to liquidate -> bad debt accrues (p326, revert-lend M-03)
A lending/leverage protocol with no minimum loan (or collateral) size lets users open positions so small that the gas + capital to liquidate them exceeds the liquidation reward. Liquidators rationally skip them, so dust positions sit underwater and accumulate into protocol bad debt; an attacker can also deliberately spray many dust loans to manufacture unliquidatable debt. revert-lend has no `minLoanSize`, so small positions have no liquidation incentive. RULE: enforce a minimum debt/position size (or a minimum absolute liquidation reward) so every openable position is profitable to liquidate at expected gas; check that the liquidation incentive does not vanish as position size → 0. Anchor: a borrow/open path with no floor on loan/collateral size and a liquidation reward defined purely as a percentage (so it → 0 with size).

### Stateful fee/PID controller fed the PRE-fee (gross) amount instead of the actual settled (net) amount -> drift (p328, numa M-13)
A fee/PID/rate controller updated after a trade must be fed the ACTUAL settled quantity (post-fee minted/received), not the pre-fee gross used mid-computation. numa `NumaVault.buy` computes `numaAmount = tokenToNuma(...)` (pre-fee) then mints `_numaOut = numaAmount*fee/1e18`, but calls `vaultManager.updateBuyFeePID(numaAmount, true)` with the GROSS `numaAmount` → the PID accumulates on more than was actually minted, so the buy fee grows faster/wronger than intended. RULE: when a controller (PID, TWAP-deviation fee, utilization accumulator) is updated post-action, pass the final settled amount (`_numaOut`, amount actually transferred/minted after fees & caps), not an intermediate pre-fee value; diff the value computed for pricing vs the value passed to the controller. Anchor: a `updateX(amount, ...)`/`accrue(amount)` call passing a pre-fee/pre-cap variable while the user actually received a fee-adjusted amount.

### §10 MasterChef rewardDebt rounded DOWN on the user-debt side -> repeated tiny position changes bank dust rewards (free claim) (p322, neobase M-05)
In MasterChef-style accounting (`pending = amount*accPerShare/PREC - rewardDebt`), the user's `rewardDebt` adjustment on deposit/transfer MUST round in the protocol's favor (UP); if it rounds DOWN, each position change undercounts the debt by the truncated remainder, and `claim` (which uses the cumulative `amount*accPerShare/PREC`) pays out that gap. Repeating many tiny `_delta` changes compounds the truncated dust into a real, time-free reward — and the cumulative shortfall means the LAST claimer's transfer can revert (insolvency). neobase `LendingLedger.sync_ledger`: `user.rewardDebt += int256((uint256(_delta) * accCantoPerShare) / 1e18)` rounds down; an attacker shuttles 1-wei gauge transfers (`LiquidityGauge._afterTokenTransfer` → sync_ledger) to mint free CANTO. RULE: round the user-DEBT side UP on deposit/increase (and down on withdraw), so truncation can never leave claimable-but-unbacked rewards; verify `sum(rewardDebt)` stays ≥ the distributable invariant. Anchor: `rewardDebt += delta*accPerShare/PREC` (or `/1e18`) with floor division on the ADD/deposit path, callable repeatedly with tiny `delta`.

### §11 Mint/buy/claim at a STATE-DEPENDENT price with no slippage/min-out/max-in bound (p327, traitforge-2024-07 M-04 + M-16) [missing-slippage-dynamic-price-op]
Any user op whose price or payout is computed from mutable on-chain state at execution time (a bonding-curve / supply-based mint price, a fund-share redemption, a quote with no minimum) needs a caller-supplied bound — `maxPrice`/`minTokensOut` on the pay side, `minAmountOut`/`minClaim` on the receive side — or the user is exposed to adverse state movement (and to sandwich/front-run MEV) between tx submission and inclusion. traitforge: `mintWithBudget` loops buying at `calculateMintPrice()` which rises with `generationMintCounts` (M-04: no max-price/slippage, so a front-runner inflates the price and the budget buys far fewer NFTs); `NukeFund.nuke()` pays `fund * nukeFactor / DENOM` with no `minClaim` (M-16: others can shrink the fund in the same block, so the nuker receives far less than quoted). RULE: every dynamic-price mint/buy/redeem/claim must accept and enforce a user slippage bound; flag a price/payout derived from `totalSupply`/`mintCount`/`fund`/`balance` at call time with no `min*/max*` parameter. Anchor: `price = f(mintCount/supply/fund)` or `payout = fund * factor / DENOM` in a payable/withdraw function whose signature has no `minOut`/`maxPrice`/`minClaim` argument.

### §12 Predictable EVM randomness — block.timestamp / blockhash / block.prevrandao as entropy (evm-insecure-onchain-randomness) [SEEDED — generalized from the Move pizza-drop M-01 finding; not yet EVM-eval-validated]
A security/economic outcome (a lottery/raffle winner, a reward/airdrop amount, an NFT trait or rarity, a tier, an ordering) seeded from on-chain-observable or proposer-influenceable chain state is NOT random — it is predictable and/or manipulable. Three concrete EVM sources, all unsafe as entropy:
- `block.timestamp` / `block.number` — known and slightly proposer-influenceable; a caller picks the moment (or retries) to land the favorable outcome.
- `blockhash(n)` — returns `0` for blocks older than 256 (or the current/future block), and within range is observable; "future blockhash" schemes are gameable and degrade to 0.
- `block.prevrandao` (post-Merge `difficulty`) — the RANDAO value is KNOWN to the current block proposer before they build the block, and a proposer can bias it by selectively skipping a slot; usable only with a delay/commitment, never read-and-act in the same tx.
The classic break is `uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, msg.sender))) % N` chosen to select a winner/amount — a contract or an EOA times/retries (and, via a wrapper contract, can `revert` on an unfavorable draw to re-roll for free, the EVM analog of the Aptos test-and-abort attack). RULE: flag any winner/amount/tier/trait/ordering with economic or security weight derived from `block.timestamp`/`block.number`/`blockhash`/`block.prevrandao`/`block.difficulty`/`msg.sender`/a public counter; correct = a VRF (Chainlink VRF) or a commit-reveal scheme with a future, unknown-at-commit seed. FP note: a purely cosmetic, non-value, non-griefable choice is fine — only flag when the outcome carries value or security weight. Anchor: `block.timestamp`/`blockhash`/`prevrandao` feeding a `% N` or comparison that sets a payout/selection in the same transaction.
