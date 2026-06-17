---
name: triage
description: "Credit-free, skill-in-session replacement for triage_findings.py. Reasons over per-finding bundles built by triage_prepare.py and writes the triage decisions, then triage_write.py validates them into the canonical buckets. Applies zero-trust ICE re-derivation and the no-silent-clear rule. Activate when user says: /triage, run triage, triage findings without API, skill triage, or when run_pipeline.sh reports no API key at the triage step."
---

# Triage (skill-in-session)

Does the work `triage_findings.py` delegates to a sonnet API call — but **in this session**,
so it costs no API credits. Three steps: prepare (deterministic) → reason (you) → write
(deterministic + schema-validated).

## When to use

When `./run_pipeline.sh full` reaches triage with no `ANTHROPIC_API_KEY`, or any time the user
wants triage without spending API credits. Policy reference: `documentation/refinement/zero_trust_triage_policy.md`.

## Procedure

1. **Prepare bundles (deterministic):**
   ```
   python scripts/triage_prepare.py
   ```
   This writes `data/triage/_bundles/<finding_id>.json` (each holds the finding + a source
   slice + gate/dupe verdicts + an `is_safety_net_code` flag) and `_bundles/index.json`.

2. **Reason over each bundle (you, in-session).** Read every bundle. For each finding,
   **re-derive ICE from the source slice — do not trust the claimed severity:**
   - **I (Impact):** worst-case protocol outcome.
   - **C (Confidence):** is the path reachable and the flaw real?
   - **E (Exploitability):** permissionless / privileged / conditional.
   Decide a `triage_status`:
   - `submit` — I≥Medium, C≥High, exploit path traced end-to-end, no PoC needed.
   - `poc_required` — credible but needs proof.
   - `downgraded` — real but lower severity than claimed.
   - `merged` — true duplicate (same root cause + function + path + invariant + impact).
   - `rejected` — invalid; **but see the no-silent-clear rule below.**
   - `unresolved_invariant` — safety-net code you cannot confirm OR safely clear.

   **No-silent-clear rule (mandatory):** if the bundle's `is_safety_net_code` is true
   (Invariable/solvency, custom sort, oracle/peg aggregator, bridge check, season/time gate,
   init/migration completeness), you may NOT mark it `rejected` ("works as designed") unless
   you write a concrete attacker-path **`disproof`** (what an attacker would need + why it is
   impossible). Without a disproof, use `unresolved_invariant` → it routes to the human queue.
   This exists because the pipeline previously cleared 5 real Beanstalk bugs this way.

   For each finding also write a `follow_up_packet`: reachable? · no privileged keys? · state
   before→after · why guards fail · scope match.

3. **Emit decisions** to `data/triage/_decisions.json` as `{"decisions": [ ... ]}` where each
   item has: `finding_id, triage_status, recommended_severity, decision_reason, ice{impact,
   confidence, exploitability}, follow_up_packet`, and `disproof` when rejecting safety-net code.

4. **Write buckets (deterministic + validated):**
   ```
   python scripts/triage_write.py
   ```
   It validates required fields, enforces the no-silent-clear reroute defensively, and writes
   `data/triage/{submit,poc_required,downgraded,merged,rejected}.jsonl` + `<id>.md`, plus any
   `unresolved_invariant` into `human_review_queue.jsonl`.

## Output

Report counts per bucket and the count routed to the human queue. Then the pipeline continues
to `generate_review_gate.py` exactly as the API path would.
