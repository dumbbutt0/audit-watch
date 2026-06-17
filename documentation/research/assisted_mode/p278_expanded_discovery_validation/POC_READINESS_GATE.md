# P278 — POC_READINESS_GATE

`poc_readiness_evidence_gate.py` applies the 10-point standard (root cause · attacker path · control point · impact
delta · victim/gainer · terminality/amplification · mechanism distinction · refutation attempted · PoC assertion ·
bounded assumptions). READY_FOR_POC_INTENT only if ALL present (non-placeholder). Statuses are advisory; no candidate
becomes confirmed/reportable/submission-ready/severity. PoC execution budget = 5 (extra READY → DEFER_POC_BUDGET).
Fail-closed on guard violations.

## Result
| status | count |
|---|---|
| NEEDS_MORE_EVIDENCE (corpus auto, 12 contests) | 84 |
| READY_FOR_POC_INTENT (hand-authored sample) | 2 |
| **severe concluded/reportable FP** | **0** |

- Corpus-wide auto-evidence yields **0 READY** — every candidate is missing the attacker/delta/victim/terminality/
  tx/assertion dimensions (the operator-to-derive gap). This is the honest, expected outcome: the pipeline *surfaces
  and routes* candidates but does not *auto-complete the evidence* PoC requires.
- The hand-authored sample reaches **READY_FOR_POC_INTENT** with PoC-intent records — proving the standard is reachable
  and not impossibly strict.
- Guard PASS; fail-closed verified (missing-field packages can never become READY).
