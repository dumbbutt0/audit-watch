# P206 — candidate inventory (local sealed holdouts)

All severities are **count-only** (from `# High/Medium Risk Findings (N)` summary headers); no finding bodies read.

## Eligible (unused for decisive validation)
| corpus | source path | answer-key | solc | framework | size (src, excl test/mock) | deps | vendored locally? | smoke-testable | used in |
|---|---|---|---|---|---|---|---|---|---|
| **munchables-2024-05** | `audits/munchables-2024-05-holdout/contracts/src` | `…/_sealed_answer_key/report.md` | **0.8.25** | foundry | 49 files / ~6.8k LOC | OZ + OZ-upgradeable + forge-std; 1× `@api3` (only `rng/RNGProxyAPI3.sol`) | not in audit dir; OZ 0.8.x / upgradeable / forge-std available elsewhere in repo | yes (expected) | PCS *screened only*, never validated |
| pooltogether-2024-03 | `audits/pooltogether-2024-03-holdout/contracts/src` | `…/_sealed_answer_key/report.md` | 0.8.24 | foundry | 6 files / ~1.4k LOC (PrizeVault/Factory/TwabERC20/HookManager/Claimable/IVaultHooks) | `openzeppelin/` + `owner-manager-contracts/` (1) | OZ 0.8.x available | yes (expected) | never used |

## Rejections (count-only basis)
| corpus | High | Med | label |
|---|---|---|---|
| badger-2024-06 | 0 | 2 | `REJECT_TOO_THIN` (0 awarded High) |
| kleidi-2024-10 | 0 | 3 | `REJECT_TOO_THIN` (0 awarded High) |
| decent-2024-01 | — | — | `REJECT_ALREADY_USED` (P202/P204) |
| vultisig-2024-06 | — | — | `REJECT_ALREADY_USED` (P205) |
| zetachain-2023-10 | — | — | `REJECT_ALREADY_USED` (P201) |
| centrifuge-2023-09 | — | — | `REJECT_ALREADY_USED` (P198) |
| predy-2024-05 | — | — | `REJECT_ALREADY_USED` (P200) |

## Severity counts (eligible)
- **munchables-2024-05**: 2 High / 4 Medium.
- **pooltogether-2024-03**: 1 High / 8 Medium.

## Read on the two eligible candidates
- **munchables** — modular Blast L2 game (managers/proxy/overlords/tokens/distributors/rng/config). solc 0.8.25
  (modern). Standard OZ 0.8.x deps satisfiable from local copies (`sentiment-v2`/`dyad` `lib/openzeppelin-contracts`,
  `plaza-finance` `lib/openzeppelin-contracts-upgradeable`, any `lib/forge-std`). Single exotic dep `@api3` is
  isolated to `rng/RNGProxyAPI3.sol` → avoidable if the positive control is not in the RNG path. **2H gives
  positive-control redundancy.** No 0.7.6/V3 web; no split-codebase ambiguity (unlike Vultisig).
- **pooltogether** — PoolTogether V5 `PrizeVault` (ERC4626 + hooks). Lightest deps + tiny scope (6 files), solc
  0.8.24. **Only 1 High** → if that single High is off-chain/trusted/oracle there is no backup positive control →
  fallback only.
