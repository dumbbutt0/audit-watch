# P211 — integrity precheck (START)

End-to-end rehearsal with `AUDITWATCH_L3_READINESS=1`. Not a live hunt; no submit/route; human review mandatory.

## START hashes (md5 first-8) — all must be byte-identical at END
| artifact | hash | note |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | unchanged |
| `scripts/min_confirm_gate.py` | `41dd3c96` | unchanged |
| `scripts/confirm_gate.py` | `4fadfc5f` | unchanged |
| `scripts/submission_readiness_review.py` | `7c4b563d` | P210 END (unchanged in P211) |
| `scripts/dashboard.py` | `857d593a` | P210 END (unchanged in P211) |
| `scripts/final_submission_pack.py` | `57cba16d` | unchanged (NOT modified) |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` | unchanged |
| `../hermes/memory/events.jsonl` | `fc446040` | unchanged |
| `config/runtime_policy.json` | — | unchanged; `api_free=true` |

## Confirmations
- `config/runtime_policy.json api_free=true` → no live Anthropic/submission route.
- Active audit = `quantamm-2024-12-eval` (blind eval). **NOT switched, NOT scored** by P211.
- `AUDITWATCH_L3_READINESS` is **unset by default**; enabled only in-process for the flag-on rehearsal steps,
  **never persisted to config**.
- decent `_sealed_answer_key` opened READ-ONLY for scoring (severity headers / awarded mapping only): 4 High / 5 Med;
  H-01 setRouter→mint, M-03 receiveFromBridge — match P204's executed L3 evidence.
- L3 records are written to `output_research/l3_readiness/` (ROOT-relative, audit-independent) — the location the
  wired loader reads. No active-audit artifact is touched.
