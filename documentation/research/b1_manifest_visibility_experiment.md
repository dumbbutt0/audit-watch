# B1 Manifest-Inheritance Visibility Experiment

**Type:** validation experiment. The detector was run **unchanged**. No detector / taxonomy / pattern /
threshold / routing / gate / answer-key / real-manifest / `build_coverage_manifest.py` change was made. Flags
preserved: `is_gate:false` / `research_only:true` / `routes_in_production:false`. A HIT was not a success
criterion — the success criterion was to *test the hypothesis with the detector unchanged and isolate the
visibility effect.*

**Artifacts (all isolated, clearly experimental):**
- Synthetic manifests: `documentation/research/_b1_experiment/{revert,panoptic,maia}_synthetic_manifest.json`
  (each marked `"_experimental": true`)
- Fetched solady source (Maia base, not vendored in-repo): `…/_b1_experiment/_src/solady_Multicallable.sol`
- Detector outputs: `…/_b1_experiment/_runs/<slug>/output/multicall_invariant_audit.json`
- Reused runner: `documentation/evals/multicall_overnight_targets/_harness.py` (isolated `get_audit_root`)
- Controls (no rerun): `documentation/evals/multicall_overnight_targets/_runs/{oz-multicall-erc2771,univ3-*}`

---

## Executive Summary

The hypothesis — *"B1 (inherited-library multicall misses) is a manifest-visibility problem, not a detector
capability gap"* — is **largely but not fully** supported. When the inherited multicall executor is attributed
to the derived in-scope contract, the **unchanged** detector flags it for **2 of 3** targets, identically to how
it already flags manifest-visible multicalls, **with zero new false positives**:

- **Revert Lend** → MISS converts to **2 executor-hits** (`V3Vault`, `AutoCompound`), `delegatecall_self_context/medium`.
- **Panoptic** → MISS converts to **3 executor-hits** (`PanopticPool`, `SemiFungiblePositionManager`,
  `PanopticFactory`), `delegatecall_self_context/high`.
- **Maia (UniswapV3Staker)** → **still 0 candidates.** Its inherited multicall is solady `Multicallable`, an
  **assembly** implementation (`delegatecall(gas(), address(), …)` inside an assembly `for {} 1 {}`). The
  detector's self-delegate signal requires the literal token `address(this)` and its loop signal requires a
  parenthesised `for(`/`while(` — neither is present in assembly — so the executor is **suppressed even when
  fully visible**.

⇒ For **Solidity-level** delegatecall multicalls (OZ, Panoptic's own base, and the OZ/UniV3 controls), B1 is a
pure **visibility** problem fixable at the manifest layer with no detector change. For **assembly-level**
multicalls (solady), visibility is necessary but **not sufficient** — an additional implementation/representation
limitation exists. Verdict: **B1 PARTIALLY VISIBILITY ISSUE.**

---

## Hypothesis

> If inherited base-class methods are surfaced into the manifest and attributed to the derived in-scope
> contract, the existing detector identifies the same multicall executors it already detects elsewhere — i.e.
> the observed inherited-library misses are caused by manifest construction, not by detector capability.

- **Support →** "B1 is a manifest-visibility problem."
- **Refute →** "B1 is partially a detector-capability problem."

---

## Experimental Design

1. **Baseline review** (no rerun) — record each target's existing classification and executor visibility.
2. **Inheritance mapping** — for each in-scope contract, trace Contract → Base → multicall source → executor,
   and whether the executor is direct / inherited / generated.
3. **Synthetic manifest** — build an *isolated* manifest per target whose items attribute the inherited multicall
   executor to the derived in-scope contract, with `file`/`source_span` pointing at the real base body (fetched
   only where the dependency was not vendored, i.e. solady for Maia). Real manifests untouched.
4. **Detector validation** — run the unchanged detector against each synthetic manifest (isolated output).
5. **Precision impact** — baseline candidates for these targets = 0, so every new candidate is the delta;
   classify each; cross-check against the full-base controls.
6. **Hypothesis evaluation** — answer the five research questions; assign one verdict.

**Why this isolates the visibility variable:** the *only* thing that changes between baseline and treatment is
whether the inherited executor appears in the manifest. The detector binary, taxonomy, patterns, thresholds, and
all other manifest entries are identical. Any change in output is therefore attributable to visibility alone.

---

## Baseline Results (from the 20-target campaign; not rerun)

| Target | In-scope contract(s) inheriting multicall | Baseline manifest coverage of the executor | Prior detector output | Prior classification |
|---|---|---|---|---|
| Revert Lend | `V3Vault`, `AutoCompound` | **Absent** — multicall inherited from `lib/openzeppelin-contracts/.../Multicall.sol` (out of scope) | 0 candidates | **MISS** |
| Maia | `UniswapV3Staker` | **Absent** — multicall inherited from `solady/utils/Multicallable.sol` (dependency, out of scope; not vendored) | 0 candidates | **MISS** (recorded TRUE NEGATIVE — no awarded multicall bug) |
| Panoptic | `PanopticPool`, `SemiFungiblePositionManager`, `PanopticFactory` | **Absent** — multicall inherited from `contracts/base/Multicall.sol` (not in the in-scope set) | 0 candidates | **TRUE NEGATIVE** (no awarded multicall bug) |
| OZ Multicall (control) | `Multicall` (the base, manifested directly) | **Present** | `Multicall.multicall` delegatecall_self_context/**medium** | ADJACENT |
| UniV3 Multicall (control) | `Multicall` (the base, manifested directly) | **Present** | `Multicall.multicall` delegatecall_self_context/**high** | HIT |

The controls already demonstrate the detector fires on the canonical OZ/UniV3 multicall **when the base is
itself manifested** — establishing capability for the Solidity-level form before this experiment.

---

## Inheritance Mapping

| In-scope contract | → Base contract | → Multicall source | → Executor fn | Executor origin | Delegatecall form |
|---|---|---|---|---|---|
| `V3Vault` (`V3Vault.sol:30`) | `Multicall` | `lib/openzeppelin-contracts/contracts/utils/Multicall.sol:17` | `multicall(bytes[])` | **inherited (lib)** | `Address.functionDelegateCall(address(this), data[i])` in `for( )` |
| `AutoCompound` (`AutoCompound.sol:16`) | `Multicall` | same OZ file | `multicall(bytes[])` | **inherited (lib)** | same |
| `PanopticPool` (`PanopticPool.sol:28`) | `Multicall` | `contracts/base/Multicall.sol:12` | `multicall(bytes[]) payable` | **inherited (in-repo base)** | `address(this).delegatecall(data[i])` in `for( )` |
| `SemiFungiblePositionManager` (`…:75`) | `Multicall` | same Panoptic base | `multicall(bytes[]) payable` | **inherited** | same |
| `PanopticFactory` (`…:25`) | `Multicall` | same Panoptic base | `multicall(bytes[]) payable` | **inherited** | same |
| `UniswapV3Staker` (`UniswapV3Staker.sol:26`) | `Multicallable` | `solady/utils/Multicallable.sol:28` (fetched) | `multicall(bytes[]) payable` → `_multicall` | **inherited (dependency, not vendored)** | **assembly** `delegatecall(gas(), address(), …)` in assembly `for {} 1 {}` |

Every executor is **inherited**, not direct — none is generated. The mapping reveals the decisive variable:
**delegatecall form** (Solidity-level `address(this)` + parenthesised loop vs. assembly `address()` + assembly
loop), not the inheritance per se.

---

## Synthetic Visibility Results (detector unchanged)

| Target | Synthetic items (attributed executors) | Candidates | Shape / confidence |
|---|---|---:|---|
| Revert | `V3Vault.multicall`, `AutoCompound.multicall` (OZ body) | **2** | `delegatecall_self_context` / **medium** ×2 |
| Panoptic | `PanopticPool.multicall`, `SemiFungiblePositionManager.multicall`, `PanopticFactory.multicall` (own payable base) | **3** | `delegatecall_self_context` / **high** ×3 |
| Maia | `UniswapV3Staker.multicall` + `_multicall` (solady assembly, generous resolution) | **0** | — (suppressed) |

All outputs carry `is_gate:false` / `research_only:true` / `routes_in_production:false` / `routed_manifest_ids:[]`.

**Why Maia stays at 0** (traced through `multicall_invariant_taxonomy.py`): the resolved body has the
name-gate hit (`multicall`) but (a) `self_delegate` is false — it needs the literal `address(this)`, while solady
uses `address()` in assembly; (b) `has_loop` is false — `_LOOP_RE` matches `for(`/`while(`, but the solady loop
is assembly `for {} 1 {}`; (c) no invariant terms. With `not has_invariant and not self_delegate`, the
thin-wrapper suppression returns no candidate. Confidence in this attribution: **high** (mechanically traced).

**Why Revert is medium not high:** OZ multicall is `external` (not payable), no msg.sender/invariant terms ⇒
`ctx` is false ⇒ `delegatecall_self_context` lands at medium (matches the OZ control exactly). **Panoptic is
high** because its base is `payable` ⇒ `ctx` true.

---

## Detector Output Comparison (before → after)

| Target | Before | After (synthetic visibility) | Δ | Converted? |
|---|---|---|---|---|
| Revert Lend | 0 candidates (MISS) | 2 × delegatecall_self_context/medium | +2 executor-hits | **Yes** |
| Panoptic | 0 candidates (TN) | 3 × delegatecall_self_context/high | +3 executor-hits | **Yes** |
| Maia | 0 candidates (MISS) | 0 candidates | 0 | **No** (assembly) |

Matches the controls: the OZ medium and UniV3 high baselines are reproduced by the now-visible Revert (medium)
and Panoptic (high) executors — i.e. visibility alone reproduces the known capability for the Solidity-level form.

---

## Precision Impact Analysis

| New candidate | Useful / weak / noisy | Real attack surface? | Note |
|---|---|---|---|
| `V3Vault.multicall`, `AutoCompound.multicall` | useful (executor lead) | the executor *surface* is real (H-01's permit bug is reached through it); the *flag itself* is opportunity, not the bug | medium, non-routing-adjacent |
| `PanopticPool/SFPM/PanopticFactory.multicall` | weak (benign multicall) | no known Panoptic multicall bug | **caveat**: high-confidence flag on a benign, audited multicall |
| (Maia) | — | — | nothing emitted |

- **New false positives from the mechanism: 0.** Each attributed executor produced exactly one candidate (the
  executor) and no spurious sibling candidates.
- **Full-base precision is corroborated by the controls:** the OZ synthetic manifest (6 items incl. ERC2771
  constructor/`_msgSender`), univ3-selfpermit (9 items incl. `selfPermit*`/payments), and univ3-swaprouter (19
  items incl. swaps/permit/`refundETH`) each produced **exactly one** candidate — the multicall — so attributing
  whole inherited bases does **not** add noise.
- **Precision delta: ~0 on false positives.** The real precision cost of a manifest-expansion is *volume*, not
  *noise*: surfacing inherited multicalls means every protocol with an inherited multicall (e.g. Panoptic) gets a
  high executor flag, most of which are benign. This is an *operational/routing* concern, not a detector-quality
  regression — and it reinforces the standing "do not route the executor-only flag" guidance.

---

## Coverage Impact Analysis

- **Executors recovered:** 5 (Revert ×2, Panoptic ×3) of 6 attributed across the 3 targets; 0 for Maia.
- **Category movement:** *inherited-library multicall (Solidity-level)* moves from Unsupported → **Supported**
  (visibility fix, detector unchanged). *inherited-library multicall (assembly, e.g. solady)* remains
  **Unsupported** pending an implementation change.
- **Mechanism coverage unchanged:** Revert's headline H-01 is a *permit-asset-mismatch* bug; this experiment
  surfaces the multicall *executor* through which it is reached, but the detector still does not model the permit
  mechanism (that remains a separate taxonomy gap / companion-detector item). Surfacing the executor is necessary
  but not sufficient to *find the bug*.

---

## Threats to Validity

1. **Synthetic ≠ real builder.** These manifests were hand-authored to *represent* inheritance resolution; a real
   `build_coverage_manifest.py` change could differ (e.g. which base wins on multi-inheritance, dedup of a single
   inherited method across many derivers). Mitigation: attribution mirrors the actual `is …, Base` declarations
   and points at the real base bodies; the detector logic exercised is identical.
2. **Import-path assumption.** Revert was attributed to OZ `utils/Multicall.sol` based on `V3Vault.sol:18`'s
   explicit `@openzeppelin/contracts/utils/Multicall.sol` import (verified); other inheritors were assumed to use
   the same base.
3. **solady version drift.** solady was fetched at HEAD, not the exact 2023-05 pin; the multicall *structure*
   (assembly delegatecall) is stable across versions, so the qualitative result (suppressed) is robust, but the
   exact line spans are from the fetched copy.
4. **Executor-flag ≠ bug.** "Converted" means the *executor* is now flagged; it does not mean a vulnerability was
   found (most flagged multicalls are benign). The experiment validates *visibility*, not *finding power*.
5. **Small N** (3 targets + 2 controls). Sufficient to demonstrate the mechanism and the assembly exception, not
   to estimate population rates of Solidity-vs-assembly multicalls.

---

## Conclusion

Surfacing inherited multicall executors into the manifest converted prior misses into executor-hits for **2 of 3**
targets **with the detector unchanged and zero new false positives**, exactly reproducing the OZ/UniV3 control
behavior. This proves the inherited-library blind spot is, for **Solidity-level** delegatecall multicalls, a
**manifest-visibility** artifact — the detector already possesses the required capability. The **Maia / solady
assembly** case shows visibility is **not sufficient** there: the detector's structural signals (`address(this)`,
parenthesised loop) do not recognize assembly-implemented multicalls, so that sub-case is an
implementation/representation limitation independent of visibility.

Answers to the research questions:
1. **Did inherited visibility convert prior misses into hits?** Yes for Revert and Panoptic; no for Maia.
2. **Which targets changed classification?** Revert (MISS → executor-hit), Panoptic (TN → executor-hit/high);
   Maia unchanged.
3. **Precision regressions?** No new false positives; the only cost is increased *volume* of (benign) executor
   flags — a routing concern, not a quality regression.
4. **Does the detector already possess the capability?** Yes for Solidity-level delegatecall multicalls; no for
   assembly multicalls.
5. **Is B1 primarily visibility / taxonomy / implementation / mixed?** **Mixed, dominated by visibility** —
   visibility for the common Solidity-level form, implementation for the assembly form.

---

## Recommendation

# B1 PARTIALLY VISIBILITY ISSUE

The dominant cause is visibility (resolved with no detector change for OZ/UniV3/Panoptic-style multicalls), but
the solady/assembly case is a genuine implementation limit, so the honest verdict is *partial* rather than full
confirmation.

**Future work — handle as a manifest-layer project, not a detector change.** Because the conversions were
achieved with the detector **untouched**, inheritance-resolution belongs in the manifest builder
(`build_coverage_manifest.py`), evaluated as a **separate manifest-layer project**: resolve `is …, Base` and
attribute inherited executor methods to derived in-scope contracts (tagging them `inherited`). That project
should be scoped with two guardrails surfaced here: (a) **volume control** — surfacing inherited multicalls will
flag many benign executors, so the executor-only flag must stay research-only / non-routing; and (b) the
**assembly-multicall gap** (solady and similar) is out of scope for a pure manifest fix and would require a
separate detector-implementation effort (recognize assembly `delegatecall(…, address(), …)` / assembly loops) —
tracked independently, not bundled into the visibility work.

---

## Final Output

### 1. Executive summary
Attributing inherited multicall executors to derived in-scope contracts converted prior misses into executor-hits
for Revert (2×medium) and Panoptic (3×high) with the **detector unchanged and 0 new false positives**, matching
the OZ/UniV3 controls — confirming the inherited-library blind spot is a manifest-visibility artifact **for
Solidity-level delegatecall multicalls**. Maia's solady **assembly** multicall stayed suppressed, exposing an
implementation limit visibility cannot fix. Verdict: **B1 PARTIALLY VISIBILITY ISSUE.**

### 2. Before/after comparison table
| Target | Before | After | Δ candidates | Converted |
|---|---|---|---:|---|
| Revert Lend | 0 (MISS) | 2 × delegatecall_self_context/medium | +2 | Yes |
| Panoptic | 0 (TN) | 3 × delegatecall_self_context/high | +3 | Yes |
| Maia | 0 (MISS) | 0 | 0 | No (assembly) |

### 3. Coverage delta
+5 executor candidates (2 of 3 targets); category *inherited-library multicall (Solidity-level)*
Unsupported → Supported; *(assembly)* remains Unsupported.

### 4. Precision delta
**0 new false positives.** Controls confirm whole-base attribution yields exactly one candidate each. Residual
cost is *volume* of benign executor flags (routing concern), not noise.

### 5. Hypothesis verdict
**B1 PARTIALLY VISIBILITY ISSUE** — visibility-dominated (capability already present for the common form), with a
distinct assembly-multicall implementation gap.

### 6. Recommendation for future work
Pursue inheritance-resolution as a **separate manifest-layer project** in `build_coverage_manifest.py` (attribute
inherited executors to derivers), keeping the executor-only flag **research-only / non-routing** for volume
control; track the **assembly-multicall recognition** gap as an independent detector-implementation item, not part
of the visibility fix. No change to the current `multicall_invariant` detector is warranted by this experiment.
