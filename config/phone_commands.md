# Phone Command Reference

Short commands for remote/phone control of the audit pipeline.
Send any of these from Claude mobile or Claude Code remote control.

---

## `/status`
Show: active audit ID, current pipeline stage, last completed step, next recommended action,
submit-ready count, and any blockers.

Claude reads `config/active_audit.json`, `audits/<id>/meta.json`, and the triage/poc/judge
JSONL files to produce a phone-readable summary. Equivalent to:
```
python scripts/generate_status.py
```

---

## `/top`
Show the top 5 findings ranked by expected payout confidence (exploitability × severity ÷ duplicate risk).
Include: finding ID, title, severity candidate, poc status, judge verdict, and submission readiness.

---

## `/poc`
Show PoC status for all active findings:
- proved (level + test name)
- failed (last error summary)
- pending (not yet generated)
- blocked (upgrade required)

---

## `/submit-ready`
Show only findings with: triage_status=submit, working PoC, checklist=passed,
completeness gate=no upgrade required, and a drafted submission file.
List ID, title, severity, and submission filename.

---

## `/risks`
For each submit-ready finding, list the top 2 reasons it could be rejected or downgraded:
- wording issues flagged by judge simulator
- duplicate risk
- PoC completeness gaps
- overclaimed severity

---

## `/continue`
Continue the next safe pipeline step without asking for approval.
Use the Decision Logic from CLAUDE.md to determine what to run.
Run scripts; update status.json. Stop before any destructive action.

---

## `/stop`
Stop all active pipeline work immediately.
Summarize: files changed this session, current findings state, next recommended action when resumed.

---

## `/package [finding-id]`
Prepare the final submission bundle for one finding or all submit-ready findings:
- Polish the submission markdown
- Verify PoC output is embedded
- Verify quality checklist is complete
- Run: `python scripts/final_submission_pack.py`

Output: `output/submission_pack.md` and `output/submissions/<ID>_submission.md`

---

## `/mode fast|normal|deep`
Switch the run mode for subsequent operations.
- **fast** — triage only; no scans, no PoC generation
- **normal** — specialists on high-impact flows; PoC for top 3 findings (default)
- **deep** — full specialist pass; PoC for all High/Critical candidates

See `config/agent_policy.json` for per-mode settings.

---

## `/novel`
Surface the findings most likely to be novel — i.e., those with the lowest
similarity to any precedent in the Solodit, Code4rena, and Sherlock knowledge bases.
These are the highest-upside candidates in a competition: other auditors using
KB-based tooling are unlikely to have flagged them.

Logic:
1. Read `data/triage/submit.jsonl`
2. For each finding, query `tools/retriever.py --all "<title> <description[:200]>"`
3. Note the top-1 similarity score (0.0 = completely novel, 1.0 = exact match)
4. Sort by similarity score ascending
5. Show the top 5 lowest-similarity findings

Output format (one screen):
```
Novel findings (lowest KB similarity):
1. [EA-001] Interest rate manipulation — 0.21 similarity  (no close KB match)
2. [CC-003] Message replay on chain fork — 0.34 similarity
3. [BT-007] Backward reachability: vault drain — 0.41 similarity
...

Highest-similarity (most likely duplicate of known issue):
5. [RE-002] Missing CEI — 0.94 similarity → <similar KB title>
```

---

---

## `/human-queue`
Show all findings in `data/triage/human_review_queue.jsonl` sorted by `human_review_score`
descending (most criteria triggered first). These are the 10% of findings requiring human
expert validation per the Jason Hadex 90/10 principle.

For each finding: ID, title, severity candidate, triggered criteria, and recommended manual action.

If the queue file doesn't exist, runs `python scripts/human_review_classifier.py` first.

---

## `/confirm [finding-id]`
Run multi-pass LLM confirmation for a single finding or all High/Critical findings.

With ID: `python scripts/multi_pass_confirm.py --finding-id <ID>`
Without ID: `python scripts/multi_pass_confirm.py`

Returns: passes completed, YES count, confirmation_score (0.0–1.0), and whether the finding
is flagged for human review. Findings below 0.60 confirmation score require human validation.

---

## `/surface`
Show the attack surface map from `output/attack_surface.json`.
Displays: total functions mapped, breakdown by class (admin/user/view/internal), and
top 10 functions by `attack_surface_score` with their one-line ITE decomposition.

If `attack_surface.json` doesn't exist, spawns `agents/attacker_mindset.md` to generate it.

---

## Notes
- All commands read from `config/active_audit.json` to resolve the active audit workspace.
- Commands that trigger scripts run from the project root (`/home/dummy/clones/audit-watch/smart-contract-auditor`).
- Never submit or mark submit-ready without a PoC or an explicit override.
- `/continue` will not run deep-mode operations unless the mode is explicitly set to `deep`.
