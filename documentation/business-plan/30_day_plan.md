# 30-Day Plan

_Concrete, prioritized, weekly milestones. Grounded in actual codebase state._

---

## WEEK 1: Pipeline Reliability

**Goal:** Make the pipeline produce trustworthy output that a second person could verify.

**Key tasks:**

1. **Run `record_fp_autopsy.py` on all existing rejected findings (2 hours)**
   Target files: all `audits/*/data/triage/rejected.jsonl` (297 entries total)
   Command: `python scripts/record_fp_autopsy.py --finding-id <ID> --judge-outcome rejected --rejection-reason "<reason from rejected.jsonl>"` for each entry where reason is known.
   Expected output: `data/fp_autopsies/rejection_rules.jsonl` with 50–100 initial rules derived from clear rejection patterns (admin-only, impossible-state, nonReentrant-covered).

2. **Fix the 47 Unknown-severity findings in submit.jsonl across audits (2 hours)**
   Add post-triage validation to `scripts/triage_findings.py`: after writing `submit.jsonl`, check that every entry has a non-empty `severity` field. Log and re-prompt for any missing.
   File: `scripts/triage_findings.py` near the write loop at the end of the main triage pass.

3. **Record known ground truth outcomes (1 hour)**
   Run `python scripts/ingest_ground_truth.py` for:
   - CHAIN-001: outcome=pending (record when confirmed)
   - TG-001/XTR-001: outcome=pending
   - TG-002/XTR-002: outcome=pending
   - GL-001 (Gearbox bot perm): outcome=rejected, reason="nonReentrant applied via ReentrancyGuard inheritance"
   - XTR-003: outcome=rejected, reason="duplicate of immunefi-78765 by @dumbbut1"
   Even 3–5 verified outcomes transforms the accuracy_report from noise to signal.

4. **Enforce 8-gate run before submission pack (1 hour)**
   In `scripts/final_submission_pack.py`, add a guard: if `gate_results.jsonl` does not exist for the active audit, print an error and exit. Do not generate a submission pack that bypasses the gate.

5. **Add `--strict` PoC completeness check to `run_pipeline.sh gate` step (30 min)**
   Currently the gate command exists in the script. Add `python scripts/analyze_poc_completeness.py --all --strict` before the final pack step.

**Measure of success:** Running `python tools/verify_setup.py && python scripts/generate_status.py` on the xterio workspace produces a report with no Unknown severities, a gate_results.jsonl present, and at least 3 rejection rules written to project-level `data/fp_autopsies/rejection_rules.jsonl`.

**What to skip this week:** Any new features. Do not add new agents, new gates, or new scripts. Only fix what is broken in the existing pipeline.

---

## WEEK 2: Evidence — Run a Real Contest and Document Results

**Goal:** Produce at least one finding with a documented, shareable audit trail from hypothesis to PoC.

**Key tasks:**

1. **Select a live contest and run the full pipeline**
   Use `python scripts/audit_manager.py new <contest-id>` to create a workspace.
   Run `./run_pipeline.sh full` or the step-by-step commands from CLAUDE.md.
   Document the run: take notes on what worked, what failed, what required manual intervention.

2. **Instrument the top 3 pipeline scripts with viz events (4 hours)**
   Priority scripts for emit() calls:
   - `scripts/multi_pass_confirm.py` — add `HYPOTHESIS_BORN` at the start of each confirmation pass, `CONFIDENCE_SHIFT` on each pass result
   - `scripts/cross_agent_connector.py` — add `HYPOTHESIS_BORN` for each compound candidate, `BRANCH_INVALIDATED` for rejected compounds
   - `scripts/run_impact_chain_escalation.py` — add `EVIDENCE_ATTACHED` for each consumer found, `CONFIDENCE_SHIFT` when ICE level updates
   This makes the reasoning graph show the most valuable signals: compound synthesis and ICE chain tracing.

3. **Write a post-contest brief (2 hours)**
   After the contest run: document in `audits/<id>/reports/` what the pipeline found, what the human confirmed, and what was discarded. This is the content for Path C (methodology post). Format: 3 findings described in ICE chain format, with before/after severity if the ICE gate changed the claimed severity.

4. **Run `multi_pass_confirm.py` explicitly and record results**
   For every High finding produced, run the explicit multi-pass confirmation. Note whether it agreed or disagreed with the initial triage. Record disagreement cases — these are calibration data.

**Measure of success:** At least 2 findings in `data/triage/submit.jsonl` for the new contest, all with verified severity (no Unknown), a gate_results.jsonl present, and at least 1 finding where the reasoning graph session shows 20+ events including KB_MATCH and CONFIDENCE_SHIFT events.

**What to skip this week:** Do not clean up SETUP.md yet. Do not contact potential customers yet. Build the evidence base first.

---

## WEEK 3: Product — Clean Setup and First External Demo

**Goal:** A new auditor can go from git clone to first finding in under 30 minutes.

**Key tasks:**

1. **Create a Docker container or GitHub Codespace template (4 hours)**
   Target: one command to get a working environment.
   Minimum viable: `docker build -t audit-watch .` with a Dockerfile that installs all Python dependencies, slither, and solc. The user provides `.env` with `ANTHROPIC_API_KEY`.
   The Solodit API key dependency is the hardest: consider making it optional for a first run (KB is empty, but the pipeline still runs — just with empty retriever results).

2. **Write a 5-minute getting-started guide (2 hours)**
   Replace SETUP.md with a "Start here" path: 3 commands, one contract, one output. Link to the full SETUP.md for details. The five-minute path: clone, add ANTHROPIC_API_KEY to .env, run `python scripts/audit_manager.py new demo`, run `./run_pipeline.sh full`.

3. **Record a 5-minute demo video or writeup of one finding**
   Show: contract → attack_surface.json → one submitted finding with its ICE chain → the reasoning graph session showing KB match and confidence evolution. This is the demo used in Path C content and Path B outreach.

4. **Send the demo to 2–3 people for feedback (1 hour)**
   Existing contacts in the security research community. Not a sales pitch — ask: "Can you get this to run? What is confusing?" Address the top 3 friction points.

**Measure of success:** A person who received only the "Start here" guide and a Docker image ran the pipeline on a sample contract and saw output in `output/findings_*.json` within 30 minutes. At least one piece of external feedback recorded.

**What to skip this week:** Do not add new specialist agents. Do not refactor the dashboard. Do not build a web UI.

---

## WEEK 4: Revenue — Identify Paying Users and Make First Attempt

**Goal:** Have a conversation with at least 3 potential paying users and make one offer.

**Key tasks:**

1. **Identify 10 candidates from public leaderboards**
   Sources: Immunefi Hall of Fame top 50, Code4rena leaderboard top 30, Sherlock contest top rankings.
   Criteria: active in 2026, participating in Immunefi programs with $50K+ bounties, publicly visible Twitter/X account.

2. **Write one public technical post (3 hours)**
   Topic: "How Impact Chain Escalation eliminated 68% of false positive findings across 10 Solidity audits"
   Content: explain the ICE chain rule, show a before/after example from xterio (TG-001: finding would have been orphaned without tracing the grace period → addMinter consumer), explain the PoC level ceiling.
   Call to action: "I'm giving early access to 5 competitive auditors. DM me."
   Do not mention price in the first post.

3. **Send 5 direct messages to target auditors (2 hours)**
   Message: "I built a structured triage pipeline for Immunefi contests that uses Impact Chain Escalation to filter false positives before they waste your review time. Happy to show you on your current contest target. No pitch — just showing the tool on real code."

4. **Make one explicit offer to whoever engages (1 hour)**
   Offer: $200/month after a confirmed working run on their contest. If they do not convert after one run, ask what stopped them — that is more valuable than the sale.

**Measure of success:** At least 3 conversations with people who are active in bug bounty contests. At least one concrete response (even "not interested" with a reason). If one person says yes, that is $200/month and the first commercial validation.

**What to skip this week:** Do not build a Stripe integration or billing infrastructure. Invoice manually for the first 5 customers.

---

## The Single Most Important Thing to Do TODAY

Run `record_fp_autopsy.py` on the GL-001 Gearbox false positive — it is fully documented in memory (`feedback_verify_attack_preconditions.md`) with the exact rejection reason. This is one command:

```bash
python scripts/record_fp_autopsy.py \
  --finding-id GL-001 \
  --judge-outcome rejected \
  --rejection-reason "nonReentrant applied via ReentrancyGuard inheritance covers all external entry points; fork test on mainnet confirmed no reentrancy path exists"
```

This produces the first real entry in `data/fp_autopsies/rejection_rules.jsonl`. It proves the FP autopsy loop works. It is the single action that costs the least time and starts compounding the most valuable asset in the system.
