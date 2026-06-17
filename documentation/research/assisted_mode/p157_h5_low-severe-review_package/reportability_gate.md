# Reportability Gate

| Field | Value |
|---|---|
| valid_finding | **yes** |
| mechanism_confirmed | true |
| attacker_reachable | true (unprivileged; cannot force keeper downtime) |
| severity_bearing | true (zero-sum reward redistribution; no protocol-fund loss) |
| runtime_status | runtime_confirmed |
| severity_recommendation | **Low baseline · Medium conditional** (sustained keeper failure, if in scope) |
| novelty_status | public_known_but_not_duplicate (novelty_clear NOT set) |
| conversion_outcome | reportable_candidate_needs_human_review |
| primary_blocker | none for mechanism/reachability; residual = severity/scope (keeper cadence) + novelty |
| submission_ready | **false** |
| routing_allowed | **false** |
| human_review_required | **true** |

## Next human decision (the package does not decide it)
- **Submit as Low** — if the program treats user-to-user reward misallocation under normal keeper cadence as
  in-scope.
- **Hold as QA / informational** — if borderline and the reviewer wants more program-scope confirmation.
- **Reject as trusted-keeper scope** — if the program treats keeper/operator timeliness as an accepted
  trusted-maintenance assumption.

No submission is made here. `routing_allowed=false`, `submission_ready=false`.
