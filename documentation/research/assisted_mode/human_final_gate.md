# Human Final Gate (P99)

The last gate before any submission. **Only a human completes this.** Audit-Watch never sets the result and never
submits. Complete every item, then record one output state.

## Checklist
- [ ] **Affected asset is in scope** — the contract(s) are on the program's in-scope list at the pinned commit.
- [ ] **Impact is in scope** — the demonstrated impact class is eligible under the program's rules.
- [ ] **Duplicate / publicly-known search completed** — checked the program's known-issues, prior submissions, and
      public reports; this is not a known/duplicate issue (or note the dup).
- [ ] **Program severity tier checked** — mapped the finding to the program's severity matrix (may differ from the
      package's conservative tier).
- [ ] **PoC reran locally** — the documented `forge test` command was executed and passes on the pinned source;
      the patch test was re-checked and the source restored (hash verified).
- [ ] **No internal tool / eval / scanner / blind language** anywhere in the report body or platform fields.
- [ ] **No overclaim** — every impact statement is bounded by what the PoC actually proves.
- [ ] **Mitigation is minimal and source-backed** — the smallest fix that addresses the root cause.
- [ ] **Title is specific and not sensational** — describes the mechanism, not a scare headline.
- [ ] **All claims cite source or PoC output** — no unsupported assertions.
- [ ] **Final submit / no-submit decision recorded** — via `record_assisted_outcome.py`.

## Output states
- `APPROVED_TO_SUBMIT` — all items pass; the human chooses to submit. (Required before any `submitted=true`.)
- `DO_NOT_SUBMIT_SCOPE` — asset or impact not in scope.
- `DO_NOT_SUBMIT_DUPLICATE` — duplicate or publicly-known.
- `DO_NOT_SUBMIT_SEVERITY_UNSUPPORTED` — claimed severity not supported by source/PoC under the program's rules.
- `DO_NOT_SUBMIT_WEAK_POC` — PoC does not convincingly prove the impact.
- `NEEDS_REPORT_EDIT` — substance is fine but wording/structure must change first.
- `NEEDS_MORE_EVIDENCE` — needs additional PoC/source evidence before a decision.

## Hard rules
- `APPROVED_TO_SUBMIT` is necessary for `submitted=true`; the outcome recorder enforces this.
- Terminal program outcomes (`accepted` / `duplicate` / `rejected`) can only be recorded once `submitted=true`.
- Scope and duplicate status are **human determinations** — Audit-Watch leaves them `PENDING` and never clears them.
- The C.0 **harness classification** (`HARNESS_SIMPLE/MODERATE/COMPLEX/BLOCKED`, see runbook) is an advisory
  **effort** signal recorded for context only — it is never a gate input here and never advances candidate status.
