# P128 — Decision: forced graduation → governance capture?

## Terminal state: **KILLED_RUNTIME**

Runtime decided across five executed scenarios, **including an actually-run governance path** (propose → vote →
execute) in both the failing (D1) and succeeding (D2) directions — so the KILL is path-tested, not asserted. No
source-only reasoning; no severity/exploitability claimed.

## What the runtime proved (resolves P127 C2)
| Question | Evidence | Verdict |
|---|---|---|
| pre-graduation: is the action path blocked? | A: stage 0 ⇒ `proposalThreshold()==type(uint256).max`; attacker (1%) `propose()` reverts | blocked |
| does forced graduation grant the attacker voting power? | B/C: forced-donation attacker holds **0 AIToken ⇒ 0 votes** | **no** |
| can the forced attacker capture governance? | D1: at the 0.01% propose threshold the proposal is **Defeated** (quorum 4M not met) → `execute` reverts; power unchanged | **no** |
| what does capture actually require? | D2: a **30% holder** passes quorum → executes `agent.setTokenURI` ("CAPTURED") — the mechanism works **only at ≥ the 4% quorum** | ≥4% of supply |
| is the agent-alive surface attacker-callable? | E: `setTokenURI` / `setProxyImplementation` revert `OwnableUnauthorizedAccount` (owner = Governor); `setProxyImplementation` is whitelist-restricted | **no** |

**Verdict:** forced premature graduation makes the agent "alive" and lowers the *propose* threshold, but **governance
control requires the 4% quorum (4M votes)** which forced graduation does **not** grant — it is funded by a currency
**donation**, giving the attacker **zero AIToken**. The attacker's voting power is **graduation-mode-independent**:
reaching quorum requires **buying ≥4% of supply** (expensive, available in honest graduation too), so forced
graduation provides **no capture, no extra control, and no value path**. The only stage-gated Agent functions are
governance-owned and impl-whitelisted. → **KILLED_RUNTIME**.

## Feedback to the P127 intent gate
**C2 (downstream harm of premature graduation) resolves BENIGN.** Per P127's escalation map, with C2 benign the
P126-F control fact moves toward **ACCEPTABLE_SELF-FUNDED_CONTROL** — *conditional on C1* (cost credibility: the
effective, owner-mutable, min-of-OR threshold). C1 remains the only open item; P126-F stays a self-funded, profit-less,
now-downstream-harmless control primitive (human-owned final call on intent + threshold magnitude).

## Incidental observation (recorded, not the P128 question; no severity)
Measured `quorum()` = **4% of supply**, while `TokenGovernor`'s inline comment states "quorum is 25% (1/4th)"
(`GovernorVotesQuorumFraction(4)` with OZ's default denominator 100). A comment/config discrepancy in the protocol's
own governance parameters — noted neutrally for a human; it does **not** change this verdict (capture still needs 4%
the forced attacker lacks). No severity, no exploitability, no report claim.

## Scope / honesty notes
- Did not re-prove P126 value conservation or M-01.
- Real OZ Governor + ERC20Votes + Agent; the test stands in only as the AgentFactory (mint/distribute/setStage/proxy
  whitelist) — the governance logic under test is unmocked.
- **No severity / exploitability / report / submission readiness** claimed.

## Hard-stop self-check
- KILLED claimed only after **executing the governance/action path** (D1 Defeated + execute revert; D2 Succeeded +
  execute). ✓
- No CONFIRMED without executed harm; the only executed "harm" (D2) requires ≥4% quorum, which forced graduation does
  not provide — correctly **not** attributed to forced graduation. ✓
- No severity / report / submission claim; incidental quorum-comment discrepancy recorded neutrally. ✓
- iq-ai `src/` **unmutated** (AIToken d964be8a, TokenGovernor 0c2ad785, Agent ba6d1e29); harness test-only under
  `/tmp/p102-iqai/test/audit/`. ✓
- Did not invent a governance consequence execution does not support. ✓
