# P205 — L3 scorecard (vultisig src/ bounded sample)

| metric | value | note |
|---|---|---|
| blind surfaces sampled | 8 | src/ ILO only (hardhat codebase out of sample) |
| blind ≥HIGH verdicts | 7/8 | 1 CRITICAL + 6 HIGH + 1 MEDIUM — reproduces P199 over-HIGH skew |
| awarded findings total | 6 | 3 High / 3 Medium (both codebases) |
| awarded findings inside sampled src/ scope | 4 | H-01, H-03, M-02, M-03 |
| awarded findings out of sample (hardhat) | 2 | H-02 (Whitelist.sol), M-01 (VULT burnable) |
| genuine awarded High recall (sampled) | H-01 exact HIT (v-02); H-03 partial (v-03/v-06) | blind recall on genuine Highs is good |
| awarded Medium over-rated to HIGH by blind | 1 (M-03 cap-bypass, v-01) | the L3 demotion target |
| **positive-control High harnessed (preserved)** | **0 — HARNESS_INCONCLUSIVE** | all src/ Highs V3-entangled; 0.7.6 OZ-3.4/v3 deps unavailable |
| **negative-control demote harnessed (executed)** | **1 — v-07, 2/2 PASS** | access-bypass+admin-prereq+no-fund-movement → DEMOTE |
| negative control maps to an awarded finding? | **NO** | v-07 = by-design ILOWhitelist, not awarded H-02 |
| false-High created by L3 | 0 | |
| genuine awarded High wrongly demoted by L3 | 0 | v-07 target is by-design, not awarded |
| production source changes | 0 | hashes byte-identical START==END |
| forge tests passed / total | 2 / 2 | solc 0.7.6, forge 1.5.1 |
| fabrication rate | 0 | every verdict backed by a run log or a documented compile obstacle |

**Net:** the L3 **demotion** side generalizes and was **executed** on a 2nd corpus (capability → demote, v-07). The
L3 **confirmation** side is **HARNESS_INCONCLUSIVE** on vultisig (V3 dependency web), already proven on decent
(P204). No false-High, no false-demotion of an awarded High. → `L3_STANDARD_PARTIAL`.
