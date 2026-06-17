# P137 — Blind Prompt Output (verbatim, fresh uncontaminated subagents)

Four fresh general-purpose subagents, each given ONLY the `deep_pass_value_provenance` prompt + one inlined code
bundle, instructed to reason solely from the provided code (no file/repo/answer-key access). I authored none of
the analysis below.

## T1 — H-03 target: NoyaValueOracle._getValue (4-arg) — agent a415b317c731d866a
**decision: `finding` (confidence high)** · shape: "stale/static loop-carried identity: hop conversion uses
static `asset` instead of updated `quotingToken`".
- `validated_subject`: quotingToken (loop-carried 'from' token, updated to sources[i], correctly used only in the
  post-loop final call).
- `mutated_subject`: static parameter `asset`, used as the source token in every in-loop hop call.
- `divergence_point`: in-loop `initialValue = _getValue(asset, sources[i], initialValue)` — uses static `asset`
  while `initialValue` is denominated in the previous hop token; validated != used for every iteration i ≥ 1.
- `claimed_effect`: for any route with ≥2 hops, intermediate conversions price an amount denominated in
  sources[i-1] using the asset→sources[i] oracle → incorrect total valuation.
- repro_hint: priceRoutes[asset][base]=[s0,s1]; distinct oracles for priceSource[asset][s1] vs priceSource[s0][s1];
  call getValue(asset,base,amount) with a 2-hop route; i=1 computes _getValue(asset,s1,valueInS0) instead of
  _getValue(s0,s1,valueInS0).
- Critic (disproof attempts, all failed): single-hop routes are correct (bug needs ≥2 hops); the two priceSource
  mappings resolve distinct oracles so not equivalent; view used for valuation → not benign.

## T2 — control (single-hop oracle): ChainlinkOracleConnector.getValue — agent aa18ffa65d9186e3d
**decision: `needs_human` (confidence medium)** · shape: "wrong-subject decimals/unit selection".
- Flags the inverse branch: `decimalsSource = isPrimaryInverse ? baseToken : asset` while `amountIn` is always in
  `asset` units → potential 10**(baseDec−assetDec) mis-scale. Routed to needs_human (cannot confirm without
  `getSourceOfAsset` / feed convention). **No confident false finding.**

## T3 — control (CPA-caught TVL): MorphoBlueConnector._getPositionTVL — agent a32013fa2ec920670
**decision: `finding` (confidence high)** · shape: "sign/role-misclassification-in-aggregation (liability summed
as asset)".
- `divergence_point`: the `+ borrowAmount` term — debt ADDED to TVL instead of subtracted; correct = supply +
  collateral − borrow. Effect: TVL overstated by 2× borrow → NAV inflation. (NB: my packet annotated supply/
  collateral=asset, borrow=DEBT — a role hint that aided this control; see optional_controls.md.)

## T4 — control (clean): MorphoBlueConnector.convertCToL — agent aaf1c69722bcd64e2
**decision: `strong_clear` (confidence high)**.
- `amount * price / ORACLE_PRICE_SCALE` matches intended semantics exactly; derived subject == used subject;
  unused `collateral` param / oracle-pairing classed as external trust, not an internal provenance bug.
  **No over-flag on the clean control.**
