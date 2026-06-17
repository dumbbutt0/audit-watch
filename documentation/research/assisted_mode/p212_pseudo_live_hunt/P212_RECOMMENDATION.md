# P212 — recommendation (STAGE 1)

## Decision: `READY_FOR_HUMAN_REVIEW`

First pseudo-live hunt executed on a fresh, never-used Sherlock contest (**sherlock-audit/2024-05-sophon**, 933-LOC
core farming contract) under full firewall discipline. The answer key is sealed and **unopened**; scoring (STAGE 2)
awaits explicit user approval. No submit/route/promote; production byte-identical; active audit untouched.

## What the hunt produced
- 8 bounded surfaces analyzed by fresh key-blind deep_trace subagents (JSON-only, token-scan CLEAN, FREEZE `c14b2421`).
- **7 deduped candidate root causes**, threat ceilings 6 HIGH + 2 MEDIUM (the expected over-HIGH skew).
- Strongest permissionless leads: **SOPH-01** (withdraw omits boostAmount decrement — conservation break),
  **SOPH-03** (depositStEth wraps full `_amount` vs stETH actually received), **SOPH-02** (accPointsPerShare 1e18
  scaling mismatch). SOPH-04 (boost dilution) likely by-design. SOPH-05/06/07 are privileged (admin-prereq).

## L3 gate behavior (the headline)
With `AUDITWATCH_L3_READINESS=1`, **0 of 5 High-ceiling candidates reached High-submission readiness** — all
`blocked_by_missing_l3_poc` (permissionless → `needs_harness_for_severity`; privileged → `medium`). No executed
material-impact PoC was built within first-hunt scope, so the gate correctly **prevented any over-rated HIGH from
being presented as submission-ready**. This is exactly the intended safety behavior on a real target: credible leads
surface, but a HIGH cannot ship without realized-impact evidence or a written human override, and human review is
mandatory.

## Key honest observations
- Sophon is a **points** system (points → future L2 allocation); most candidate impacts are points-accounting, not
  direct token theft, which is precisely the kind of "capability/ceiling-High" the L3 standard is designed to gate.
- Whether SOPH-01/02/03 are genuine Mediums/Highs or benign requires authored harnesses + spec confirmation — the
  human-review packages name exactly the missing evidence and verify commands.

## Next
1. **Human review** of the 5 packages (`REPORT_PACKAGES/`); decide which warrant a harness.
2. On approval, **STAGE 2**: open the sealed Sherlock report and score (HIT/PARTIAL/ADJACENT/MISS/FP/DUP), severity
   calibration, and **L3 effectiveness** (did blocking over-rated Highs match the official severities?).
3. Author L2/L3 harnesses under `pocs/p212/` for any candidate the human advances (then re-run the overlay → PASS or
   demote). This also feeds the L2/L3 harness-authoring cost-model follow-up (P211).

## Guardrails honored
Fresh C4/Sherlock target (not in audits/, not P186-P211); answer key sealed+unread until STAGE 2; no live
submission/routing; L3 flag on for High readiness; 8 surfaces (not sprawl); every reportable candidate has a
human-review package; High requires L3 PASS or written override; production hashes byte-identical START==END; JSON
valid; firewall log maintained; fabrication 0.
