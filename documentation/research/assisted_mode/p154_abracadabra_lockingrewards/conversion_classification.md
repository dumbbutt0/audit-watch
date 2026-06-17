# P154 — Stage 5 Conversion Classification

Candidate: `H5-abracadabra-lockingrewards-boost` (LockingMultiRewards post-expiry boost retention)

| field | value |
|---|---|
| mechanism_confirmed | **true** (runtime: real contract keeps 3× after `unlockTime`; corrected real-code reference → 0 delta) |
| attacker_reachable | **true** (unprivileged EOA `stake(amount,true)`; no privileged setup; user cannot self-remediate) |
| severity_bearing | **true** (zero-sum reward theft from honest stakers; quantified 174.999…e18; magnitude operator-delay-dependent) |
| novelty_clear | **unknown** (`duplicate_unknown` — empty local answer key; no novelty inferred) |
| reportable | **unknown** (final reportability + severity grade is the human decision this outcome routes) |
| runtime_status | **runtime_confirmed** |
| runtime_confidence | **high** |
| reachability_verdict | **unprivileged_user_reachable_no_self_remediation** |
| severity_class | **medium_potential_operator_delay_dependent** (human to finalize Low↔High) |
| duplicate_status | **duplicate_unknown** |
| conversion_outcome | **reportable_candidate_needs_human_review** |
| primary_blocker_if_not_reportable | **null** (it IS a reportable candidate; the residual is a severity/scope grade, not a defeating blocker) |
| human_review_required | **true** |
| routing_allowed | **false** |
| submission_ready | **false** |

## Promotion-rule check (all six must hold to use `reportable_candidate_needs_human_review`)
1. **Mechanism runtime-confirmed** ✓ — 4/4 tests; corrected reference (real code) zeroes the delta.
2. **Attacker reachability through production flow** ✓ — unprivileged `stake`; no privileged precondition;
   no user opt-out.
3. **Severity-bearing impact concrete** ✓ — zero-sum redistribution, A's gain = B's loss, quantified.
4. **Blocker is NOT privileged-only / unreachable / mechanism-absent / intent-ambiguous** ✓ — the
   mechanism is present, reachable, and impactful; **intent does not refute it** (contrast P149, where
   NatSpec framed the behavior as intended and refuted the external-theft framing). Here the NatSpec
   *expects* prompt processing, which implies the boost is **not** supposed to persist — so intent points
   *toward* a defect, not away. The residual is a **severity/scope grade** (how the program treats
   operator-cadence reliance), which is the proper subject of human review, not an intent-refutation.
5. **Evidence human-reviewable** ✓ — deterministic Foundry harness + quantified deltas + real-code control.
6. **No submission** ✓ — `submission_ready=false`, `routing_allowed=false`.

## Honesty notes / what would have changed the verdict
- Had `processExpiredLocks` been user-callable, the user could self-remediate → severity would drop (likely
  `severity_too_low`).
- Had the NatSpec framed persistent post-expiry boost as intended → `needs_context` / `intent_ambiguous`
  (the P149 pattern).
- Had `balanceOf` de-boosted automatically at `unlockTime` → `runtime_refuted`.
None of these hold, so the honest outcome is `reportable_candidate_needs_human_review` with the severity
grade deferred to a human.
