# P209 — recommendation

## Decision: `L3_WIRING_DESIGN_READY`

The submission-confirm path is mapped from real code, the six placement options are compared, one design is chosen and
the rest explicitly rejected, and the state machine / interface / backward-compat / implementation plan / risk
register are written — with **no wiring and no production behavior change** (production hashes byte-identical
START==END).

## Chosen design — LAYERED (option F)
- **Enforcement** in `submission_readiness_review.py` (the existing research-only, append-only readiness overlay that
  never flips `submission_ready`/`routing_allowed`): when `severity_target==High` and `l3_status∉{PASS,HUMAN_OVERRIDE}`
  → readiness `blocked_by_missing_l3_poc`, computed via the P208 `decide()`.
- **Visibility** in dashboard/report package as read-only L3 evidence state (threat_ceiling vs
  calibrated_severity_after_l3 shown as distinct labels).
- **Unchanged:** discovery, `min_confirm_gate` (field presence), `confirm_gate` (reachability truth), deep-trace,
  routing. L3 runs only *after* mechanism/source confirmation; fail-closed for High readiness, fail-open everywhere
  else; human review stays mandatory; human override must be explicit, written, and visible.

## Why F (and why not the others)
`confirm_gate` proves *reachability*, `min_confirm_gate` proves *field presence* — neither proves *realized
magnitude*, which is the L3 gap. Putting L3 **before the gates (A)** or **between them (B)** would suppress discovery
or waste harness effort on unreachable paths; **inside confirm_gate (C)** would overload a deterministic reachability
gate and hard-block the pipeline on a missing harness, conflating "unreachable" with "impact-unproven";
**dashboard-only (E)** has no enforcement (a High could be packaged without L3). The layered **D+E** puts enforcement
exactly where readiness already lives, adds visibility, and leaves gates/discovery/recall untouched.

## Backward compatibility
P204/P207 dry-run records still classify 10/10 (re-run probe); Medium path unaffected; no historical record rewritten;
no route-to-submit change; missing-L3 defaults to `NEEDS_L3_HARNESS` for High (fail-closed), no effect for Medium.

## Next (P210, NOT this phase)
Implement the layered wiring per `IMPLEMENTATION_PLAN.md` behind a default-safe flag (`AUDITWATCH_L3_READINESS=1`):
add L3 fields to the readiness record, call `decide()` from `submission_readiness_review.py` only, add
`blocked_by_missing_l3_poc`, add a read-only dashboard panel, add tests + an explicit no-submit guard + old-record
defaulting. Human review remains mandatory. Deep-pass recall + oracle track remain separate.
