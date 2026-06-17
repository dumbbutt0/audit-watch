# P222 — Plan

> Note: the task spec reused `P221_*` deliverable filenames (a copy-paste slip — P221 already shipped the
> reachability taxonomy). This phase is **P222**; deliverables live in `p222_human_review_priority/`.

## Goal
Stop the pipeline from burying real, L3-proven findings that are not *auto*-reportable because the attacker
path uses a trusted/system actor (TSS, bridge executor, keeper, relayer, admin, module). Add a **review-priority
layer** — `HIGH_PRIORITY_HUMAN_REVIEW` — that surfaces such findings above noise. Not an auto-submit layer.

ZETA-04 is the motivating case: CLEAN_HIT vs the official awarded finding, L3 PASS (paused connector still mints
via `onReceive`; guarded sibling `onRevert` reverts under pause), real impact (emergency pause does not halt
inbound delivery), but the direct caller is `onlyTssAddress` → `attacker_model=privileged_only` blocks auto-High.
Correct for auto-submission, wrong for prioritization.

## Core distinction
`submission_ready` (canonical, machine-owned, stays false) and `human_review_priority` (new, display-only) are
**independent axes**. A candidate can be not-submission-ready, blocked from auto-High, and still high-priority for
human review.

## Approach (1 new helper + 6 code edits + 2 data edits; `dashboard_sync.py` UNCHANGED)
1. `scripts/human_review_priority.py` — pure `evaluate_priority(record)` → six fields. Reads only
   display/evidence; writes only priority fields; never touches severity/safety flags.
2. `scripts/sync_hunt_findings.py` — call the helper in `build_bundle` after the P221 reachability block; pull
   the artifact-backed `impact_type` from the L3 record; add the six fields to the return dict + `CARD_INJECT`.
3. `output_research/l3_readiness/ZETA-04.json|ZETA-11.json` — additive `impact_type` over the proven impact.
4. `scripts/finding_detail.py` — read-only `top_line_status` banner.
5. `scripts/funnel.py` — whitelist priority fields into rows.
6. `scripts/findings_overview.py` — priority-aware secondary sort (`_effective_rank`, boost-only).
7. `scripts/dashboard.py` — read-only `?human_review_priority=` filter on `/api/findings` + `/api/candidates`.
8. `scripts/validate_hunt_sync_completion.py` — three new invariant checks.

## Strict scope (honored)
No auto-submit · no `routing_allowed:true` · no canonical `submission_ready:true` · no severity auto-promotion ·
no browser-computed severity · L3 High gate not weakened · `deep_trace.md` / `min_confirm_gate.py` /
`confirm_gate.py` not modified · answer keys / historical labels unchanged · dashboard/readiness/prioritization
only.

## Decision space
`HUMAN_REVIEW_PRIORITY_READY` · `HUMAN_REVIEW_PRIORITY_PARTIAL` · `HUMAN_REVIEW_PRIORITY_FAILED_SAFETY` ·
`HUMAN_REVIEW_PRIORITY_FAILED_VISIBILITY` · `INVALID_RUN`. **Expected & achieved: HUMAN_REVIEW_PRIORITY_READY.**
