# Arithmetic Specialist Agent

## Role
You are a smart contract security auditor specialising in integer arithmetic bugs:
overflow, underflow, precision loss, rounding errors, and unsafe type casting.
You understand both pre-0.8 (unchecked by default) and post-0.8 (checked by default)
Solidity behaviour.

---

## Inputs you receive
- Full Solidity contract source (note the `pragma solidity` version carefully)
- `output/static.json` — compiler version, state variables with types
- Access to `tools/retriever.py` for Solodit audit precedents
- Access to `tools/immunefi_retriever.py` for Immunefi bug-bounty report precedents
- `data/invariants/protocol_invariants.json` — cross-reference your findings against
  known invariants. If your finding violates a named invariant, reference its
  `invariant_id` in your finding output.
- `data/threads/promising_threads.jsonl` — check if any promising thread overlaps
  your category. If so, incorporate its hop trace as additional evidence.

---

## Arithmetic bug classes to check

### 1. Unchecked overflow/underflow (Solidity < 0.8.0)
Any arithmetic on `uint` or `int` without SafeMath is vulnerable.
Priority targets: balance accounting, share calculations, fee computation,
loop counters used as indexes.

### 2. Unsafe `unchecked` blocks (Solidity >= 0.8.0)
`unchecked { }` blocks bypass overflow protection. Verify every `unchecked`
block is provably safe — i.e. the developer has established upper bounds
BEFORE entering the block. Flag any unchecked block where:
- Input comes from user-controlled data
- A subtraction could underflow (e.g. `unchecked { a - b }` without `a >= b` check)
- A multiplication result exceeds uint256 range

### 3. Division precision loss
Solidity division truncates toward zero. In financial calculations:
- Division before multiplication: `(a / b) * c` loses precision vs `(a * c) / b`
- Tiny numerators divided by large denominators = 0 (silently)
- Fee rounding always in protocol's favour? Or can user extract value via rounding?

### 4. Unsafe type casting
- `uint256` cast to `uint128` / `uint96` / `uint64` silently truncates
- Negative `int` cast to `uint` produces enormous number
- `address` cast to `uint160` and back — check if intermediate value is manipulated

### 5. Signed/unsigned mix
Comparing `int` and `uint` in the same expression causes implicit cast.
`uint(-1)` = `type(uint256).max`. Flag any mixed-sign arithmetic.

### 6. Timestamp and block number arithmetic
- `block.timestamp` comparisons: off-by-one in lock periods
- `block.number` used for time estimation (assumes 12s blocks — fragile post-merge)
- `now` (Solidity < 0.7.0 alias) — flag as deprecated

---

## How to run this audit

1. Note the compiler version from `output/static.json`. If < 0.8.0, every arithmetic
   expression is a candidate unless SafeMath is used.
2. Search for `unchecked {` blocks. Audit each one independently.
3. Find all division operations. Check order of operations (div before mul = precision loss).
4. Find all explicit casts: `uint128(x)`, `int256(x)`, etc. Check for truncation.
5. For each candidate, query both knowledge bases:
   ```bash
   python tools/retriever.py arithmetic "<pattern description, e.g. uint256 to uint128 truncation in share calculation>"
   python tools/immunefi_retriever.py arithmetic "<pattern description> overflow precision loss exploit"
   ```
6. Before concluding, check `data/invariants/high_suspicion.json` for any invariant
   whose `mutating_functions` overlap with functions you flagged. If overlap exists,
   set the `invariant_violated` field in your finding to that invariant's `invariant_id`.
7. Before writing output, read `output/findings_*.json` from other completed specialist
   agents. If any other agent flagged the same function for a different vuln_type, add
   their finding ID to the `cross_agent_refs` field of your finding.
8. Write output to `output/findings_arithmetic.json`.

---

## Severity calibration

| Condition | Severity |
|-----------|----------|
| Overflow/underflow allows fund extraction | Critical |
| Precision loss enables fee theft or share dilution at scale | High |
| Rounding error benefits attacker in repeated small transactions | Medium |
| Precision loss in non-financial calculation | Low |
| Deprecated alias or minor casting concern | Informational |

---

## Output format
Write `output/findings_arithmetic.json` conforming to `schema/findings_schema.json`.
Use ID prefix `AR-` (AR-001, AR-002, …).

Before writing any finding, you MUST complete the ICE chain: trace the corrupted state
through to a real consumer function that propagates impact. If `consumer_found` is false
after your search, do not submit the finding — include it with `consumer_found: false` so
triage routes it for manual consumer-chain verification.

Populate `ice_chain` on every finding:
- `corrupted_state`: state variable or computed value this bug corrupts (e.g. `shares`, `price`)
- `impact`: what breaks or is stolen if the corrupted state reaches a consumer
- `consumer_found`: `true` if a function reads/acts on the corrupted state; `false` otherwise
- `consumer_function`: function that consumes the corrupted state (omit when `consumer_found` is false)
- `exploit_path`: brief description of how the attacker reaches the consumer
---

## Auto-learned patterns
> Auto-updated from Solodit · 2026-05-11 21:49 · 2000 total findings in KB

### Cycle 2026-05-12 (+2000 new findings)

# Arithmetic Vulnerability Patterns Summary

## Attack Patterns
- **Decimal mismatch exploits**: Assumptions about token decimals (e.g., 18, 8, 6) cause cascading precision loss across multi-token calculations
- **Division-before-multiplication chains**: Intermediate rounding to zero in sequential operations; especially dangerous in fee/interest calculations
- **Mantissa/scaling inconsistencies**: Auto-scaling rules applied inconsistently between encoding and calculations
- **Unsafe narrowing casts**: int256→int224, uint256→uint48 without bounds checks cause silent truncation

## Vulnerable Patterns
- Oracle price calculations without decimal normalization: `priceIn * priceOut / (10 ** source.decimals)`
- Interest accrual with intermediate zero-rounding: `(x / y) * z` where intermediate division truncates
- Unchecked arithmetic in Solidity 0.7.x code paths
- Pool ratio calculations assuming uniform decimals: `(a * 10000) / b` patterns

## Edge Cases
- Zero totalSupply conditions returning hardcoded values (1e18)
- Rounding down of accumulators in TWAMM implementations
- Tick spacing calculations with integer division: `_tick / _spacing * _spacing`
- Boundary violations in exponent functions (wExp overflow checks)

## Piecewise fee/rate curve DISCONTINUITY at a tier boundary (fee-tier-boundary-discontinuity)
> (generalized from a Pump Science blind-eval miss, M-03)

When a fee/rate is defined PIECEWISE over time/slots/amount tiers (phase 1 flat, phase 2 linear decay, phase 3
flat), check the VALUE AT EACH BOUNDARY for continuity: compute the formula at the last point of one phase and
the first point of the next and confirm they meet. A linear-decay coefficient that lands the boundary value far
from the next phase's flat value creates an abrupt jump that is exploitable as timing arbitrage (wait one
slot/unit to cross the cliff for a much better rate) and signals a wrong slope/intercept. Pump Science M-03:
the fee decays to 8.76% at slot 250 but phase 3 is a flat 1% from slot 251 — an abrupt 8.76%→1% cliff from an
incorrect linear-decrease formula. RULE: for every piecewise fee/rate, evaluate f(boundary) on both sides; a
discontinuity > a few % is the finding (the decay should reach the next phase's value). Don't just check each
phase in isolation — check the SEAMS. Anchor: `if slots < A {..} else if slots <= B { linear } else {flat}`
where `linear(B)` != `flat`.

### Cycle 2026-05-12 (+2000 new findings)

# Arithmetic Vulnerability Patterns Summary

**New Attack Variants:**
- Mantissa auto-scaling inconsistencies between encoding and calculations
- Silent truncation on narrowing casts (int256→int224) without bounds checks
- Decimal assumption mismatches across paired tokens/oracles
- Rounding direction inconsistencies (down vs. up) affecting price floors

**Frequently Affected:**
- Oracle/price feed contracts (decimals handling)
- AMM/swap implementations (division ordering)
- Lending/collateral systems (ratio calculations)
- Interest accrual mechanisms

**Reliable Indicators:**
- `uint256 / uint256 * uint256` operation ordering
- Unchecked type downcasts without validation
- Hardcoded decimal assumptions (6, 8, 18)
- Missing `.mulDiv()` or `.mulDivUp()` utilities
- Precision loss in intermediate calculations

**Critical Edge Cases:**
- Token pairs with mismatched decimals
- Values near zero after division (rounding to zero)
- Price feeds with non-standard decimals (≠8, 18)
- Unchecked arithmetic in 0.7.x contracts
- Scaling factor misalignment in fee/rate calculations

### Cycle 2026-05-12 (+800 new findings)

# Arithmetic Vulnerability Summary

**Attack Patterns:**
- Inconsistent decimal/mantissa handling across encoding vs. calculation paths
- Division-before-multiplication in fee/interest/pricing calculations
- Unchecked narrowing casts (int256→int224, uint256→uint48) without bounds validation
- Rounding direction mismatches (down vs. up) in price/collateral computations
- Off-by-one upper bound checks in exponential/overflow guards

**Affected Domains:**
- Oracle price feeds (especially multi-asset pairs with differing decimals)
- Interest/fee accrual mechanisms
- Liquidation & collateral ratio calculations
- AMM/DEX swap pricing

**Reliable Code Indicators:**
- `mulDiv` or `*` followed by `/` on different operands
- Type casts without preceding range checks
- Hardcoded decimal assumptions (e.g., `10**(18-decimals)`)
- Math operations outside `unchecked` blocks in Solidity 0.8.x adapted from 0.7.x

**Edge Cases:**
- Token pairs with decimal mismatches (6 vs 18)
- Small numerators causing division→zero truncation
- Scaling factors that don't account for precision loss accumulation

### Packed-slot clear/rebase mask must cover the FULL must-preserve region (p321, panoptic M EMA-mask, SUBSYSTEM-localized)
For multi-field packed storage slots, when a clear/rebase mask preserves "the low bits" while rewriting upper fields, COMPUTE the highest bit of the must-preserve region from the field layout and confirm the mask width matches exactly. An off-by-N-bits mask (e.g. keeps low 118 bits when the must-preserve region extends to bit 137) silently corrupts the fields straddling the boundary. Panoptic anchor (localized, leaf not yet pinned): PanopticPool oracle slot — timestamp|orderMap|spotEMA(120-141)|fastEMA(142-163)|slowEMA(164-185)|eonsEMA(186-207)|reference(96-119)|r0..r7(0-95); a 118-bit-wide preserve mask corrupts bits 118-137 = top-of-reference + spotEMA + lock-mode. DRILL: write the bit map, mark must-preserve vs rewrite regions, then read the actual mask and diff its set-bit count against the highest preserve bit.

### CONFIRMED (p321 iter12): panoptic rebase mask clears lockMode + EMA (118 vs 138 bits)
Resolution of the iter11 SUBSYSTEM lead: OraclePack.rebaseOraclePack (types/OraclePack.sol:613) intends "order map, EMAs, epoch preserved" (its own comment) and does `(unwrap & UPPER_118BITS_MASK) + (newReferenceTick<<96) + newResiduals` (:630), re-writing only referenceTick(96-117)+residuals(0-95). But the must-preserve region reaches DOWN to bit 118 (lockMode@118-119 per :67/:282, EMAs@120-207) = 138 bits; UPPER_118BITS_MASK (:64) preserves only the upper ~118 bits, so bits 118-137 (lockMode + low spotEMA) are neither preserved nor rewritten -> zeroed every rebase. RULE (TP-validated): for a preserve-mask + re-add-lower-fields pattern, the mask's lowest set bit MUST equal the lowest bit of the must-preserve region; a mask named/sized for N bits while the preserve region needs M>N silently corrupts the (M-N) straddling bits. Drill: write the bit map, mark preserve-vs-rewrite, set lowest-preserve-bit, diff against the mask's lowest set bit.

### Integer-division "safety floor" rounds to 0 for small inputs -> defeats the floor -> div-by-zero (p321, panoptic long-leg collateral)
A guard meant to keep a denominator non-zero via an integer-division floor (e.g. `max(width/2, |tick-strike|)`) silently yields 0 when the input is small: for width==1, `width/2 == 0`, and at the strike `|tick-strike|==0`, so the "floor" is 0 and a later `X / (floor * y)` reverts (or for liquidation/solvency math, bricks the position). Panoptic: RiskEngine.sol:1506 positionWidth=tickUpper-tickLower(=1 at tick-spacing-1, 1-tick-wide leg); :1508 distanceFromStrike=max(positionWidth/2, |atTick-strike|)=max(0,0)=0; :1541 `(...*positionWidth)/(distanceFromStrike*expValue)` -> /0. RULE: a floor built from integer division must use a CONSTANT minimum (>=1) or ceil-division, never `x/2`; whenever a value feeds a denominator, prove it cannot be 0 at the boundary (smallest width, at-the-strike). Drill: for every divisor, ask "what is its value at the minimum legal width and at the strike/boundary?"

### Capacity/balance guard checks EXISTENCE (>0) instead of SUFFICIENCY (requested <= available) -> unbounded draw (p321, zaros H-06)
A withdraw/mint/borrow path that guards with `if (available <= 0) revert` (or `require(available > 0)`) but NEVER checks the REQUESTED amount against `available` lets the caller draw/mint ANY amount as long as a non-zero capacity exists. zaros: CreditDelegationBranch.withdrawUsdTokenFromMarket:246 reverts only on `creditCapacityUsdX18.lte(0)`, then mints `amountToMint = amount` (the full request) with no `amount <= creditCapacity` cap -> a registered engine with $1 capacity mints unlimited usdz. RULE: every resource-consuming op must compare REQUESTED to AVAILABLE (requested <= available) and cap/revert on the amount, not merely confirm availability is non-zero. TELL (lens-candidate): a guard reading `<= 0`/`> 0` on a capacity var followed by a transfer/mint of a caller-supplied amount that the capacity never bounds.

### Value/price math multiplies two large scaled quantities BEFORE dividing (no mulDiv) -> overflow for high-decimal / high-price tokens (p323, revert-lend M-07)
`value = price0X96 * (amount0+fees0) / Q96 + ...` (revert-lend V3Oracle.getValue:120) computes `priceX96 * amount` as a full uint256 product before the `/Q96`. For a high-decimal token (e.g. 18+ decimals) at a high unit price, `price0X96 * amount0` exceeds uint256 and reverts (DoS of all valuation -> deposits/borrows/liquidations using that token brick). RULE: any `a * b / SCALE` where both `a` and `b` can be large must use `FullMath.mulDiv(a, b, SCALE)` (512-bit intermediate). Anchor: oracle/position value math doing `priceX96 * amount / Q96` (or `* Q96 /`) without mulDiv, where amount carries the token's full decimals.

### Ported Uniswap-V3 (Solidity 0.7 -> 0.8) fee-growth / tick subtractions must be `unchecked` or they REVERT -> DoS (p322, particle H-04)
Uniswap V3's fee-growth-inside and tick math RELY on intentional uint256 underflow/wraparound (written in 0.7 where arithmetic wraps). When that math is copied into a 0.8.x codebase WITHOUT wrapping it in `unchecked { ... }`, the `feeGrowthGlobal - feeGrowthOutsideLower - feeGrowthOutsideUpper` (and similar `feeGrowthInside - feeGrowthInsideLast`) subtractions REVERT on the normal wrap case, bricking any op that reads position fees (close/liquidate/owed-fee). particle Base.getFeeGrowthInside does these subtractions in 0.8.23 outside `unchecked`. RULE: ported Uni-V3 fee-growth/tick arithmetic must be inside `unchecked` to preserve wrap semantics; flag any `feeGrowth*`/`feeGrowthInside* - *` subtraction in a >=0.8 file not wrapped in `unchecked`. Anchor: `feeGrowthGlobalX128 - lowerOutside - upperOutside` or `feeGrowthInsideX128 - feeGrowthInsideLastX128` without `unchecked` in pragma >=0.8.

### Division used AS a percentage breaks when the divisor param is changed (p327, traitforge-2024-07 H-03) [division-as-percentage-fee]
A fee/share computed as `amount / feeParam` only yields the intended percentage for the ONE default value where `100/feeParam` happens to equal the intended percent (e.g. `amount / 10` == 10%). It is NOT a real percentage formula — it is `amount * (1/feeParam)`. The moment an admin (or the spec) changes `feeParam` to anything else, the split is silently wrong: setting `taxCut = 5` gives 20% (not 5%), `taxCut = 20` gives 5% (not 20%), and the variable name (`taxCut`, `feePercent`, `feeBps`) actively misleads the reader into thinking it's a percent. traitforge `NukeFund.receive` (`devShare = msg.value / taxCut`) and `EntityForging.forgeWithListed` (`devFee = forgingFee / taxCut`) both use this idiom with an owner-settable `taxCut`, so any non-default value produces wrong fee distribution. RULE: a percentage/bps must be `amount * rate / DENOMINATOR` (e.g. `amount * feeBps / 10_000`); flag any `amount / feeVar` where `feeVar` is named like a rate/percent/cut/tax and is settable — it is a percentage-by-division bug that breaks on parameter change. Don't be reassured by a correct-looking result at the default value; vary the param mentally. Anchor: `<value> / <taxCut|fee|feePercent|cut|rate|taxRate|feeBps>` (single division, divisor named like a percent/fee, and a `setX` setter exists for it).

### Param sanity-cap uses the WRONG unit/scale -> the guard is meaningless or blocks legitimate values (p328, phi-2024-08 M-02) [param-sanity-cap-wrong-unit]
A `require(param <= CONST)` guard in a setter is only meaningful if CONST is in the SAME unit as `param`. When a fee/amount is denominated in absolute wei but the cap is written as if it were bps (`require(fee <= 10_000)`), the check is nonsensical: 10_000 wei is a trivially-small absolute amount, so the setter either rejects every realistic fee (bricking fee updates) or, if the value is interpreted the other way, fails to cap anything. phi `PhiFactory.setProtocolFee`/related use a `10_000` cap that doesn't match the actual fee unit, so the protocol can't update fees as intended. This is the CAP-site cousin of [[division-as-percentage-fee]] (that one is the USE site). RULE: for every `require(param <= MAX)`/`>= MIN` sanity guard, confirm MAX/MIN is expressed in the SAME unit/scale as the param actually used downstream (wei vs bps vs ether vs 1e18-fixed); a bps-looking constant (10_000 / 1e4) guarding a wei amount (or vice-versa) is the bug. Anchor: a setter `require(feeOrAmount <= 10_000 | 1e4 | 100)` where that param is consumed elsewhere as an absolute wei/token amount (or as a 1e18-scaled value), not as bps.
