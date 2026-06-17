# P212 — human review checklist (STAGE 1 output; answer key NOT opened)

## Candidate list (7 root causes; threat ceiling ≠ final severity)
Permissionless: SOPH-01 (withdraw boost conservation), SOPH-02 (accPointsPerShare scaling), SOPH-03 (depositStEth
wrap off-by-one), SOPH-04 (boost denominator dilution — likely intended). Privileged: SOPH-05 (withdrawal-window lock),
SOPH-06 (add/set withUpdate), SOPH-07 (heldProceeds under-withdraw — benign).

## Recommended reportable candidates (need human verification before any submission)
1. **SOPH-01** — strongest concrete omission (boostAmount not decremented on withdraw). Verify materiality.
2. **SOPH-03** — depositStEth wrap-vs-received; verify stETH path in-scope + impact (DoS vs residual draw).
3. **SOPH-02** — accPointsPerShare scaling; decide view-only vs settled impact.
SOPH-04 likely by-design (confirm vs spec). SOPH-05 privileged (Sherlock admin-input rules). SOPH-06/07 lower.

## L3 / readiness status
**0 candidates are High-submission-ready.** All High-ceiling candidates are blocked
(`blocked_by_missing_l3_poc`): permissionless ones → `needs_harness_for_severity`; privileged → `medium`. No High may
be submitted without an executed L2/L3 harness (PASS) or a written human override. Human review mandatory.

## What evidence is missing
- Executed Foundry harness for SOPH-01/02/03 (deploy proxy + initialize + add pool + mock LST(s); prove material
  realized impact or its absence). None built within first-hunt scope.
- Spec confirmation for SOPH-04 (is boost dilution intended?).
- Admin trust/timelock model for SOPH-05 (Sherlock often invalidates pure admin-input issues).

## Exact commands to verify (when harnesses are authored under pocs/p212/)
- `cd documentation/research/assisted_mode/p212_pseudo_live_hunt/pocs/p212 && forge test -vvv` (harnesses TBD)
- Readiness overlay (already run): `AUDITWATCH_L3_READINESS=1 python3 scripts/... l3_evaluate` → all blocked.

## STOP — awaiting user
Reply "ready for scoring" (or "these findings are ready for submission review") to authorize STAGE 2 (open the sealed
Sherlock report + score). The answer key has NOT been opened.
