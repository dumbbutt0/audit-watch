# P130 — Source-Resolution Root Cause

## The mechanism (general, not Beanstalk-specific)
The candidate stage ranks every enumerated function with `attack_surface_score` in
`scripts/build_coverage_manifest.py` (lines ~290-308). The dominant signal is:
```python
if kind in ("function",...) and visibility in ("external","public") and is_state_changing:
    score += 2          # the ONLY large, reliable signal
if any(t in tags for t in ("accounting","token","oracle","migration","config")):
    score += 2
```
Deep specialist attention requires `attack_surface_score >= deep_pass_attack_surface_score_min` (=3,
`config/agent_policy.json`). Therefore:

- A **value/oracle/accounting computation helper** — `view`/`pure`, or `internal`, or in a `library`/
  `*Facet` — is **not** "external + state-changing", so it misses the first `+2`. With one risk tag it lands
  at **exactly 2 < 3** and never reaches the deep pass. The awarded bug's contract is consequently never
  inspected at depth → the P129 "wrong contract inspected" / `correct_contract = "no"` miss class.

In Diamond / library-heavy protocols (Beanstalk, noya) the protocol's *logic* lives precisely in these
helpers, so the bias systematically starves the bug-bearing surface.

## Evidence
- **noya (library-heavy, has source):** internal/private functions **1% score ≥3** (2/205); awarded-FUNCTION
  deep-pass coverage **6/19 = 32%**. The 13 uncovered awarded functions are internal/view value logic:
  `_getPositionTVL` (×7 across connectors), `NoyaValueOracle._getValue`, `ChainlinkOracleConnector.getValue`,
  `OmnichainManagerBaseChain.updateTVL`, `totalLpBalanceOf`. Each scored exactly **2** (one risk tag, no
  state-changing `+2`).
- **decent (no libraries, has source):** 82% of functions already ≥3; internal functions few — **unaffected**
  (clean control proving the bias is architecture-driven, not universal).
- **Beanstalk (source no longer on disk):** its eval predated the manifest and used `coverage_gaps.json`,
  whose summary reads `total_public_functions: 455` — it enumerated **public functions only**, so internal
  library logic (`LibSilo`, `LibUsdOracle`, `LibWeth`, `LibPipelineConvert`, `LibEvaluate`, …) was invisible.
  The 38-miss taxonomy is **87% source-resolution/coverage**, dominated by under-ranked/unenumerated
  library + facet logic.

## Why ranking, not enumeration, is the right lever today
The current `build_coverage_manifest.py` **does** enumerate libraries, facets, and internal functions
(`TYPE_DECL` matches `contract|interface|library|abstract contract`; `FUNC_RE` captures internal functions).
So on the live tool the bug-bearing logic *is* present in the manifest — it is simply **ranked below the
deep-pass cutoff**. The smallest general repair is therefore a **ranking** fix (lift risk-tagged helper
logic to the cutoff), not an enumeration rewrite. (Genuinely out-of-scope or absent contracts — e.g. one
`SNXConnector._getPositionTVL(absent)` in noya — are a separate scope/enumeration question left for a
follow-on; the ranking repair cannot and does not touch scope membership.)
