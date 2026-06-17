## Report Gate — mandatory before writing any submission

Answer all 8 questions in draft notes before writing the report.
This gate is required even if `output/findings_ice.json` is present for the finding.

1. What exact state did the attacker corrupt?
2. What protocol function consumes that state?
3. Did the PoC reach that consumer?
4. Did the consumer perform a real protocol action?
5. What impact was directly proven?
6. What impact was only plausible?
7. What severity is justified only by the direct proof?
8. What would be needed to increase severity?

If questions 2 or 3 are unanswered: **do not write the report. Continue consumer tracing.**
Spawn `agents/impact_chain_escalation.md` or check `output/ice_manual_review.jsonl`.

---

# Contest Submission Format

Use this format for all individual finding submissions (Code4rena, Immunefi, Cantina, etc.).
Internal tools (quality checklist, severity justification, pipeline scores) must NOT appear
in the final submission — they are for internal review only.

---

## Title

```
<Vulnerability classification> in <function/contract> leads to <concrete impact>
```

The reader must understand the basics from the title alone. Name the root-cause class
and the impact. Do not use finding IDs, internal codes, or implementation details as
the primary descriptor.

**Good examples:**
- "Oracle unit mismatch in close-factor calculation allows liquidators to seize excess collateral beyond protocol limits"
- "Integer underflow in liquidation math permanently blocks insolvent positions from being liquidated, enabling bad debt accumulation"
- "Missing reentrancy guard on flash loan callback allows repeated collateral withdrawal"
- "Lack of access control in liquidation engine allows any caller to impersonate an arbitrary liquidator"

**Bad examples (too vague or internal):**
- "Bug in calculate_liquidation"
- "LG-005: U128 underflow"
- "High severity finding in arithmetic module"

---

## Description

### Brief/Intro

One paragraph. State the bug, its root cause, and its consequence if exploited in
production. No hedging ("could potentially", "might"). Name the victim and the loss
or harm type. A reviewer reading only this paragraph should understand what is broken
and why it matters.

### Vulnerability Details

Provide enough detail to prove the bug exists without requiring the reader to run code.

- Exact file path and line number(s) of the buggy code
- Root cause: what invariant or assumption is violated and why
- Annotated code snippet showing the vulnerable code
- Concrete arithmetic trace or step-by-step attack scenario (use real numbers)
- Comparison to correct implementation in the same codebase, if one exists

### Impact Details

- Who is affected (protocol, specific users, liquidators, borrowers, LPs)
- What they lose or what the protocol loses (quantified where possible: amounts, percentages, affected positions)
- Why the claimed severity level is correct — map to the contest's severity criteria
- Reference analogous historical findings if applicable

### References

List exact file paths + line numbers and a one-line description of each. Include:
- Buggy location(s)
- Correct reference implementation (if one exists in the same repo)
- One-line description of the fix

---

## Proof of Concept

Provide a runnable test command and its expected output. Annotate 2–4 key assertions
from the test code to show what is being proved.

```bash
# run command
cargo test --manifest-path pocs/k2/<ID>/Cargo.toml <test_module> 2>&1
```

Expected output:
```
test <test_name> ... ok
test result: ok. N passed; 0 failed
```

Key assertions (annotated inline):
```rust
// What this assertion proves and why it maps to the claimed impact
assert_eq!(buggy_value, expected_buggy, "...");
assert!(exploited_balance < victim_before, "...");
```

---

## Mitigation

Provide a concrete fix. Include:
- The exact file path and line number to change
- A before/after code snippet
- One sentence explaining why the fix is correct

---

## Format rules

- Remove any section named "Summary", "Severity Justification", or "Quality Checklist" from the final submission — these are internal pipeline outputs
- The Description sub-sections (Brief/Intro, Vulnerability Details, Impact Details, References) are rendered as part of the Description field in the contest submission UI
- Proof of Concept is a separate top-level field
- Keep the report factual and precise; avoid subjective language
