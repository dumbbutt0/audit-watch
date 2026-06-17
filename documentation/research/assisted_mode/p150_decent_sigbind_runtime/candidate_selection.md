# P150 — Candidate Selection (≥3 enumerated)

Restrictions: `duplicate_unknown` (no local answer key); not noya/blackhole/centrifuge/velodrome; prefer small,
source-clean, local-dep, crisp state delta; preferred shapes (sibling parity, batch-vs-single, recipient/accounting
mismatch, missing consume/decrement, preview/execute, authorization subject mismatch, route/loop error); reject
candidates needing live RPC / oracle history / external infra / major dep rewrites / speculative markets.

| # | audit | contract.function | suspected shape | expected state delta | duplicate_unknown? | harness feasibility | likely control/reference | verdict |
|---|---|---|---|---|---|---|---|---|
| A | vultisig-2024-06-holdout | `ILOPool.claim` | recipient / vesting-decrement | claimed-amount delta | yes (no answer key) | **heavy** — 469-line contract; UniV3-core + `ILOVest` + `LiquidityManagement` deps; needs UniV3 pool mocks + vesting math | sibling/decrement reference | **REJECTED** (not deploy-light; not crisp) |
| B | kelp-2023-11-holdout | `LRTDepositPool.depositAsset` / `getTotalAssetDeposits` | accounting mismatch (tracked vs actual) | minted rsETH / deposit count delta | yes | **moderate** — OZ-upgradeable + oracle + RSETH + config + NodeDelegator mocks | corrected accounting reference | **REJECTED** (heavier; less crisp; oracle dep) |
| C | **decent-2024-01-holdout** | **`UTBFeeCollector.collectFees`** | **authorization subject mismatch** — signature over `packedInfo` not bound to executed `fees` | **charges an unsigned fee amount** (signer authorized SMALL, executes LARGE) | yes (no answer key — verified) | **light** — `solmate/Owned` + `forge-std/IERC20` + `FeeStructure`; sign via `vm.sign` | corrected: bind `fees`↔`packedInfo` (reverts); matched control | **SELECTED** |
| (alt) | munchables-2024-05-holdout | `SignatureVerifier` | signature replay / wrong-subject | — | yes | light–moderate | — | considered, not selected (C crisper) |
| (alt) | pooltogether-2024-03-holdout | `PrizeVault` preview/execute | preview vs execute mismatch | — | yes | moderate (ERC4626 vault deps) | — | considered, not selected |

## Why C
Deploy-light (3 small deps; no oracle/RPC/external infra), a **crisp** state delta (charges an amount the signer
never authorized), a clean corrected reference (bind `fees` to the signed `packedInfo`) + matched control, and a
**5th distinct architecture** (cross-chain bridge fee/signature authorization) for cross-architecture yield. Not
biased toward confirmation — the classification followed the runtime result, and reachability/severity is honestly
deferred to human review.
