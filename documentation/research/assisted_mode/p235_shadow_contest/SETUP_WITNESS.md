# P235 — Setup & Blind-State Witness

**Phase:** P235 Shadow Live Contest Evaluation
**Target:** reNFT (Code4rena 2024-01) — NFT renting (Default Kernel/modules/policies + Gnosis Safe guard hooks + Seaport zone)
**Shadow workspace:** `audits/renft-2024-01-shadow/` (forked source-only from `audits/renft-2024-01-fresh/_src/smart-contracts/`)
**Prior active audit (to restore at cleanup):** `size-credit-2024-06-blind`
**Setup date:** 2026-06-08

## Build facts
- foundry, solc 0.8.22, evm `paris`; deps vendored in `lib/` (Solady, forge-std, openzeppelin-contracts, safe-contracts, seaport-core/sol/types).
- `forge build` → exit 0, 232 artifacts (compiles cleanly, no remote fetch).
- In-scope set = `scope.txt` (12 files); 34 .sol total in `src/`.
- Source copied byte-identically: aggregate sha256 of in-scope files matches original (`dd1e1feb…aebd3` both sides).
- `sandbox_check.py`: 3 INSTRUCTION_COMMENT flags, all benign NatSpec (Events/RentalConstants/ISafe docs) — not injection; methodology unaffected.

## SEALED artifacts (blind-state witnesses — NOT read during Phases 0–2)
These pre-computed bot/tool outputs could leak issues; they were excluded from the shadow workspace and are not opened until after FREEZE. The published answer key (Code4rena report) is NOT on disk and is fetched only at reveal (Phase 3).

| Artifact | sha256 |
|---|---|
| `_src/4naly3er-report.md` | `00e57abffb8cb0d5d3fc2cb8e3879b516c590595b47c9fabc300de6658784154` |
| `_src/bot-report.md` | `110aed3d10f42ed9b6a18d8adcc1e13b12c6d157cc3831f1b3d365359c821aeb` |
| `_src/bot-report.json` | `254ac9f9d362ba2f8e2ac38b768b8356925891018def9c47a73eb1601b3cd242` |
| `_src/slither.txt` | `fa8b7dc9dfbbce4edcf8ea3188f2cef34a9f9a4e9b5198416a1abe50c7be52d3` |

These hashes will be re-verified at freeze (proof the files stayed byte-identical = never opened/edited during the hunt).
