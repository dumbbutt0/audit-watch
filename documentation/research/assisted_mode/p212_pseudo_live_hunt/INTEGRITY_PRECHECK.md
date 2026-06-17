# P212 — integrity precheck (START)

Pseudo-live hunt; human-review mode; answer key SEALED until user approves scoring. No submit/route.

## START production hashes (md5 first-8) — must be byte-identical at END
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` |
| `scripts/min_confirm_gate.py` | `41dd3c96` |
| `scripts/confirm_gate.py` | `4fadfc5f` |
| `scripts/submission_readiness_review.py` | `7c4b563d` |
| `scripts/dashboard.py` | `857d593a` |
| `scripts/final_submission_pack.py` | `57cba16d` |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` |
| `../hermes/memory/events.jsonl` | `fc446040` |

## Confirmations
- `config/runtime_policy.json api_free=true`; no live route-to-submit; active audit = quantamm (NOT switched).
- L3 flag (`AUDITWATCH_L3_READINESS`) unset by default; enabled only in-process for readiness overlay; never persisted.
- Target = `sherlock-audit/2024-05-sophon` SOURCE only, cloned under `targets/2024-05-sophon/`.
- Answer key (Sherlock judging repo) cloned QUIETLY into `targets/2024-05-sophon/_sealed/judging/` (267 files) and
  **NOT read**. No finding bodies/titles/judging opened. To be opened only in STAGE 2 after user approval.
