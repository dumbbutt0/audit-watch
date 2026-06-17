# multicall_invariant — Detector Evolution Program

**Type:** research / analysis / planning only. **No detector code, patterns, manifests, routing, gates,
thresholds, or answer keys were modified.** Flags remain `is_gate:false` / `research_only:true` /
`routes_in_production:false`. This document optimizes for *architectural coverage, mechanism coverage, precision
preservation, explainability, reproducibility, and low-noise operation* — **not** for answer-key matching or
higher HIT counts.

**Evidence base (all read-only):**
- 20-target results — `documentation/evals/overnight_multicall_scorecard.jsonl` + per-target notes
  `documentation/evals/multicall_overnight_targets/<slug>.md`
- Final classification — `documentation/evals/multicall_invariant_final_evaluation_report.md`
  (verdict **NARROW SCOPE CONFIRMED**) + `…/multicall_invariant_integrity_review.md` (VERIFIED CLEAN)
- Detector source — `scripts/multicall_invariant_taxonomy.py`, `scripts/multicall_invariant_audit.py`,
  `config/multicall_invariant_patterns.json`
- Manifest mechanics — `scripts/build_coverage_manifest.py`

---

## 1. Current Detector Scope (what it actually detects today)

A function-scoped, manifest-driven recall lens. For each in-scope manifest function it brace-matches the body
(+1-level same-contract helper resolution) and applies a **two-signal gate** then four shapes
(`multicall_invariant_taxonomy.py:97-223`):

- **Signal A — batch executor:** a name-gate hit (`multicall/batch/aggregate/executeBatch/…`) **OR** a
  call/delegatecall loop (`.call(`/`delegatecall`/`functionCall` inside `for`/`while`) **OR** a self-delegatecall.
- **Signal B — accounting invariant:** `balanceOf/totalSupply/supplyCap` (supply), `cap/limit/ceiling` (cap),
  `credit/debt/collateral/shares/balance/supply/borrow` (acct).
- **Shapes:** `pre_post_supply_invariant` (Size M-01), `per_call_check_batch_bypass`, `same_tx_state_reuse`,
  `delegatecall_self_context`.

**Effective scope (evidence, not intent):** it reliably recognizes a **manifest-visible `bytes[]`
`address(this).delegatecall` multicall executor** (the OZ / Uniswap-v3-periphery `Multicall` shape and direct
forks), and additionally the Size-style `balanceOf`-vs-`totalSupply` before/after invariant on such an executor.
It flags the **executor (opportunity)**, never the **mechanism (bug)**.

---

## 2. Proven Strengths (demonstrated by the campaign)

| Strength | Evidence |
|---|---|
| Deterministic detection of its target shape | 7/7 in-scope `bytes[]` self-delegatecall executors flagged (Size, Tokemak, Zaros, OZ, UniV3×3). |
| Zero high-confidence noise | Across 20 targets, **no `high` candidate was a clear false positive**; both FP targets emit only `needs_context`. |
| Correct silence under temptation | 9 TRUE NEGATIVE incl. **Recall** (8 batch-named + 9 delegatecall files → 0 candidates) and **Maia** `_multicall` (a real in-scope multicall router correctly suppressed as a thin external-`aggregate` delegator). |
| Explainable, reproducible | Pure classifier, config-driven terms, brace-matched bodies; every candidate carries `reason`+`invariant_terms`; outputs byte-stable. |
| Capability is real, not lucky | Fetched OZ (`medium`) and UniV3 (`high`) prove the canonical multicall is caught **whenever it is in scope**. |

---

## 3. Proven Weaknesses (demonstrated by the campaign)

| Weakness | Evidence |
|---|---|
| Single-architecture coverage | All 7 useful signals are the *same* shape; 7 of 8 enumerated multicall architectures are missed. |
| Flags opportunity, not mechanism | On permit/value/context targets (UniV3 selfpermit/swaprouter, OZ ERC2771) only the executor is flagged; the actual bug mechanism is never modeled. |
| Recall gated by manifest scope | Inherited multicalls (`lib/`) are invisible (Revert/Maia/Panoptic) — `build_coverage_manifest.py` does no inheritance resolution. |
| Structure- & vocabulary-bound | Misses batches expressed as internal Solidity calls, typed-struct dispatch, or cross-library indirection, and invariants expressed as mode/price/permit/value rather than supply/cap. |
| Two FP leaks | ERC1155 `balanceOfBatch` view getters and router fee-on-transfer swaps slip to `needs_context`. |

---

## 4. Per-Target Structured Records (20)

Behavior abbreviations: **exec-hit** = executor flagged; **mech-miss** = bug mechanism not modeled;
**silent** = 0 candidates. Confidence = analyst confidence in the root-cause attribution.

| # | Target | Architecture | Ground truth (multicall lens) | Detector behavior | Expected behavior | Root cause | Conf |
|--:|---|---|---|---|---|---|---|
| 1 | tokemak-2023-06 | bytes[] self-delegatecall (payable) | payable multicall msg.value-reuse hazard | `Multicall.multicall` delegatecall_self_context/high (+swapForQuote medium) | exec-hit | **Success:** in-scope self-delegatecall bytes[] | High |
| 2 | size-credit-2024-06 | bytes[] self-delegatecall | M-01 balanceOf-vs-totalSupply | both shapes high on `Multicall.multicall` | exec-hit + invariant | **Success:** before/after supply + self-delegatecall | High |
| 3 | revert-lend-2024-03 | inherited-lib multicall + typed-struct + permit | H-01 permit2 token≠asset via inherited Multicall | silent | exec-hit *if manifested*; mechanism out of scope | **Visibility** (B1) for executor; **Taxonomy** (B3) for permit | High |
| 4 | oz-multicall-erc2771 | inherited-lib multicall (manifested) + ERC2771 | CVE-2023-40014 context spoof | `Multicall.multicall` delegatecall_self_context/medium | exec-hit; ctx mechanism missed | **Taxonomy** (B5) — no context shape | High |
| 5 | univ3-periphery-multicall | bytes[] self-delegatecall (payable) | canonical inherited multicall (ref) | delegatecall_self_context/high | exec-hit | **Success** | High |
| 6 | univ3-periphery-selfpermit | payable multicall + permit | permit-through-batch reuse | exec-hit; `selfPermit*` not flagged | exec-hit; permit mechanism missed | **Taxonomy** (B3) | High |
| 7 | univ3-swaprouter | payable multicall router | msg.value reuse across batched swaps | exec-hit; `refundETH`/swaps not flagged | exec-hit; value mechanism missed | **Taxonomy** (B6) | High |
| 8 | beanstalk-2024-05 | diamond `farm` batch + ERC1155 getters | none multicall-awarded; real exec = `farm` | 2 FP (`balanceOfBatch`,`lastBalanceOfBatch` needs_context); `farm` silent | suppress getters; ideally see `farm` | **Implementation** (B8 view leak) + **Visibility/Taxonomy** (farm cross-lib delegatecall, name not gated) | High |
| 9 | noya-2024-04 | connector/router (batch fns oos) | none multicall-awarded | silent | silent | **Correct miss** (no in-scope exec) | High |
| 10 | maia-talos-2023-05 | external-aggregate router + inherited multicall | none multicall-awarded | silent (`_multicall` suppressed) | silent | **Correct** (thin-wrapper suppression working) | High |
| 11 | silo-finance-2025-03 | ERC4626 vault | none multicall-awarded | silent | silent | **Correct miss** | High |
| 12 | hybra-finance-2025-10 | ve(3,3) | none multicall-awarded | silent | silent | **Correct miss** | High |
| 13 | blackhole-2025-05 | router FoT swap loop | none multicall-awarded | 2 FP (RouterV2 FoT swaps needs_context) | suppress | **Implementation** (helper-resolution over-reach + slippage balanceOf) | High |
| 14 | zaros-2025-01 | bytes[] self-delegatecall + diamond upgrade | no confirmed multicall bug | `createTradingAccountAndMulticall` high (useful) + `RootUpgrade.upgrade` medium (FP) | exec-hit + suppress upgrade | **Success** (exec) + **Implementation** (diamond-cut FP) | High |
| 15 | quantamm-2024-12 | AMM math | none multicall-awarded | silent | silent | **Correct miss** | High |
| 16 | panoptic-2025-12 | UniV3 (inherited multicall) | none multicall-awarded | silent | silent | **Correct miss** (any multicall inherited → B1) | Med |
| 17 | ark-project-2024-07 | NFT bridge | none multicall-awarded | silent | silent | **Correct miss** | High |
| 18 | recall-2025-02 | facet storage/claim batches | none multicall-awarded | silent | silent | **Correct** (non-invariant batches suppressed) | High |
| 19 | swan-dria-2024-10 | marketplace | none multicall-awarded | silent | silent | **Correct miss** | High |
| 20 | ethos-reserve-2023-02 | internal-call batch liquidation | `batchLiquidateTroves` reuses `recoveryModeAtStart` once across the batch (in-class) | silent | should flag (in-class) | **Taxonomy** (B7) — internal-call loop + mode invariant, neither modeled | High |

---

## 5. Coverage Category Support Matrix (17 categories)

Legend: **S** supported (reliable) · **P** partial (executor only / conditional) · **U** unsupported.

| Category | Status | Evidence / why |
|---|:--:|---|
| manifest-visible bytes[] self-delegatecall | **S** | 7/7 (Size, Tokemak, Zaros, OZ, UniV3×3). The only reliable competency. |
| inherited-library multicall | **U→P** | U as-deployed (Revert/Maia/Panoptic, B1); **caught when the base is manifested** (OZ/UniV3) → a *visibility*, not capability, gap. |
| typed-struct batch execution | **U** | Revert `V3Utils.execute(Instructions)` dispatch produces no executor signal. |
| internal-call batch execution | **U** | Ethos `batchLiquidateTroves` loops via internal Solidity calls — not in `batch_executor_calls`. |
| router execution | **U / FP** | UniV3 swap fns unflagged; Blackhole router FoT swaps **mis-flagged**. 0 useful. |
| transformer execution | **U** | Revert `V3Vault.transform` single `transformer.call(data)` (no loop) → correctly not flagged but uncovered. |
| diamond/facet execution | **U / FP** | Beanstalk `farm` missed (cross-lib delegatecall, name not gated); Zaros `RootUpgrade` FP. |
| permit validation | **U** | No permit shape; UniV3 `selfPermit*` never flagged. |
| permit asset mismatch | **U** | Revert H-01 (permit token ≠ vault asset) structurally out of reach. |
| Permit2 flows | **U** | Revert `permit2.permitTransferFrom` not modeled (depends on the same permit concepts). |
| msg.value reuse | **P** | Payable multicall executor flagged (Tokemak, UniV3) but reuse never traced; `refundETH` unflagged. |
| ERC2771 context reuse | **P** | OZ executor flagged; `_msgSender`/`_msgData` corruption (CVE-2023-40014) not modeled. |
| arbitrary call execution | **U** | `transform`/router arbitrary-call surfaces not modeled. |
| snapshot/state reuse | **U** | Shape 3 (`same_tx_state_reuse`) exists but is unit-tested only; never fired on real source (needs an `isMulticall`-style flag absent in targets). |
| mode reuse | **U** | Ethos `recoveryModeAtStart`-reused-across-batch: invariant vocabulary has no mode/price concept. |
| approval reuse | **U** | Not modeled (allowance/approve not in invariant vocab as a reuse concept). |
| signature reuse | **U** | Not modeled (nonce is in `state_reuse_terms` but only via the unfired shape 3). |

**Census:** 1 S · 3 P · 13 U (one of which, inherited-library, is U→P pending a visibility fix).

---

## 6. Miss Taxonomy (A–E)

| Target / family | Class | Justification |
|---|---|---|
| Revert inherited multicall executor | **B Visibility** | The `multicall` body exists in-repo but in out-of-scope `lib/`; `build_coverage_manifest.py:73-144` enumerates per-file with **no inheritance resolution**, so it is never attributed to `V3Vault`. Fixable at the manifest layer. |
| Revert H-01 permit-asset-mismatch | **C Taxonomy** | Permit-token-identity is not a concept the two-signal gate can express. |
| oz-multicall-erc2771 (CVE) | **C Taxonomy** | No `_msgSender`/`_msgData` context-corruption concept. |
| univ3 selfpermit / swaprouter mechanism | **C Taxonomy** | No permit / msg.value-flow concept (executor correctly caught). |
| Ethos `batchLiquidateTroves` | **C Taxonomy** (+D) | In-class (per-call invariant reused across a batch) but needs internal-call-loop recognition (D, `batch_executor_calls` lacks internal calls) **and** a mode/price invariant concept (C). |
| Beanstalk `farm` | **B Visibility + C Taxonomy** | Cross-library `LibFunction` delegatecall beyond +1-level same-contract resolution (visibility/call-graph) and name 'farm' not gated (taxonomy/vocab). |
| typed-struct / transformer / router / arbitrary-call / approval / signature families | **A Correct miss** (mostly) | These were never in the detector's intended scope; their inclusion would require new reasoning, not a fix to the existing lens. |

**Distribution:** the *mechanism* misses (permit, msg.value, ERC2771, mode/internal-call) are overwhelmingly
**Taxonomy** misses — they require concepts the lens does not have. Exactly **one** clean **Visibility** miss
exists (B1 inherited multicall) and it is fixable without touching detector logic. This split is the crux of the
recommendation (§11).

---

## 7. False-Positive Taxonomy

| FP | Signal that fired | Why it fired | Useful? | Suppress? | Real attack surface? |
|---|---|---|---|---|---|
| Beanstalk `balanceOfBatch` / `lastBalanceOfBatch` | name-gate `batch` + invariant `balanceof`, shape `pre_post_supply_invariant`/needs_context | ERC1155 batch **view getters** loop over a mapping; the view suppression (`taxonomy.py:133`) only fires for *aggregates without invariant and without self-delegatecall*, so a `view` getter **with** a balanceof term leaks | No | **Yes** — add a visibility/`view`-aware suppression (ERC1155 `balanceOfBatch`/`safeBatchTransferFrom`) | No (read-only getters) |
| Blackhole `swap…SupportingFeeOnTransferTokens` ×2 | helper-resolved `_swap` external-call loop + `balanceOf(to)` before/after, shape `pre_post_supply_invariant`/needs_context | +1-level helper resolution pulls the `_swap` loop into the body; the FoT slippage check (`balanceOf(to)` delta ≥ `amountOutMin`) reads as a before/after invariant | No | **Yes** — exclude single-recipient slippage checks (`balanceOf(to)` not `address(this)`) | No (standard slippage guard) |

Both FPs are confined to the **non-routing `needs_context`** tier, so neither would have routed; but both are
genuine *precision leaks* worth closing **in a companion/suppression layer, not by loosening the core gate**.

---

## 8. Coverage Expansion Opportunities — Ranked Backlog

Score = **Impact × Precision-Retained × (1 / Effort)**, each on 1–5; higher = do sooner. "Precision-Retained"
is 5 when the change cannot add noise, 1 when it likely collapses precision. Every item states benefit **and**
cost; no item relies on answer-key knowledge or broad keyword matching.

| # | Title | Category | Impact | Prec-Ret | Effort | Score | Coverage Δ | Precision impact | Complexity | Risk |
|--:|---|---|:--:|:--:|:--:|:--:|---|---|---|:--:|
| 1 | **Manifest inheritance/library resolution for multicall bases** | inheritance/library expansion | 5 | 5 | 2 | **12.5** | inherited-library U→S (Revert/Maia/Panoptic + any OZ/UniV3 inheritor) | **None** — detector logic unchanged; it simply sees more in-scope executors | Resolve `is X, Base` → attribute base methods to deriver in the manifest, even from `lib/`, tagged `inherited` | **Low** |
| 2 | **ERC1155 batch-getter / `view` suppression** | invariant expansion (suppression) | 3 | 5 | 1 | **15** | closes Beanstalk FP | **Positive** (removes a leak) | add `view`-visibility + `balanceOfBatch`/`safeBatchTransferFrom` exclusion | **Low** |
| 3 | **Single-recipient slippage-check suppression** | router modeling (suppression) | 3 | 5 | 1 | **15** | closes Blackhole FP | **Positive** | suppress before/after on `balanceOf(<param>)` not `address(this)` | **Low** |
| 4 | **Companion: internal-call batch + reused mode/price invariant** | internal-call batch modeling + state-transition modeling | 4 | 3 | 4 | **3** | internal-call U→P (Ethos class) | Moderate cost — internal-call loops are common; needs a *reused-snapshot-across-iterations* signal to stay tight | new detector; data-flow of a pre-loop snapshot used inside/after the loop | **Med** |
| 5 | **Companion: permit-asset-validation / Permit2** | permit modeling + signature modeling | 5 | 3 | 4 | **3.75** | permit-validation/asset-mismatch/Permit2 U→P (Revert H-01 class) | Moderate — must tie a permit/permit2 transfer to an asset-identity check; risk of flagging every permit | new detector; match `permit*`/`permitTransferFrom` + absence of token==asset assertion | **Med** |
| 6 | **Executor call-graph (multi-level helper / cross-library delegatecall)** | executor graphing + call graph analysis | 4 | 3 | 5 | **2.4** | recovers Beanstalk `farm`; strengthens #4 | Moderate — deeper resolution can over-attribute; needs depth cap + dedup | build a per-contract call graph; resolve delegatecall through `LibFunction`-style libraries | **Med-High** |
| 7 | **Companion: msg.value reuse in payable batch** | msg.value modeling | 4 | 2 | 4 | **2** | msg.value P→S (Tokemak/UniV3) | Higher cost — `payable` + loop is common; must prove per-iteration `msg.value` read | new detector; `payable` executor + `msg.value`/`address(this).balance` used inside loop | **High** |
| 8 | **Companion: ERC2771 context reuse** | ERC2771 modeling | 3 | 3 | 3 | **3** | ERC2771 P→S (OZ CVE class) | Moderate — narrow trigger (inherits both `Multicall` + `ERC2771Context`) keeps it tight | new detector; detect co-inheritance + `_msgSender/_msgData` in delegatecalled path | **Med** |
| 9 | **Typed-struct dispatch executor recognition** | typed-struct modeling | 3 | 2 | 4 | **1.5** | typed-struct U→P (Revert `execute(Instructions)`) | Higher cost — struct-dispatch heuristics are fuzzy; risk of flagging any enum switch | recognize `enum whatToDo` + branchy dispatch over a struct array | **High** |
| 10 | **Transformer / arbitrary-call execution** | transformer modeling | 3 | 2 | 4 | **1.5** | transformer/arbitrary-call U→P | Higher cost — single `.call(data)` to whitelisted target is everywhere; needs trust-boundary context | new detector; `target.call(data)` where target is caller-influenced | **High** |
| 11 | **Approval/signature reuse across batch** | signature modeling | 3 | 2 | 4 | **1.5** | approval/signature reuse U→P | Higher cost — overlaps permit companion; nonce/allowance reuse is subtle | extend #5 with allowance/nonce reuse-across-iterations | **High** |

**Reading the ranks:** the only items that are *both* high-value and precision-safe are **#1 (manifest
inheritance)** and the two **FP-suppression** items (#2, #3). Everything that adds *mechanism* coverage (#4–#11)
costs precision in-core and therefore scores low — which is the signal to build them as **separate companion
detectors** rather than expand the core lens.

---

## 9. Precision Risks (how future changes could damage performance)

1. **Broadening the invariant vocabulary** (adding mode/price/permit/value/approval terms to `accounting_terms`)
   would fire on nearly every loop that reads a balance or a config flag → mass `needs_context` noise. *Guardrail:*
   never widen the core vocab; put new invariants in companions with their own two-signal gates.
2. **Admitting internal Solidity calls as a batch-executor signal** would flag every liquidation loop, reward
   loop, and router swap. *Guardrail:* require a *reused pre-loop snapshot* (state-transition signal), not just a
   loop.
3. **Deeper / cross-library helper resolution** (call-graph) can over-attribute bodies and inflate candidates.
   *Guardrail:* depth cap, dedup by `lens_id`, and attribute only delegatecall/`bytes[]` executors.
4. **Typed-struct / transformer heuristics** are inherently fuzzy (enum switches, `target.call(data)` are
   ubiquitous) → low precision-retained. *Guardrail:* keep experimental, require a trust-boundary signal, never
   route.
5. **Treating an executor flag as a finding** (routing the current `delegatecall_self_context/high`). The detector
   fires high on *benign* OZ/UniV3 multicalls; routing it would surface opportunity, not bugs. *Guardrail:* keep
   `research_only`; only a *mechanism* companion (permit/value/ERC2771/mode) should ever be considered for routing.

---

## 10. Evolution Roadmap

### Low Risk / High Reward (precision-neutral or precision-positive)
- **#1 Manifest inheritance/library resolution (B1).** Surface inherited `Multicall` bases into the manifest as
  methods of in-scope derivers. Converts the inherited-library category U→S with **zero detector-logic change**.
- **#2, #3 FP suppressions.** Close the ERC1155 view-getter and router-slippage leaks (in a suppression/companion
  layer, not by touching the core gate).

### Medium Risk / Medium Reward (new companion detectors, narrow triggers)
- **#4 Internal-call batch + reused mode/price invariant** (Ethos class) — keyed on a pre-loop snapshot reused
  across iterations.
- **#5 Permit-asset-validation / Permit2** (Revert H-01 class) — keyed on a permit transfer lacking a
  token==asset assertion.
- **#8 ERC2771 context reuse** (OZ CVE class) — keyed on co-inheritance of `Multicall` + `ERC2771Context`.

### High Risk / Experimental (research-only, never routed)
- **#6 Executor call-graph** (cross-library delegatecall, e.g. Beanstalk `farm`).
- **#7 msg.value reuse**, **#9 typed-struct dispatch**, **#10 transformer/arbitrary-call**, **#11 approval/
  signature reuse** — fuzzy triggers; build only with explicit precision guardrails and FP autopsies.

---

## 11. Recommendation

# Freeze Current Detector + Create Companion Detectors

**Why (decision framework, from the evidence):**
- *"If most misses require fundamentally different reasoning → Create Companion Detectors."* The mechanism misses
  (permit, Permit2, msg.value, ERC2771, internal-call+mode) are **Taxonomy** misses — concepts the current lens
  cannot express. Each needs its own signal model. ✔
- *"If precision would likely collapse under expansion → Freeze Current Detector + Create Companion Detectors."*
  Adding those mechanisms in-core means loosening the executor signal and the invariant vocabulary, which
  re-admits the exact noise the two-signal gate currently suppresses (every liquidation/router loop, every
  permit). ✔
- *"If most misses are visibility misses → Expand Scope Conservatively."* Only **one** clean visibility miss
  exists (B1 inherited multicall) — and it is fixable at the **manifest layer**, not by expanding the detector.

**Therefore:** freeze the core `multicall_invariant` detector at its proven narrow scope (it is *clean and
correct*, not broken), and grow coverage through **separate, narrowly-triggered companion detectors** — each
research-only, each with its own two-signal gate and FP autopsies. The **single conservative expansion** is the
**B1 manifest inheritance/library visibility fix**, which lives in the manifest builder and changes no detector
logic, so it carries no precision cost. Do **not** route the core detector (it flags opportunity, not bugs).

---

## 12. Final Output

### 1. Executive Summary
Across 20 targets the detector proved a **clean, precise, single-architecture** recall lens: 7/7 detection of
manifest-visible `bytes[]` self-delegatecall multicalls with **zero high-confidence noise** and correct silence
on 9 non-batch / non-invariant codebases. Its limits are structural: it is gated by manifest scope (inherited
multicalls invisible) and by a narrow invariant vocabulary (misses internal-call/typed-struct batches and
permit/msg.value/ERC2771/mode mechanisms). Exactly one gap is a *visibility* miss fixable without touching the
detector (B1); the rest are *taxonomy* misses that need fundamentally different reasoning. Expanding the core
lens to cover them would collapse its precision. **Freeze the core, fix B1 at the manifest layer, and add
narrow companion detectors for the mechanism families.**

### 2. Top 10 Improvement Opportunities (by score)
1. Manifest inheritance/library resolution (B1) — precision-neutral, highest reward.
2. ERC1155 batch-getter / `view` suppression — closes Beanstalk FP.
3. Single-recipient slippage-check suppression — closes Blackhole FP.
4. Companion: permit-asset-validation / Permit2 (Revert H-01 class).
5. Companion: internal-call batch + reused mode/price invariant (Ethos class).
6. Companion: ERC2771 context reuse (OZ CVE class).
7. Executor call-graph (cross-library delegatecall; recovers Beanstalk `farm`).
8. Companion: msg.value reuse in payable batch (Tokemak/UniV3 class).
9. Typed-struct dispatch executor recognition (Revert `execute` class).
10. Transformer / arbitrary-call execution modeling.

### 3. Top 5 Precision Risks
1. Widening the core invariant vocabulary → mass `needs_context` noise.
2. Admitting internal Solidity calls as an executor signal → every liquidation/reward loop fires.
3. Deeper/cross-library helper resolution → over-attribution / candidate inflation.
4. Fuzzy typed-struct & arbitrary-`.call` heuristics → low precision-retained.
5. Routing an executor-only flag → opportunity, not bugs (benign OZ/UniV3 multicalls flagged high).

### 4. Recommended Roadmap
**Now (Low-risk):** B1 manifest inheritance fix + the two FP suppressions. **Next (Medium-risk):** permit-asset
& internal-call/mode companions, then ERC2771. **Later (Experimental, research-only):** executor call-graph,
msg.value, typed-struct, transformer, approval/signature companions.

### 5. Estimated Coverage Gains
- **B1 alone:** inherited-library U→S — converts the executor side of Revert/Maia/Panoptic and *any* OZ/UniV3
  inheritor to detectable; no precision cost.
- **+ FP suppressions:** 2 FP targets → 0 (eval FP rate on this set drops to 0).
- **+ Medium companions:** adds executor-or-mechanism coverage for permit/Permit2, internal-call+mode, ERC2771 —
  i.e. 3 of the currently-U categories move to P/S, each behind its own gate.
- **Net trajectory:** from **1 S / 3 P / 13 U** today toward **~3 S / ~6 P** without loosening the core gate.

### 6. Recommended Next Experiment
**B1 manifest-inheritance probe (pure validation, no logic change).** Re-run the *unchanged* detector on
Revert/Maia/Panoptic after surfacing their inherited `Multicall` base into the manifest (a manifest-layer
experiment in an isolated workspace). **Expected:** MISS → executor-hit (`delegatecall_self_context/high`),
**precision-neutral**, confirming B1 is a visibility artifact and quantifying the conversion before any code is
written. This validates the highest-leverage, lowest-risk item first and informs whether the manifest fix is
worth productizing — all while honoring "no detector changes."
