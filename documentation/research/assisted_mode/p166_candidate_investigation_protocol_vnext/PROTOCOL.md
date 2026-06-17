# Candidate Investigation Protocol vNext (P166)

**Status:** canonical operator protocol for the research-only Option-A campaign track. Reject-first. Advisory
gates (nothing hard-blocks, auto-routes, or auto-submits). The **only hard rule is `fabrication_rate = 0`**.
research_only=true / routing_allowed=false / submission_ready=false.

> A candidate is **not** advanced because it looks suspicious. A candidate advances only after surviving
> systematic attempts to disprove it. **The goal is not to prove candidates correct — it is to discover why
> candidates fail and eliminate those failure modes earlier in future campaigns.**

Success metric: **reportables per harness built.** Secondary: harnesses_avoided · source_refutations ·
runtime_confirmations · fabrication_rate=0. **Raw finding count is not a success metric.**

---

## Step 1 — Construct the strongest refutation (REFUTATION CASE)
Before building a harness, try to prove the candidate is NOT reportable. Explicitly search for: permission
gates · role restrictions · recipient restrictions · fixed beneficiaries · ownership corrections · state
guards · invariant enforcement · accounting reconciliation · batch-finalization checks · settlement checks ·
checkpoint updates · caller-is-not-recipient · donation/MEV dependence · self-funded profit · time-dependent
assumptions · design-intended behavior · an equivalent sibling path that already handles the issue.

Output a **REFUTATION CASE** listing every reason the candidate might fail. Do not proceed until each
refutation is either **confirmed** (it holds → the candidate is refuted) or **disproven from source**.

## Step 2 — Determine the failure mode (one bucket, with source evidence)
Classify into exactly one bucket; cite specific source (file:line). Never use generic language.

| Bucket | Meaning |
|---|---|
| `SOURCE_REFUTED` | a source guard / absent mechanism makes the bad state unreachable or inert |
| `GATE_REFUTED` | fails a pre-screen gate (non-time/MEV/self-funded; no comparand; etc.) |
| `DESIGN_INTENT` | the behavior is the documented/intended design |
| `PRIVILEGED_ONLY` | only a role/keeper/owner/controller can trigger it |
| `NO_ATTACKER_PROFIT` | value moves but the caller gains nothing |
| `NO_RECIPIENT_CONTROL` | value goes to a fixed/owner/beneficiary the attacker can't control |
| `NEEDS_CONTEXT` | unresolved from local source (intent/scope/deps ambiguous; or source access poor) |
| `HARNESS_CANDIDATE` | survives refutation → eligible for a harness |

## Step 3 — Converter analysis (only if it survives refutation)
1. Who receives value? 2. Can the attacker control that recipient? 3. Can the attacker trigger the path?
4. Can the attacker retain the gain? 5. Who loses value? 6. Is the loss measurable? 7. Is the path
permissionless? 8. Is the gain independent of MEV/donations/timing/external cooperation? **If any answer
fails, stop** (classify the matching Step-2 bucket).

## Step 4 — Harness decision
A harness is allowed **only if**: reachability is unresolved · attacker profit is plausible · recipient
control exists · no source-level refutation exists. Otherwise → **`SOURCE_REFUTED_NO_HARNESS`**.
(Build = read-only candidate-scoped Foundry PoC under `audits/<arch>/pocs/pNNN/`, real contract + minimal
mocks, sibling/corrected control, L1 attacker entry / L2 named storage+balance asserts / L3 economic delta;
remove `lib/` after.)

## Step 5 — Prediction logging (before any harness)
Predict the outcome — one of `runtime_confirmed` · `runtime_refuted` · `reportable_candidate_needs_human_review`
· `static_false_positive` — and record **why**, BEFORE investigating/harnessing:
```
echo '{"candidate_id":"H-..","predicted_outcome":"static_false_positive","rationale":"..."}' \
  | python scripts/research/option_a_campaign.py predict
```
After investigation, the recorded ledger outcome is joined to the prediction. Maintain the running calibration:
```
python scripts/research/option_a_campaign.py calibration   # accuracy k/n, by_predicted, unresolved
```

## Step 6 — Campaign learning (every candidate)
Record, via `option_a_campaign.py record`, for every candidate: `first_failed_gate` · `rejection_type`
(rejection reason also in `primary_blocker`/`why`) · `attacker_recipient_status` · `profit_source` ·
`permission_model` · `harness_built` · `runtime_status` (runtime outcome) · `predicted_outcome`. The campaign
scorecard then reports `reportables_per_harness`, `harnesses_avoided`, refutations, `prediction_accuracy`, and
`fabrication_rate` (`python scripts/research/option_a_campaign.py scorecard`).

---

## How the protocol maps to the tooling (P164 + P166)
- **Step 5 prediction log:** `output_research/option_a_campaign/prediction_log.jsonl` (append-only) via
  `log_prediction()`; `calibration()` joins it to the ledger.
- **Step 6 learning fields:** additive ledger columns (`attacker_recipient_status`, `profit_source`,
  `permission_model`, `harness_built`, `predicted_outcome`, plus the P164 `rejection_type` /
  `first_failed_gate`). Existing rows are not backfilled.
- **Success metric:** `scorecard()["reportables_per_harness"]`; calibration → `["prediction_accuracy"]`.
- **Dashboard (read-only):** `/api/campaign-scorecard` + `/api/campaign-calibration`; the `/findings`
  scorecard panel shows the tiles. Display-only; no routing/severity/submission writes.

## Hard rules / boundaries
- **`fabrication_rate = 0` is the only hard gate:** `record()` raises on a positive (`runtime_confirmed` /
  `reportable`) that lacks harness evidence (harness_path / real_contract_deployed / "real contract" in
  deploy_complexity / or a matching `runtime_confirmed` row in the canonical runtime sidecar).
- All other gates are **advisory** — they inform the bucket, they do not auto-block or auto-advance. The
  correction-layer selector is an **experimental booster** (KEEP_EXPERIMENTAL per P163), never a hard gate.
- Never set `submission_ready` / `routing_allowed` true. `sandbox_check.py` before reading candidate source.
- Holdout/eval `_sealed_answer_key` is not opened → `duplicate_status = duplicate_unknown`.
