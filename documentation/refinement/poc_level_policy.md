# PoC Level Policy

A PoC proves three layers. A High/Critical claim is not final until its PoC reaches Level 3.

## Levels

- **L1 — Entry:** attacker transaction crafted from an EOA with **no privileged setup**. Proves
  the entrypoint is reachable permissionlessly.
- **L2 — State Flip:** specific storage slots or balances **named and asserted** before/after
  (`vm.load()` / explicit reads). Proves the vulnerable state change actually occurs.
- **L3 — Outcome:** the final economic or security consequence **proven in test output**, not
  inferred. Proves impact.

All three must pass. **An honest partial PoC (L1/L2 only) is more useful than a fabricated
passing L3** — mark it partial and cap severity accordingly.

## Fork-PoC-first

For any selected finding, first try to prove it against the **deployed** contract on a fork:

1. Identify the exact on-chain address where the vulnerable code lives.
2. Fork at a recent block; reach the entrypoint as an EOA (L1).
3. Assert the state flip on real storage (L2).
4. Demonstrate the realized impact (L3): attacker entrypoint → trigger → vulnerable logic →
   failed defense → state flip → final impact.

If a fork PoC is impossible (not yet deployed, unverified source, infra gap), say why explicitly
and produce the strongest **local** PoC possible (Foundry against the in-repo source).

## Severity caps when L3 is unproven

`analyze_poc_completeness.py` enforces:

| Proven | Max severity claimable |
|---|---|
| L3 (outcome demonstrated) | Critical/High as warranted |
| L2 only (state flip, impact inferred) | capped at **Medium** |
| L1 only (reachable, no state flip) | capped at **Low** / informational |
| none | not submit-ready |

"May not claim High if the PoC stops before proving impact."

## Severity-floor rules (carried from the Beanstalk eval)

- **Init/migration OOG or revert ⇒ ≥ High.** A one-shot routine that can't complete bricks the
  whole launch — an availability failure, not "admin robustness." (Beanstalk #140 was
  under-called as Low.)
- Migration-blocking address/config bugs (wrong bridge/WETH/pipeline/chainId on the target
  chain) ⇒ ≥ High when they break a core flow.

## Budget

PoC count is gated by `config/agent_policy.json → active_mode`: `fast` = 0, `normal` = 3,
`deep` = unlimited (with scope-approval prompt). PoCs run only after the human selects finding
IDs at the review gate — never automatically.
