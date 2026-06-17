# P128 — Governance threshold trace (propose → vote → execute)

All numbers are **measured at runtime** (see `execution_output.txt`), not assumed.

## proposalThreshold() — the gate forced graduation flips
```
proposalThreshold() = agent.stage()==0 ? type(uint256).max
                                       : token.getPastTotalSupply(t-1) * proposalThresholdPercentage / 10_000
```
- stage 0 → `type(uint256).max` ⇒ **no one can propose** (A: attacker with 1% still reverts).
- stage>0 → `proposalThresholdPercentage = 1` ⇒ **0.01% of supply = measured 10,000e18**.

So forced graduation lets a holder of ≥10,000 AIToken **propose**. Proposing ≠ controlling.

## quorum() — the gate forced graduation does NOT provide
```
quorum(timepoint) = token.getPastTotalSupply(timepoint) * quorumNumerator / quorumDenominator
                  = 100_000_000e18 * 4 / 100  =  measured 4,000,000e18  (= 4% of supply)
```
(`GovernorVotesQuorumFraction(4)`, OZ default denominator 100. The inline comment says "25% (1/4th)" — an incidental
discrepancy recorded in `downstream_state_map.md`; it does not affect this verdict — capture still needs 4% the
attacker does not have.)

## Lifecycle and the capture algebra
`propose` → snapshot = `now + votingDelay(2m)` → `castVote` (power = `getPastVotes(snapshot)`) → deadline =
`snapshot + votingPeriod(5m)` → `state` Succeeded iff (quorum met AND for>against) → `execute` (runs as the Governor,
which owns the Agent).

- To **execute** any Agent action (e.g. `setTokenURI`, `setProxyImplementation`), the proposal must reach **quorum =
  4M for-votes**.
- Forced-via-donation attacker holds **0** AIToken ⇒ 0 votes ⇒ cannot meet quorum (and at exactly the propose
  threshold, the vote is **Defeated**, D1).
- The `setProposalThresholdPercentage` / `setVotingDelay` / `setVotingPeriod` knobs are `onlyGovernor` (`msg.sender ==
  address(this)`) ⇒ changeable **only by a passed proposal** ⇒ circular vs quorum (can't lower the bar from below it).

## Measured runtime outcomes
| Holder | AIToken | propose? | reaches quorum (4M)? | proposal state | Agent controlled? |
|---|---|---|---|---|---|
| pre-graduation attacker (1%) | 1,000,000e18 | **revert** (threshold=max) | — | — | no (A) |
| forced-donation attacker | 0 | no (below 0.01%) | no | — | no (C) |
| forced attacker @ propose-threshold | 10,000e18 +1 | yes | **no** | **Defeated** | no (D1) |
| whale | 30,000,000e18 (30%) | yes | **yes** | **Succeeded** → executed | **yes** (D2) |

⇒ Governance control requires **≥ quorum (4%)** voting power, attainable only by **buying ≥4% of supply** — a
mode-independent, expensive action that **forced graduation does not grant**.
