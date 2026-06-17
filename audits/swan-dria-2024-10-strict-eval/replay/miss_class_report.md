# Swan/Dria miss-class replay vs new validators

Frozen source (read-only, copied): `/home/dummy/clones/audit-watch/smart-contract-auditor/audits/swan-dria-2024-10-strict-eval/output/pre_answer_key_snapshot`

## A. Literal frozen replay (new validators over the exact frozen clears)
- cleared dispositions classified: **57**
- new math blocks: `{'missing_math_proof': ['function:LLMOracleManager:getFee#f5466b9b'], 'incomplete_math_proof': ['function:LLMOracleRegistry:isRegistered#17bd39d8', 'function:Swan:list#1da48835']}`
- new dependency/locality blocks: `{'missing_dependency_metadata': ['function:Statistics:sqrt#7d4961a9', 'function:BuyerAgent:withdraw#b159b818', 'constant:?:SwanBuyerPurchaseOracleProtocol#8c969aea', 'constant:?:SwanBuyerStateOracleProtocol#b1261fe9']}`  (guard_not_path_dominant = **0**)
- **getFee** literal status → math:`missing_math_proof` dep:`finding_linked_dependency`
  - before/after taxonomy patch: `not_math_estimator_sensitive (cheap-swept; <<-by-variable not a signal)` → `missing_math_proof`
  - RESOLVED by the economic-shift taxonomy patch: getFee `2 << difficulty` now classifies math-sensitive (fee/difficulty economic terms next to a shift, no bitmask context) → math:`missing_math_proof` → routes to math_estimator_review instead of cheap-sweep. Before the patch it was not_math_estimator_sensitive.
- new-blocked manifest_ids: `['constant:?:SwanBuyerPurchaseOracleProtocol#8c969aea', 'constant:?:SwanBuyerStateOracleProtocol#b1261fe9', 'function:BuyerAgent:withdraw#b159b818', 'function:LLMOracleManager:getFee#f5466b9b', 'function:LLMOracleRegistry:isRegistered#17bd39d8', 'function:Statistics:sqrt#7d4961a9', 'function:Swan:list#1da48835']`

### Baseline delta (blocks NET-NEW from the shipped change vs frozen validation baselines)
- net-new **dependency/locality** blocks: `NONE` (frozen baseline already blocked: `['constant:?:SwanBuyerPurchaseOracleProtocol#8c969aea', 'constant:?:SwanBuyerStateOracleProtocol#b1261fe9', 'function:BuyerAgent:withdraw#b159b818', 'function:Statistics:sqrt#7d4961a9']`)
- net-new **math** blocks: `['function:LLMOracleManager:getFee#f5466b9b', 'function:LLMOracleRegistry:isRegistered#17bd39d8', 'function:Swan:list#1da48835']` (frozen baseline blocked none of these — they were `math_proof_valid` under the old 14-field proof)
  - net-new dependency blocks should be 0 (locality adds guard_not_path_dominant only when a non-local guard is asserted, which the frozen clears do not); net-new math blocks = the pre-adversarial-proof clears now missing the 5 fields PLUS getFee, which the economic-shift taxonomy patch now classifies math-sensitive (was cheap-swept) — intended stricter routing, all clears, none a HIT finding

### Noise audit (items the economic-shift patch newly routes to math review)
- in-scope manifest items: 74 · math-sensitive now: 10 · newly routed by economic-shift: **1**
- newly routed: `['getFee']`
- economic-shift ∩ HIT surface: `EMPTY` (no HIT finding is newly routed)

## B. Reconstructed miss-class fixtures (derived from the frozen clear text)
- **getFee** math-sensitive: `True` · with confirmatory proof → **`confirmatory_proof`** · proofless → **`missing_math_proof`** (→ needs_deep_pass under strict)
  - reasons: ['intended_formula matches implemented_formula without an external source (whitepaper/protocol_docs/derived_in_review) or an independent economic-direction analysis', "re-derivation asserts internal consistency ('appears intended'/'matches the code') without citing a non-code source", 'monotonicity_and_economic_direction names no economic variable (fee/stake/difficulty/price/reward/weight/…) — direction never checked']
- **round** field-presence gate → **`guard_not_path_dominant`**; with call graph → **`guard_not_path_dominant`**
  - non-local guard requires guard_locality in {same_contract_dominates, cross_contract_dominates} with path_dominance_evidence

## C. FP check on the 9 HIT findings
- HITs: ['H-01→SC-01', 'M-01→SC-02', 'M-02→SC-03', 'M-03→SC-05', 'M-05→SC-09', 'M-06→SC-12', 'L-01→SC-11', 'L-02→SC-04', 'L-07→SC-10']
- new-blocked functions: `['getfee', 'isregistered', 'list', 'sqrt', 'swanbuyerpurchaseoracleprotocol', 'swanbuyerstateoracleprotocol', 'withdraw']`
- new-block ∩ HIT surface: `EMPTY` (validators only classify `status:cleared`; all 9 HITs are findings)

## Verdict
- getFee no longer cleared by implemented-formula consistency: **True**
- non-local guard no longer clears the missing local round check: **True**
- zero new false-positive blocks on the 9 HIT findings: **True**
