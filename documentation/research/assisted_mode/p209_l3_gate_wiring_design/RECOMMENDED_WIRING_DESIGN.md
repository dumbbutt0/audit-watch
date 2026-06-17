# P209 — recommended wiring design: LAYERED (option F)

## Recommendation
Wire the L3 HIGH gate as a **layered design**: enforcement in `submission_readiness_review.py` (option D) + read-only
visibility in dashboard/report package (option E), with discovery and the two deterministic gates
(`min_confirm_gate`, `confirm_gate`) left **byte-identical**.

## Design
1. **Discovery / adjudication unchanged.** Deep-trace severity stays a `threat_ceiling`. L3 never runs before
   candidate creation or `min_confirm_gate`, and never suppresses mechanism investigation or recall.
2. **Gates unchanged.** `min_confirm_gate` (field presence) and `confirm_gate` (reachability truth) keep their exact
   current behavior. L3 is applied **after** mechanism/source confirmation (post-`confirm_gate`).
3. **`submission_readiness_review.py` is the canonical High blocker.** When `severity_target == High` and
   `l3_status ∉ {PASS, HUMAN_OVERRIDE}`, readiness = **`blocked_by_missing_l3_poc`**. It computes this by calling the
   P208 `decide()`; it still **never flips `submission_ready`/`routing_allowed`** (research-only/append-only overlay).
4. **Medium path untouched.** Medium readiness does NOT require L3; it proceeds if mechanism + impact are source-proven
   (existing checklist). L3 is optional supporting evidence for Medium.
5. **NEEDS_HARNESS stays investigable.** A NEEDS_L3_HARNESS candidate remains a valid Medium/early candidate and can be
   worked on; it simply cannot become **High**-submission-ready.
6. **`confirm_gate` may record `threat_ceiling` + candidate severity** (display), but the layered design ensures it
   cannot, by itself, make a High submission-ready without L3.
7. **Dashboard / report package** display L3 status, calibrated severity, and blocker reason **read-only** (no flags
   flipped). `final_submission_pack` annotates High items lacking L3 as "not High-ready (missing L3 PoC)".
8. **Human override** is allowed but must be explicit, written, and visible (`l3_status=HUMAN_OVERRIDE` +
   `human_override_reason`), still subject to the same concrete-asset/material-delta/control conditions.

## Why F over the alternatives (explicit rejections)
- **A (before min_confirm):** would gate candidates before fields/reachability exist → **suppresses discovery**. Reject.
- **B (between gates):** runs L3 before reachability is proven → wasted harness on dead paths; mis-ordered. Reject.
- **C (inside confirm_gate):** overloads a deterministic reachability gate; its submission-mode HARD-FAIL would
  **block the pipeline** on a missing harness and conflate "unreachable" with "impact-unproven"; changes core gate
  behavior. Reject.
- **D alone:** correct enforcement locus but no dashboard/package visibility → include, but pair with E.
- **E alone:** display only, **no enforcement** → a High could be packaged without L3. Reject as sole mechanism.
- **F = D + E:** enforcement where readiness already lives + visibility, gates and discovery unchanged, fail-open
  (never a pipeline hard-fail), fail-closed for High. **Chosen.**

## Invariants preserved
Recall untouched; deterministic gates byte-identical; no auto-submit/route; canonical `submission_ready`/
`routing_allowed` never flipped; human review mandatory; every L3 artifact `research_only:true`/`routes_in_production:false`.
