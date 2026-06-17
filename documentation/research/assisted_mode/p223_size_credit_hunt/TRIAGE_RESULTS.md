# P223 — Triage results (Step 5, zero-API in-session)

Flow: `run_pipeline.sh full` (Steps 2.5→3.8, api-free; enhancers skipped cleanly) → in-session triage decisions
(`data/triage/_decisions.json`) → `triage_write.py` → `run_pipeline.sh review-gate`.

## Step 2.5–3.8 (pre-triage)
- Cross-agent/compound/multi-pass enhancers SKIP cleanly (api_free). report_generator re-merged: 12 findings.
- Pre-submission gate (3.7): **12 PASS, 0 HUMAN_REVIEW, 0 REJECT** (2 WARN per finding = no exploitability/judge
  model, expected for this lean path).
- Dupe screen (3.8): no submitted findings to screen.

## Triage buckets (ICE re-scored from raw source, not prior-stage summaries)
| bucket | count | findings |
|--------|-------|----------|
| poc_required | 3 | SC-01 (High), SC-03 (Medium), SC-04 (Medium) |
| downgraded | 9 | SC-02, SC-05, SC-06, SC-07, SC-08, SC-09, SC-10, SC-11, SC-12 (all Low) |
| submit | 0 | — |
| rejected | 0 | — (downgraded with source-backed rationale instead of rejecting) |
| merged | 0 | — |

## Rationale highlights
- **SC-01 → poc_required (High ceiling):** `executeDeposit` uses `address(this).balance` vs `validateDeposit`'s
  `msg.value` check; next unprivileged `deposit()` caller sweeps any ETH in the contract. Confirmed from source;
  only the credited delta needs a test → PoC. The clean-reportable flagship.
- **SC-03 / SC-04 → poc_required (Medium):** negative-APR offer DoS (revert) and compensate fragmentation-fee
  waiver — both source-confirmed; harnesses pin the reachability/precondition that bounds severity to Medium.
- **9 downgraded to Low:** wrong-units validations (SC-02/SC-10), scaled-token dust (SC-05/SC-12), design-band
  constraints (SC-06/SC-07/SC-08), integrator/indexer footguns (SC-09/SC-11). All real but minor; none rejected
  (each carries a source-backed downgrade rationale).

## Gates after triage (review-gate)
- **Coverage gate: PASS (OVERRIDE).** in-scope 193/221, dispositioned-as-finding 12, unassigned 181 →
  coverage 6.2%. Override used per the pre-authorized plan path. **Honest caveat:** the 5 discovery clusters
  swept the entire high-value action/library surface (deposit/withdraw/multicall, all action libs, accounting,
  offers, liquidation, oracle pricing, tokens, config), but a full *evidence-anchored* sweep of the 181 view/
  getter/role/config tail (97 of which are high-surface needing strong-clears) was not performed — this is the
  known recall-discipline gap a real submission would close before the gate would pass without override.
- **Min-confirm gate: PASS** — 3 candidates, 3 confirmed (skeleton fields present), 0 blocking.
- **Bridge thread escalation: PASS** (0 bridge threads).
- review_gate.md written; pipeline paused after Step 4. "Confirmed findings: 0" in the gate doc reflects that
  no High/Critical has an L3-PASS yet (PoC pending) — expected pre-harness.
