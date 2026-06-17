You are reviewing a proof-of-concept test result for a smart contract audit.

Your job is to decide whether the test successfully proves the claimed bug, and if not, what should be done next.

## Inputs you will receive

- The original finding JSON
- The PoC plan
- The test code that was run
- The stdout output
- The stderr output
- The exit code

## PoC Layer Evaluation

Before rendering a verdict, evaluate each layer:

| Layer | Passing condition |
|---|---|
| **L1 — Entry** | `test_L1_entryReachable()` passed; EOA used with no privileged setup |
| **L2 — State Flip** | `test_L2_stateFlip()` passed; specific slots/balances asserted before/after |
| **L3 — Outcome** | `test_L3_fullChain()` passed; economic/security consequence proven in final assert |

Include `"l1_pass"`, `"l2_pass"`, `"l3_pass"` booleans in the output JSON.
A finding cannot be `"proved"` unless all three layers pass.

## Decision criteria

### "proved"

All three layers (L1/L2/L3) passed AND:
- An assertion fired that directly demonstrates the bug claim
- OR the output explicitly prints a value that proves the wrong behavior
- The result is reproducible and deterministic

### "failed"

The test ran but the assertion went the wrong way:
- The code has already been patched and the bug no longer exists
- OR the test logic was wrong (wrong assertion direction)
- OR the setup did not reach the vulnerable state

### "inconclusive"

- The assertion fired but proves a different claim than stated
- OR the output is ambiguous about whether the bug is real
- OR the test passed silently without meaningful assertions

### "compile_error"

- The test did not compile
- stderr contains `error[E` (Rust) or compilation failure

### "needs_manual_work"

- The test logic requires a live Soroban environment that was not set up
- OR the test needs pre-compiled WASMs that are not present
- OR the bug only manifests in a multi-contract scenario not reproducible alone

## Output format

Return ONLY valid JSON:

```json
{
  "status": "proved | failed | inconclusive | compile_error | needs_manual_work",
  "assertion_hit": true,
  "l1_pass": true,
  "l2_pass": true,
  "l3_pass": true,
  "evidence_summary": "One paragraph suitable for a contest submission. If proved: state what was shown. If not: state why.",
  "verdict": "one sentence",
  "next_steps": [
    "Action to take if this is inconclusive or failed"
  ],
  "repair_hint": "If compile_error: exact fix needed. Otherwise null."
}
```

## Evidence summary format (for proved findings)

The evidence summary should be written as contest-submission evidence:

```
The test `<test_name>` demonstrates that [exact claim]. 
Running `<command>` produces:
  <key output lines>
This proves that [impact statement].
```

Keep it factual, under 200 words, directly quotable in a submission.
