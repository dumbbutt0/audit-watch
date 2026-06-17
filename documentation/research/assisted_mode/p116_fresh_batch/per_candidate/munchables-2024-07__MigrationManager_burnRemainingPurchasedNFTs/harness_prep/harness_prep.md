# Harness prep — munchables-2024-07 :: MigrationManager.burnRemainingPurchasedNFTs

**Harness classification (advisory EFFORT estimate): HARNESS_COMPLEX**
_large protocol graph (7 in-scope contracts to deploy)_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] Local deployment is sufficient (no fork)
- [ ] Deploy `BaseBlastManager`
- [ ] Deploy `ClaimManager`
- [ ] Deploy `LockManager`
- [ ] Deploy `MigrationManager`
- [ ] Deploy `MunchNFT`
- [ ] Deploy `NFTOverlord`
- [ ] Deploy `SnuggeryManager`
- [ ] Initialize / configure to a valid pre-state
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `admin` — owner/role/privileged guard present

## Dependencies
- in-scope deployables: ['BaseBlastManager', 'ClaimManager', 'LockManager', 'MigrationManager', 'MunchNFT', 'NFTOverlord', 'SnuggeryManager']
- external integrations (fork): []
- tokens: ['@openzeppelin/contracts/interfaces/IERC20.sol', '@openzeppelin/contracts/interfaces/IERC721.sol']

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

