# Extending Audit-Watch

---

## Safe Extension Rules

Before adding anything to the pipeline, read these rules:

1. **Never auto-submit.** No extension may submit to a live bounty program without explicit human confirmation.
2. **Never raise severity without a confirmed consumer PoC.** ICE must trace the full chain before severity can increase.
3. **Never hide mocks.** Any PoC that uses mock contracts must disclose them clearly in the submission.
4. **Never delete audit evidence.** Pipeline outputs in `audits/<id>/` are audit trail artifacts. Archive, do not delete.
5. **Never modify `data/evaluation/ground_truth.jsonl` programmatically.** This is the human-only calibration anchor.

---

## Adding a New Specialist Agent

### Step 1: Create the agent specification

Copy an existing agent as a template:
```bash
cp agents/reentrancy.md agents/my_new_agent.md
```

Edit `agents/my_new_agent.md` to:
- Set the Role section describing the new vulnerability domain
- List the Inputs the agent receives
- Define the Checks to perform
- Specify the Output file path: `output/findings_my_new_agent.json`
- Define a unique finding ID prefix (e.g., `MN-` for "my_new")

### Step 2: Update the schema

Add the new agent name to the `agent` enum in `schema/findings_schema.json`:
```json
"enum": [
  "reentrancy",
  ...
  "my_new_agent"
]
```

### Step 3: Add to the Step 2 spawn list

In `CLAUDE.md`, under "Step 2 — Spawn specialist subagents in parallel", add:
```
- agents/my_new_agent.md
```

### Step 4: Update the run_pipeline.sh triage step (if needed)

If the agent produces findings that need PoC, no changes needed (triage handles all agents). If it has special handling, add to the `triage` case in `run_pipeline.sh`.

### Step 5: Test

```bash
# Create a minimal test contract
echo 'contract Test {}' > /tmp/test.sol
python tools/static_analysis.py /tmp/test.sol
# Spawn the agent manually via Claude Code Task tool
# Verify output/findings_my_new_agent.json exists and is valid
python scripts/validate_agent_output.py output/
```

---

## Adding a New Prompt

Prompts are instruction templates loaded into agent context.

### Step 1: Create the prompt file

```bash
# Create in prompts/
touch prompts/my_new_prompt.md
```

### Step 2: Reference it in the relevant agent

In `agents/my_new_agent.md`, add to the Inputs section:
```
- `prompts/my_new_prompt.md` — read this as your [specific framework] before analyzing
```

### Step 3: Document it

Add an entry in [documentation/prompts.md](prompts.md) with file, purpose, pipeline stage, inputs, and output.

---

## Adding a New Skill

Skills are Claude Code slash commands.

### Step 1: Create the skill directory and SKILL.md

```bash
mkdir -p .claude/skills/my-skill
```

`.claude/skills/my-skill/SKILL.md` format:
```markdown
---
name: my-skill
description: "Brief description for trigger matching. Activate on: /my-skill, keyword1, keyword2."
---

# My Skill Title

One paragraph description.

## Instructions

Step-by-step instructions for what to do when this skill is invoked.
```

### Step 2: Test the skill

In Claude Code, type `/my-skill` to invoke it. Verify it executes the expected steps.

### Step 3: Document it

Add an entry in [documentation/skills.md](skills.md).

---

## Adding a New Pipeline Stage

### Step 1: Create the script

```bash
touch scripts/my_new_stage.py
```

Follow the pattern of existing scripts:
```python
#!/usr/bin/env python3
"""
my_new_stage.py — Description.
Usage: python scripts/my_new_stage.py [--all] [--finding-id <ID>]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

OUTPUT_DIR = audit_path("output")
TRIAGE_DIR = audit_path("data/triage")
```

### Step 2: Update audit_context.py if a new subdirectory is needed

Add the new path to the `_AUDIT_SUBDIRS` list in `scripts/audit_context.py`:
```python
_AUDIT_SUBDIRS = [
    ...
    "data/my_new_stage",
]
```

### Step 3: Add to CLAUDE.md

Insert the new step in the appropriate position in the pipeline workflow section of `CLAUDE.md`.

### Step 4: Add to run_pipeline.sh

Add a case entry in `run_pipeline.sh` if the stage should be accessible via the shell runner.

### Step 5: Update generate_status.py

If the stage produces output files that should appear in the dashboard, add readers in `scripts/generate_status.py`.

---

## Adding a New MCP

### Step 1: Create the tool file

```bash
touch tools/my_new_mcp.py
```

Follow the pattern of `tools/quicknode_mcp.py`:
- Non-fatal on missing API keys (return `{}` or `[]`)
- Print warning to stderr if key absent
- Validate schema of responses before passing to agents

### Step 2: Register in .mcp.json

```json
{
  "mcpServers": {
    "my-new-mcp": {
      "command": "python",
      "args": ["tools/my_new_mcp.py"],
      "env": {
        "MY_API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

### Step 3: Add to network_allowlist

Add the new API domain to `config/zero_trust_policy.json` → `network_allowlist`.

### Step 4: Document it

Add an entry in [documentation/mcp-integrations.md](mcp-integrations.md).

---

## Adding a New Triage Gate

### Step 1: Add gate logic to pre_submission_gate.py

Each gate is a function that takes a finding dict and returns `{"verdict": "PASS"|"FAIL"|"WARN", "reason": "..."}`.

```python
def gate_my_new_check(finding: dict, ...) -> dict:
    """Gate N: My new check."""
    # ... logic ...
    return {"verdict": "FAIL", "reason": "...", "tag": "my_new_tag"}
```

Add the gate to the `run_all_gates()` function.

### Step 2: Add the invalidation tag

Add the new tag to `config/agent_policy.json` → `invalidation_tags` → `canonical_tags`:
```json
"canonical_tags": [
  "already_guarded",
  ...
  "my_new_tag"
]
```

### Step 3: Update the gate documentation

Add a row to the gates table in [documentation/triage-and-severity.md](triage-and-severity.md).

---

## Continuous KB Updates

The knowledge base can be kept fresh automatically:

```bash
python scripts/solodit_scraper.py --continuous
```

Agent files are automatically updated with an "## Auto-learned patterns" section after each scrape cycle. Pattern history is stored in `kb/patterns/<vuln_type>.json`.

Agents updated automatically: reentrancy.md, access_control.md, arithmetic.md, oracle.md, flash_loan.md, logic.md, dos.md, snapshot.md
