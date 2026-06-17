# P212 — Pseudo-live first hunt on a fresh C4/Sherlock contest (sealed answer key, human-review mode)

## Context
P211 validated the dark-wired L3 readiness gate end-to-end on a known corpus. P212 is the first real-hunt-style
campaign: hunt a COMPLETED, never-before-used Sherlock/Code4rena contest with full firewall discipline — source first,
**answer key sealed until the human says findings are ready for scoring**. Not autonomous, not live submission. The L3
HIGH gate is enabled (`AUDITWATCH_L3_READINESS=1`); threat ceiling is never final severity; human review mandatory.

## Decisions (from user)
- **Target:** I pick a **fresh, obscure** completed C4/Sherlock contest NOT in `audits/` and NOT used in P186-P211,
  cloning **source only** (findings repo/report stays sealed), with an explicit orchestrator-pretraining-memorization
  caveat recorded (mitigated: discovery verdicts come from fresh **key-blind subagents**; the answer key is sealed).
- **Methodology:** bounded **blind deep_trace-per-surface** (the validated campaign workhorse), not the full pipeline.

## Firewall rules (hard)
- Clone only the SOURCE repo. Do NOT clone the findings repo, read finding bodies/titles/judging/dup discussions, or
  web-search "known findings" for the target after selection.
- Count-level screening only: grep ONLY the report's `# High/Medium Risk Findings (N)` header lines, then immediately
  seal the report file under `_sealed/` and do not reopen until the human approves scoring.
- Source artifacts kept separate from sealed answer-key artifacts. Any leak → log in `FIREWALL_LOG.md` + abandon target
  or mark `FIREWALL_CONTAMINATED`.
- Network: clone confirmed working (C4 + Sherlock source repos reachable). `WebSearch`/`WebFetch` NOT used for the
  target (firewall risk).

## Execution — STAGE 1 (this turn): hunt → human-review pause (DO NOT open answer key)
Work dir: `documentation/research/assisted_mode/p212_pseudo_live_hunt/`. Clone target under `targets/<id>/` (gitignored
scratch); seal report under `targets/<id>/_sealed/`.

1. **INTEGRITY_PRECHECK.md** — START prod hashes (`deep_trace.md ef93a6c2`, `min_confirm_gate.py 41dd3c96`,
   `confirm_gate.py 4fadfc5f`, `submission_readiness_review.py 7c4b563d`, `dashboard.py 857d593a`,
   `final_submission_pack.py 57cba16d`, `validate_p208_l3_readiness.py 7e148e18`, ledger `fc446040`); confirm
   `api_free=true`, no route-to-submit, L3 flag behavior, answer key sealed, no target findings read.
2. **TARGET_INVENTORY.md** — probe 5-10 candidate fresh C4/Sherlock SOURCE repos via `git ls-remote` (leading
   candidates to try: `code-423n4/2024-02-thirdweb`, `code-423n4/2023-08-goodentry`, plus 1-2 small Sherlock repos;
   exclude anything already in `audits/`). Record platform/name/date/repo/size/compiler/deps/architecture/used?/
   sealable?/scope. Pick the smallest manageable Solidity one that clones + has a sealed report with a High/Medium mix
   (header count only).
3. **TARGET_SELECTION.md** — chosen target: why selected, why alternatives rejected, source path, sealed-key path,
   scope boundaries, dependency/harness risk, firewall status (+ memorization caveat).
4. **SCOPE_MANIFEST.md** — source-only: contract list, entry points, privileged roles, asset-custody points, external
   integrations, accounting/invariant surfaces, upgrade/admin controls, token-transfer paths, high-value attack
   surfaces. (Orchestrator may read SOURCE — allowed.)
5. **SURFACE_SELECTION.md** — pick **6-12** high-value surfaces (custody / withdraw-redeem / mint-burn / accounting
   conversion / liquidation-solvency / access-control transitions / cross-chain-msg / signature-permit / refund-failure
   / fee-reward). Not full-protocol coverage.
6. **Blind discovery** (`DISCOVERY_LOG.md`, `CANDIDATE_REGISTER.json`, `REJECTED_LEADS.md`): one fresh key-blind Sonnet
   subagent per surface = production `deep_trace.md` + verbatim source; token-scan prompts/outputs CLEAN; record leads,
   rejections (+reason), confirmed candidates, source refs, threat-ceiling per candidate. **FREEZE** raw outputs (hash).
7. **Candidate verification** (`CONFIRMED_CANDIDATES.md`): per credible candidate — affected contracts/functions,
   attacker model, exploit path, who loses/gains, source-backed impact, assumptions, admin/trusted prereq check,
   intended-behavior check, duplicate/known-pattern risk (WITHOUT the target key).
8. **L3 requirement** (`L3_READINESS_RECORDS.md` + `output_research/l3_readiness/<cid>.json`): for every High/Critical
   ceiling candidate, build/reuse an L2/L3 harness if feasible (isolated under `pocs/p212/`, no production-source edit,
   record cmd/result/actual/control) and run the `AUDITWATCH_L3_READINESS=1` readiness overlay. No feasible L3 →
   `NEEDS_HARNESS_FOR_SEVERITY`, not High-ready.
9. **Report packages** (`REPORT_PACKAGES/<cid>.md`): title·summary·affected·root cause·details·attacker model·exploit
   steps·impact·who loses/gains·poc path·poc command·actual·expected/control·mitigation·assumptions·severity rec·L3
   status·human-review checklist.
10. **HUMAN_REVIEW_CHECKLIST.md** + **PRE_SCORE_FREEZE.md** — candidate list, recommended reportable candidates,
    packages needing review, exact PoC-verify commands, missing evidence. **STOP. Do not open the answer key.**
    STAGE-1 decision: `READY_FOR_HUMAN_REVIEW` (or `NO_REPORTABLE_CANDIDATES` / `NEEDS_MORE_HARNESS_WORK` /
    `FIREWALL_CONTAMINATED` / `INVALID_RUN`). Also write `metrics.json` (stage 1) + `integrity_checks.md` (END==START)
    + copy plan → `P212_PLAN.md` + memory.

## Execution — STAGE 2 (only AFTER user says "ready for scoring")
Open the sealed report; produce `ANSWER_KEY_SCORECARD.md` (HIT/PARTIAL/ADJACENT/MISS/FALSE_POSITIVE/DUPLICATE_OR_KNOWN
per candidate), `SEVERITY_CALIBRATION_RESULTS.md` (exact/over/under/unscored), `L3_EFFECTIVENESS.md` (did L3 block
severity overstatement?), `MISSES_AND_FALSE_POSITIVES.md`, and a STAGE-2 decision: `LIVE_HUNT_READY` /
`LIVE_HUNT_READY_WITH_LIMITS` / `NEEDS_MORE_REHEARSAL` / `SEVERITY_GATE_REGRESSION` / `TOO_MANY_FALSE_POSITIVES` /
`INVALID_SCORE`. Update metrics + memory.

## Strict scope
No submit; no external routing; nothing marked final-submission-ready without human review; no High promoted without L3
PASS or written override; threat ceiling ≠ final severity; do NOT open the answer key before user approval; production
prompt/gate/ledger byte-identical START==END (only the 2 P210 files exist, unchanged); L3 records under
`output_research/l3_readiness/`; harnesses isolated under `pocs/p212/`; cloned target source under `targets/` (never
edited).

## Decision states
STAGE 1 ends: `READY_FOR_HUMAN_REVIEW` (expected) · `NO_REPORTABLE_CANDIDATES` · `NEEDS_MORE_HARNESS_WORK` ·
`FIREWALL_CONTAMINATED` · `INVALID_RUN`. STAGE 2 (post-approval) ends with one of the live-hunt-readiness states above.

## Acceptance criteria
Fresh C4/Sherlock target (not in audits/, not P186-P211); answer key sealed until human approves scoring; no live
submission/routing; L3 flag on for High readiness; 6-12 surfaces (not sprawl); every reportable candidate has a
human-review package; High requires L3 PASS or written override; scoring only after human verification; production
hashes byte-identical START==END; JSON valid; firewall log maintained.

## Verification
`git ls-remote`/clone of the chosen SOURCE repo succeeds; report grepped at header-count level then sealed; blind
prompts/outputs token-scan CLEAN (no leaked finding ids); `CANDIDATE_REGISTER.json`/`metrics.json` valid JSON;
High-ceiling candidates carry an L3 record and are blocked unless PASS/override; production hashes unchanged at END;
no answer-key file opened before STAGE 2; active audit (quantamm) not switched.
