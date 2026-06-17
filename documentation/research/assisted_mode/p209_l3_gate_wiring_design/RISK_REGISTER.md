# P209 — risk register

| # | risk | likelihood | impact | mitigation |
|---|---|---|---|---|
| 1 | **False confidence from a passing PoC built on unrealistic mocks** (mock manufactures the bug) | med | high | policy requires `dependency_mocks != creates_vulnerable_condition` + a control/expected-vs-actual case; reviewer checks `source_validity_notes`; P204/P207 used external-only mocks + single-actor controls. |
| 2 | **Expensive harness cost slows workflow** | high | med | L3 required ONLY for High submission readiness, not discovery/Medium; NEEDS_L3_HARNESS stays investigable; cost model + auto-scaffold-vs-human is the P210/next decision. |
| 3 | **Blocking valid Highs that lack a harness** | med | high | fail-open everywhere except High readiness; `HUMAN_OVERRIDE` path (written rationale) preserves genuine Highs; blocked≠rejected (candidate persists, harness can be added). |
| 4 | **Human-override abuse** (rubber-stamp) | med | high | override must be explicit + written + visible (`human_override_reason`), satisfy conditions 2–7, and is auditable in the append-only overlay; surfaced read-only in dashboard. |
| 5 | **Dashboard shows threat ceiling as final severity** | med | med | dashboard panel shows `threat_ceiling` and `calibrated_severity_after_l3` as DISTINCT labels (per the policy); never presents ceiling as final. |
| 6 | **Accidental route-to-submit coupling** | low | high | layered design touches only the readiness overlay (never flips `submission_ready`/`routing_allowed`) + read-only display; explicit no-submit guard test (P210); `api_free` untouched. |
| 7 | **Stale L3 artifacts** (PoC no longer matches source) | med | med | record `poc_path`+`poc_command`+source hash in evidence; P210 can invalidate L3_PASS if source changes; re-run is cheap once deps assembled. |
| 8 | **Dependency setup failures** (cf. P205 0.7.6 web) | med | med | L3_INCONCLUSIVE state is explicit (not a pass, not a hard-fail); P207 showed deps are usually forge-installable; inconclusive → NEEDS_L3_HARNESS, candidate not lost. |
| 9 | **Triager disagreement with the impact/magnitude threshold** | med | med | `magnitude_basis` is explicit and reviewable; threshold lives in policy (versioned), not hard-coded in a gate; human override + written rationale resolves edge cases. |
| 10 | **Over-blocking reduces recall (perception)** | low | med | recall is structurally untouched (discovery/gates unchanged); L3 only affects High *readiness*, measured by the backtest (0 false-blocks on validated controls). |
