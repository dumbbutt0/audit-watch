# Impact Chain Escalation (ICE)

---

## Why ICE Exists

Smart contract auditing tools — both static analyzers and LLMs — routinely stop analysis at the first observable anomaly: a state variable becomes incorrect, an authorization check is missing, an arithmetic result is imprecise. This is insufficient. A corrupted state that no trusted protocol function ever consumes causes no harm. Severity is valid only when the full chain is traced.

ICE prevents the pipeline from reporting severity based on orphaned state changes.

The canonical false positive ICE was designed to prevent: "The attacker can set `isBytecodeAudited[token] = true` without authorization." This is a finding only if some protocol function later calls `deploy()` or `borrow()` based on that flag. If the flag is never read by a trusted function, there is no exploitable impact.

---

## The Core Rule

> **Root cause → corrupted state → protocol consumer → real protocol action → proven impact**

Every link in this chain must be confirmed, not assumed. Plausible escalation is not severity.

This rule is defined in `prompts/impact_chain_escalation.md` and takes precedence over `prompts/human_auditor_methodology.md` on severity-assignment.

---

## PoC Levels (ICE Scale)

| Level | What is proven |
|-------|---------------|
| 0 | Static reasoning only — identified the corrupted state, no code demonstrates the path |
| 1 | Isolated harness — math or logic copied from source; bug behavior asserted in isolation |
| 2 | Root cause confirmed — the corrupted state is demonstrably set (real contract function called) |
| 3 | Consumer reached — the protocol consumer function is called with the corrupted state |
| 4 | Protocol action proven — the consumer performs a real protocol action (deploy, borrow, liquidate) |
| 5 | Direct impact proven — financial impact asserted (balance change, unauthorized mint, etc.) |

ICE levels map to severity ceilings:

| PoC Level | Max severity |
|-----------|-------------|
| 0–1 | Low |
| 2 | Medium |
| 3 | High |
| 4 | High |
| 5 | Critical |

---

## Consumer Search Methodology

`scripts/run_impact_chain_escalation.py` searches for consumers using `rg` (ripgrep) against the contract source directory. The search looks for the corrupted state variable name and common consumer action patterns:

**Consumer action patterns searched:**
`_mint(`, `deploy(`, `borrow(`, `withdraw(`, `liquidate(`, `authorize(`, `whitelist(`, `mint(`, `transfer(`, `governance(`, `approve(`

**Search confidence levels:**
- **High**: Consumer found, action is a top-tier high-value action (deploy, borrow, liquidate)
- **Medium**: Consumer found, action is a mid-tier action
- **Low**: Consumer found via indirect pattern (interface call, inheritance — rg may have missed it)

**Limitations:** rg-based search misses:
- Interface calls (calls through a typed interface rather than direct reference)
- Delegatecall paths
- Inheritance chains (parent contract reads the state)
- Compiler-generated accessors

Findings with `consumer_search_confidence == "low"` go to `output/ice_manual_review.jsonl` for human tracing.

---

## Severity Ceiling Assignment

The ICE block sets `severity_ceiling` based on:
1. The highest PoC level achieved
2. The type of consumer action found

If `ice.hold == true` (high-risk vuln type with no consumers found), the finding is routed to `poc_required` or `manual_review` but is NOT permanently rejected. Hard rejection requires the pre-submission gates to also mark the finding invalid.

---

## How to Run

```bash
python scripts/run_impact_chain_escalation.py
python scripts/generate_status.py
```

Optional arguments:
```bash
python scripts/run_impact_chain_escalation.py --audit-id my-protocol-2026-06
python scripts/run_impact_chain_escalation.py --contract-dir contracts/fassets/
```

---

## Output Files

| File | Contents |
|------|---------|
| `output/findings_ice.json` | All merged findings enriched with `ice` blocks |
| `output/ice_manual_review.jsonl` | Findings needing human consumer tracing (low confidence) |
| `output/ice_poc_required.jsonl` | Findings needing PoC to reach the next severity level |

---

## ICE Block Structure

```json
"ice": {
  "corrupted_state": "isManagerOf[token][attacker]",
  "consumers": [
    "TokenGateway.addMinter()",
    "TokenGateway.onlyManagerOrGateway modifier"
  ],
  "consumer_actions": ["addMinter", "onlyManagerOrGateway"],
  "poc_level": 2,
  "severity_ceiling": "High",
  "consumer_search_confidence": "medium",
  "hold": false,
  "needs_manual_review": false,
  "manual_override": {
    "enabled": false
  }
}
```

**Manual override:** To force a severity ceiling that differs from the automated assessment, set:
```json
"manual_override": {
  "enabled": true,
  "reviewer": "auditor-name",
  "reason": "Confirmed via code review that addMinter() is called with corrupted state in production deployment"
}
```

---

## Manual Consumer Tracing

When `needs_manual_review == true` or `hold == true`, spawn the impact chain escalation agent for that finding:

```bash
# The agent reads the existing ice block and traces consumer paths in code
# Spawn via Task tool in Claude Code:
# "Run agents/impact_chain_escalation.md for finding XTR-001"
```

The agent supplements the heuristic rg pass — it does not replace it. It reads actual source code to confirm consumer paths the search missed (interfaces, inheritance, delegatecall).

---

## Examples

**Example 1: ICE correctly blocks a finding**

Finding: "Attacker can call `setApproved(token, true)` without authorization."

ICE search: `rg 'isApproved\[' contracts/` → 0 results in trusted functions.

Result: `ice.consumers = []`, `ice.hold = true`, routes to `ice_manual_review.jsonl`.

After human tracing: `isApproved` is read only in an internal view function never called externally. Finding severity: Low (information disclosure at most).

**Example 2: ICE correctly escalates a finding**

Finding: "Attacker can set `isBytecodeAudited[token] = true` by calling `markAudited()` without proper validation."

ICE search: `rg 'isBytecodeAudited\[' contracts/` → hit in `deploy()` function.

`deploy()` action: Creates a new contract and grants it permissions.

Result: `ice.consumers = ["Registry.deploy()"]`, `ice.poc_level = 3` (consumer reached), `ice.severity_ceiling = "High"`.

**Example 3: ICE prevents over-reporting**

Finding: "Arithmetic precision loss in `calculateFee()` can result in fee being 1 wei less than expected."

ICE search: `rg 'calculateFee\b' contracts/` → called only in a view function used for display.

Fee value never used to update balances or transfer assets.

Result: `ice.consumers = []`, severity_ceiling: "Low". Cannot claim High.
