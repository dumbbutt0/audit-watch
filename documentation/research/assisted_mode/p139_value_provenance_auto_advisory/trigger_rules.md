# P139 — H-03-class Trigger Rules (conservative)

Auto-run a value-provenance deep-pass job for a `deep_pass_recommendations[]` entry ONLY when ALL hold:
1. `recommended_prompt` ∈ `auto_run_value_provenance_allowed_prompts` (default `["deep_pass_value_provenance"]`).
2. **Re-verified value-provenance signal from the EXACT function body** (read via the coverage_manifest source
   span — no overshoot): a loop (`for`/`while`) with a **value-conversion call** in the loop region
   (`_getValue|convert*|getPrice|getReserves|getAmountOut|toAssets*`). A loop that only assigns mappings / does
   no conversion does NOT qualify.
3. NOT mock/test/fixture (file/contract contains `mock` or a test/fixture path segment).
4. NOT a trivial/empty body.
5. NOT already `confirmed` / `submission_ready`.
6. NOT `research_only` unless `auto_run_value_provenance_surface_research_only=true`.
Caps: `max_per_audit` / `max_total` (default 5).

Does NOT trigger on: generic arithmetic, generic oracle mention, config-setter loops, or every value function.
(During noya measurement this trigger — after tightening — surfaced the H-03 `NoyaValueOracle._getValue` target
and excluded the `updateDefaultPriceSource`/`updateAssetPriceSource` config-setter loops that a looser version
falsely caught.)
