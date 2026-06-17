---
name: human-queue
description: "Show findings that require human auditor validation before submission. These represent the 10% in the Jason Hadex 90/10 AI/human split — novel patterns, low AI confirmation scores, multi-hop chains, or Critical claims without PoC. Activate when user says: /human-queue, what needs human review, show human queue, which findings need me, what should I look at manually."
---

# Human Review Queue

Shows findings the AI pipeline has flagged for human expert validation.
These are the 10% in the Jason Hadex 90/10 split — the findings where AI
cannot reliably confirm exploitability on its own.

## Instructions

### 1. Check if classifier has run

Check if `data/triage/human_review_queue.jsonl` exists in the active audit workspace
(read `config/active_audit.json` to resolve the audit root).

If missing or empty, run the classifier first:
```bash
python scripts/human_review_classifier.py
```

If still empty after running: "No findings require human review — all AI-confirmable. ✅"

### 2. Display the queue

Read `data/triage/human_review_queue.jsonl`. Sort by `human_review_score` descending.

Print one block per finding:

```
Human review queue: N findings requiring expert validation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] RE-003  Missing CEI in withdraw()                High     score: 5/8
    Triggered: confirmation_score=0.38, kb_similarity=0.22, trace_depth=3,
               no_compound_match, bsa_finding
    Why: AI disagrees with itself (38% confirmation) AND pattern not in KB.
         Do not submit at High without manually tracing the reentry path.
    Action: Read withdraw() → callback path in [file:line]. Verify reentry is possible.

[2] CC-001  Cross-chain message replay attack         Critical  score: 4/8
    Triggered: cross_chain_category, critical_no_poc, confirmation_score=0.50
    Why: Critical claim with no Level 2 PoC and AI only 50% consistent.
    Action: Trace the replay precondition. Write at least a Level 2 PoC before submitting Critical.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI-confirmed: M findings are ready for specialist review without manual intervention.
Use /submit-ready to see what can be submitted.
```

### 3. Offer next actions

```
Next steps:
- /confirm <ID>   — re-run multi-pass on a specific finding (try to AI-confirm it)
- /poc            — check PoC status for queue findings
- /risks <ID>     — see rejection risks before manually upgrading severity
- /surface        — re-check which functions were flagged as high attack surface
```

### 4. After human review

When the user has personally validated a finding in the queue and wants to clear it:
- They should run `/confirm <ID>` to re-run multi-pass (it may now confirm with better framing)
- Or they can manually set `human_review_required: false` in the finding JSON and re-run triage

Do NOT automatically remove findings from the human review queue. Only the human auditor
can clear a finding from this queue by either confirming it passes multi-pass or by
making a deliberate decision to submit it as-is.
