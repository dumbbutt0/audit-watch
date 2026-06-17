# P228 — Bug Bounty Readiness Stress Test

> **Type:** read-only assessment. No code changes, no severity edits, no sync, no submit/route/promote.
> Every score below is tied to a cited script or L3 record. Generated against active audit
> `size-credit-2024-06-blind`, post-P227.

## Objective

The standard is **not** "Can we find bugs?" It is: **"Can we reliably go from a fresh protocol URL to a
reportable, L3 runtime-confirmed finding with minimal operator intervention?"** This document grades every
pipeline stage, scores architecture coverage, analyzes the deferred harnesses, estimates fresh-blind readiness,
and issues a single readiness verdict.

Evidence base: a stage-by-stage trace of `run_pipeline.sh`, `scripts/`, the api-free skills
(`/deep-analysis`, `/ite-audit`, `/coverage-sweep`, `/triage`, `/poc`), the research detector families under
`documentation/architecture/`, and the executed `output_research/l3_readiness/SC-*.json` / `ZETA-*.json` records
from P223–P227.

---

## Pipeline Stage Maturity (URL → submission)

| # | Stage | Verdict | Evidence |
|---|---|---|---|
| 1 | Source acquisition | **BLOCKING** | `scripts/audit_manager.py` (`new`/`switch`) takes a local path via interactive prompts; no URL→clone. Operator clones manually. |
| 2 | Build environment | **OPERATOR_ASSISTED** | `scripts/setup_solidity_deps.sh` auto-detects deps + patches pragma caps; `compile_for_analysis.sh` 3-layer fallback. Fragile on transitive deps. |
| 3 | Surface discovery | **OPERATOR_ASSISTED** | Step 0.25 via `generate_step0_brief.py` → attack_surface.json; advisory, human reviews. |
| 4 | Candidate generation | **OPERATOR_ASSISTED** | Step 2 specialists run in parallel via `/ite-audit` (in-session skill); deterministic but operator-invoked. |
| 5 | Defense mapping | **AUTONOMOUS** | Step 1.5 `defense_mapper.py` reads static.json, classifies coverage, no API. |
| 6 | Invariant mapping | **OPERATOR_ASSISTED** | Step 0 `deep_analysis_prepare.py` pauses for `/deep-analysis` skill handoff. |
| 7 | Exploitability analysis | **OPERATOR_ASSISTED** | `multi_pass_confirm.py` + `pre_submission_gate.py` (8 gates); Step 3.9 coverage gate can block. |
| 8 | Harness generation | **BLOCKING (api-free reality)** | `generate_poc_test.py` (auto-PoC + 3-attempt repair) is API-path; the P223–P227 harnesses were all **hand-authored in-session**. |
| 9 | Runtime proof | **AUTONOMOUS** | `run_poc_tests.py` executes `forge test` → `data/runtime_poc/results.jsonl`. |
| 10 | Evidence completion | **FRAGILE** | `finding_detail.py` / sync; depends on every prior output existing. |
| 11 | Submission package | **AUTONOMOUS** | `final_submission_pack.py` aggregates pre-computed fields deterministically. |

Net: 3 AUTONOMOUS, 5 OPERATOR_ASSISTED, 1 FRAGILE, **2 BLOCKING (source acquisition, harness generation)**.

---

## Part A — URL → L3 Friction (reconstructed from SC-03/04/05/08)

Friction scale: 0 = fully autonomous · 10 = requires expert auditor.

**Critical reality:** in the api-free pipeline that actually ran (P223–P227), every L3 harness was
**hand-authored in-session**. `generate_poc_test.py` (the auto-PoC-with-repair loop) is on the **API path and was
not used** — so harness authoring is, in practice, expert-human work, not automation.

| Finding | Manual decisions | Manual edits | Harness adjustments | Failed attempts | Severity corrections | Arch insights | Friction |
|---|---|---|---|---|---|---|---|
| **SC-03** (negative-APR DoS, unit) | ~3 | 2 (copy YieldCurveLibrary, write test) | 1 | 0 | 2 (P226 `unknown` workaround → P227 permissionless+bounded cap) | 2 (internal `getAdjustedAPR` reached via external `getAPR`; `marketRateMultiplier=0` → SafeCast revert) | **5** |
| **SC-04** (Compensate zero-fee bypass, integration) | ~5 | 4 (copy Compensate.sol, MockPriceFeed, seed 2 debt+2 credit, dual-role compensator) | 2 | 1 | 1 (kept `unknown` — precondition needs price-drop) | 3 (dual-role lender; `Math.min(fee,0)=0`; healthy-borrower seeding) | **7** |
| **SC-05** (scaled-token dust, unit) | ~3 | 3 (NonTransferrableScaledToken harness, MockVariablePool) | 2 | 1 (residual-dust over-claim → dropped to `balanceOf < nominal`) | 1 | 2 (double-`mulDivDown` under-credit at index 1.5 RAY) | **5** |
| **SC-08** (CapsLibrary cap bypass, unit) | ~2 | 2 | 0 | 0 | 1 (bounded → Medium) | 1 (increase≤decrease boundary) | **3** |

**URL → L3 Friction Score: ~5/10 (mean), spiking to 7 for integration harnesses.** Drivers are constant: (1)
human triage of which candidate is harness-feasible, (2) hand-authoring the harness + mocks, (3) debugging
false-start assertions, (4) manual severity calibration. Isolated-unit harnesses (SC-05/08) are ~3–5; integration
harnesses (SC-04) are ~7.

---

## Part B — Architecture Coverage (recall / precision / harness / severity, 0–10)

| Category | Recall | Precision | Harness | Severity | Status / evidence |
|---|---|---|---|---|---|
| **Lending** (Size, Silo, credit) | 7 | 8 | 7 | 7 | **Only broadly-validated category.** 6 specialists + units/defi-accounting/liquidation-health lenses + `cross_contract_sibling_parity` (Size M-06) + `value_flow_parity` (Size M-02). Real hits: Size Credit, Ethos Reserve. |
| **Rewards / Distribution** (Blackhole, claims, emissions) | 4 | 7 | 3 | 5 | **Narrow.** `sibling_function_parity` validated on **ve(3,3) only** (Blackhole M-04). General Curve/Aura/Balancer emissions: no recovery data. |
| **Routers** (multicall, batching, swap/bridge routing) | 3 | 7 | 4 | 5 | **Very narrow.** `multicall_invariant_v1` recovers only the `bytes[]` self-delegatecall shape (3 HIT / 2 PARTIAL / 2 MISS / 2 FP). Assembly multicalls, ERC2771 reuse, msg.value reuse = PLANNED, not built. |
| **Oracle** (valuation, pricing, conversions) | 5 | 6 | 3 | 6 | **Mature spec, scarce validation.** Comprehensive `oracle` agent + units(oracle_price_decimals) + cross_chain_constants. Only one holdout recovery (Abracadabra M-10, 40% recall, vocabulary-limited). No answer-key validation corpus. |
| **NFT / Gaming** (TraitForge, Munchables) | 2 | 4 | 2 | 3 | **Not validated.** ERC1155 token_standard taxonomy is production-ready but never tested on an NFT-primary contest. Munchables holdout: no metrics. Game-mechanic invariants out of scope. |
| **Cross-Chain** (Decent, intents, bridges, ZetaChain) | 3 | 5 | 4 | 4 | **Production-wired, weak validation.** `cross_chain` agent + constants/migration lenses. Holdout deterministic recall **0%**; agentic deep-pass 40%. ZetaChain harnesses exist (p220) but severity calibration for trusted-system actors recurs (P221/P222). |

**Coverage verdict: only Lending clears a "broad + validated" bar.** Everything else is architecture-narrow
(rewards, routers), spec-mature but validation-scarce (oracle, cross-chain), or unvalidated (NFT/gaming).

---

## Part C — Deferred Harness Analysis (SC-11, SC-12, ZETA-02)

| Finding | Blocker class | Why deferred | Effort | Risk |
|---|---|---|---|---|
| **SC-11** (LiquidateWithReplacement transient REPAID event) | **architecture complexity** | Needs full loan state machine (State + DebtPosition lifecycle ACTIVE→REPAID, multi-step `liquidateWithReplacement`) + `vm.recordLogs` event-ordering capture; p223 realsrc is missing the action-library stack (Liquidate/LiquidateWithReplacement/Claim). | 8–12 h | **MEDIUM-HIGH** |
| **SC-12** (Claim sequential-index rounding, SC-05 family) | **architecture complexity** | Needs multi-credit positions + an index timeline (repay@idx0, claim@idx1<idx2); MockVariablePool only supports a fixed constructor index. SC-05 proved the single-token math; SC-12 needs the stateful drift. | 10–14 h | **MEDIUM-HIGH** |
| **ZETA-02** (ERC20Custody fee-on-transfer drift) | **harness tooling / missing mock** (light) | ERC20Custody not yet copied to p220 realsrc; needs a ~20-line MockFeeOnTransferToken. Tooling pattern already exists. | 2–4 h | **LOW** |

**Pattern:** the gap is the **integration tier**. Every successful harness (SC-05/08, ZETA-04/10/11) is
single-library/single-contract isolation. SC-11/SC-12 require crossing multiple stateful libraries over a shared
`State` — there is no reusable lifecycle-harness scaffold, so each is a from-scratch ~10-hour build. ZETA-02 is a
quick win (copy + mock).

---

## Part D — Fresh Blind Readiness (PoolTogether, Decent, TraitForge)

Probabilities: P(reportable candidate) / P(≥1 L3 runtime-confirmed) / P(submission-quality package).

| Target | Architecture | Candidate | L3-confirmed | Submission | Reasoning |
|---|---|---|---|---|---|
| **PoolTogether** | prize-savings / yield / distribution (≈ lending+rewards) | **~70%** | **~45%** | **~35%** | Closest to the validated lending+rewards surface; deep_trace/ite-audit recall is the strongest stage (found SC-01 blind). Drop-off at hand-authored harness + packaging. |
| **Decent** | cross-chain / bridge / intent | **~55%** | **~30%** | **~20%** | Cross-chain candidate recall is moderate (agentic 40%, deterministic 0%); p220 harness pattern exists but trusted-system severity calibration recurs and integration harnesses are slow. |
| **TraitForge** | NFT / gaming | **~40%** | **~20%** | **~12%** | Weakest — no validated NFT detectors; ERC1155 taxonomy untested in context; game-mechanic invariants out of scope. Candidate generation may still surface generic reentrancy/AC issues. |

Shared shape: **candidate generation travels well; harness generation and severity calibration do not.** The
funnel narrows hardest exactly where the work is most manual.

---

## Part E — Top 10 Choke Points (blocking BUG_BOUNTY_READY)

| # | Choke point | Impact | Likelihood | Recommended fix | Phases |
|---|---|---|---|---|---|
| 1 | **Harness generation is 100% hand-authored** (api-free; auto-PoC unused) | High | Certain | Wire/validate `generate_poc_test.py` for api-free, or build a harness-scaffold generator | 2–3 |
| 2 | **No integration-tier harness scaffold** (SC-11/SC-12 class) | High | High | Reusable lending `State`-lifecycle harness library (deposit→borrow→liquidate→claim) | 1–2 |
| 3 | **Source acquisition is fully manual** (no URL→clone→workspace) | Med | Certain | `audit_manager.py` URL intake → clone → `new`/`switch` | 1 |
| 4 | **Build env is fragile** (transitive deps, pragma caps) | Med | High | Harden `setup_solidity_deps.sh`/`compile_for_analysis.sh`; cache toolchains | 1 |
| 5 | **Only Lending broadly validated** | High | Certain | Validate oracle + NFT/gaming on real holdouts; expand router/reward families | 3+ |
| 6 | **Severity calibration recurs** (trusted-system/DoS floors) | Med | High | Codify the P221/P222/P227 calibration rules into a reviewed policy + tests | 1–2 |
| 7 | **Cross-chain deterministic recall 0%** (routing-recall blocker) | Med | Med | Broaden lens vocabulary; promote agentic deep-pass routing | 2 |
| 8 | **Coverage gate can block indefinitely** without operator sweep | Med | Med | Auto-disposition long tail with evidence anchors; better sweep UX | 1 |
| 9 | **4 in-session skill handoffs** (deep-analysis/ite-audit/coverage/triage) | Low | Certain | Acceptable by design; document operator runbook to reduce stalls | 1 |
| 10 | **Evidence completion is fragile** (depends on every prior output existing) | Low | Med | Defensive defaults + a pre-pack completeness preflight | 1 |

---

## Final Verdict

**B — READY_WITH_OPERATOR_SUPERVISION.** The system can hunt live programs but still depends on human expertise
at the critical stages: source acquisition (BLOCKING), harness authoring (hand-built per finding), integration-tier
harnesses (deferred), and severity calibration.

| Field | Value |
|---|---|
| **Readiness Score** | **58 / 100** |
| **Confidence** | **MEDIUM** |
| **Biggest Remaining Weakness** | Harness generation — expert hand-work in the api-free reality; no integration-tier scaffold, so multi-state findings (SC-11/SC-12 class) stall at 10+ hours each. |
| **Strongest Proven Capability** | Blind candidate generation with FP-tight calibration — SC-01 was a genuine out-of-focus blind discovery; the funnel held **0 false-Highs across P223–P227**. |

### Three Highest-ROI Next Phases
1. **Build automation** — URL intake + hardened compile (kills the one source BLOCKING stage + the fragile build).
2. **Integration-tier harness scaffold** — reusable lending `State`-lifecycle library; bank the ZETA-02 quick win
   (2–4 h) and unblock SC-11/SC-12.
3. **Coverage validation + calibration pass** — validate oracle & NFT/gaming on real holdouts; codify the
   trusted-system/DoS severity-floor rules into a reviewed, tested policy.

### Recommendation
**"Run these phases first."** Justification (evidence, not optimism): the pipeline has 2 BLOCKING and several
FRAGILE stages, harnesses are 100% hand-authored, integration harnesses are deferred at 10+ h each, and only 1 of
6 architectures is broadly validated — so aggressive live hunting today would succeed mainly on lending targets
and stall at the harness/packaging steps elsewhere.
