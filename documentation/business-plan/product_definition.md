# Product Definition — Audit-Watch

---

## What Audit-Watch Is

### For a solo bug bounty hunter

Audit-Watch is a Claude Code-orchestrated audit pipeline that runs 34 specialist AI agents in parallel against a Solidity codebase, enforces an Impact Chain Escalation framework so only findings with proven state-consumer-impact chains survive to submission, and uses an 8-gate structural filter to kill admin-only, impossible-state, and already-guarded false positives before you read them. It does not replace your judgment — it eliminates the 68% of candidates that a good human triage would also reject, so you spend time on the 32% that matter. Setup requires a Solodit API key, Anthropic API key, Python 3.12, slither, and 20 minutes.

### For an audit firm owner

Audit-Watch is a structured reasoning framework that turns Claude Code into a multi-agent audit pipeline with workspace isolation, per-finding confidence scoring, human-AI routing, and an FP autopsy loop that accumulates rejection rules across contests. Each audit lives in `audits/<id>/` with full data lineage from raw agent findings through triage to submission-ready markdown. It does not automate auditing — it automates the triage layer and enforces methodology consistency across auditors so senior review time is spent on the 10% of findings that AI cannot confirm.

### For an investor

Audit-Watch is a methodology-first AI auditing tool targeting the $80–250K/program Immunefi bug bounty market, where a single confirmed Critical finding is worth more than a month of traditional audit engagements. The core differentiation is a five-layer filter system — ICE chain enforcement, 8-gate pre-submission filter, multi-pass LLM confirmation, FP autopsy learning loop, and a reasoning graph cognitive debugger — that reduces false positive noise and increases the quality of findings that reach submission. The market is competitive auditors earning $50K–$500K/year who currently use Slither plus manual review and would pay for a systematic amplifier. The tool is in active use across 10 real contest workspaces.

---

## Primary User: The Solo Competitive Auditor

### Current workflow without the tool

A competitive auditor today: (1) reads slither output and ignores 80% of it, (2) manually traces call graphs to find interesting state mutation patterns, (3) writes hypotheses in a notes file, (4) manually checks each hypothesis against the defense landscape, (5) writes PoC tests one at a time, and (6) spends 3–8 hours on findings that ultimately fail triage because they require admin compromise or impossible state. The estimation, triage, and deduplication steps are entirely manual.

### What Audit-Watch replaces, augments, or eliminates

**Replaces:** Manual slither output review. The defense mapper and 8-gate automate the "does a guard already cover this?" check.

**Augments:** Human hypothesis generation. The parallel specialist agents surface candidates the human might miss under time pressure. The attacker mindset agent scores all functions before specialists run, so the human knows where to focus.

**Eliminates:** Repeated manual triage of findings that are structurally invalid (admin-only, impossible-state). The 8-gate kills these before they consume the human's review time.

**Does not replace:** Reading the actual exploit path. The ICE framework enforces that the human must confirm the consumer chain. The human must still understand why the bug is exploitable.

### What it gives them that no scanner or AI agent gives them

A forced ICE chain requirement means every finding that survives the pipeline has an identified corrupted state, a confirmed consumer function, and a classified protocol action. Generic LLM agents produce findings that say "this function is vulnerable" without tracing what happens next. Slither produces findings with no impact chain at all. Audit-Watch's ICE enforcement — backed by a PoC level scale that gates severity — is the specific thing that prevents the most common submission failure mode: reporting a state change with no proven impact.

The reasoning graph dashboard is the second unique asset: it shows the cognitive path from hypothesis to PoC, with KB match evidence and branch invalidation history. No scanner or LLM agent product shows you WHY it reached a conclusion and which branches it ruled out.

### What they still have to do manually

- Read the critical exploit path themselves before submitting a High or Critical
- Confirm ICE chain consumers where ripgrep-based search is low-confidence (interface calls, delegatecall paths)
- Write the final submission narrative (the pipeline produces a submission_pack.md template, not a polished report)
- Verify PoC test assumptions against mainnet state for market-dependent findings
- Identify novel vulnerability classes not in the Solodit/Immunefi knowledge base

### What would make them pay $X/month

A competitive auditor earns $200–$500 per confirmed Medium and $2,000–$20,000 per confirmed High in Immunefi programs. One confirmed High pays for 3–12 months of tooling at $150–$200/month. They pay when:
1. The tool has confirmed at least one High they would not have found on their own
2. Setup takes under 2 hours on a new contest
3. The false positive rate is low enough that they trust the submit.jsonl output without reviewing every entry

Realistic price: $150–$250/month for an individual seat. $800–$1,500/month for a 2–4 person team. Not per-contest pricing — auditors run 2–4 active contests at a time.

---

## Secondary Users

### Small audit teams (2–5 people)

**Fit: Medium.** The per-audit workspace isolation and human-AI routing (`human_review_queue.jsonl`) are natural for teams. One senior auditor handles the 10% human queue; junior auditors run the pipeline and feed findings. The reasoning graph dashboard is more valuable for team review than for solo use. However, the current setup is single-user (one `active_audit.json`, no multi-user auth). A team would need to either run separate instances or coordinate via the workspace files.

**Revenue potential:** 2–5 seats at $200/month = $400–$1,000/month per team.

### Independent security researchers (CVE hunting, non-bounty)

**Fit: Low.** The pipeline is optimized for EVM Solidity smart contracts and Immunefi/Code4rena submission formats. CVE hunting is different — different formats, different impact models, different evidence requirements. The ICE framework is applicable in principle but the tooling is not.

### Protocol security teams (own codebase review)

**Fit: Medium.** The pipeline can audit a protocol's own code. The false positive concern is inverted — you want to find issues, not filter them. The 8-gate being aggressive might eliminate findings the protocol team wants to know about even if they cannot be exploited by an external attacker. The defense mapper would be very useful for verifying modifier coverage claims. Custom deployment would be needed.

### Audit firms (10+ auditors)

**Fit: Low (today).** Audit firms need multi-user auth, audit trail, client-facing reporting format, compliance features, and integration with their existing workflow tools. The current pipeline is Claude Code-native (runs inside a terminal session) and not a web product. Serving an audit firm requires building a different product layer on top.

### AI security researchers (benchmarking, pipeline research)

**Fit: High.** The pipeline's architecture — parallel specialist agents, structured finding schemas, ground truth evaluation framework — is directly applicable as a benchmark harness. The `evaluate_pipeline_accuracy.py` script and `ground_truth.jsonl` format are purpose-built for this use case. This is a secondary market (academic, not commercial) but creates word-of-mouth and credibility.

---

## What Audit-Watch Is NOT

- **Not a fully autonomous auditor.** It requires human confirmation of the ICE chain for High/Critical findings, human review of the `human_review_queue.jsonl`, and human judgment on PoC assumptions. The 90/10 principle (AI handles 90%, human handles 10%) is documented and enforced.

- **Not a static scanner.** Slither and Mythril are dependencies, not competitors. Audit-Watch consumes their output and adds reasoning, triage, and severity calibration layers that static scanners do not have.

- **Not a replacement for human reading of the exploit path.** The submission_writer prompt explicitly requires the human to answer 8 questions confirming the full exploit path before writing a submission. The pipeline produces evidence, not conclusions.

- **Not a PoC guarantor.** The PoC generator produces Level 1–3 proofs. Level 3 PoCs for market-dependent exploits (sandwich attacks, oracle manipulation) require mainnet state that cannot be fully reproduced in a mock environment. The tool is honest about this.

- **Not a duplicate detector without contest context.** The duplicate detection uses Solodit/Immunefi KB similarity. It cannot detect that a finding was already submitted by another contestant in the same live contest. XTR-003 would have been submitted as a duplicate if the human had not manually identified Immunefi report 78765.
