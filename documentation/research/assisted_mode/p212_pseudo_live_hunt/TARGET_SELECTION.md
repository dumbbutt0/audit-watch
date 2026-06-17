# P212 — target selection

## Selected: sherlock-audit/2024-05-sophon (Sherlock, 2024-05)
- **Source:** `targets/2024-05-sophon/farming-contracts/` (cloned source only).
- **Sealed key:** `targets/2024-05-sophon/_sealed/judging/` (267 files, cloned quietly, NOT read; STAGE 2 only).
- **In-scope (README):** `farm/SophonFarming.sol` (933 LOC, core), `farm/SophonFarmingState.sol`,
  `proxies/{Proxy2Step,SophonFarmingProxy,Upgradeable2Step}.sol`. **Bridging OUT of scope.**
- **Architecture:** MasterChef-style farming/points contract with a custom boost mechanic (deposit→boost split,
  accPointsPerShare reward accounting, multi-asset predefined-pool conversions, UUPS-ish 2-step proxy).
- **Compiler:** solc 0.8.25 (modern; harnessable if a High emerges).

## Why selected
Manageable single-core-contract scope (not a monorepo); rich, classic attack surfaces (custody, reward accounting,
boost/share math, units/decimals conversions, admin param transitions, proxy/ownership); completed contest with a
sealable Sherlock report; not in `audits/`, not used in P186-P211.

## Why alternatives rejected
- goodentry (C4 2023-08): 180 .sol / 17k LOC — enormous, not a first-hunt scope.
- curves (C4 2024-01): 7 .sol / 730 LOC — viable fallback but thin surface set.
- pooltogether (C4 2024-03): already in `audits/` + count-screened in P206.
- cork-protocol (Sherlock 2024-08): larger depeg-swap protocol.

## Firewall status
SOURCE-only clone; answer key sealed+unread; bot/4naly3er reports not used; count-level severity DEFERRED to STAGE 2
(reading Sherlock judging severities risks title exposure). Orchestrator-memorization caveat recorded in FIREWALL_LOG.md
(mitigated by blind subagents + sealed key).

## Dependency/harness risk
solc 0.8.25 + OpenZeppelin (SafeERC20/Math) — standard, locally available (cf. P206 OZ v5). L3 harness feasible if a
genuine permissionless material High emerges; predefined-pool external integrations (sDAI/wstETH/weETH) would be mocked.
