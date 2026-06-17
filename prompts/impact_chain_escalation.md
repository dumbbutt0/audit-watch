# Impact Chain Escalation — Mandatory Framework for Every Finding

This module is mandatory for every finding produced by any specialist agent or human auditor.
Its purpose is to prevent the pipeline from reporting severity based on a corrupted state that
no trusted protocol function ever consumes. Severity is valid only when the full chain is traced.

Read alongside `prompts/human_auditor_methodology.md`. When in conflict, this module takes
precedence on impact-chain and severity-assignment rules.

---

## The Core Rule

Never stop at a vulnerable state change. For every finding:

> **Root cause → corrupted state → protocol consumer → real protocol action → proven impact**

Each link in the chain must be confirmed, not assumed. Plausible escalation is not severity.

---

## Stage 1 — Identify the Corrupted State

State exactly what the attacker controls after the exploit succeeds:
- Which storage variable, mapping slot, or return value has been changed?
- What is the before and after value (e.g., `isBytecodeAudited: false → true`)?
- Is this state persistent (storage) or ephemeral (memory/return value)?

A corrupted state must name a specific identifier — "the contract is in a bad state" is not
a corrupted state. "registry.audits[addr].isAudited = true (was false)" is.

---

## Stage 2 — Find All Consumers of the Corrupted State

Search the codebase for every function that reads the corrupted state identifier:

```bash
rg "<state_identifier>" contracts/ --type sol -n
```

For each consumer found, record:
- File, function name, line number
- What action the function takes when it reads this state
- Whether the function is callable by an untrusted caller

**Do not stop at one consumer.** The highest-value consumer may not be the first one found.

**Confidence assignment:**
- `high`: state is a plain public variable or uniquely named event; 5+ rg matches confirmed
- `medium`: state is a struct field or mapping entry; 2–4 matches; indirect paths possible
- `low`: state is internal, interface-gated, accessed via delegatecall, or 0–1 matches found

Low confidence means the consumer search may be incomplete — flag for manual review.

---

## Stage 3 — Classify Each Consumer's Action

For each consumer function, classify the protocol action it performs when the corrupted state
passes its check:

| Action type | Examples |
|-------------|----------|
| `deploy` | creates a new contract, adds to registry |
| `mint` | mints tokens to caller or account |
| `transfer` | moves tokens or native value |
| `withdraw` | releases collateral or backing assets |
| `liquidate` | initiates forced position close |
| `borrow` | extends credit to an account |
| `authorize` | grants role, permission, or whitelist entry |
| `governance` | queues or executes governance proposal |
| `approve` | sets allowance for external contract |
| `whitelist` | adds address to trusted set |
| `price_read` | provides price used in financial calculation |
| `state_read` | reads state used in access gate |

Actions in the `HIGH_CONSUMER_ACTIONS` set (`mint`, `transfer`, `withdraw`, `liquidate`,
`borrow`, `authorize`, `whitelist`, `deploy`, `governance`, `approve`) directly cause
fund movement or authorization change. These are the consumers that matter for severity.

---

## Stage 4 — Trace to the Highest Protocol Action

Starting from the first consumer, trace forward through any intermediate calls:

```
corrupted_state
  → consumer_function_A (action: state_read)
    → consumer_function_B (action: authorize)
      → consumer_function_C (action: mint)  ← highest action reached
```

The highest protocol action in the chain determines severity ceiling, not the corrupted
state or the first consumer.

For every hop in the chain, confirm:
1. The caller of the next hop is trusted by the next hop (no auth guard blocks it)
2. The corrupted state value propagates correctly through any transformation
3. No intermediate check independently invalidates the corrupted value

---

## Stage 5 — PoC Level Assignment

Assign a PoC level based on what has been confirmed in the chain:

| Level | What is proven | Severity ceiling |
|-------|---------------|-----------------|
| 0 | Root cause identified, no consumer traced | Low |
| 1 | Root cause confirmed in isolation | Low |
| 2 | Consumer function reached, state transition confirmed | Medium |
| 3 | Consumer performed a real HIGH_CONSUMER_ACTION | High |
| 4 | Financial impact calculated, victim identified | High |
| 5 | Exact loss amount proven with running test | Critical |

**The severity ceiling applies regardless of claimed severity.** A finding claiming Critical
with only PoC level 2 must be capped at Medium until the PoC advances.

---

## Stage 6 — Directly Proven vs. Plausible Escalation

Distinguish what the PoC actually proves from what could be true:

**Directly proven:** The PoC demonstrates this outcome. A human reviewer could reproduce it
in one command. No assumptions about external state, third-party behavior, or future conditions.

**Plausible escalation:** Logically follows from the directly proven impact if certain
conditions hold. Informative but not severity-bearing.

Write both fields explicitly. If the plausible escalation is much more severe than the
directly proven impact, name what PoC step would close the gap.

---

## Stage 7 — Defenses Checked

For each consumer in the chain, check all defenses that could prevent the corrupted state
from being acted upon:

- Access control modifiers on the consumer function
- Sanity checks on the consumed value (range checks, zero checks, etc.)
- Time locks or rate limits between consumption and action
- Multi-sig requirements on the triggered action
- Inherited guards (OpenZeppelin ReentrancyGuard, Ownable, AccessControl)

For each defense checked, record: what it is, whether it was checked, and the result.
A finding with no defenses checked is incomplete.

---

## Stage 8 — Triager Invalidation Pre-emption

Before submitting, anticipate the three most likely triager objections to this finding
and pre-emptively address them:

For each objection:
- State the objection as a triager would phrase it
- Provide the evidence that counters it
- Mark whether the objection is still partially valid (still_weak: true/false)

**Common triager objections:**
- "Admin can simply not upgrade" → evidence: attack does not require admin action
- "The consumer has an independent check" → evidence: trace through the check with corrupted value
- "PoC requires pre-existing condition X" → evidence: X arises from normal protocol use
- "Same bug exists in prior audit" → evidence: v1.3.0 delta, new code path not in prior scope
- "Frontrunning is not viable on this chain" → evidence: block time + mempool window data

---

## Stage 9 — Bug-Type Specific Tracing Rules

### Access Control / Registry Findings

The corrupted state is typically: `roles[addr] = ROLE` or `registry.trusted[addr] = true`

Required chain for High severity:
```
roles[addr] set → consumer reads role → authorizes action → HIGH_CONSUMER_ACTION executed
```

Do not stop at "attacker now has ROLE X". Push to: what does ROLE X allow the attacker to do?
What is the most destructive single action ROLE X enables?

### Oracle / Price Feed Findings

The corrupted state is typically: `price = stale_or_manipulated_value`

Required chain for High severity:
```
getPrice() returns stale value → liquidation CR check uses price → position appears healthy →
liquidation does not trigger → bad debt accumulates
```

The impact is not "stale price used" — it is the downstream effect on financial solvency.
Quantify: how long does the price need to be stale for bad debt to appear? What price drop
percentage causes the first insolvency?

### Liquidation / Collateral Findings

Required chain for High severity:
```
collateral check passes with corrupted state → liquidation blocked → price continues to drop →
specific position becomes insolvent → bad debt not covered by protocol reserves
```

High requires tracing to actual insolvency — "liquidation may be delayed" is Medium.

### Cross-Chain / Attestation Findings

The corrupted state is typically: `proof.verified = true` for a replay or invalid proof

Required chain for High severity:
```
proof verified → trusted function called with proof → mint/transfer/withdraw executed →
unbacked tokens issued or funds stolen
```

Name the specific token amount and destination. "Unbacked FAssets could be minted" is
Medium; "attacker can mint N FXRP per proof replay with no cost" is High.

### Upgrade / Diamond Proxy Findings

The corrupted state is typically: `implementation = attacker_contract` or `manager = attacker`

Required chain for High severity:
```
implementation set → user calls public function → delegatecall to attacker → attacker
drains storage or returns arbitrary data that causes victim loss
```

Do not stop at "implementation is now attacker's contract". What does the first delegatecall
from a real user result in?

---

## Stage 10 — Severity Assignment from Chain

Assign severity only from the highest PoC level achieved:

| PoC Level | Severity ceiling | Required to claim |
|-----------|-----------------|-------------------|
| 0–1 | Low | Root cause only |
| 2 | Medium | Consumer reached, state transition confirmed |
| 3 | High | HIGH_CONSUMER_ACTION confirmed (no financial proof required) |
| 4–5 | Critical | Exact loss proven with running PoC |

Apply contest-specific modifiers after the base severity from chain:
- Flare/FAssets: frontrunning −1 level, malicious agent −1 level, dust <$1000 = griefing
- Immunefi v2.2: MEV = Critical, protocol insolvency = Critical, temp freeze = High, DoS = Medium

Do not apply modifiers before the chain severity is established. The modifier is relative to
the proven chain severity, not the hypothesized maximum.

---

## Stage 11 — ICE Block Schema

Every finding output must include an `ice` block conforming to this schema:

```json
{
  "ice": {
    "corrupted_state": "exact variable/mapping/return changed by attacker",
    "consumers_found": [
      { "file": "...", "function": "...", "action_type": "mint|transfer|..." }
    ],
    "consumer_search_confidence": "high | medium | low",
    "highest_consumer_reached": "most downstream consumer found, or empty string",
    "poc_level_achieved": 0,
    "directly_proven_impact": "what the PoC actually demonstrates",
    "plausible_escalation": "what could be true if conditions hold",
    "severity_ceiling": "Critical | High | Medium | Low | Info",
    "recommended_next_poc_step": "what to prove next to increase severity",
    "hold": false,
    "needs_manual_review": false,
    "triager_objections": [
      { "objection": "...", "evidence_against": "...", "still_weak": false }
    ],
    "defenses_checked": [
      { "defense": "...", "checked": true, "result": "..." }
    ],
    "manual_override": {
      "enabled": false,
      "reason": "",
      "reviewer": "",
      "new_severity_ceiling": ""
    }
  }
}
```

**Hold assignment:**
- `hold = true`: `consumers_found` is empty AND `vuln_type` is in
  `{access-control, oracle, registry, factory, attestation, cross-chain, upgrade, logic}`
- `needs_manual_review = true`: `consumer_search_confidence == "low"` OR `hold == true`

A held finding routes to `poc_required` or `manual_review` — it is NOT permanently rejected.
Override a hold with `manual_override.enabled = true`, reviewer name, and reasoning.

---

## Stage 12 — Consumer Action Classification Table

Use this table when classifying `action_type` for each consumer found:

| Solidity pattern | action_type |
|-----------------|-------------|
| `_mint(...)` | `mint` |
| `IERC20.transfer(...)` | `transfer` |
| `payable(...).call{value}(...)` | `transfer` |
| `collateral.release(...)` | `withdraw` |
| `_liquidate(...)` | `liquidate` |
| `_borrow(...)` | `borrow` |
| `grantRole(ROLE, addr)` | `authorize` |
| `whitelist[addr] = true` | `whitelist` |
| `new Contract(...)` | `deploy` |
| `IGovernance.queue(...)` | `governance` |
| `IERC20.approve(...)` | `approve` |
| `getPrice()` call site | `price_read` |
| `require(registry[addr])` | `state_read` |

When in doubt, use `state_read` and trace further — a `state_read` alone does not establish
High severity. Keep tracing until a HIGH_CONSUMER_ACTION is found or the chain terminates.

---

## Stage 13 — Heuristic Enrichment vs. Manual Tracing

`scripts/run_impact_chain_escalation.py` performs heuristic consumer search using `rg`.
This pass has known limitations:

- **Misses:** interface calls, delegatecall paths, inherited functions, generated accessors
- **May return false positives:** variable name collisions, comment matches
- **Confidence = low:** for internal state, interface-gated state, or 0–1 matches

When `consumer_search_confidence = "low"` or `hold = true`, the finding is written to
`output/ice_manual_review.jsonl`. A human auditor or the `agents/impact_chain_escalation.md`
specialist agent must trace the consumer chain manually before severity can be finalized.

Manual tracing supplements the heuristic — it does not replace the ICE block requirement.
After manual tracing, update the `ice` block with confirmed consumers and remove the hold.

---

## Stage 14 — Integration with Pipeline

| Step | What happens |
|------|-------------|
| Step 3: `report_generator.py` | Produces `merged_findings.json` (no ice blocks) |
| Step 3.4: `run_impact_chain_escalation.py` | Enriches each finding with `ice` block |
| Step 3.5: `multi_pass_confirm.py` | Confirms High/Critical findings (reads ice blocks) |
| Step 3.7: `pre_submission_gate.py` | Gates run against confirmed findings |
| Step 4: `triage_findings.py` | `pre_check_ice_hold()` routes held findings to `poc_required` |

The heuristic enrichment (Step 3.4) runs before multi-pass confirmation so confirmation
agents can incorporate the consumer chain context when re-confirming severity claims.

Manual consumer tracing via `agents/impact_chain_escalation.md` can be run at any time
between Step 3.4 and final submission. Output goes to `output/findings_ice_manual.json`
and is merged into the main ice blocks before triage.

---

## Stage 15 — Report Gate

This is the mandatory pre-submission check for every finding, independent of ICE file state.

Before writing any submission report, answer all 8 questions in draft notes:

1. What exact state did the attacker corrupt?
2. What protocol function consumes that state?
3. Did the PoC reach that consumer?
4. Did the consumer perform a real protocol action?
5. What impact was directly proven?
6. What impact was only plausible?
7. What severity is justified only by the direct proof?
8. What would be needed to increase severity?

**If questions 2 or 3 are unanswered: do not write the report. Continue consumer tracing.**

Spawn `agents/impact_chain_escalation.md` with the finding JSON, or check
`output/ice_manual_review.jsonl` for prior tracing work.

The gate is required even when `output/findings_ice.json` exists for this finding — the ICE
file records heuristic search results; this gate is your final confirmation before publishing.
