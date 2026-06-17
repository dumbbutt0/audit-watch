# P203 — refined gate v2 (plan)

## Goal
Test a v2 severity gate that adds an **independent source-substantiation precondition** before HIGH_CONFIRMED, over
**frozen P202 decent artifacts** (no rerun, no production change). Hypothesis: v2 keeps H-01 HIGH_CONFIRMED while
demoting M-03 (receiveFromBridge) and the unawarded false-Highs (decent-06/12) that v1 over-confirmed.

## Backfit firewall
Orchestrator is doubly answer-aware → the v2 regrade is applied by a **fresh cold-start key-blind firewall subagent**
(general v2 rule + frozen raw outputs + v1 calibration + decent source; NO answer key / P202 scoring / expected
outcomes / PCS / memory). Rule written before application. Orchestrator only scores v1-vs-v2 post-regrade.

## Sequence
precheck → write v2 rule (general, before) → v1 failure extraction (no key) → fresh key-blind v2 regrade
(V2_MECHANISM_REGRADING.json) → score v1 vs v2 vs P202 key (validate_p203.py) → scorecards + HIGH-precondition audit
→ recommendation/decision → integrity + memory.

## Decision space
V2_GATE_PROMISING · V2_GATE_PARTIAL · V2_GATE_FAILED_FALSE_DEMOTION · V2_GATE_FAILED_FALSE_HIGH · INVALID_RUN.

## Guardrails
Frozen P202 artifacts (FREEZE1 54abf9ca / FREEZE2 90cf2a4f) reused; production hashes byte-identical START==END;
v2 regrade key-blind by fresh subagent; every HIGH_CONFIRMED requires source-proven custody/value-flow + material
magnitude; H-01 and M-03 explicitly tested; v1 vs v2 scored separately; JSON valid; no key-backfit into rules.
