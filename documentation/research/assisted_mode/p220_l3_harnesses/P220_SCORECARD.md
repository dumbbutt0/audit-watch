# P220 — Scorecard

All three High-ceiling candidates were attempted with source-valid, isolated Foundry harnesses on real unmodified
Zeta contracts. 7/7 harness tests pass.

| ID | Mechanism | Harness | l3_status | decide() severity | Category |
|----|-----------|---------|-----------|-------------------|----------|
| ZETA-04 | onReceive missing whenNotPaused | 3/3 PASS | PASS | medium (High blocked: TSS-gated) | **L3_PASS_MEDIUM** |
| ZETA-10 | getEthFromZeta missing nonReentrant (theft) | 2/2 PASS | FAIL | invalid (theft refuted) | **L3_FAIL_DEMOTED** |
| ZETA-11 | Trident getPools()[0] unvalidated (theft) | 2/2 PASS | PASS (dos) | medium | **WRONG_MECHANISM_PARTIAL** |

## Reading
- **ZETA-04** — clean executed PASS of the pause-bypass mechanism (paused mint succeeds; guarded sibling reverts).
  Severity is calibrated Medium because the trigger is the privileged TSS caller; promotion to High is a deliberate
  human-judgment call (the answer key rates it High — recorded only as a post-score note, never used to shape the run).
- **ZETA-10** — the missing `nonReentrant` is real, but the executed harness shows the reentrancy realizes **no
  theft**: the consumer pools no balances and every re-entrant call is self-funded. A clean refutation.
- **ZETA-11** — the unvalidated `getPools()[0]` reproduces a **DoS** on real source (with control). The candidate's
  **theft** mechanism depends on an unproven external-factory property and is not source-confirmable → wrong-mechanism.

## Net
- False-Highs introduced: **0** (no candidate auto-promoted to High; every blocked High carries a written blocker).
- Over-rating guard intact; ZETA-10 demonstrates the refutation path works on a live theft claim.
- Under-rating note: ZETA-04 (and the DoS reading of ZETA-11) again surface the known TSS-gated / DoS severity-floor
  gap from P212/P215 — flagged for human review, not silently upgraded.

**Phase decision: `ZETA_L3_PARTIAL`** — one executed PASS (Medium), one executed refutation, one wrong-mechanism
partial. All three attempted, all source-valid, missing/absent evidence kept explicit.
