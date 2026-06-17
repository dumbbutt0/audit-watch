# Harness prep — phi-2024-08 :: CuratorRewardsDistributor.distribute

**Harness classification (advisory EFFORT estimate): HARNESS_MODERATE**
_4 in-scope contract(s), local deploy with ordering / initialization_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] Local deployment is sufficient (no fork)
- [ ] Deploy `Cred`
- [ ] Deploy `CuratorRewardsDistributor`
- [ ] Deploy `Logo`
- [ ] Deploy `PhiRewards`
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `admin` — owner/role/privileged guard present
- `victim_user` — per-user accounting present

## Dependencies
- in-scope deployables: ['Cred', 'CuratorRewardsDistributor', 'Logo', 'PhiRewards']
- external integrations (fork): []
- tokens: []

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

