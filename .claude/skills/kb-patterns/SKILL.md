---
name: kb-patterns
description: "Surface real-world attack patterns from the Solodit knowledge base without running an agent. Use to understand what variants of a vulnerability class have been found in production. Activate on: /kb-patterns, show KB patterns, what patterns exist for X, solodit patterns, what vulnerabilities have been found for, KB recon, knowledge base."
---

# KB Pattern Surface Tool

Surfaces real-world attack patterns from Solodit and Immunefi without running a full agent. Use this for intelligence gathering before deciding which specialist to invoke.

## Phase 1: Parse Vuln Type Argument

Parse the user's command for a vuln-type argument: `/kb-patterns [vuln-type]`

Valid vuln-types:
- `reentrancy` — CEI violations, ERC-777, read-only reentrancy
- `access-control` — missing guards, privilege escalation
- `signature-replay` — nonce bypass, cross-chain replay
- `arithmetic` — overflow, precision loss, decimal mismatch
- `oracle-manipulation` — spot price, TWAP, Chainlink staleness
- `flash-loan` — balance-based accounting, governance attacks
- `logic-error` — accounting invariants, state machines, rounding
- `dos` — unbounded loops, locked ETH, external call in loop
- `gas-griefing` — gas-specific DoS patterns
- `proxy-upgrade` — storage collision, uninitialized proxy
- `storage-collision` — slot collision in upgradeable contracts
- `front-running` — MEV, sandwich, frontrunning
- `snapshot` — governance snapshot manipulation
- `other` — miscellaneous patterns

If the user provides an unrecognized vuln-type, show the list above and ask which one they meant.
If no vuln-type provided, show the list and ask which one.

## Phase 2: Read Local Pattern Synthesis

```bash
python -c "
import json, sys
try:
    with open('kb/patterns/<vuln-type>.json') as f:
        data = json.load(f)
    for c in data['cycles'][-3:]:
        print('--- Cycle:', c.get('timestamp', 'unknown'), '---')
        print(c.get('synthesis', 'No synthesis'))
except FileNotFoundError:
    print('Pattern file not found for this vuln-type')
" 2>/dev/null
```

## Phase 3: Live KB Query

```bash
python tools/retriever.py <vuln-type> "<vuln-type> common attack patterns variants" --top-k 10
python tools/immunefi_retriever.py <vuln-type> "<vuln-type> exploit bounty report real world" --top-k 5
```

## Phase 4: (Skip — no agent in this skill)

Not applicable for this meta-skill. Display: "No agent spawned — this skill surfaces patterns only."

## Phase 5: Display Pattern Summary

```
KB Pattern Summary: <vuln-type>
Solodit KB entries: N  |  Immunefi reports: M

Auto-learned patterns (last 3 synthesis cycles):
  <synthesis text from Phase 2>

Live KB top matches (by similarity):
  [score: 0.94] <title> — <severity> — <protocol>
  [score: 0.91] <title> — <severity> — <protocol>
  ... (up to 10)

Immunefi real-world exploits:
  1. <title> | <severity> | <protocol>
     <description excerpt (first 100 chars)>
     URL: <url>
  ... (up to 5)

To run a targeted agent scan:
  /reentrancy        — for reentrancy patterns
  /access-control    — for access control patterns
  /arithmetic        — for arithmetic patterns
  (etc.)
```
