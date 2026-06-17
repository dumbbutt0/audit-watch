# P126 — Decision: kill() → moveLiquidity() lifecycle transition

## Terminal state: **KILLED_RUNTIME** (value-safety) + one recorded runtime CONTROL fact (forced-early migration)

Runtime decided across six executed scenarios (A–F). The transition is value-safe; the only attacker-influence on the
migration outcome is **timing** (self-funded, profit-less). No source-only reasoning; no severity/exploitability claim.

## What the runtime proved
| Question | Evidence | Verdict |
|---|---|---|
| value conserved across the transition | A/B: `poolCurrency = pairCurrency + feeTo.cf`; `poolAgent = pairAgent + agentLeftover + feeTo.af`; LM residual 0 | HOLDS |
| fees handled correctly | A/B: both fee legs swept to the AgentFactory, excluded from migrated liquidity | HOLDS |
| donations not extractable by the donor | C/D: attacker recoups **0**; donations become agent-owned migrated liquidity | HOLDS |
| migration output integrity | A: pair seeded at the pool spot price with the LM's real holdings; LP→agent; `stage→1` | HOLDS |
| no profit from boundary price manipulation | E: spend 50,000 → recover 29,625 → **net loss ≈ 20,375** (no extraction even on a favorable mock) | HOLDS |
| availability (no DoS) | D: an agent-donation inflating `liquidityAmount` does not block migration | HOLDS |
| control (no forced-early) | F: forced-early migration **is** possible but **self-funded** (cost = the full gate) and **profit-less** | PARTIAL (control fact) |

## The one non-clean result (scenario F) — stated precisely, not inflated
`moveLiquidity()` is permissionless and the end-criterion gate is measured on the **real currency reserve**, which a
direct donation inflates. So an attacker can donate exactly `targetCCYLiquidity` and immediately force migration that
would otherwise revert (`"Bootstrap end-criterion not reached"`). Runtime facts:
- the migration fires and `setAgentStage(agent,1)` advances the protocol **when it otherwise could not**;
- the attacker **recoups nothing** — the donated currency becomes agent-owned migrated liquidity;
- the cost is the **full gate threshold** (here 10,000), a hard floor.

This is a **timing/control** primitive — functionally "anyone may complete the bootstrap by self-funding it to the
target" — **not** a value extraction. Whether "completion-by-donation" is *materially earlier than intended* is an
**intent/design judgement** (the gate's criterion is satisfied either way) and is **human-owned**. Per the hard stops,
**no severity, exploitability, report-readiness, or submission-readiness is claimed.**

## Attribution (Stage 5)
The control fact originates at the **interaction boundary**, not in either contract's isolated logic:
- **BootstrapPool**: donation/fee/reserve accounting is sound (proven in P125) — not the origin.
- **moveLiquidity value logic**: conserves value and seeds faithfully — not the origin.
- **boundary**: permissionless `moveLiquidity()` (no caller restriction) + a gate read from a **donation-inflatable**
  real-currency reserve ⇒ migration timing is controllable by anyone willing to fund the gate. ← origin.
- **external dependency** (Fraxswap): mocked faithfully; not implicated in F.

## Scope / honesty notes
- Exercised the clean `createPair` migration branch; the awarded **pair-adoption M-01** ("pair already exists" branch)
  was **not** retested (out of scope, not rediscovered).
- Fraxswap destination is a faithful UniV2 (0.3%) mock; the extraction result (E) is a net **loss**, so it is robust to
  the mock. A Fraxtal-fork confirmation (à la P104) would only be warranted had E shown a profit.

## Hard-stop self-check
- Terminal state from passing runtime tests only (A–F all PASS, executed). ✓
- No severity / exploitability / report-ready / submission-ready claim — the F control fact is reported as
  intent-dependent and human-owned. ✓
- No production wiring. iq-ai `src/` **unmutated** (LiquidityManager 9a68efe4, BootstrapPool 6bd9e4bc); harness is a
  test-only file under `/tmp/p102-iqai/test/audit/`. ✓
- Did not invent a consequence execution does not support — F is reported exactly as executed (forced, self-funded,
  profit-less); extraction (A–E) is reported as held/net-loss. ✓
