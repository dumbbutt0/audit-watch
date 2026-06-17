# P212 — reviewing the hunt bugs in the dashboard (`/p212`)

A read-only review page was added so the sophon hunt candidates + L3 verdicts are browsable in the dashboard, without
creating an audit workspace or switching away from the active quantamm eval.

## How to view
```
python scripts/dashboard.py        # http://localhost:8765
```
Open **http://localhost:8765/p212** (also linked from the home page and the `/findings` nav).

## What it shows (read-only)
A table of SOPH-01..07 with: title · surface · threat ceiling · attacker model · **L3 status** · calibrated severity ·
`high_promotion_allowed` · L3 blocker · links to the report package(s), harness-results doc, and PoC command.
- SOPH-01/02 → REFUTED (invalid), SOPH-03 → CONFIRMED MEDIUM (DoS), SOPH-04 → needs-harness, SOPH-05/06/07 → privileged.
- Banner shows the target, stage decisions (READY_FOR_HUMAN_REVIEW / READY_FOR_SCORING), and **answer key: SEALED**.

## Routes added (in `scripts/dashboard.py`, additive)
- `GET /p212` → serves `dashboard/p212.html`.
- `GET /api/p212` → JSON: `CANDIDATE_REGISTER.json` + per-candidate L3 record run through
  `submission_readiness_review.l3_evaluate()` (pure; no flag needed) + package/harness links + stage decisions.
  Stamped `research_only:true`, `answer_key:"SEALED"`, `active_audit_unchanged:true`.
- `GET /view/p212/{name}` → renders a P212 `.md`/`.json` artifact read-only; **path-traversal-guarded**, and
  `_sealed/`/`targets/` are refused (403) so the sealed Sherlock report is never served.

## Authoritative status + supersession (update)
`/api/p212` makes the **UPDATED_REPORT_PACKAGES** entry authoritative: when present it supersedes the older
`REPORT_PACKAGES/` draft (the draft is shown only as a muted "superseded" note, not linked as a live verdict). Each row
carries a computed `display_status` chip + badges:
- **SOPH-03** → `CONFIRMED MEDIUM`, `human_reviewable=true`, `high_promotion_allowed=false` (package = DoS doc only;
  the `…wrap_offbyone.md` draft is superseded).
- **SOPH-04** → `NEEDS_HARNESS / likely by-design`, `by_design=true`, not submission-ready.
- **SOPH-01/02** → `REFUTED` (REFUTED docs supersede the drafts).
- **SOPH-05/06/07** → `PRIVILEGED (admin-prereq)`.
`submission_ready_as_high` is always false (L3-gated). Fields added: `display_status`, `human_reviewable`, `by_design`,
`superseded`, `submission_ready_as_high`.

## Safety
Read-only; no submit/promote/route controls; active audit not switched; sealed answer key never served (verified:
`/view/p212/_sealed/...` and `/view/p212/targets/.../_sealed/...` → HTTP 403). Only `scripts/dashboard.py`
(857d593a → 520a94e8) + new `dashboard/p212.html` changed; all other production files byte-identical.
