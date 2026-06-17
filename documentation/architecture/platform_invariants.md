# Audit-Watch — Research Platform Invariants

Each research-track layer has exactly one job and one invariant that keeps it from quietly taking on a downstream
layer's job. The invariants are the reason the platform stays auditable and precision-preserving as it grows.
All three are enforced in code and asserted in tests.

---

## Layer 1 — Detectors: **"Signal, don't submit"**
- **Why it exists:** a detector's value is *recall of a narrow shape at high precision*. The moment a detector
  starts deciding severity, exploitability, or submission, its precision claims become unverifiable and it can push
  noise into a bounty/report flow.
- **Problem it prevents:** a research detector silently becoming a (low-precision) auto-submitter or
  severity-assigner.
- **Example violations:** a detector emitting `severity:"High"`; setting `routes_in_production:true`; populating
  `routed_manifest_ids`; minting a finding into the production triage flow.
- **Required safeguards (in place):** every detector report carries `is_gate:false`, `research_only:true`,
  `routes_in_production:false`, `routed_manifest_ids:[]`; detectors are un-wired (no reference from routing/gates/
  run_pipeline/agent_policy); candidates describe an *opportunity/surface*, not a proven bug.

## Layer 2 — Normalization: **"Rank, don't relabel"**
- **Why it exists:** to compare findings across detector families you must put them on one scale — but the scale
  must not mutate the detectors' own judgments, or the comparison becomes a hidden re-classifier.
- **Problem it prevents:** the normalizer "upgrading" a medium candidate to high (or down-grading), so that ranking
  silently overrides detector confidence.
- **Example violations:** rewriting `confidence`; computing a per-finding severity; emitting a bug verdict;
  normalizing a source that is production-routed.
- **Required safeguards (in place):** `confidence` is copied **verbatim** (tested across all levels);
  `declared_severity_potential` is a *family-level capability hint*, never a per-finding severity;
  `review_priority` is a transparent, deterministic function whose factors are echoed in `why_priority`; the
  normalizer **refuses** any source with `routes_in_production:true` or non-empty `routed_manifest_ids`; every
  record is `routing_allowed:false` / `research_only:true`.

## Layer 3 — Evidence Bundle Gate: **"Assemble, don't adjudicate"**
- **Why it exists:** before anyone (human or future judge) investigates a candidate, it must be *evidence-complete*.
  But completeness is not correctness — deciding "is this a bug" is a later, different job.
- **Problem it prevents:** an evidence/triage step drifting into a bug/severity/exploitability verdict, collapsing
  two distinct responsibilities and overstating what the platform concluded.
- **Example violations:** emitting `is_bug` / `severity` / `exploitability_score` / `recommended_next_step`
  (poc/submit/downgrade/reject); changing carried confidence; consuming a routed input.
- **Required safeguards (in place):** the bundle contains **no verdict fields** (tested absent) — only a
  *completeness* recommendation (`ready_for_review` / `needs_more_evidence`); `confidence` and
  `declared_severity_potential` are carried verbatim; the gate **refuses** input whose `routing_allowed` ≠ false;
  it is read-only and never calls the production exploitability/submission/gate engine.

---

## The general pattern (for future layers)
Every future research-track layer (judge, PoC-feasibility, submission-readiness) must declare a one-line invariant
of the same form — *do your job, refuse the next layer's job* — and back it with: (1) the four research flags on
every output, (2) verbatim pass-through of upstream judgments it is not authorized to change, (3) a defensive
refusal of any non-research / routed input, and (4) tests asserting the forbidden outputs are absent. A layer that
cannot state what it **refuses to do** is not ready to be added.

## Non-negotiable platform-wide rules
- No research-track component routes, submits, or sets production severity/exploitability autonomously.
- Confidence set by a detector is immutable downstream (rank/age/annotate, never relabel).
- Each layer consumes only the prior layer's research-only output and refuses anything marked routable.
