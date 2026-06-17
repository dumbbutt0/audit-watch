# Audit-Watch — Research Platform Roadmap

Documentation only — this records direction, not commitments, and **implements nothing**. Items are split into
Completed / In Progress / Planned. All research-track items are research-only by default; promotion to production is
always a separate, later, human decision.

---

## Completed (research-only, validated)
- **`multicall_invariant_v1`** — RESEARCH-STABLE / NARROW SCOPE CONFIRMED (20-target eval).
- **B1 inherited-multicall sidecar** — research-only visibility aid; B1 PARTIALLY VISIBILITY ISSUE (validated, 0 new FP).
- **`permit_asset_binding`** — RESEARCH-STABLE / HIGH PRECISION VALIDATED (7-target prototype + 20-target validation).
- **`sibling_function_parity`** — RESEARCH-STABLE / architecture-narrow (Blackhole M-04; 0 FP).
- **`cross_contract_sibling_parity`** — RESEARCH-STABLE / NARROW (Size M-06; 0 FP).
- **`value_flow_parity`** — RESEARCH-PROTOTYPE / narrow (Size M-02; 0 FP).
- **`registry_position_lifecycle`** — RESEARCH-STABLE / narrow; **distinct family (not parity)** (NOYA H-23 + H-18; 0 FP).
- **Research-family promotion rollup** — 5-criteria bar; portfolio 5 bugs / 3 architectures / 0 FP; **validated, no promotion yet** (`research_family_promotion_status.md`).
- **Normalization layer** — comparable records + review_priority ("rank, don't relabel").
- **Evidence Bundle Gate** — evidence-completeness triage ("assemble, don't adjudicate").
- **Documentation consolidation** — this `documentation/architecture/` set.

## In Progress
- None currently. (The platform is at a clean checkpoint: detectors → normalization → evidence-bundle, all
  validated and un-wired.)

## Planned — future detector families (research-only; from the multicall evolution research)
Ranked by prior research; each must run the full lifecycle (`research_methodology.md`) and ship research-only:
1. **Internal-call batch / state-reuse** — e.g. a per-call invariant (mode/price snapshot) reused across an
   internal-call batch loop (Ethos `batchLiquidateTroves` recovery-mode-once class). The clearest recurring
   multicall blind spot.
2. **ERC2771 context reuse** — `Multicall` + `ERC2771Context` `_msgSender`/`_msgData` corruption (OZ
   CVE-2023-40014 class).
3. **msg.value reuse** — payable multicall re-reading `msg.value` per batched sub-call (Tokemak/UniV3 router class).
4. **Router / transformer execution** — arbitrary-call surfaces (`transform`, swap routers) — must also suppress
   the benign router-swap FP pattern.

(Also noted earlier: a manifest-layer **inheritance-resolution** project to generalize the B1 sidecar beyond
multicall — separate from detector work; assembly-multicall recognition is its own detector item.)

## Planned — future platform layers (research-track; NOT built)
Each would consume the prior layer's research-only output and must declare its own "do X, refuse the next layer's
job" invariant before being added (see `platform_invariants.md`):
- **Judge layer** — plausibility estimate over READY evidence bundles. *(Production has a separate wired
  `judge_simulate.py`; this would be the research-track version.)*
- **PoC feasibility gate** — PoC-ability + missing-proof estimate. *(Production has a separate wired PoC engine.)*
- **Submission readiness gate** — gate research findings toward human submission review; never auto-submit.
  *(Production already has the `submission/` engine.)*

> Reminder: these future layers do **not** imply autonomous submission, severity, or exploitability. They would be
> research-only assistive stages, human-in-the-loop, and connecting them to the production pipeline is an explicit
> future decision.

## Non-goals (explicitly out of scope unless separately approved)
- Autonomous submission, autonomous severity assignment, autonomous exploitability determination.
- Wiring any research-track detector/layer into production routing or gates.
- Broadening a RESEARCH-STABLE detector beyond its validated scope without re-running the lifecycle.
