# P207 — L3 scorecard (vultisig 2nd corpus, positive + negative)

| metric | value |
|---|---|
| dependency assembly | RESOLVED (OZ v3.4.0 + v3-core v1.0.0, no v3-periphery; isolated in pocs/p207/lib) |
| target contracts compile (no source edit) | YES (58 files, solc 0.7.6) |
| **H-01 (awarded High) — positive control** | **HIGH_CONFIRMED** (executed material fee loss: B's 40e18 → feeTaker, B claim reverts) |
| H-01 control (single investor) | claims fine, 200e18, feeTaker 0 (defect needs multi-user commingling, not the mock) |
| **M-03 (awarded Medium) — negative control** | **MEDIUM_OR_LOWER** (cap bypassed 200e18>100e18 but full price paid, no theft) |
| genuine awarded High preserved by executable material impact | 1 (H-01) |
| awarded Medium demoted executably | 1 (M-03) — a **genuine awarded finding** (closes P205's gap) |
| false-Highs created by L3 | 0 |
| genuine awarded High wrongly demoted | 0 |
| forge tests passed / total | 3 / 3 |
| production source changes | 0 (hashes byte-identical START==END; realsrc `d9489e47`) |
| fabrication rate | 0 |

## Does P205 PARTIAL convert to VALIDATED?
**YES.** P205 established the demotion side and reproduced the over-HIGH skew but left the positive High-preservation
side `HARNESS_INCONCLUSIVE` purely due to dependency assembly. P207 assembles the deps (OZ 3.4 + v3-core, no periphery)
and executes **both** sides on the same 2nd corpus: H-01 `HIGH_CONFIRMED` (preserve) + M-03 demoted — a clean
two-sided separation with 0 false-Highs and 0 false-demotions.

## Limitations (honest)
- The V3 pool is a faithful single-position model, not the canonical full `UniswapV3Pool` (deploying a real pool +
  real swap was avoided for budget). Faithfulness is argued + isolated by the single-investor control test; principal
  composition is simplified (token0-only fees) which is conservative and does not manufacture the fee bug.
- `ManagerStub` supplies the project config the real `ILOManager` would; the real `ILOPool`/`ILOManager` logic runs
  unmodified. H-03/M-02 (other src/ awarded findings) not harnessed — out of the two-control scope.
