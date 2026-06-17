# P274 — IMPACT_FIRST_TRIAGE (Phase 5, frozen P269)

Frozen `impact_first_poc_triage.py` (`63c88d02d2c7eefa`) over the 5 coverage-handoff representatives
(`outputs/triage_candidates.json`). Output `outputs/triage_decisions.json` (+ `.md`). poc_budget = 4. Guard: **0
violations**.

## Decisions
| id | class | impact_fit | heavy | outcome |
|---|---|---|---|---|
| `distribute` | ACCOUNTING | 13 | yes | **SELECT_FOR_PARTIAL_RUNTIME** |
| `wq_withdraw` | DOS_LIVENESS | 11 | yes | **SELECT_FOR_PARTIAL_RUNTIME** |
| `burnAndWithdraw` | STATE_MACHINE | 11 | no | **SELECT_FOR_FULL_POC** |
| `offers` | ORDER_VALIDATION | 11 | yes | **SELECT_FOR_PARTIAL_RUNTIME** |
| `pool_redeem` | SHARE_ROUNDING | 2 | no | **DEFER_LOW_IMPACT** |

## Reading
- **4 PoC candidates across 4 distinct award classes** selected (ACCOUNTING, DOS, STATE, ORDER). The cross-class
  coverage from Phase 4 survived impact ranking — no class was dropped for harness weight (heavy → PARTIAL_RUNTIME,
  never de-scoped).
- The only deferral is `pool_redeem` (SHARE rounding), correctly judged low-impact dust — it was the *easy* control
  candidate, and impact-first declined to spend a slot on it. This is the anti-easy-PoC discipline at the triage stage
  (the P269 fix) working in concert with the coverage layer.
- All 4 selected are heavy except `burnAndWithdraw`; the heavy ones route to PARTIAL_RUNTIME rather than being
  dropped — matching the P269 "harness weight is a constraint, not a de-scope" rule.

Net: the full selection chain (selector → coverage → triage) delivers a **class-diverse, impact-ranked** PoC queue with
no accounting monoculture and no easy-proof drift. Next: Phase 6 — completion (class-specific) on the 4 selected.
