# Scope Reconstruction — QuantAMM 2024-12 (CodeHawks)

**Reconstructed entirely from non-answer-key sources** (contest landing page, source repo, README).
The filtered submissions page (the answer key) was NOT opened.

## Sources used
- Contest landing page: `https://codehawks.cyfrin.io/c/2024-12-quantamm` (SPA — rendered metadata
  only: dates, prize pool, nSLOC; "View repo" link not resolvable from static fetch).
- WebSearch → identified source repo: **`https://github.com/Cyfrin/2024-12-quantamm`**.
- Repo README `## Scope` → exact in-scope file list, build instructions, dependencies, out-of-scope.
- `git clone` of the repo → pinned commit HEAD.

## Contest
- **Program:** QuantAMM — Blockchain Traded Funds (BTFs) built on Balancer V3 weighted pools whose
  weights are continuously updated on-chain by quantitative "update rules" fed by oracle prices.
- **Dates:** 2024-12-20 → 2025-01-15. **Prize pool:** 49,600 OP (44,640 H/M + 4,960 Low).
- **Reported size:** 3,359 nSLOC.

## Repository + commit
- **Repo:** `https://github.com/Cyfrin/2024-12-quantamm`
- **Commit (pinned):** `a775db4273eb36e7b4536c5b60207c9f17541b92`
- **Branch:** `main` · **Commit date:** 2024-12-21 16:20 -0700 ("Update README.md") — consistent
  with the Dec 20 contest start; this is the contest HEAD.

## In-scope contracts (25)
**`pkg/pool-quantamm/contracts/`** (core, 6): ChainlinkOracle, MultiHopOracle, QuantAMMStorage,
QuantAMMWeightedPoolFactory, QuantAMMWeightedPool, UpdateWeightRunner.
**`pkg/pool-quantamm/contracts/rules/`** (7): AntimomentumUpdateRule, ChannelFollowingUpdateRule,
DifferenceMomentumUpdateRule, MinimumVarianceUpdateRule, MomentumUpdateRule, PowerChannelUpdateRule,
UpdateRule.
**`pkg/pool-quantamm/contracts/rules/base/`** (6): QuantammBasedRuleHelpers,
QuantammCovarianceBasedRule, QuantammGradientBasedRule, QuantammMathGuard, QuantammMathMovingAverage,
QuantammVarianceBasedRule.
**`pkg/pool-hooks/contracts/hooks-quantamm/`** (2): LPNFT, UpliftOnlyExample.
**`pkg/interfaces/contracts/pool-quantamm/`** (4): IQuantAMMWeightedPool, IUpdateRule,
IUpdateWeightRunner, OracleWrapper.

## Out of scope
- `mock/**`, `echidna/**` (test/fuzz harnesses) under pool-quantamm.
- All Balancer V3 base contracts (vault, swaps, deposits/withdrawals, solidity-utils, pool-utils).
- Non-standard ERC20s (rebasing/allowlist/double-entrypoint).
- **Known issues** already documented in `audits/` (certora, spearbit, trail-of-bits) and
  `pkg/pool-quantamm/audit` — explicitly out of scope.
- Balancer V3 batch-swap routing issues unrelated to QuantAMM integration.

## Build / toolchain
- `yarn install` at repo root; `forge compile` / `forge test` from each in-scope package.
- Foundry + yarn-managed Balancer V3 monorepo fork. Solidity pragma to be read from sources.
- Deps: Balancer V3, PRBMath (18-dp fixed point), OpenZeppelin (incl. Timelock), Chainlink.

## Confidence
**HIGH.** Repo + commit + exact in-scope file list all reconstructed from the README and clone;
every listed in-scope path verified present in the clone. No answer-key access required. No
ambiguity → no STOP triggered.
