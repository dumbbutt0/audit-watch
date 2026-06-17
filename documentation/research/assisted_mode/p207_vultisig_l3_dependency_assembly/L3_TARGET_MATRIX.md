# P207 — L3 target matrix (reuses P205-mapped classes; no new blind run)

## H-01 — POSITIVE control (awarded HIGH)
- **Finding:** "Most users won't be able to claim their share of Uniswap fees" — `ILOPool.claim`.
- **Expected L3:** `HIGH_CONFIRMED` if a later legitimate claimer suffers material fee loss when executed.
- **Target contract(s):** real `ILOPool` (cloned) + `ManagerStub` + `FaithfulV3Pool` (external dep).
- **Attacker/threat model:** permissionless — any two position holders; the loss falls on whichever investor claims
  *second*. No privileged role.
- **Setup:** investors A (60e18) and B (40e18) buy → share ONE pool position; `launch()` deploys liquidity; a real
  swap accrues 100e18 token0 fees; fully vest.
- **Tx sequence:** A `claim()` (first) → B `claim()` (second).
- **Measured invariant:** B's fair fee share (40e18) must remain claimable by B. Pass(=High) if B's share is instead
  routed to the feeTaker AND B's claim reverts.
- **Pass/fail:** `assertEq(feeTaker, 40e18)` + `expectRevert` on B's claim; control: sole investor claims fine.

## M-03 — NEGATIVE control (awarded MEDIUM; blind v-01 over-rated to HIGH)
- **Finding:** "Transfer of ILOPool NFT bypasses `maxCapPerUser`" — `ILOPool.buy`.
- **Expected L3:** `MEDIUM_OR_LOWER` unless material value movement executes.
- **Target contract(s):** real `ILOPool` (cloned) + `ManagerStub` (no V3 pool — `buy` never calls it).
- **Attacker/threat model:** permissionless single actor.
- **Setup:** `maxCapPerUser = 100e18`; attacker funds raise token.
- **Tx sequence:** buy(cap) → (same-position buy reverts "UC") → transfer NFT to a fresh account → buy(cap) again.
- **Measured invariant:** attacker-controlled allocation vs cap, and whether protocol/victim funds are extracted.
- **Pass/fail:** allocation `> cap` (invariant bypassed) BUT attacker paid full `raiseAmount` each time and pool
  custody == exactly paid in (no theft) → demote below High.
