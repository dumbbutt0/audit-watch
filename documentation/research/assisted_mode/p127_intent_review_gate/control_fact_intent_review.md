# P127 — Human Intent Review Gate: the P126-F forced-early-migration control fact

**This is a judgment gate, not an automation gate.** It classifies a runtime-confirmed *control fact* against the
protocol's documented intent and routes it to a human. It assigns **no severity, no exploitability, no
report/submission readiness** — the verdict is a routing label plus the deciding evidence.

## The control fact under review (from P126-F, runtime-proven)
`LiquidityManager.moveLiquidity()` is permissionless, and its end-criterion gate is read from a **donation-inflatable
real-currency reserve**. An external donor can therefore **force lifecycle completion ("graduation") early by
self-funding the full threshold**: P126-F executed a migration that otherwise reverts (`"Bootstrap end-criterion not
reached"`) by donating exactly `targetCCYLiquidity`. It is **self-funded, profit-less** (attacker recoups 0; the
donation becomes agent-owned LP) and causes **no funds stuck/stolen**.

> Review question (human-owned): *Can an external donor force lifecycle completion earlier than intended by paying the
> full threshold — and does that matter?*

## The seven checks (with cited evidence)

| # | Check | Finding | Evidence |
|---|---|---|---|
| 1 | Docs require migration only after **organic** demand? | **No.** Migration is gated on a liquidity threshold only; no organic-demand requirement. | README:73 "intended to move liquidity … **given certain conditions are met**"; "**Documentation: N/A**" |
| 2 | Reaching the target **by donation** explicitly allowed? | **Not addressed.** The literal condition is satisfied by any currency in the reserve regardless of source — permitted-by-omission, not blessed-by-design. | `LiquidityManager.sol:107-112` gate reads `getReserves() - phantomAmount` (= raw balance − fees), source-agnostic |
| 3 | Does forced migration **harm** users / agent / launch / pricing / fees? | Fees conserved; pricing-manipulation is a net loss; **but** it forces premature graduation → agent **"alive"** + **governance active** + irreversible liquidity move (launch-sequencing disturbance). **No funds stuck/stolen.** | P126 I1/I2/I5; `Agent.sol:41-43` `onlyWhenAlive`→`NotAlive` while `stage==0`; `TokenGovernor.sol:75` `proposalThreshold()==type(uint256).max` while `stage==0` |
| 4 | Attacker cost **recoverable indirectly**? | Not directly (donation → agent LP). Possible *indirect* angle: early **governance activation** could benefit an AIToken-holding attacker — **unproven** (downstream question C2). | `TokenGovernor.sol:75`; P126-F attacker recoups 0 |
| 5 | Is the cost **high enough to be non-credible**? | **Unknown / configurable.** Effective bar = **min** of two OR-ed targets; the global factory target is owner-mutable. High target ⇒ costly griefing (griefer subsidizes protocol); low/lowered target ⇒ cheap forced graduation. | `LiquidityManager.sol:109-112` OR-gate; `AgentFactory.sol:275` `setTargetCCYLiquidity` (onlyOwner) |
| 6 | **Fair-launch / bootstrap-period** assumptions promised? | **No documented promise.** | README:73 + "Documentation: N/A" |
| 7 | **Owner/admin mitigation after** forced migration? | **None.** `Agent.setStage` is monotonic and `BootstrapPool.killed` is permanent ⇒ no un-migration. Owner can only *pre-set* the threshold. | `Agent.sol:106` `if (_stage > stage) stage = _stage`; `BootstrapPool.kill()` sets `killed=true` permanently |

## Verdict: **GRIEFING_NEEDS_MORE_CONTEXT**

The behavior is a real, **self-funded, profit-less, irreversible** lifecycle-control primitive that **satisfies the
literal documented condition**, **violates no documented fair-launch promise**, and causes **no funds-stuck/stolen**
(the team's own stated severity bar) — all of which argues toward *acceptable*. **However**, it forces premature
graduation (agent **alive** + governance **active**) with **no owner mitigation**, in an area the team **explicitly
flagged for attack review** ("Graduation of agents and transfer of LP to Fraxswap", README:215). Its acceptability
therefore hinges on two unresolved context items — making "needs more context" the honest routing label rather than
declaring it acceptable or report-worthy outright.

### Deciding unknowns
- **C1 — cost credibility / intended threshold magnitude.** Is the effective gate (min of the two OR-ed,
  owner-mutable targets) large enough that forced graduation is non-credible? A low or owner-lowerable global target
  makes it cheap for *every* agent.
- **C2 — downstream harm of premature graduation.** Does forcing agent-"alive" + early governance enable a follow-on
  attack (governance capture, premature agent operation, proxy-impl interaction)? Currently **unproven**.

### Escalation map (for the human / a future phase — not executed here)
- **→ ACCEPTABLE_SELF-FUNDED_CONTROL** if C1 (high/credible cost) **and** C2 (no downstream harm) both resolve benign,
  and the team confirms threshold-only graduation is intended.
- **→ REPORT_CANDIDATE_NEEDS_HUMAN_REVIEW** if **either** C1 (cheap/owner-lowerable bar) **or** C2 (a demonstrated
  downstream consequence) resolves adverse.
- **→ INTENDED_BEHAVIOR** only on an explicit protocol statement that donation-funded graduation is by design.

## Hard-stop self-check
- Verdict is a **routing label** only — no severity, no exploitability, no report/submission readiness claimed. ✓
- All evidence is traceable to real README lines + `src/{Agent,TokenGovernor,LiquidityManager,AgentFactory}.sol`; no
  fabricated quotes. ✓
- No harness run, no code changed, M-01 not revisited; iq-ai `src/` untouched. ✓
- Did not invent harm (premature-graduation downstream impact is explicitly marked **unproven** / C2) nor dismiss it
  as noise. ✓
