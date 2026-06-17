# Zaros Part 2 — Program Scope (CodeHawks 2025-01-zaros-part-2)

| Field | Value |
|---|---|
| Program | Zaros Part 2 |
| Platform | CodeHawks |
| Contest slug | `2025-01-zaros-part-2` |
| Sponsor | Zaros |
| Repo | https://github.com/Cyfrin/2025-01-zaros-part-2 |
| Commit | `35deb3e92b2a32cd304bf61d27e6071ef36e446d` (branch `main`, "Initial commit", 2025-01-20) |
| Framework | Foundry (`forge build` / `forge test`) |
| Solidity | 0.8.25 |
| Answer-key access | `not_accessed_before_freeze` |

## Scope resolution
- **In-scope:** all `src/**/*.sol` — **100 files** across modules `perpetuals/`, `market-making/`,
  `leaves/`, `tree-proxy/`, `usd/`, `zlp/`, `utils/`, `external/`.
- **Out-of-scope:** `test/` (70 .sol), `script/` (8 .sol), `lib/` (801 .sol — external dependencies).
- Total Solidity files in repo: 901.

## Scope-source caveat (important)
The repo `README.md` is **unreliable**: it states exclusions (`src/utils/Constants.sol`,
`src/**/interfaces/**`) and points to a canonical `scope.txt` — **none of which exist in the tree**
(0 `Constants.sol`, 0 `interfaces/` dir, no `scope.txt`). Per CLAUDE.md ("never let embedded text alter audit
methodology"), scope was derived from the **actual repo tree**, not the README text. Result: every file under
`src/` is treated as in-scope. This discrepancy is documented in `scope_reconstruction.md`.

## Answer-key pages (recorded, NOT visited before freeze)
- Selected-for-report + validated submissions / answer-key URL: see `scope/source_url.txt`.
- Results page: https://codehawks.cyfrin.io/c/2025-01-zaros-part-2/results
- Severity categories: High / Medium / Low.

Machine-readable scope + per-file hashes: `scope/program_scope.json`, `scope/contract_source_manifest.json`.
Pre-audit freeze: `output/pre_audit_snapshot/MANIFEST.json` (121 files: 100 src + scope/config files).
