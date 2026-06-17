# P120 — Runtime matrix

Command: `forge test --use 0.8.26 --match-contract FeeCollectorRuntime -vvv`
Project: `/tmp/p120-feecollector-harness` (standalone; ramses `contracts/` unmutated, imported via remapping).
Pool fees seeded per case: `FEE0 = 1000e18` (token0), `FEE1 = 500e18` (token1).

| Case | Scenario (attacker = permissionless caller) | Result | Recipient evidence | Attacker balance |
|---|---|---|---|---|
| **A** | live gauge + alive + isTokenLive; `treasuryFees = 2000` (20%) | **PASS** | treasury = 20% (200e18 t0 / 100e18 t1); feeDist.notified = 80% (800e18 t0 / 400e18 t1); FeeCollector drained to 0 | **0 before & after** |
| **B** | no gauge set (`gaugeForPool == 0`) | **PASS** | `pool.collectProtocol` recipient == `treasury`; treasury got 100% (1000e18 t0 / 500e18 t1); feeDist untouched | **0** |
| **C** | attacker-deployed fake pool (gauge 0 → treasury branch) | **PASS** | fake pool `collectProtocol` recipient == `treasury` (NOT attacker); 777e18 routed to treasury | **0** |
| **D** | pre-seed FeeCollector with 123e18 residual, then collect a live-gauge pool; `treasuryFees = 0` | **PASS** | feeDist.notified(t0) == `FEE0 + 123e18` — the residual is swept into THIS pool's feeDist (balanceOf quirk = cross-pool misattribution) | **0** (residual came from a donation/self-loss, not the attacker's gain) |

All 4 tests pass (executed). Full log: `execution_output.txt`.

## Reading
- **A/B/C** establish the theft/redirection answer: across every reachable branch, the permissionless caller
  receives nothing and every recipient is the hardcoded `treasury` / `address(this)` / voter-resolved `feeDist`.
  The arbitrary `pool` argument cannot steer funds to the caller (C proves an attacker-controlled pool still routes
  to `treasury`).
- **D** confirms the `balanceOf(this)` quirk is real (residual misattribution) but **not attacker-profitable** — it
  requires a donation to the FeeCollector (a self-loss); no value flows to the caller.
