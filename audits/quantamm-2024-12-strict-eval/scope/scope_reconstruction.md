# QuantAMM 2024-12 — Scope Reconstruction

**Reconstructed independently from the repository README scope block, per-package `foundry.toml`,
contract pragmas, and `package.json` — NOT from the answer key (post-freeze only).** Confidence: **HIGH**.

## Target
- Repo: `github.com/Cyfrin/2024-12-quantamm` @ `a775db4273eb36e7b4536c5b60207c9f17541b92`
- Platform: CodeHawks `2024-12-quantamm` · Prize pool 49,600 OP (44,640 H/M + 4,960 Low)
- Contest window: 2024-12-20 12:00 UTC → 2025-01-15 12:00 UTC · nSLOC reported: 3359
- The repo is a snapshot/fork of the Balancer V3 monorepo; QuantAMM adds a custom TFMM (Temporal
  Function Market Making) pool type whose weights change between blocks.

## In scope — 25 contracts (3 packages)
**`pkg/pool-quantamm/contracts/`**
- `UpdateWeightRunner.sol` — singleton coordinator of inter-block weight updates ("perform update"),
  oracle data gathering (optimised + backup caches), rule registration/gating, final weight setting.
- `QuantAMMWeightedPool.sol` — reserves & trading; G3M-per-block weighted pool; `getNormalizedWeights`,
  multiplier/interpolation, Balancer V3 pool surface.
- `QuantAMMWeightedPoolFactory.sol` — pool creation/registration.
- `QuantAMMStorage.sol` — packed 9dp/18dp weight+multiplier SSTORE pack/unpack helpers.
- `ChainlinkOracle.sol`, `MultiHopOracle.sol` — oracle wrappers (Chainlink, multi-hop A→B).
- `rules/` — `UpdateRule.sol` (base `CalculateNewWeights` w/ guards + moving averages),
  `MomentumUpdateRule`, `AntimomentumUpdateRule`, `PowerChannelUpdateRule`,
  `ChannelFollowingUpdateRule`, `DifferenceMomentumUpdateRule`, `MinimumVarianceUpdateRule`.
- `rules/base/` — estimator building blocks + guard/moving-average: `QuantammMathGuard.sol`,
  `QuantammMathMovingAverage.sol`, `QuantammGradientBasedRule.sol`, `QuantammCovarianceBasedRule.sol`,
  `QuantammVarianceBasedRule.sol`, `QuantammBasedRuleHelpers.sol`.

**`pkg/pool-hooks/contracts/hooks-quantamm/`**
- `UpliftOnlyExample.sol` — router/hook taking uplift-based withdrawal fees using an oracle price.
- `LPNFT.sol` — NFT representing LP positions (transfer affects fee accounting).

**`pkg/interfaces/contracts/pool-quantamm/`**
- `IQuantAMMWeightedPool.sol`, `IUpdateRule.sol`, `IUpdateWeightRunner.sol`, `OracleWrapper.sol`.

## Out of scope
- All base Balancer V3 infrastructure (`pkg/vault`, `pool-weighted`, `pool-stable`, `pool-gyro`,
  `pool-utils`, `solidity-utils`). Vault/swap/deposit/withdraw mechanics are inherited and out of scope.
  EXCEPTION: an issue arising from the **combination** of the Balancer batch-swap router AND a
  QuantAMMWeightedPool is in scope.
- Test files, mocks, scripts. Issues already acknowledged in the included root + pool-quantamm audit
  folder reports (known issues).

## Compatibilities
- Chains: Ethereum Mainnet, OP Mainnet, Arbitrum, Base.
- Tokens: **standard ERC20 only**. Non-standard tokens (rebasing, allowlist, fee-on-transfer /
  double-entrypoint, etc.) are explicitly out of scope — this materially narrows the token-integration lens.

## Build / toolchain
- Monorepo: `yarn install` at root (yarn workspaces `pkg/* pvt/*`).
- Per package (`pkg/pool-quantamm`, `pkg/pool-hooks`, `pkg/interfaces`): `forge compile`, `forge test`.
- `pkg/pool-quantamm/foundry.toml`: `solc_version = 0.8.26`, `auto_detect_solc = false`,
  `evm_version = cancun`, `optimizer = true`, `optimizer_runs = 999`, **`ffi = true`**,
  `ignored_error_codes = [2394, 5574, 3860]` (transient storage, code size). Remappings resolve to
  `node_modules` (`@balancer-labs`, `@openzeppelin`, `@prb` PRBMath, `permit2`, `@chainlink`, `forge-std`).
- Pragmas: 24 in-scope files `>=0.8.24`, 1 file `>=0.8.20`; all compile under 0.8.26/cancun.
- **`ffi = true`** is a supply-chain signal to flag in Step 1 (`/supply-chain`).

## Known-issue / out-of-scope nuances that shape the audit (from README "Known Issues")
These are the rails that the strict dependency-clear policy must respect — i.e. legitimate scope
boundaries, NOT excuses to short-clear in-scope math:
- **Oracle**: Chainlink assumed in-spec; manipulation of trajectories/fees out of scope. BUT
  mishandling of *in-spec* Chainlink data (e.g. wrong decimal conversion in the wrapper) IS in scope.
- **Rule math**: theoretical limits that *revert* (div-by-0, caught overflow) are expected. BUT
  **silent overflows, unintended sign changes vs whitepaper, weight vectors violating whitepaper
  equations, and guard-rail breaches inside the weighted pool ARE in scope.** ← primary deep-review target.
- **Guard rails**: multi-block MEV under *inappropriately configured* guard rails is out of scope;
  guard-rail *breaches under appropriate config* are in scope.
- **Admin**: `quantammAdmin` is a trusted, correctly configured OZ timelock; malicious-takeover out of scope.
- **Pool-creator trust**: 3 types. Type 3 (creator NOT in `approvedPoolActions`) is **untrusted** —
  creator manipulation of such pools IS in scope. Types 1 & 2 trust the creator.
- 0-fee pool manipulation, random-interval effects, update failures/restarts, block.timestamp use,
  single-asset-deposit extreme-value failures: out of scope (with narrow in-scope carve-outs noted in JSON).

## Ambiguities
1. The "known/acknowledged issues" list lives in the included `audits/` folder reports, not the README;
   acknowledged items are out of scope but require reading those reports to fully enumerate.
2. Interfaces + `QuantammBasedRuleHelpers` are in scope but mostly declarative; substantive logic is in
   the runner, pool, rules, rules/base estimators, storage packing, oracles, and the uplift hook.

**Conclusion:** scope reconstructed confidently from public repo materials. Proceeding to Phase 2.
