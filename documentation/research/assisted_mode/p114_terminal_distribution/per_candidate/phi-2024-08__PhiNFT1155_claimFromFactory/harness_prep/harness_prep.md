# Harness prep — phi-2024-08 :: PhiNFT1155.claimFromFactory

**Harness classification (advisory EFFORT estimate): HARNESS_MODERATE**
_5 in-scope contract(s), local deploy with ordering / initialization_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] Local deployment is sufficient (no fork)
- [ ] Deploy `Claimable`
- [ ] Deploy `CreatorRoyaltiesControl`
- [ ] Deploy `PhiFactory`
- [ ] Deploy `PhiNFT1155`
- [ ] Deploy `PhiRewards`
- [ ] Initialize / configure to a valid pre-state
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `admin` — owner/role/privileged guard present
- `protocol` — external protocol surface (factory/pair/pool/oracle)

## Dependencies
- in-scope deployables: ['Claimable', 'CreatorRoyaltiesControl', 'PhiFactory', 'PhiNFT1155', 'PhiRewards']
- external integrations (fork): []
- tokens: ['@openzeppelin/contracts-upgradeable/token/ERC1155/ERC1155Upgradeable.sol', '@openzeppelin/contracts-upgradeable/token/ERC1155/extensions/ERC1155SupplyUpgradeable.sol']

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

