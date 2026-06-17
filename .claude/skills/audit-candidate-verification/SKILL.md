---
name: audit-candidate-verification
description: "RESEARCH-ONLY / REVIEW-ONLY verification loop for a P77 investigation candidate or bundle. Run this BEFORE assigning POC_REQUIRED or READY_FOR_HUMAN_REVIEW to encode the manual audit verification process (source reachability, caller/permission, defense ledger, invariant hypothesis, exploit path, impact, source falsification) so missed steps fail closed. Activate when: investigating a STATIC_LEAD, filling/reviewing a deep-pass bundle, or before promoting a candidate. Never produces a finding; only the 4 review states. POC_REQUIRED = local PoC permission only; READY_FOR_HUMAN_REVIEW = bundle ready for a human to review, not a submission verdict."
---

# Audit Candidate Verification (skill-in-session)

A static detector/lens **nominates a question**; it does not decide a bug. Before any candidate may reach
`POC_REQUIRED` or `READY_FOR_HUMAN_REVIEW`, run this full loop and fill the P77 bundle. The deterministic scaffold
(`scripts/investigation/deep_pass.py`) computes the outcome from the evidence you fill; `scripts/investigation/
hygiene_validate.py` fail-closes on missed steps. **You may not promote on a suspicious pattern alone.**

## Hard rules
- Only these final classifications: `REJECTED`, `NEEDS_CONTEXT`, `POC_REQUIRED`, `READY_FOR_HUMAN_REVIEW`.
- FORBIDDEN words anywhere: confirmed bug · valid finding · submission ready · ready to submit · auto-submit · exploitable
  confirmed.
- No `STATIC_LEAD → POC_REQUIRED/READY` shortcut; no detector output → finding.
- Every ADVANCE must survive source falsification; every REJECT must cite source-backed evidence.
- The author of a bundle does NOT judge its own promotion — an isolated `/adversarial-bundle-review` PASS is required
  before `READY_FOR_HUMAN_REVIEW`.

## Loop (A–H) — each step is source-backed or marked unknown
**A. Source reachability** — trigger function present? source lines/snippets resolved? call path reachable? helper/
modifier/library calls resolved or explicitly `unresolved`? (unresolved critical source → `NEEDS_CONTEXT`).

**B. Caller & permission** — who can call the entrypoint? roles/ownership/modifiers/gates/registry checks on the path? can
the attacker actually reach the vulnerable path?

**C. Defense ledger completeness** — classify each relevant defense (16 fields) as `blocks_candidate | partially_covers_
candidate | irrelevant | bypassed | unknown | source_unavailable`: access_control · pause_guard · reentrancy_guard ·
nonce_or_replay_guard · state_consume_or_check · accounting_invariant · slippage_or_price_bound · caps_or_limits ·
final_invariant_check · role_or_admin_escape_hatch · external_dependency · oracle_or_price_dependency ·
user_controlled_inputs · cross_contract_assumptions · upgradeability_or_owner_controls · time_or_deadline_checks. A
defense that is `irrelevant` needs only the one-line reason it is irrelevant. A **critical/relevant** defense (by detector
family or listed in `critical_defenses`) that is `unknown`/`source_unavailable` **blocks promotion** → `NEEDS_CONTEXT`. Any
defense `blocks_candidate` → `REJECTED`.

**D. Invariant hypothesis** — which protocol invariant breaks? what state must stay true? which transition violates it? is
it source-backed or only guessed (guessed → not promotable)?

**E. Exploit path** — require: attacker_profile · entrypoint · preconditions · transaction_sequence · state_before ·
state_after · broken_invariant · why_defenses_do_not_block · minimum_profit_or_damage_condition. **Write the strongest
rejection case FIRST** (reject-first); only if it fails may the candidate advance.

**F. Impact** — measurable damage/profit/freeze/unauthorized-control/accounting-corruption? direct vs speculative? in
scope? is a PoC needed before human review?

**G. Source falsification** — try to DISPROVE: code unreachable · caller actually authorized · state immutable · missing
check exists in a helper/modifier/library · later invariant covers the path · behavior intentional by design ·
hash/signature/accounting value bound to mutable state · name/variable confusion · out-of-scope/unavailable source · no
economically meaningful impact. **Any falsifier that succeeds → `REJECTED` with the falsifying source evidence.**

**H. Final classification** — only the 4 states. `READY_FOR_HUMAN_REVIEW` requires A–G complete, falsification survived,
all critical fields source-backed, and an adversarial review PASS.

## Procedure
1. Normalize the lead: `scripts/investigation/lead_schema.py` (`normalize_lead`) — refuses routed sources.
2. Fill the evidence (A–G) by reading source (use Read); run `scripts/investigation/deep_pass.py` to produce the bundle.
3. Run `scripts/investigation/hygiene_validate.py --bundle <bundle.json>` — fix every violation it prints.
4. Hand the bundle to `/adversarial-bundle-review`. Promotion requires that review = PASS.
5. Record the bundle; do not draft a report and do not use any finality language.

Everything here is `research_only:true review_only:true is_gate:false routes_in_production:false routed_manifest_ids:[]`
and never wired into production.
