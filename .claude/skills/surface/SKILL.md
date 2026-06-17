---
name: surface
description: "Map the attack surface of a smart contract using the ITE (Intent/Technique/Evasion) framework. Classifies all functions by attacker relevance, scores them 1–5, and produces ITE decompositions for high-value targets. Activate when user says: /surface, map attack surface, ITE analysis, show attack surface, what should I focus on, where should I look first."
---

# Attack Surface Mapping

Runs the `attacker_mindset` agent to classify and score all contract functions
using the ITE framework before specialist agents run. This is Step 0.25 of
the ITE audit pipeline and can also be run independently.

## Instructions

### 1. Determine scope

If the contract path was not provided, list available contracts:
```bash
find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
```
Ask: "Which contract should I map? I found: [list]"

### 2. Sandbox pre-check

```bash
python scripts/sandbox_check.py <contract_path>
```
Stop if flags are raised without `--allow-flagged`.

### 3. Spawn attacker_mindset agent

Spawn `agents/attacker_mindset.md` as a Task. Provide:
- Full contract source
- `output/static.json` if it exists (read it first)
- `output/findings_protocol_context.json` if it exists
- `data/interactions/dangerous_chains.json` if it exists

### 4. Validate output

```bash
python scripts/validate_agent_output.py output/findings_attacker_mindset.json
```

### 5. Display results

Read `output/attack_surface.json` and print:

```
Attack surface: N functions mapped
  admin: N   user: N   view: N   internal: N

Top attack targets (score 5/5):
  withdraw()      user    — Intent: drain ETH balance; Technique: reenter during .call{value}
  flashLoan()     user    — Intent: manipulate oracle price; Technique: callback before repay check

High value (score 4/5):
  setOracle()     admin   — Intent: redirect price feed; Technique: unguarded if no two-step
  liquidate()     user    — Intent: exploit stale price; Technique: sandwich oracle call

Standard targets (score 3/5):
  ...

Specialist agents should focus on: withdraw(), flashLoan(), setOracle(), liquidate()

Run /ite-audit to proceed with the full pipeline.
```

If `output/attack_surface.json` already exists from a previous run, show the cached
results and offer to re-run:
"Cached attack surface found (from [timestamp]). Show cached results or re-run?"
