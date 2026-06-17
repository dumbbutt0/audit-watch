# P126 — Transition state map: BootstrapPool.kill() → LiquidityManager.moveLiquidity()

Read-only; framing only. Every element that survives or influences the `kill() → moveLiquidity` transition and where
it flows. (`moveLiquidity()` is **permissionless** — no access modifier.)

## State present at the moment of `moveLiquidity()`
| Element | Source | Role in the transition |
|---|---|---|
| `phantomAmount` | BootstrapPool immutable (`initialPrice*bootstrapAmount/1e18`) | inflates `getPrice`/`getReserves`; **subtracted** for the gate measure |
| `reserveCurrency` (incl. phantom) | `getReserves()` | feeds `price = reserveCurrency*1e18/reserveAgent` (spot, captured pre-kill) |
| real currency reserve = `currencyBalance - currencyTokenFeeEarned` | `reserveCurrency - phantomAmount` | the **gate** quantity (`>= targetCCYLiquidity`) |
| `reserveAgent = agentBalance - agentTokenFeeEarned` | `getReserves()` | denominator of `price` |
| `currencyTokenFeeEarned` / `agentTokenFeeEarned` | BootstrapPool accumulators | **swept at kill()** to `LiquidityManager(owner).owner()` (the AgentFactory); excluded from migration |
| pool real balances (`currencyBalance-cf`, `agentBalance-af`) | transferred by `kill()` → LM | become the migration inputs |
| `price` (spot) | captured pre-kill | sets `liquidityAmount = currencyAmount*1e18/price` ⇒ the Fraxswap pair's seed ratio |
| `currencyAmount = currencyToken.balanceOf(LM)` (post-kill) | = real pool currency | currency leg seeded into the pair |
| `liquidityAmount` | derived | agent leg seeded into the pair |
| LP minted | `pair.mint(LM)` | split: `shareToBamm`→BAMM, **rest → agent** |
| leftover agent / currency in LM | after seeding | swept → `agent` |
| `setAgentStage(agent,1)` | AgentFactory | protocol stage advance (the migration's terminal side effect) |

## Flow at kill() (value routing)
`kill()` = `_sweepFees()` (cf→feeTo, af→feeTo) then `transfer(LM, balance)`:
- LM currency = `currencyBalance - cf`; LM agent = `agentBalance - af`.
Then `moveLiquidity`:
- pair currency = `currencyAmount` (= `currencyBalance - cf`); pair agent = `liquidityAmount`.
- agent contract = leftover agent (`(agentBalance-af) - liquidityAmount`) + leftover currency (≈0) + all LP.
- feeTo (AgentFactory) = `cf` currency + `af` agent.

## Attacker levers on the surviving state (what P126 probes)
- **currency donation** → raises `currencyBalance` ⇒ raises the gate quantity (can cross it) and the migrated currency.
- **agent donation** → raises `agentBalance` ⇒ lowers `price` ⇒ raises `liquidityAmount` (DoS risk if > LM agent).
- **buys/sells** → accrue fees (swept) and move the spot `price` captured for seeding.
- **timing** → `moveLiquidity` is permissionless, so whoever satisfies the gate controls *when* it fires.

## Conservation identities (tested)
- currency: `currencyBalance(pre-kill) == pairCurrency + feeTo.cf`
- agent: `agentBalance(pre-kill) == pairAgent + agentLeftover + feeTo.af`
- LM retains ~0 of both.
