# P128 — Runtime matrix

Command: `forge test --match-contract GovernanceCaptureRuntime --evm-version cancun -vvv`
Project: `/tmp/p102-iqai` (REAL `AIToken` + `TokenGovernor` + `Agent`; the test contract acts as the AgentFactory;
`src/` unmutated; test-only file under `test/audit/`). Measured: quorum **4,000,000e18 (4%)**, proposal threshold
**10,000e18 (0.01%)**, supply 100,000,000e18.

| Scenario | Setup | Result | Evidence |
|---|---|---|---|
| **A pre-graduation** | stage 0; attacker holds 1% | **PASS** | `proposalThreshold()==type(uint256).max`; attacker `propose()` **reverts** — action path blocked |
| **B/C graduation state** | stage→1; forced-donation attacker (0 tokens) + a small organic holder | **PASS** | attacker voting power **0**; small holder far below quorum; quorum is a positive 4% fraction |
| **D1 forced attacker capture attempt** | stage→1; attacker holds just over the 0.01% propose threshold | **PASS** | proposes + votes For, but **Defeated** (quorum 4M not met) → `execute` **reverts**; attacker power unchanged |
| **D2 quorum-holder control** | stage→1; whale holds 30% | **PASS** | passes quorum → **Succeeded** → `execute` sets `agent.tokenURI(0)=="CAPTURED"` — governance controls the Agent **only at ≥quorum** |
| **E agent-alive direct calls** | stage→1; attacker calls Agent fns directly | **PASS** | `setTokenURI` and `setProxyImplementation` **revert** (`OwnableUnauthorizedAccount` — owner is the Governor) |

All 5 scenarios pass (executed). Full log: `execution_output.txt`.

## Reading
- The governance/action path is **actually executed** (propose → delay → vote → deadline → execute) in D1 (defeated)
  and D2 (succeeded) — so the KILLED verdict is **path-tested**, not asserted.
- **Forced graduation grants the attacker no voting power** (donation ≠ AIToken) and **no quorum**. It only enables
  *proposing* earlier; *executing* still needs the 4% quorum (D1 Defeated).
- The mechanism works **only at ≥ quorum** (D2): a 30% holder can pass + execute an Agent action — but reaching that
  bar requires buying ≥4% of supply, **independent of how graduation was triggered**.
- The stage-gated Agent functions are **governance-owned** (revert for the attacker directly, E) and
  `setProxyImplementation` is additionally **whitelist-restricted** (factory-trusted).

⇒ Forced graduation makes the agent alive but does **not** hand the attacker control, voting power, or a value path.

## Incidental observation (recorded, not the P128 question)
Measured `quorum()` is **4% of supply**, while `TokenGovernor`'s inline comment says "quorum is 25% (1/4th)". A
comment/config discrepancy in the protocol's own governance parameters — noted neutrally; it does not change this
verdict (capture needs 4% the forced attacker still lacks). No severity assigned.
