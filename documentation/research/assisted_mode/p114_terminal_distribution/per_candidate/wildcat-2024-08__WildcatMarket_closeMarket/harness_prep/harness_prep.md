# Harness prep — wildcat-2024-08 :: WildcatMarket.closeMarket

**Harness classification (advisory EFFORT estimate): HARNESS_MODERATE**
_6 in-scope contract(s), local deploy with ordering / initialization_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] Local deployment is sufficient (no fork)
- [ ] Deploy `WildcatMarket`
- [ ] Deploy `WildcatMarketBase`
- [ ] Deploy `WildcatMarketConfig`
- [ ] Deploy `WildcatMarketToken`
- [ ] Deploy `WildcatMarketWithdrawals`
- [ ] Deploy `WildcatSanctionsSentinel`
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `victim_user` — per-user accounting present
- `liquidity_provider` — liquidity/reserve mechanics present

## Dependencies
- in-scope deployables: ['WildcatMarket', 'WildcatMarketBase', 'WildcatMarketConfig', 'WildcatMarketToken', 'WildcatMarketWithdrawals', 'WildcatSanctionsSentinel']
- external integrations (fork): []
- tokens: []

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

