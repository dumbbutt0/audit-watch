---
name: confirm
description: "Run multi-pass LLM confirmation for High/Critical findings to handle non-determinism (Jason Hadex principle: confirm 3–5 times before trusting a claim). Findings confirmed less than 60% of the time are flagged for human review. Activate when user says: /confirm, confirm findings, multi-pass check, how confident are we, validate High findings, or /confirm <ID>."
---

# Multi-Pass Confirmation

Implements the Jason Hadex principle: LLM reasoning is non-deterministic.
High/Critical claims must be confirmed 3–5 times independently before being trusted.
A finding that passes once but fails four times is not ready to submit.

## Instructions

### 1. Determine scope

Parse the user's message for a finding ID (pattern: 2-3 uppercase letters, dash, 3 digits):
- If found (e.g. `/confirm RE-001`): run for that specific finding only
- If not found: run for all High and Critical findings across `output/findings_*.json`

### 2. Check config

Read `config/agent_policy.json` → `multi_pass` block:
- `enabled` (default: true) — if false, inform user and stop
- `passes_high` (default: 3) — confirmation passes for High findings
- `passes_critical` (default: 5) — confirmation passes for Critical findings
- `confirmation_threshold` (default: 0.6) — minimum fraction to avoid human review

Also check `active_mode` — if `fast`, skip and inform user.

### 3. Run confirmation

First decide the route:

```bash
python scripts/llm_runtime.py --have-key   # exit 0 = API available, non-zero = api-free (default)
```

**API path (have-key):** run the script directly.
```bash
python scripts/multi_pass_confirm.py            # or --finding-id <ID>
```

**Credit-free path (api-free default — DO THIS IN-SESSION):** the script would otherwise skip and leave
High/Critical unconfirmed (which the canonical record then routes to `human_pending`). Instead:

```bash
python scripts/confirm_prepare.py               # stages output/confirm/_bundles/<id>.json (High/Critical only)
```
Then, for EACH bundle in `output/confirm/_bundles/` (skip `index.json`), run the required number of
**independent** passes (`passes_required` in the bundle) yourself, in-session:
- Each pass is a fresh yes/no judgment: *is the vulnerable path reachable from an unprivileged entry AND is the
  logic flaw real?* Reset your reasoning each pass — do not anchor on the previous pass. Use ONLY the bundle's
  `claim` + `source_slice`; never invent reachability the source doesn't show.
- Record `passes_yes` / `passes_run` honestly. A finding that passes once and fails the rest is NOT confirmed.

Write the decisions to `output/confirm/_decisions.json`:
```json
[{"id": "H-1", "passes_run": 3, "passes_yes": 2, "human_review_reason": ""}]
```
Then persist (computes score + human_review flag, validates against the staged bundles):
```bash
python scripts/confirm_write.py
```
Either path produces the same `output/findings_confirmed.json`.

### 4. Display results

Read `output/findings_confirmed.json` and print one line per finding:

```
Multi-pass confirmation results:

[RE-001] Missing CEI in withdraw()                        High
  Passes: 3/3 YES  score: 1.00  ✅ Confirmed — AI consistent

[FL-002] Flash loan oracle price manipulation             Critical
  Passes: 3/5 YES  score: 0.60  ✅ Confirmed — at threshold

[OR-003] Spot price used as oracle in getPrice()          High
  Passes: 1/3 YES  score: 0.33  ⚠️  Human review required
  Reason: AI inconsistent — trace the oracle call path manually before submitting

Summary: N confirmed, M flagged for human review
```

Symbols:
- ✅ `confirmation_score >= threshold` — AI is consistent; proceed to triage
- ⚠️ `confirmation_score < threshold` — human review required before submitting

### 5. Update human queue

After confirmation runs, update the routing:

```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

Tell the user: "Human review queue updated. Use /human-queue to see flagged findings."
