# DOS-001 — Integrated PoC (real in-scope 0xMarkets Oracle revert)

This is the **hardened** variant of the DOS-001 PoC. The primary PoC
(`../poc/PoC_ParentBrickOnChildRevert.t.sol`) models the fault with a hand-written `RevertingReader`
stand-in. This variant removes the stand-in entirely: it **deploys the real, in-scope 0xMarkets
`Oracle`** (the GMX-v2-fork contract `contracts/oracle/Oracle.sol` from the bounty repo) and routes
child B's pricing oracle to it. With no primary price set for the index token — the ordinary case for
a view price read outside an oracle-priced keeper transaction — the real `Oracle.getPrimaryPrice`
reverts the real `Errors.EmptyPrimaryPrice`, and that genuine revert bricks every parent operation.

**Headline assertion:** `parentVault.totalAssets()` reverts with the exact
`EmptyPrimaryPrice(indexToken)` selector — the in-scope 0xMarkets error surfaces **verbatim** at the
parent boundary, proving the trigger is real code, not a contrived stand-in.

## What it proves

| Test | Proves |
|---|---|
| `test_RealOracle_RevertsEmptyPrimaryPrice` | The real in-scope `Oracle.getPrimaryPrice(unpricedToken)` reverts `EmptyPrimaryPrice` — the exact production condition. |
| `test_RealOxMOracleRevert_BricksAllParentOps` | That real revert propagates through `CarthaParentVault.totalAssets()`'s unguarded cross-child loop and freezes `totalAssets` / `releaseFromParent` / `processQueuedParentWithdrawals` / `depositAndLockSpread`; the healthy sibling still prices (isolation); restoring a working oracle recovers the parent ($1,000,000) and a real $500k exit succeeds. |

## How to run

The test compiles the real 0xMarkets contracts cross-repo. It lives in an **isolated Foundry profile**
(`integration`) with its own test dir (`test-integration/`) so the default `forge test` / CI never
compiles 0xMarkets and is completely unaffected.

1. Both repos cloned side by side:
   - Cartha: `cartha-vaults-main` (commit `4c51f2a8915f438976b57134d646b55199a11318`)
   - 0xMarkets: `0xMarkets_contract-main` (commit `e94daee6558f90e479c2c967dedae1d7cd06fb0c`) — with its
     `node_modules` installed (provides `@openzeppelin/contracts-v4`, `@chainlink/contracts`, `prb-math`).
2. Place the test at `cartha-vaults-main/test-integration/PoC_RealOxMOracleRevert_BricksParent.t.sol`.
3. Add this profile to `cartha-vaults-main/foundry.toml` (point the `zeromark/` and npm remappings at
   your 0xMarkets clone path):

```toml
[profile.integration]
src = "src"
out = "out-integration"
libs = ["lib"]
test = "test-integration"
solc = "0.8.24"
remappings = [
    "solady/=lib/solady/src/",
    "@openzeppelin/contracts-v4/=<ABS_PATH>/0xMarkets_contract-main/node_modules/@openzeppelin/contracts-v4/",
    "@chainlink/contracts/=<ABS_PATH>/0xMarkets_contract-main/node_modules/@chainlink/contracts/",
    "prb-math/=<ABS_PATH>/0xMarkets_contract-main/node_modules/prb-math/",
    "zeromark/=<ABS_PATH>/0xMarkets_contract-main/contracts/",
]
optimizer = true
optimizer_runs = 50
via_ir = false
```

4. Run:

```bash
FOUNDRY_PROFILE=integration forge test \
  --match-path "test-integration/PoC_RealOxMOracleRevert_BricksParent.t.sol" -vv
```

Expected: `2 passed`. Real 0xMarkets `Oracle` compiles with solc 0.8.24 (no viaIR). See `run_output.txt`.

## Why a mock reader is still used for `getMarket`

The revert in `PoolDeployLib._getGmPrice` originates at `oracle.getPrimaryPrice(mkt.indexToken)` — the
**oracle**, which here is the real in-scope contract. `reader.getMarket(...)` only returns the market's
token addresses (a struct), so it is left as the lightweight mock; standing up a fully-stored market in
a real `DataStore` would not change the revert site or the outcome. The substantive realism — the
genuine `EmptyPrimaryPrice` from real 0xMarkets code reaching the parent — is fully exercised.
