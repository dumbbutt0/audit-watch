# SOPH-02 — accPointsPerShare 1e18 scaling mismatch (updatePool vs _pendingPoints)
- **Severity recommendation:** Medium (ceiling High; L3 NEEDS_HARNESS)
- **Affected:** SophonFarming.sol `updatePool` (L411-435), `_pendingPoints` (L357-384)
- **Root cause:** updatePool stores `accPointsPerShare = pointReward/lpSupply + accPointsPerShare` (no extra 1e18),
  while `_pendingPoints` reads `accPointsPerShare*1e18` and adds `pointReward*1e18/lpSupply` then `/1e36` — the view
  over-reports the unsettled (since-last-update) period by ~1e18x; settled accounting (rewardDebt `/1e18`) is
  self-consistent. Also `pointReward/lpSupply` truncates to 0 when lpSupply≫pointReward (silent reward loss).
- **Attacker model:** permissionless (read path); affects all users. **Fund theft:** none (points accuracy).
- **PoC:** NEEDS_HARNESS — assert pendingPoints vs realized-after-updatePool divergence. **L3:** blocked.
- **Mitigation:** make stored and viewed scaling consistent (single 1e18/1e36 convention); guard truncation.
- **Human review:** decide if this is a reporting-only view bug (Low/Info) or affects on-chain settled allocation (higher).
