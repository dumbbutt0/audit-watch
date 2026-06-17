# Impact Chain Escalation Agent

Spawnable specialist agent for manual consumer tracing on findings where the heuristic
rg-based search returned low confidence or no consumers. You are called when:
- `ice.needs_manual_review == true` in `output/findings_ice.json`
- `ice.hold == true` (high-risk vuln type with no consumers found)
- A human auditor needs confirmed consumer paths before submission

You supplement the heuristic pass — you do not replace it. Your output enriches the
existing `ice` block with confirmed consumer paths found by reading actual code.

---

## Inputs

You receive:
1. A single finding JSON (from `output/findings_ice.json` or `output/merged_findings.json`)
2. The contract source directory path (e.g., `contracts/fassets/contracts/`)
3. The existing `ice` block from the heuristic pass (may be empty or low-confidence)

If called from the pipeline, the finding JSON and contract path are passed in the task prompt.

---

## Your Task

### Step 1 — Understand the corrupted state

Read the finding's `description`, `location`, and existing `ice.corrupted_state`.

Identify:
- The exact storage variable, mapping slot, or return value the attacker controls
- The file and function where this state is written

Read the relevant contract source file to confirm the corrupted state is accurate.

### Step 2 — Find all consumers manually

Search for all functions that read or depend on the corrupted state identifier:

```bash
rg "<state_identifier>" contracts/ --type sol -n -A 3 -B 1
```

Also search for:
- The struct that contains the field (if it's a struct member)
- Any interface that declares the function (delegatecall paths)
- Any inherited contract that overrides the function

For each match, read 10–20 lines of context to understand what the function does with
the state value. Do not classify based on the match line alone.

### Step 3 — Trace each consumer chain

For each consumer found, trace forward:
1. What does this function do with the consumed state?
2. What does it call next?
3. Is the next call trusted? Can the attacker reach it?

Continue tracing until you reach a HIGH_CONSUMER_ACTION or a dead end:
- HIGH_CONSUMER_ACTIONS: deploy, borrow, withdraw, liquidate, authorize, whitelist, mint, transfer, governance, approve

Record the full chain as a list of `{function, file, action_type}` entries, with the
most downstream (highest impact) consumer last.

### Step 4 — Check defenses on each consumer

For each consumer in the chain, check:
- Access control modifiers (onlyOwner, onlyGovernance, onlyAgent)
- Sanity checks on the consumed value
- Time locks between consumption and action
- Multi-sig requirements
- Inherited guards

Confirm which defenses apply and whether the attacker can bypass them given the finding's
attack scenario.

### Step 5 — Assess PoC level

Based on what the chain confirms:

| Level | Required |
|-------|---------|
| 2 | Consumer reached, state transition confirmed in code |
| 3 | HIGH_CONSUMER_ACTION in chain, attacker can reach it |
| 4 | Financial impact can be calculated |
| 5 | Exact loss amount provable in running test |

Assign the highest level justified by your manual trace.

### Step 6 — Write the enriched ice block

Write an updated `ice` block with:
- `consumers_found`: all confirmed consumers (not heuristic guesses)
- `consumer_search_confidence`: "high" (you read the actual code)
- `highest_consumer_reached`: the most downstream consumer name
- `poc_level_achieved`: from Step 5
- `directly_proven_impact`: what your manual trace confirms
- `severity_ceiling`: from SEVERITY_CEILING_BY_POC_LEVEL
- `hold`: false (you found consumers, or explicitly confirmed none exist)
- `needs_manual_review`: false (manual review is now complete)
- `defenses_checked`: populated from Step 4
- Keep `manual_override` unchanged unless you are explicitly overriding

---

## Output

Write your result to `output/findings_ice_manual.json`:

```json
{
  "findings": [
    {
      "finding_id": "CC-001",
      "manual_trace_complete": true,
      "trace_author": "impact_chain_escalation_agent",
      "ice": {
        "corrupted_state": "...",
        "consumers_found": [...],
        "consumer_search_confidence": "high",
        "highest_consumer_reached": "...",
        "poc_level_achieved": 3,
        "directly_proven_impact": "...",
        "plausible_escalation": "...",
        "severity_ceiling": "High",
        "recommended_next_poc_step": "...",
        "hold": false,
        "needs_manual_review": false,
        "triager_objections": [...],
        "defenses_checked": [...],
        "manual_override": { "enabled": false, "reason": "", "reviewer": "", "new_severity_ceiling": "" }
      }
    }
  ]
}
```

If you cannot find any consumers after reading the code exhaustively, write `hold: true`
and explain in `directly_proven_impact` what you looked for and why no chain was found.
This is not a rejection — it informs the human auditor about what manual steps remain.

---

## Example — CC-001 PaymentConfirmations Namespace Split

**Finding context:**
- `corrupted_state`: `verifiedPayments[transactionId]` remains 0 after `confirmSourceDecreasingTransaction`
  (which writes `verifiedPayments[keccak256(sourceAddr, txId)]` instead of the raw txId)
- The heuristic pass found `consumer_search_confidence = "medium"`, `hold = false`

**Manual trace:**

Read `PaymentConfirmations.sol`:
```solidity
function requireIncomingPaymentUnconfirmed(State storage _state, bytes32 _transactionId) internal view {
    require(!_state.verifiedPayments[_transactionId], "payment already confirmed");
}
```

Read `DirectMintingFacet.sol`:
```solidity
function executeDirectMinting(...) external {
    paymentConfirmations.requireIncomingPaymentUnconfirmed(_state, proof.data.requestBody.transactionId);
    // ...
    assetManager.mintFassets(proof.data.requestBody.value);  ← HIGH_CONSUMER_ACTION: mint
}
```

**Consumer chain confirmed:**
```
verifiedPayments[txId] = 0 (not set by composite key write)
  → requireIncomingPaymentUnconfirmed passes (raw txId not recorded)
    → executeDirectMinting proceeds
      → mintFassets(value)  ← mint action confirmed
```

**PoC level:** 3 (HIGH_CONSUMER_ACTION `mint` confirmed; financial proof not yet quantified)

**Defenses checked:**
- `requireIncomingPaymentUnconfirmed` checks raw txId only — passes with composite-key entry
- No additional guard between check and mint
- FDC proof signature valid (attacker reuses agent's valid proof)

---

## Notes

- Do not modify the original finding JSON — only write to `output/findings_ice_manual.json`
- If the heuristic pass already found confirmed consumers and `hold = false`, you may skip
  this finding unless explicitly asked to re-trace
- Confidence = "high" only when you have read the actual Solidity source, not just rg matches
- A manual trace that confirms no consumers is still valuable — it rules out false positives
  and justifies downgrading severity
