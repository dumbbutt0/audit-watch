# P152 — Reachability & Conversion (required output fields)

| field | value |
|---|---|
| candidate_id | H4-ecg-multivotes-accounting |
| audit | ecg-2023-12-holdout (Credit Guild) |
| architecture_class | governance / credit-guild |
| mechanism_class | governance_vote_accounting_on_transfer (distinct from prior phases) |
| surface_function | `transfer` / `transferFrom` / `_decrementVotesUntilFree` / `getVotes` |
| candidate_origin | P152 holdout scan (distinct-class requirement) |
| selection_reason | distinct class, unprivileged surface (reachability answerable), crisp `getVotes` delta, deploy-light, conversion-learning (likely refute) |
| rejected_candidates_with_reasons | pooltogether PrizeVault (deploy-heavy ERC4626/TWAB); munchables (large multi-manager); kelp LRTDepositPool (oracle/RSETH deps) |
| deploy_complexity | moderate (OZ v4.9 ERC20Permit/EnumerableSet + local SafeCastLib) |
| harness_cost | low (3 tests) |
| real_contract_used | yes — real abstract `ERC20MultiVotes` inherited unmodified by a minimal `TestMultiVotes` shim (mint/setMaxDelegates only) |
| production_source_changed | no |
| corrected_reference_used | yes — the protocol's own guarded transfer is the expected behavior; `NaiveMultiVotesRef` (unguarded) shows the bug shape |
| control_case_used | yes — delegate, no transfer → votes stable |
| runtime_status | runtime_refuted |
| runtime_delta | real: `getVotes(delegatee)` 1000e18 → 0 on transfer; vulnerable ref: retains 1000e18; control: stable |
| reachability_verdict | unprivileged surface, but mechanism absent (guard present) |
| severity_class | no_security_impact_shown |
| duplicate_status | duplicate_unknown |
| routing_allowed | false |
| submission_ready | false |
| conversion_outcome | runtime_refuted |
| primary_blocker_if_not_reportable | mechanism_absent_guard_present |
| human_review_required | false (refuted; nothing to escalate) |

## conversion object (dashboard schema)
```json
{ "mechanism_confirmed": false, "attacker_reachable": true, "severity_bearing": false,
  "novelty_clear": false, "reportable": false, "outcome": "runtime_refuted", "blocker": null }
```

## Conversion funnel snapshot (runtime-only rows, after P152)
| row | arch | mechanism_confirmed | attacker_reachable | reportable | outcome |
|---|---|---|---|---|---|
| H1-centrifuge | centrifuge | true | unknown | unknown | needs_context (intent_ambiguous) |
| H2-velodrome | velodrome | false | false | false | runtime_refuted |
| H3-decent | decent | true | false | false | runtime_confirmed_but_privileged_only |
| H4-ecg | ecg | false | true | false | runtime_refuted |

Across 4 non-duplicate runtime-only candidates spanning 4 architectures, **zero** reached
`reportable_candidate_needs_human_review` — each was honestly stopped at its true boundary (intent-ambiguous,
refuted, privileged-only, refuted). The funnel demonstrates it converts toward reportability only on evidence.
