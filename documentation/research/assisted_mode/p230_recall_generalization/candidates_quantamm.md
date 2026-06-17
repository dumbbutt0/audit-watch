# P230 measurement artifact — QuantAMM (Oracle-heavy) blind candidate set

Subject: `audits/quantamm-2024-12-eval` (oracle-driven Balancer-V3 weighted pool / TFMM). Keys SEALED (not opened).
Method: blind Sonnet deep_trace pass driven by `prompts/deep_trace.md` + `agents/{oracle,arithmetic,economic_attack,logic,access_control,behavioral_state_analysis}.md` + `config/{units_invariant_patterns,defi_accounting_patterns}.json`.
Full raw output: session tool-result `toolu_01PEKyFaY1i5C4G52ZLuXz18.json`. Tally: 25 candidates — HIGH 8 · MED 9 · LOW 4 · NOISE 1.

| id | title | bug class | contract | conf | signal |
|---|---|---|---|---|---|
| QAMM-01 | uplift-fee setter overwrites swap-fee (shared storage slot) | state-transition | UpdateWeightRunner | Confirmed | HIGH |
| QAMM-02 | removeOracle auth check after state change (CEI) | access-control | UpdateWeightRunner | Confirmed | MED |
| QAMM-03 | numAssetOracles==1: staleness revert unreachable → stale primary used | oracle | UpdateWeightRunner | High | HIGH |
| QAMM-04 | int216 downcast of scaled Chainlink price unchecked | arithmetic | ChainlinkOracle | Medium | LOW |
| QAMM-05 | calculateBlockNormalisedWeight negative-mult underflow at interp boundary (CYFRIN H02) | arithmetic/invariant | QuantAMMWeightedPool | High | HIGH |
| QAMM-06 | normalizeWeightUpdates residual can push weight below guard rail | invariant-violation | QuantammMathGuard | Medium | MED |
| QAMM-07 | MultiHopOracle no per-hop zero/negative price validation | oracle | MultiHopOracle | Medium | MED |
| QAMM-08 | onAfterRemoveLiquidity `i>=0` uint loop / underflow-OOB | arithmetic | UpliftOnlyExample | High | HIGH |
| QAMM-09 | getPoolLPTokenValue double-scales already-18-dec price → 1e18-inflated deposit value into fee calc | accounting/arithmetic | UpliftOnlyExample | High | HIGH |
| QAMM-10 | uplift-fee proportional change via integer division → truncates to 0 for <100% growth (fee never charged) | economic | UpliftOnlyExample | Confirmed | HIGH |
| QAMM-11 | _splitWeightAndMultipliers packing for 5–8 token pools | state-transition/arith | QuantAMMWeightedPool | Speculative | LOW |
| QAMM-12 | 18→9→18 pack/unpack precision loss breaks weight-sum invariant | arithmetic/invariant | QuantAMMStorage | Confirmed | MED |
| QAMM-13 | afterUpdate stores uint32(block.number) into uint40 timestamp field | arithmetic | UpliftOnlyExample | Confirmed | MED |
| QAMM-14 | setRuleForPool permissionless → any caller registers as pool (pre-registration DoS) | access-control | UpdateWeightRunner | High | HIGH |
| QAMM-15 | privilege if/else-if locks admin out when both mask bits set | access-control/logic | UpdateWeightRunner | High | MED |
| QAMM-16 | _clampWeights rescales only upper-clamped weights → sum-to-one broken with interior weights | invariant/arith | QuantammMathGuard | High | HIGH |
| QAMM-17 | DifferenceMomentum re-init allowed via OR condition | state-transition | DifferenceMomentumUpdateRule | High | MED |
| QAMM-18 | setWeights has no value validation (defense-in-depth) | access-control/invariant | QuantAMMWeightedPool | High | MED |
| QAMM-19 | getData MASK_POOL_GET_DATA config DoS on deposit | access-control/logic | UpliftOnlyExample/UWR | High | MED |
| QAMM-20 | variance rule prev-MA OOB read for future REQUIRES_PREV_MAVG=0 | state-transition/logic | QuantammVarianceBasedRule | Speculative | LOW |
| QAMM-21 | unpack index0 arithmetic shift vs int32 cast (no diff) | arithmetic | QuantAMMStorage | Speculative | NOISE |
| QAMM-22 | FILO pop/delete ordering + uint underflow (same root as QAMM-08) | state-transition/logic | UpliftOnlyExample | Confirmed | MED |
| QAMM-23 | ChainlinkOracle missing answeredInRound staleness check | oracle | ChainlinkOracle | High | MED |
| QAMM-24 | absoluteWeightGuardRail uint64→int64→int256 narrowing cast | arithmetic | UpdateWeightRunner | Medium | LOW |
| QAMM-25 | epsilon speed-limit measured from drifting interpolated weight, not last-set | logic | UpdateWeightRunner | Speculative | LOW |
