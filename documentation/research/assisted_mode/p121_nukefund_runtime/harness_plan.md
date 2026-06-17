# P121 — Harness plan & feasibility

**Classification: HARNESS_MODERATE, no fork.** Standalone project (traitforge has no vendored OZ and needs **OZ v4**
— `security/` paths + no-arg `Ownable()` — whereas only OZ v5.6.1 was on disk). NukeFund.sol imported via remapping
(UNMUTATED).

## Project — `/tmp/p121-nukefund-harness/`
`foundry.toml`: solc **0.8.26** (satisfies NukeFund `^0.8.20`), `evm = cancun`, `optimizer_runs = 200`. Remappings:
```
forge-std/=lib/forge-std/src/                  (symlink -> /tmp/p89-phi/lib/forge-std)
@openzeppelin/=lib/openzeppelin-contracts/     (forge install OpenZeppelin/openzeppelin-contracts@v4.9.6 — REAL OZ v4)
traitforge/=/tmp/p87-traitforge/contracts/     (NukeFund.sol + ITraitForgeNft, unmutated)
```
OZ v4.9.6 was obtained via `forge install` (network available) — the real library, not shims. If network were
unavailable the fallback was minimal v4-faithful shims for `access/Ownable` + `security/{ReentrancyGuard,Pausable}` +
`token/ERC721/extensions/IERC721Enumerable` (type-only); not needed here.

## Deploy plan (real contract under test)
`new NukeFund(mockNft, mockAirdrop, payable(dev), payable(dao))` — plain constructor (sets refs; Ownable v4 →
deployer = owner). The test contract (owner) calls `setAgeMultplier(10000)` so high-entropy tokens exceed
`nukeFactorMaxParam`. Fund is loaded by sending ETH through `receive()` (90% → `fund`, 10% devShare → dao).

## Mocks (only what nuke()/calculateNukeFactor()/canTokenBeNuked() call — selector dispatch; cast by address)
| Mock | Implements | Behavior |
|---|---|---|
| `MockTraitForgeNft` | `ownerOf`, `getApproved`, `isApprovedForAll`, `isApprovedOrOwner`, `getTokenEntropy`, `getTokenCreationTimestamp`, `getTokenLastTransferredTimestamp`, `burn` | per-token configurable; `burn` zeroes owner |
| `MockAirdrop` | `airdropStarted`, `daoFundAllowed` | both true (only used by `receive()`) |

`MockTraitForgeNft` is passed as `ITraitForgeNft(address(mock))` — the cast needs only the type (imported), not a
full `IERC721Enumerable` implementation.

## Actors
`attacker`, `victim`, `dev`, `dao` (`makeAddr`). The attacker/owner is the permissionless caller in every case (no
privileged setup beyond owning the token being nuked).

## Test matrix (Cases A–E) → `NukeFundRuntime.t.sol`
- **A** guards: non-owner → revert "caller is not token owner or approved"; owner-but-NukeFund-not-approved → revert
  "Contract must be approved…"; immature → revert "Token is not mature yet".
- **B** high factor (entropy 999999 → factor > 50000) → claim == fund/2 exactly; fund −= claim; attacker += claim; burned.
- **C** no re-nuke: after a successful nuke, a second `nuke` reverts (token burned).
- **D** multi-token drain: 2 mature tokens nuked → each takes exactly 50% of the then-current fund; fund never
  underflows; contract ETH balance ≥ fund (solvent); 25% remains.
- **E** low factor (entropy%10 == 0 → age term 0 → factor = entropy/40 ≤ 50000) → claim == fund*factor/MAX_DENOMINATOR,
  ≤ fund/2.

## Deps present?
forge-std ✓ (phi copy), OZ v4.9.6 ✓ (forge install), traitforge contracts ✓, solc 0.8.26 ✓. → MODERATE confirmed;
harness built and runs (see `runtime_matrix.md` / `execution_output.txt`).
