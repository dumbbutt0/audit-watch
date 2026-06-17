# Harness prep — secondswap-2024-12 :: SecondSwap_Marketplace.spotPurchase

**Harness classification (advisory EFFORT estimate): HARNESS_MODERATE**
_6 in-scope contract(s), local deploy with ordering / initialization_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] Local deployment is sufficient (no fork)
- [ ] Deploy `ERC20`
- [ ] Deploy `SecondSwap_Marketplace`
- [ ] Deploy `SecondSwap_MarketplaceSetting`
- [ ] Deploy `SecondSwap_VestingManager`
- [ ] Deploy `SecondSwap_Whitelist`
- [ ] Deploy `SecondSwap_WhitelistDeployer`
- [ ] Initialize / configure to a valid pre-state
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `admin` — owner/role/privileged guard present
- `victim_user` — per-user accounting present

## Dependencies
- in-scope deployables: ['ERC20', 'SecondSwap_Marketplace', 'SecondSwap_MarketplaceSetting', 'SecondSwap_VestingManager', 'SecondSwap_Whitelist', 'SecondSwap_WhitelistDeployer']
- external integrations (fork): []
- tokens: ['./interface/IERC20.sol', '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol']

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

