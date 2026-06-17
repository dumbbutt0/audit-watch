# P206 — harness feasibility smoke check (non-mutating)

## munchables-2024-05 — COMPILES CLEANLY (dependency burden = minor; far lighter than Vultisig)
- Throwaway foundry project; munchables `contracts/src` copied (excl `test/`, `mock/`, `rng/` — `rng/RNGProxyAPI3.sol`
  is the only `@api3` consumer); remapped to **OpenZeppelin v5** (`contracts` + `contracts-upgradeable`) from a local
  copy (`recall-2025-02-strict-eval/.../node_modules/@openzeppelin`); solc 0.8.25.
- Result: **`Compiling 94 files with Solc 0.8.25` → `Compiler run successful!`** (remaining output = `forge lint`
  style suggestions, not errors). See `smoke_build_result.txt` + `smoke_foundry.toml`.
- Version note: munchables uses **OZ v5** paths (`utils/ReentrancyGuard.sol`). The first remap attempt used a local
  OZ **4.9.6** (sentiment-v2) and failed on the v4→v5 path move (`security/`→`utils/`); switching to a local OZ v5
  resolved it. OZ v5 (contracts + upgradeable) is present locally (recall-2025-02). So munchables deps are fully
  satisfiable locally — **no version reconstruction needed**, unlike Vultisig's solc-0.7.6 OZ-3.4 / v3-core /
  v3-periphery web (no compatible local deps).
- Smoke artifacts trimmed (heavy `src/`+`out/` copies removed) to keep the research tree lean; remap + result saved.

## pooltogether-2024-03 — not smoke-tested (not a viable positive control; see screening)
Very light (6 files, OZ-only, 0.8.24) and would almost certainly compile, but its single High is `trusted_prereq`
permanent-loss → not a positive control, so no smoke test was run.

## Decisive feasibility conclusion
**Compile feasibility is NOT the blocker for munchables** (opposite of Vultisig). The blocker is **finding content**:
the firewall screening (step 4) shows munchables' 2 Highs are permissionless **DoS/griefing with no value transfer**
(demote-class), so munchables — though trivially harnessable — provides **no L3 positive-control High**. It is an
excellent *negative/demotion* corpus (awarded permissionless DoS Highs + 4 demotable Mediums), not a positive one.
