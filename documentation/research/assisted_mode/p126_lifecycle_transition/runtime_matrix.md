# P126 — Runtime matrix

Command: `forge test --match-contract LifecycleTransitionRuntime --evm-version cancun -vvv`
Project: `/tmp/p102-iqai` (REAL `LiquidityManager` + `BootstrapPool`; mock `AgentFactory` + a faithful constant-product
Fraxswap pair etched at the hardcoded `0xE30521…`; iq-ai `src/` unmutated, test-only file under `test/audit/`).
Config: `initialPrice=1e18`, `initialLiquidity=1e24` agent, `targetCCYLiquidity=10_000e18`, `feeBps=100`, `shareToBamm=0`.

| Scenario | Setup | Result | Evidence |
|---|---|---|---|
| **A clean** | organic buy 20,000 → migrate | **PASS** | fees swept to factory; `pairCurrency == poolCurrency-cf`; currency & agent conserved; LM residual 0; LP→agent; `stage→1` (I1/I2/I4) |
| **B fee-heavy** | buys + a sell accrue both fee legs → migrate | **PASS** | `cf>0 & af>0` swept to factory; only fee-excluded currency migrated; agent conserved incl. the agent-fee leg (I2/I1) |
| **C currency donation** | attacker donates 5,000 currency → migrate | **PASS** | attacker recoups **0**; donation flows into the migrated pair liquidity (`pairCurrency > 20,000`) (I3) |
| **D agent donation** | attacker donates 50,000 agent → migrate | **PASS** | migration **completes** (no DoS, `stage→1`); attacker recoups **0** (I3/I6a) |
| **E manipulate + arb** | attacker buys 50,000 (pumps spot price), migrate, sells captured agent into the new pair | **PASS** | attacker spent **50,000**, recovered **29,625** (arb out) → **net loss ≈ 20,375**; no profit (I5) |
| **F forced-early** | pool below gate; unforced migrate **reverts**; attacker donates `TARGET` (10,000) → forces migrate | **PASS** | migrate fires (`stage→1`) when it otherwise reverts; attacker recoups **0** (cost = 10,000) — runtime CONTROL fact (I6b) |

All 6 scenarios pass (executed). Full log: `execution_output.txt`. Key logged numbers (E): `attacker_spend
= 50000e18`, `attacker_recovered = 29625.4e18`, `arb_sellOut = 29625.4e18`. (F): `forced_migration_cost = 10000e18`.

## Reading
- **Value safety holds across the whole transition** (I1–I5): conservation, fee routing, donation-non-extractability,
  output integrity, and — critically — the boundary price-manipulation arb is a **net loss** for the attacker even on
  a favorable mock destination. The cheap-to-manipulate bootstrap pool does NOT let an attacker profitably mis-seed
  the larger Fraxswap pair: the spread paid to pump the bootstrap price exceeds the arb recovered from the new pair.
- **Availability holds** (I6a): an agent-donation that inflates `liquidityAmount` does not DoS migration.
- **The one non-clean result is timing/control** (I6b, scenario F): the permissionless `moveLiquidity` + a
  donation-inflatable gate let an attacker force migration before organic bootstrap — but only by **self-funding the
  full gate threshold**, recouping nothing. It is "completion-by-donation," profit-less, and intent-dependent; **no
  severity/exploitability claimed**.

## Mock caveat
The Fraxswap destination is a faithful UniV2 (0.3% fee) mock, not the exact Fraxswap (TWAMM/fee nuances). The
extraction verdict (E) is a **net loss**, so it is robust to the mock (a favorable spot mock still yields no profit);
were E ever to show a profit, the honest next step would be a Fraxtal-fork confirmation (à la P104), not a CONFIRMED on
a mock.
