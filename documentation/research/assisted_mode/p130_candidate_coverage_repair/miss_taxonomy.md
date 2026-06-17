# P130 — Beanstalk Miss Taxonomy (38 misses)

Source: `evals/beanstalk_finale/match_matrix.json` (per-miss `failure_reason`, `correct_contract`) +
`awarded_contract_yardstick.json` (contract tokens extracted from each public finding — read-only eval
yardstick, never used in production logic). `correct_contract = "no"` on **all 38** misses.

The 12-category label is **derived** from `failure_reason` + the target contract type (library / facet /
other). It is interpretive for misses whose title carried no extractable contract token (`other`);
`failure_reason` is the authoritative signal.

| Category | n | Class | P130-addressable |
|---|---|---|---|
| candidate_cutoff_excluded_correct_contract | 13 | source-resolution | ✅ (under-ranked logic) |
| contract_in_scope_but_low_ranked | 7 | source-resolution | ✅ (under-ranked logic) |
| library_or_helper_not_mapped | 6 | source-resolution | ✅ (library/helper logic) |
| inherited_function_not_mapped | 5 | source-resolution | ⚠️ partial (depth, post-coverage) |
| proxy_or_facet_alias_failure | 2 | source-resolution | ⚠️ partial (facet routing) |
| unknown (domain / triage) | 5 | reasoning/domain | ❌ out of P130 scope |

**Source-resolution / coverage: 33/38 (87%).** Directly addressable by the P130 under-ranking repair
(library/facet/helper logic that exists + is in-scope but never reaches the deep-pass cutoff): **26/38 (68%).**

Target contract types among misses (where extractable): library 10, facet 6, other/unclassified 22.

### Representative examples
- `candidate_cutoff_excluded_correct_contract`: `LibUsdOracle` USD price path; `LibSilo.transferStalk`
  rounding; `LibDibbler` block-time constants — internal library logic, never deep-passed.
- `library_or_helper_not_mapped`: `LibPipelineConvert` grown-stalk-on-BDV-drop; `LibEvaluate.evalPrice`.
- `contract_in_scope_but_low_ranked`: `TractorFacet` counter getter; `DepotFacet` hardcoded PIPELINE;
  `SeasonGettersFacet.totalDeltaB`.
- `proxy_or_facet_alias_failure`: L1/L2 `BRIDGE` address mismatch; multiple-sunrise architecture.
- `unknown` (out of scope): permit-token incompatibility (domain knowledge), found-but-not-escalated (triage).

### Categories with zero observed misses
`contract_not_in_scope_manifest`, `function_missing_from_manifest`, `source_path_normalization_failure`,
`interface_vs_implementation_confusion`, `detector_filter_excluded_correct_contract`,
`wrong_contract_inspected` (as a *literal* category — folded into low-ranked/cutoff above). Note: Beanstalk's
eval predated the manifest and used `coverage_gaps.json` (public-function-only enumeration), so internal
library logic was effectively `function_missing_from_manifest` *at that time*; on the current manifest tool
the same logic is enumerated but under-ranked, which is why the repair targets ranking, not enumeration.

**Takeaway:** the dominant, generalizable miss class is **risk-bearing library/facet/helper logic that is
enumerated and in-scope but ranked below the deep-pass cutoff** — exactly what P130 repairs.
