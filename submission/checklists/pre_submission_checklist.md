# Pre-Submission Checklist

Human checklist mirroring the eight hard gates. The automated gate
(`submission/gates/submission_gate.py`) enforces these mechanically; this list
is for the human who gives final approval. **Submission is never automatic — a
human must approve every submission.**

A candidate may be submitted only when its computed status is
`READY_TO_SUBMIT_AFTER_APPROVAL` (or `READY_FOR_HUMAN_REVIEW` that a human has
personally cleared) **and** a human has approved.

## 1. Scope
- [ ] The affected asset is in the program's scope list (`scope_status = in_scope`).
- [ ] The impact category is accepted by the program (`impact_in_scope = true`).
- [ ] The exploit does **not** depend on any out-of-scope assumption.
- [ ] No admin/governance privilege is required — or the program explicitly
      accepts privileged-role attacks.
- [ ] No reliance on social engineering, leaked/compromised keys, phishing, or
      compromised infrastructure.

## 2. Attacker reachability
- [ ] There is a concrete external attacker entrypoint (callable from an EOA).
- [ ] The exact call path is written out.
- [ ] Preconditions / required state setup are listed.
- [ ] It is stated why the relevant defenses do not block the path.

## 3. Impact / severity
- [ ] The impact is concrete (named asset delta or state transition).
- [ ] Severity is mapped to the program's impact table.
- [ ] Severity is not inflated (claim ≤ supportable ceiling for the impact + proof).
- [ ] Worst-case and realistic-case impact are separated.

## 4. Proof of Concept (required for High/Critical)
- [ ] The PoC compiles or executes (`poc_status` is passing/compiling).
- [ ] Reproduction steps are deterministic.
- [ ] Before/after state or balance delta is shown.
- [ ] Attacker and victim setup is clear.
- [ ] **No mainnet attack. No public-testnet abuse. No fabricated assumptions.**

## 5. Duplicate / known issue
- [ ] Local prior-audit reports were searched.
- [ ] Program known-issues / prior public disclosures were searched.
- [ ] Any possible duplicate / prior-audit overlap is recorded and compared.

## 6. Evidence completeness
- [ ] Code lines (file:line) are linked.
- [ ] Affected functions are named.
- [ ] Call trace is present.
- [ ] State transition is present.
- [ ] Logs / test output / proof artifact path are present.

## 7. Invalidation / defense
- [ ] Likely defenses are listed.
- [ ] For each, why it fails or does not apply is stated.
- [ ] Any uncertainty is clearly marked.

## 8. Human approval
- [ ] A human has read the readiness report.
- [ ] A human approves this specific submission.
- [ ] The submission will be filed manually by a human.
