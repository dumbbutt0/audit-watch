# Human Auditor Methodology

This document codifies the reasoning framework that separates expert human auditors
from pattern-matching tools. All specialist agents apply this as their base reasoning
before any pattern-matching. It encodes the principles articulated by Jason Hadex
(legendary hacker, former CISO of Ubisoft, founder of Arcanum pentesting firm).

---

## Attacker-First Thinking

Before asking "what vulnerability pattern does this look like?", ask:
"If I were trying to steal from this protocol, which function gives me the most leverage?"

This reframes analysis from defensive (looking for known bad patterns) to offensive
(understanding what an attacker actually wants and how they would get it). The difference
is not cosmetic — it changes which functions you prioritize and which attack angles you see.

Start every analysis with:
1. What is the most valuable thing an attacker could extract from this protocol?
2. Which functions touch that value?
3. What is the shortest path from an unauthenticated call to that extraction?

---

## ITE Decomposition Protocol

Every finding must have three components: Intent, Technique, Evasion.

**Intent** — What does the attacker achieve? One sentence. Name the victim and the loss.
- Good: "drain the ETH balance of any depositor without their authorization"
- Bad: "reentrancy vulnerability in withdraw()"

**Technique** — How exactly is the attack executed? Be specific about the call sequence.
- Good: "call withdraw(); during the external .call{value}() at line 47, attacker's fallback() re-enters withdraw() before the balance mapping at line 51 is updated; balances[attacker] is still the original value on the second entry"
- Bad: "reentrancy via fallback"

**Evasion** — What protection did the developer intend? What is the exact gap?
- Good: "nonReentrant modifier exists on deposit() (line 23) and repay() (line 89) but was not applied to withdraw() (line 44) — the guard is incomplete"
- Bad: "no reentrancy guard"

The ITE structure forces you to verify three things before reporting: that the attack is
actually achievable (technique is traced step by step), that the impact is real (intent
names specific harm), and that you understand why the developer's defense fails (evasion).

---

## Cross-System Creativity Rule

A finding that exists only at the intersection of 3+ subsystems is your most valuable finding.

Reasoning: systematic auditors using knowledge-base tools and pattern matchers can find
single-system bugs. They often miss bugs that require simultaneously understanding the
oracle, the lending market, and the liquidation queue. These compound bugs survive multiple
audits not because they are subtle within one system but because they require holding the
whole protocol in your head at once.

When you detect a vulnerability in two interacting systems, explicitly ask:
"Is there a third system that amplifies this?"

Common third amplifiers:
- A snapshot or checkpoint that captures the manipulated state
- A flash loan that makes the attack costless
- A governance mechanism that lets the attacker change parameters mid-exploit
- A price feed that lags behind the manipulated pool

---

## Non-Determinism Awareness

LLM reasoning is non-deterministic. Your output on the same input is not guaranteed to be
the same across runs. This has a specific implication for confidence fields.

Set confidence fields accurately:
- **High**: you traced the exact call path hop by hop and confirmed the state transition
  at every step. You can write out the full attack sequence with specific line numbers.
- **Medium**: you have the pattern (e.g. CEI violation) but have not traced every intermediate
  hop or confirmed that no guard elsewhere breaks the exploit.
- **Low**: you see the structural condition (e.g. external call before state update) but
  the full exploit path is not confirmed.

High/Critical claims at Medium or Low confidence trigger multi-pass confirmation by
`scripts/multi_pass_confirm.py`. This is a feature, not a failure — it means the claim
gets an independent second opinion before reaching the human auditor.

Do not inflate confidence to avoid this check. Accurate confidence scores make the
pipeline more reliable, not less.

---

## Patient Zero Awareness

Threat actors target developers, not just users. A compromised build dependency or
malicious test helper can inject code into a protocol before it ships — and that code
will pass all audits because it was injected after review.

When examining a codebase:
- Flag any dependency not pinned to a specific commit hash or verified tag
- Flag `ffi = true` in `foundry.toml` — this allows build scripts to execute arbitrary
  shell commands during compilation
- Flag imports that resolve to non-standard sources (raw GitHub URLs, unknown forks)
- Flag test helper files imported into non-test production code
- Flag build scripts that curl, wget, or eval remote content

These are supply chain signals. They do not mean the contract is exploitable, but they
mean the audit boundary includes the build chain, not just the contract source.

Set `human_review_required: true` on any finding of this type — supply chain issues
require human judgment about the developer's intent and the actual risk.

---

## Human Escalation Triggers

Set `human_review_required: true` on any finding where ANY of the following apply:

1. **Multi-block economics**: the exploit requires reasoning about protocol state across
   multiple blocks or epochs (funding rates, interest accrual, vesting schedules). LLMs
   reliably miss off-by-one and boundary conditions in time-based accounting.

2. **Deep cross-contract chain**: the vulnerable path crosses more than 2 external contracts.
   Each hop introduces state assumptions that are hard to trace reliably without tracing
   the actual deployed code.

3. **No KB precedent**: when querying `tools/retriever.py`, the top-1 similarity is below
   0.40. A novel pattern means there is no auditor consensus on what a real finding looks
   like here — human judgment is required.

4. **Partial exploit path**: you can articulate the attacker's goal and the entry function,
   but the exact path to the impact is unclear. Do not claim a severity you cannot trace.
   Report at Low confidence with `human_review_required: true` and let the human complete it.

5. **Governance/social vectors**: the attack requires a governance vote, a validator
   misbehavior, or a social-engineering step. These involve off-chain actors and
   probability assessments that LLMs handle poorly.

6. **Developer supply chain**: any finding from the supply chain check agent (SC-* prefix).

---

## When AI Should Stop and Hand Off

AI is reliable at:
- Pattern recognition against known vulnerability classes (reentrancy, integer overflow, access control)
- Tracing single-transaction call paths where all contracts are in the audit scope
- Checking for missing guards on isolated functions
- Verifying CEI compliance function by function
- Cross-referencing findings against Solodit and Immunefi precedents

AI is unreliable at:
- Novel economic design attacks not present in training data
- Multi-step governance manipulation with off-chain components
- Creative cross-protocol interactions requiring simultaneous reasoning about 4+ systems
- Timing attacks that depend on mempool behavior or validator ordering
- Supply chain compromise assessment

For unreliable categories: produce a hypothesis-level finding:
- `severity: "Low"` (downgrade from whatever your intuition says)
- `confidence: "Low"`
- `human_review_required: true`
- `human_review_reason`: explain specifically what you cannot confirm

Let the human auditor complete the analysis. A low-confidence hypothesis that gets
confirmed by a human is worth more than a high-confidence false positive that wastes
everyone's time.

---

## The 90/10 Principle

AI handles 90% of systematic analysis:
- All known vulnerability classes (reentrancy, arithmetic, access control, oracle, flash loan)
- Standard compound patterns (COMP-A through COMP-J)
- KB-backed precedent matching
- PoC planning and generation for confirmed findings
- Judge simulation and severity calibration

Human handles the 10%:
- Novel patterns with no KB match (kb_similarity < 0.4)
- Findings that AI cannot confirm consistently (confirmation_score < 0.6)
- Deep cross-contract chains (trace_depth >= 3)
- Economic attacks over multiple blocks
- Supply chain and governance vectors

Scale does not replace expertise — it amplifies it. The goal is for AI to clear the
systematic backlog so the human auditor can spend their time on the findings that
actually require human creativity. That is how you find bugs that survive multiple audits.

---

## Quality Gate Reminder

Before finalizing any High or Critical finding:

1. Can you write the attack scenario in 4 steps or fewer, with specific line numbers?
2. Is there a direct financial loss to a victim (not just a theoretical state inconsistency)?
3. Is the attack permissionless (no privileged key, no pre-existing allowance)?
4. Is the victim condition realistic (arises from normal protocol use)?
5. Can you write the impact in one sentence naming the victim and the loss?

If any of these fail: downgrade to Medium and set `human_review_required: true`.

---

## Impact Chain Escalation Rule (mandatory for every finding)

Never stop at a vulnerable state change. For every finding you produce:

1. Identify the exact corrupted state or return value the attacker controls
2. Search the codebase for all consumers of that state (use rg, read call chains)
3. Trace the longest realistic chain: root cause → consumer → protocol action → impact
4. Severity must be assigned only from the **highest directly proven PoC level**, not plausible escalation

Registry, attestation, factory, oracle, access-control, and cross-chain findings are
**incomplete** until the PoC proves the first trusted protocol action that consumes the
corrupted state. Do not stop at: `isBytecodeAudited == true` or `flag is set`.
Push toward: `consumer function accepts the state → protocol performs deploy/borrow/liquidate/mint`.

See `prompts/impact_chain_escalation.md` for:
- PoC levels 1–5 and severity ceilings per level
- Consumer action classification table
- Registry/oracle/liquidation/cross-chain specific tracing rules
- Triager invalidation table template
- Defenses checked table template

## No-Silent-Clear Rule (mandatory)

You may **not** conclude "cleared / safe / sound / works as designed / not exploitable" on
**safety-net code** without a written attacker-path **disproof**. Safety-net code = anything
whose job is to protect the protocol: solvency/invariant modifiers (`Invariable`, `fundsSafu`,
`noNetFlow`/`noOutFlow`/`oneOutFlow`), custom sorts / normalization / distribution math, peg &
oracle aggregators and price selection, bridge-address / cross-domain-sender checks,
season/epoch/time gates, and one-shot init/migration completeness.

A valid disproof names the concrete thing an attacker would need and why it is impossible
(e.g. _"to break this the attacker must make X exceed Y, but X is set to Y in the same tx
before any user action, so no intermediate state is reachable"_). "Looks correct" / "standard
pattern" is **not** a disproof.

If you cannot produce a disproof, do **not** clear it — emit the finding with
`"verdict": "unresolved_invariant"` so it routes to the human review queue. When you do clear
safety-net code, the finding must carry both `"verdict": "cleared"` and a non-empty
`"disproof"`; `scripts/validate_agent_output.py` rejects a cleared safety-net finding that
lacks a disproof. This rule exists because the pipeline previously cleared 5 real Beanstalk
bugs (Invariable entitlement, quickSort, multi-sunrise, fundsSafu window, bridge mismatch).
