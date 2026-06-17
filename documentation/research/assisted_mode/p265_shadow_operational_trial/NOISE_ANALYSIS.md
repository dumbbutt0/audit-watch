# P265 — NOISE_ANALYSIS

Question: as a shadow stream, does the harness flood the operator, and is the noise structured or random?

## Volume is bounded and stable
- 11–23 advisory candidates/audit (mean 16.6), hard-capped at `max_swept_loci_json=25`. No contest approached an
  unbounded flood even on large manifests (reserve has 2188 manifest functions → still only 23 candidates).
- **12/13 contests hit the mechanism-cap truncation** (`max_total_mechs_to_ranking=30`): the harness generates more
  mechanism hypotheses than it forwards, and bounds them deterministically. This is the cap *working*, not a leak —
  but it is a burden signal: there is more raw mechanism breadth behind the 30-cap than the operator sees.

## Noise is structured, not random
Template-family distribution across the 216 candidates is spread across all 9 shapes, weighted toward the
award-carrying families:
`T2 redemption-coupling 82 · T5 liveness 53 · T1 external-dep 49 · T8 share-price 48 · T7 solvency 40 · T9 math 33 ·
T3 reentrancy 31 · T6 drift 25 · T4 migration 17`.
The dominant families (T2/T5/T1/T8/T7) are exactly the families that carried awards across P254–P263 — so the bulk
of the stream is on-class, not random surface.

## False-positive posture (metric #6)
- **0 severe concluded/reportable FP across all 13** — guard PASS, 0 promotion flags. Enforced by construction:
  every candidate is `ADVISORY_RECALL_CANDIDATE` with severity null and all promotion flags false; the harness
  fails closed (no advisory output) if any candidate carried a promoted/concluded field.
- **This is "0 concluded/reportable FP", NOT true 0-FP.** ~2/3 of advisory candidates are *not* worth review by the
  operator rubric (66.7%). Those are the real "noise" cost — benign loci surfaced by the recall-first clauses. The
  guard guarantees none of them can masquerade as a confirmed finding, but they still consume triage time.

## Net
Noise is **manageable**: bounded volume, on-class distribution, 0 concluded-FP, ~1/3 useful by proxy, ~12 min/useful
lead. The residual cost is the ~2/3 benign recall-delta loci an operator must skim — acceptable for a shadow recall
engine, and the natural target if a future phase wants to *tighten* (caps/ranking handoff), not widen, discovery.
