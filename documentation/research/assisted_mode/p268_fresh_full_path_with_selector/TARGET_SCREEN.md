# P268 — TARGET_SCREEN (content-safe; existence not content)

Goal: a FRESH external scored contest with **zero prior exposure** in this repo (the P266 lesson: the in-repo corpus
is contamination-saturated). Findings-repo availability checked via `git ls-remote` (refs only, `GIT_TERMINAL_PROMPT=0`,
control = known-public benddao-findings). No finding titles / bodies / report sections / severity tables / award
summaries opened.

## Decision: **SELECT `code-423n4/2024-07-karak`** (Karak restaking)
| criterion | status |
|---|---|
| EVM / Solidity | **yes** (solc, foundry project) |
| answer key retrievable | **PUBLIC** — `code-423n4/2024-07-karak-findings` (control benddao-findings confirms the probe) |
| in this repo already? | **NO** (not under `audits/`) — cloned fresh, source-only, into `/tmp/p268_fresh/karak` |
| prior-phase exposure | **NONE** (no match in `documentation/research/assisted_mode/`; not in any contaminated family) |
| contaminated family? | **NO** (distinct from dyad/wildcat/fenix/ramses/centrifuge/predy/phi/etc.) |
| PoC-feasible | **yes** — scope is small: 7 core contracts (Core 391, Vault 364, NativeVault 635 lines) + entity libs; forge-std vendored; OZ/solady via npm (cloned pinned for PoC, as in P266) |
| accounting/state surface | **rich** — Vault (ERC4626-style shares), Core (operator delegation), NativeVault (native ETH beacon restaking + slashing), Withdraw queue, deposit limits, slashing |

In-scope set (scope.txt): `Vault.sol · Core.sol · NativeVault.sol · SlashingHandler.sol · NativeNode.sol ·
SlashStore.sol · Querier.sol` + entities (`Operator/SlasherLib/NativeVaultLib/CoreLib/BeaconProofsLib/MerkleProofs/
HookLib/Pauser/VaultLib/Withdraw/CoreStorageSlots`) + utils (`CommonUtils/ExtSloads`). 20 in-scope files.

## Rejected / not chosen (recorded)
- **In-repo, all exposure-saturated** (so excluded for a clean blind test): dyad/wildcat/fenix/ramses (P259-
  contaminated); centrifuge/predy (P129 ground-truth + P200 unseal = answer-key seen); munchables/decent/kleidi/
  vultisig (P239 candidate-gen); traitforge/nextgen/dittoeth/ai-arena (P242 recall-sprint candidate-gen); phi (P266
  scoring). secondswap/lambowin/fenix = private findings.
- **External probes that didn't resolve or were unsuitable:** tadle/flayer/sablier/kakarot/chakra/superposition
  (findings repo not retrievable or non-EVM/Stylus/Cairo); thorchain/nibiru (non-Solidity); renzo/wildcat (in a
  contaminated family).

## Confound recorded (disclosed)
- **Training-confound:** karak is 2024-07 (pre-Jan-2026 cutoff) and public ⇒ its awards may be in training. Accepted
  exactly as in P263/P266; the full-path comparison stays honest (the selector decision is made blind, pre-reveal).
- **Zero repo-exposure** — the decisive improvement over P266 (phi had shallow P107/P115/P119 exposure; karak has none).

## Pre-reveal forbidden (held)
No finding titles / issue bodies / report finding sections / severity tables / award summaries / award-bearing
searches before Phase 11. If award content leaks before freeze: mark contaminated, exclude, re-screen.
