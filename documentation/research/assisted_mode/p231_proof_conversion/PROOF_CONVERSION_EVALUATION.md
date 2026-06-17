# P231 — Cross-Architecture Proof Conversion Evaluation

> **Type:** execution + measurement. Built real Foundry harnesses and ran forge for one candidate per
> architecture. Judges *conversion quality*, not candidate quality. No submit/route/promote; no production /
> detector / prompt / routing / severity / forbidden-file edits; real audit source copied into `pocs/` (audits/
> untouched); answer keys never opened. Failures would be recorded and classified — none occurred.

## Selected candidates (highest-confidence per architecture, from P230; all re-confirmed REAL)
- **Oracle → QAMM-03** — `UpdateWeightRunner._getData`: single-oracle pools (`numAssetOracles==1`) skip the
  stale-fallback loop, so the staleness revert is unreachable and a stale price is silently returned.
- **Cross-chain → DEC-01** — `UTB.receiveFromBridge` is `public` with no modifier → `_swapAndExecute` →
  `UTBExecutor.execute` on attacker-chosen target/payload.
- **NFT/Gaming → TF-17** — `EntropyGenerator.initializeAlphaIndices` is `onlyOwner` but called by non-owner
  `TraitForgeNft._incrementGeneration`, bricking generation rollover (and minting) at the cap.

---

## Part A — Proof Conversion Score

| Candidate | Candidate quality (0–10) | Harness difficulty (0–10) | Runtime proof | Time cost | Human intervention |
|---|---|---|---|---|---|
| **DEC-01** (cross-chain) | 9 | 3 | **PASS** (2/2) | <2h | arch insights 2 (executor-owned-by-UTB topology; access-control-asymmetry control) · state recon 1 (registerSwapper + transferOwnership) · mocks 3 (token/swapper/victim) · debug 0 |
| **TF-17** (NFT) | 9 | 4 | **PASS** (3/3, mechanism-level) | <2h | arch insights 2 (deploy topology owner≠nft; OZ-4.9 revert string) · state recon 1 (wire setEntropyGenerator) · mocks 0 (real contracts) · debug 0 |
| **QAMM-03** (oracle) | 8 | 6 | **PASS** (2/2) | 2–6h | arch insights 3 (loop-bound logic; setRuleForPool-as-pool path; MASK_POOL_GET_DATA) · state recon 2 (PoolSettings + register-via-pool + approvedActions + addOracle-as-admin) · mocks 2 (oracle/pool) · debug ~1 (monorepo remappings) |

All three converted to runtime PASS on real, byte-identical source with external-only mocks and a control test.

---

## Part B — Failure Analysis

**No conversion failed.** One scoping note (not a failure): **TF-17 is proven at the call level** — the harness
reproduces the exact external call `_incrementGeneration` makes (`vm.prank` as the TraitForgeNft address calling
`initializeAlphaIndices()`), with the real deploy topology asserted (owner == deployer ≠ TraitForgeNft, allowedCaller
== TraitForgeNft). The full 10,000-mint generation rollover was **not driven** — that is the integration tier
(lifecycle scaffold, per P229). The access-control mechanism and the DoS consequence are fully proven; only the
end-to-end lifecycle path is shortcut. If forced into the taxonomy this is a partial **Architecture/integration
depth** limitation, not an Exploitability or Harness failure.

---

## Part C — Conversion Funnel (per architecture)

| Stage | Oracle (QAMM-03) | Cross-chain (DEC-01) | NFT (TF-17) |
|---|---|---|---|
| Candidate | 1 | 1 | 1 |
| → Exploitable | 1 (confirmed) | 1 | 1 |
| → Harnessable | 1 | 1 | 1 |
| → Runtime-Proven | 1 | 1 | 1 (mechanism) |
| → Submission-Ready | 0 (research_only; blind holdout; needs impact magnitude) | 0 (research_only; blind holdout) | 0 (research_only; full lifecycle pending scaffold) |

**Candidate → Runtime-Proven: 3/3 = 100%.** Submission-Ready is 0 by design — these are sealed blind-holdout
subjects used for measurement; nothing is submitted/routed/promoted.

`decide()` classification (faithful, not tuned): **DEC-01 = high** (permissionless, material, control, PASS — a
genuine unguarded arbitrary-execution bug; not inflated), **QAMM-03 = medium** (attacker_model=unknown: systemic
correctness, no clean beneficiary), **TF-17 = medium** (core DoS, no beneficiary).

---

## Part D — Generalization Test (vs lending)

Lending baseline (P223/P226/P227): SC-01/04/05/08 all converted to L3 PASS via the recipe "copy real `@src`
byte-identical → vendor only needed deps → external-only mocks → L1/L2/L3 + control."

P231 applied the **identical recipe** to three non-lending architectures and got **3/3 runtime PASS.** Proof
generation **does not collapse outside lending.** Crucially, the difficulty ranking (cross-chain 3 < NFT 4 <
oracle 6) tracks **framework/dependency weight**, not architecture class:
- The "HARD" oracle case was a dependency-**availability** problem (Balancer-V3 monorepo), and the deps were
  already in the workspace — wiring remappings made it compile in 86 files.
- Cross-chain (a non-lending architecture) was the **easiest** conversion of all — easier than several lending
  harnesses.

So conversion is **not architecture-biased**; it is gated by (a) dependency availability and (b) for emergent
multi-transaction bugs, integration-tier lifecycle depth.

---

## Part E — Counterfactual (reusable integration scaffold)

No candidate failed, so none needed rescuing. A reusable scaffold (P229 design, generalized) would still improve:
- **TF-17:** upgrade from call-level to a full-lifecycle L3 (drive minting → cap → rollover) instead of the
  `vm.prank` shortcut.
- **QAMM-03:** cut the 2–6h setup (PoolSettings seeding + monorepo remapping/dependency wiring) toward <2h via a
  dependency-resolver + state-seeding helpers.
- **DEC-01:** marginal (already a clean <2h end-to-end PASS).

Estimated improvement: conversion **feasibility** is already there; the scaffold raises **depth** (full lifecycle)
and **speed/robustness** (dependency wiring), not pass/fail.

---

## Final Verdict

# A — PROOF_GENERALIZES

Runtime proof generation works across architectures: **3/3 conversions PASS** (oracle, cross-chain, NFT) on real,
byte-identical source using the same recipe as lending, each with a passing control. The hardest case (oracle /
Balancer-V3) succeeded once in-repo dependencies were wired. Conversion is gated by dependency availability and
integration-tier lifecycle depth — **not** by architecture class.

This refines the arc: P229 ranked harness generation the binding constraint (assuming recall was the gap); P230
showed recall generalizes; **P231 shows proof conversion also generalizes.** The residual is depth + setup
friction + (still unmeasured) live-target precision — the system is materially closer to ready than P228's 58/100
implied.

---

## Deliverables

| Field | Value |
|---|---|
| **Proof Conversion Score** | **85 / 100** (3/3 runtime PASS; 2 clean end-to-end, 1 mechanism-level pending lifecycle; faithful severity; setup friction on oracle) |
| **Oracle Conversion Result** | **PASS** (QAMM-03, 2/2, `decide`=medium) — stale-price bypass proven via real registration path + control |
| **Cross-Chain Conversion Result** | **PASS** (DEC-01, 2/2, `decide`=high) — unprivileged arbitrary execution end-to-end + guarded-executor control |
| **NFT/Gaming Conversion Result** | **PASS** (TF-17, 3/3, `decide`=medium) — owner-mismatch rollover brick at call level + topology + control |
| **Strongest Architecture** | **Cross-chain** — cleanest full end-to-end proof, lowest harness difficulty (3) |
| **Weakest Architecture** | **NFT/Gaming** — proof depth limited to the mechanism (call level); full lifecycle needs the integration scaffold. (Oracle had the highest *setup friction*.) |
| **Biggest Harness Limitation** | Full-lifecycle / multi-transaction integration — driving emergent protocol state (e.g., a 10k-mint generation rollover) still needs per-protocol manual seeding; the call-level shortcut covers access-control mechanisms but not emergent multi-tx economic bugs (the P229/P230 temporal-invariant gap) |
| **Biggest Missing Scaffold Capability** | A reusable **lifecycle + dependency-wiring** harness layer: (1) deploy/wire/drive real protocol actions for full-lifecycle L3; (2) auto-resolve in-repo monorepo dependencies (the QuantAMM remapping friction) |
| **Estimated Readiness After Scaffold** | **~85–88/100, approaching BUG_BOUNTY_READY** — conversion proven to generalize; scaffold removes depth + setup friction; residual gate is live-target precision verification |

### Recommendation: **Build multi-architecture scaffold**

Defended by the measured friction (not optimism): conversion already **generalizes** (3/3), so neither "one more
validation phase" nor a lending-only "integration scaffold" is the highest-ROI step. The two real, measured
limitations are (a) integration-tier lifecycle depth (TF-17 call-level shortcut) and (b) dependency-wiring setup
friction (QuantAMM 2–6h). A **multi-architecture scaffold** — a reusable lifecycle/state-seeding layer plus a
dependency resolver spanning the now-validated architectures — directly removes both and subsumes the P229 lending
scaffold. Live hunting should follow immediately after, gated only by live-target precision verification.
