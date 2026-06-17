# L3 DoS carve-out rule (written BEFORE testing; general, research-only)

Repairs the too-blunt "DoS → Medium" floor in the L3 severity mapping. Narrow and additive: it can only **raise** a
DoS finding to High when an executed harness proves a deterministic, no-workaround failure of a core supported path.
It never lowers anything and never upgrades a refuted/invalid case. **No broad "DoS == High".**

## Severity ladder (DoS family)
| situation | label |
|---|---|
| ordinary DoS (recoverable / probabilistic / has workaround) | **Medium** |
| griefing / optional self-inflicted failure (user griefs self or via optional action) | **Medium / Low** |
| bounded local inconvenience (single user, edge case) | **Medium / Low** |
| **deterministic core-path DoS** (all 10 criteria below, L3-proven) | **High** |
| permanent fund lock / protocol-wide entry-exit failure, L3-proven | **High** |
| scope / workaround unclear, or no executed harness | **NEEDS_HARNESS_FOR_SEVERITY** |
| source-refuted | **invalid** |

## High-carve-out predicate (ALL ten required)
`repaired_label = "high"` iff every one holds; otherwise fall through to the existing `old_label` (and never upgrade an
`invalid`/source-refuted case):
1. **deterministic_l3_proof** — an *executed* harness shows deterministic revert / permanent blockage / unavoidable failure.
2. **core_path** — entry / exit / redeem / claim / deposit / withdrawal / conversion / liquidation / settlement.
3. **supported_asset** — the affected path/asset is explicitly supported by the protocol.
4. **not_optional_griefing** — not a user griefing another via an optional action.
5. **source_valid_token_behavior** — failure is valid under realistic token/protocol behavior.
6. **attacker_model ∈ {permissionless, unavoidable, normal_user_behavior}**.
7. **no_workaround** — no practical workaround for the affected supported path.
8. **affects_class_or_protocol** — a class of users or a protocol-wide function (not only a self-inflicted edge).
9. **control_case_present** — the harness includes a control showing the path succeeds absent the bug.
10. **no_admin_prereq** — no trusted/admin prerequisite.

If ANY criterion is missing → Medium / Needs-Harness / invalid per the ladder. **Do not call it High only because it
reverts.**

## Why this is narrow (won't reintroduce over-HIGH)
- Criterion 1 requires an EXECUTED deterministic harness → static/unharnessed "DoS Highs" (e.g. munchables P206
  screening) cannot auto-upgrade.
- Criteria 4/8 exclude optional/self-inflicted griefing; 6/10 exclude admin-gated and privileged-only; 7 excludes
  cases with a workaround; 9 requires a control. SOPH-03 satisfies all ten; the P204/P207 negative controls
  (auth-bypass, cap-bypass, false-Highs) are not DoS and fail criterion 2 → unchanged.
