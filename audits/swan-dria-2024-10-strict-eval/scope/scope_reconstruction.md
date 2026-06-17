# Swan / Dria 2024-10 — Scope Reconstruction

> Reconstructed **only** from public contest material (repo `README.md`, `AUDIT.md`,
> `hardhat.config.ts`, in-scope source files). **No selected/validated submissions were opened.**
> `answer_key_used: false`.

## Target
- **Project:** Swan (by FirstBatch / Dria) — an AI-agent marketplace where buyer agents (LLM-driven)
  purchase listed ERC-721 assets, coordinated by a decentralized LLM oracle network.
- **Platform / contest:** CodeHawks `2024-10-swan-dria`
- **Repo:** `github.com/Cyfrin/2024-10-swan-dria`
- **Pinned commit:** `c8686b199daadcef3161980022e12b66a5304f8e` (2024-10-26, "Update README.md")
- **Contest window:** 2024-10-25 16:00 UTC → 2024-11-01 16:00 UTC
- **Prize pool:** $21,000 ($20,000 H/M + $1,000 Low)
- **nSLOC reported:** 1034 (README); 1747 raw LOC incl. comments (AUDIT.md)

## In scope (9 contracts)
LLM oracle subsystem:
- `contracts/libraries/Statistics.sol` — mean/variance/std-dev for validator score outlier filtering
- `contracts/llm/LLMOracleCoordinator.sol` — request/response/validation lifecycle, PoW nonce, fees
- `contracts/llm/LLMOracleManager.sol` — oracle parameters (fees, scoring, deviation factor)
- `contracts/llm/LLMOracleRegistry.sol` — generator/validator registration + staking
- `contracts/llm/LLMOracleTask.sol` — task parameter struct/interface

Swan marketplace subsystem:
- `contracts/swan/BuyerAgent.sol` — buyer AI agent; phase/round lifecycle, purchase, state update
- `contracts/swan/Swan.sol` — marketplace: list / purchase / createBuyer / fee accounting
- `contracts/swan/SwanAsset.sol` — single-supply ERC-721 asset
- `contracts/swan/SwanManager.sol` — Swan owner config (operators, market params, factories)

## Out of scope
- Oracle node software (`firstbatchxyz/dkn-l2-oracle`, Rust) — explicitly black-box.
- `contracts/assets/*`, `contracts/core/*` (incl. `WETH9.sol`, `BatchToken`, `KnowledgeRegistry`,
  `DatasetAccessRegistry`), `contracts/mock/*`, `test/*`, deployment scripts.
- Known issues (documented in README; treated as out-of-scope / accepted):
  1. `SwanAssetFactory` / `BuyerAgentFactory` `deploy()` callable by anyone (no state impact claimed).
  2. Last oracle to call `validate` pays more gas (triggers `finalizeValidation`).
  3. Changing any interval bumps round count of all buyers by 1 (intended).
  4. Malicious **centralized** Swan operator can deplete a buyer's tokens via repeated oracle requests.
  5. Malicious buyer owner can front-run operator with a dummy `oraclePurchaseRequest` /
     `oracleStateRequest` to buy nothing / set arbitrary state and collect fees.
  6. Non-`tokenAddress` funds locked.
  7. Additional LightChaser issues (repo issue #1).

## Compatibilities
- **Chains:** EVM; primary deployment Base Sepolia + Base Mainnet.
- **Tokens:** ERC-721 (SwanAsset, single supply); ERC-20 (WETH / ETH) for payments + oracle fees.
- **Non-standard ERC-20 (fee-on-transfer, blacklist) NOT supported** → such token quirks are
  out-of-scope as bug sources.

## Build / toolchain
- **Framework:** Hardhat (TypeScript) + Ethers + Mocha (parallel). NOT Foundry.
- **Compilers:** `0.8.24` (in-scope contracts, pragma `^0.8.20`), optimizer **enabled** (runs not set →
  default 200), evmVersion not set (solc 0.8.24 default). `0.5.17` only for out-of-scope `WETH9.sol`.
- **Install:** `yarn install`. **Compile:** `yarn compile`. **Test:** `yarn test` (Hardhat+Ethers).
- Uses OpenZeppelin upgradeable contracts (`.openzeppelin/` present → UUPS/transparent proxies for
  Coordinator/Registry).

## Protocol-specific attention areas (from AUDIT.md author notes — public, not answer key)
- No pausability; no reentrancy guards (CEI claimed).
- Phase & round management, especially when owner changes market parameters mid-round.
- Proof-of-work logic in `LLMOracleCoordinator` (randomness via resource usage).
- Statistics & validator score calculation (std-dev + outlier filtering).
- Struct packing not implemented.

## Ambiguities
- Optimizer `runs` not explicitly set in `hardhat.config.ts` → assumed solc default (200). Not
  material to logic findings.
- Exact contest commit confirmed as repo HEAD at pin time; CodeHawks contest repos archive the scope
  state on `main`, and the README scope-open/scope-close block matches the in-scope tree → HIGH
  confidence.

## Conclusion
Scope confidently reconstructed: **9 in-scope Solidity contracts**, solc 0.8.24, Hardhat, Base
L2 target, ERC-721 + standard ERC-20. Confidence: **HIGH**. Commit pinned. Proceeding to build.
