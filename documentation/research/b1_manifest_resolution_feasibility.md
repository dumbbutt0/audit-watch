# B1 Manifest-Inheritance Resolution — Feasibility & Design Study

**Type:** architecture research only. **No code, manifest, manifest builder, detector, routing, gate, answer-key,
or evaluation artifact was modified. No prototype was built.** Flags remain `is_gate:false` / `research_only:true`
/ `routes_in_production:false`. This study estimates risk and design *before* any implementation, and keeps the
visibility question strictly separate from detector-logic changes.

**Inputs read (read-only):** `scripts/build_coverage_manifest.py` (full), `scripts/multicall_invariant_taxonomy.py`,
`documentation/research/b1_manifest_visibility_experiment.md`, `…/multicall_detector_evolution.md`, the 20-target
scorecard, and the B1 experiment outputs under `documentation/research/_b1_experiment/`.

---

## 1. Executive Summary

Inherited-executor attribution at the manifest layer is **feasible and precision-safe in a minimal, multicall-only,
isolated form**, and **high-risk in a global form**. The B1 experiment already proved the detector needs *only*
visibility (it converts Solidity-level inherited multicalls with zero new false positives, detector unchanged).
The dominant engineering risk is **not** detector precision — it is **polluting the canonical
`coverage_manifest.json`**, which the production Step 3.9 coverage-completeness gate and every specialist lens
consume. The recommendation is therefore **IMPLEMENT MULTICALL-ONLY ATTRIBUTION**, delivered as a **read-only
sidecar** that research detectors merge at read-time and that is **never written into the canonical manifest** —
isolating the visibility gain from routing, gating, and evaluation reproducibility. A full inheritance graph
(attribute all base methods globally) is rejected: it explodes the manifest, destabilizes the coverage gate, and
buys no measured precision.

---

## 2. Current Manifest Behavior

From `scripts/build_coverage_manifest.py` (read-only):

- **Per-file regex enumeration.** `main()` (`:336-402`) walks each `.sol` file, runs `FUNC_RE`/`CTOR_RE` line by
  line, and brace-matches bodies (`_signature_block :156-188`). There is **no AST, no import graph, no inheritance
  resolution.**
- **Contract attribution is textual/positional.** `TYPE_DECL` (`:61`) matches `contract|interface|library|abstract
  contract <Name>` and captures **only the name** — it does **not** capture the `is Base1, Base2, …` clause. A
  function is attributed to `contract_at[idx]` (`:346-356`, `:366`), i.e. the most recent contract declaration
  **in the same file** preceding the function line.
- **Scope is per-file.** `_in_scope` (`:127-144`) uses `scope.txt`/`out_of_scope.txt` allow/deny if present, else
  `DEFAULT_EXCLUDE_GLOBS`; `lib/` is excluded and pure interfaces are dropped.
- **Deterministic IDs.** `_short_id` (`:67-70`) = `sha256(kind:contract:name:file:line)[:8]`, with `~k`
  de-collision in `add()` (`:277-283`). Manifest records `git_commit` + scope counts for reproducibility.
- **Function-derived enrichment.** `add()` (`:275-334`) computes tags, `attack_surface_score`, and
  `external_calls`/`in_tainted_sink`/`has_loop` from name+signature+`static.json` — so a synthesized item must
  carry a real signature/body to be scored sensibly.

**Why inherited methods are absent.** The inherited `multicall` lives in a *base* file (e.g.
`lib/openzeppelin-contracts/contracts/utils/Multicall.sol`), which is (a) a different file from the deriving
contract and (b) typically out of scope (`lib/`). With no inheritance graph, the builder never attributes the
base method to the deriving in-scope contract. This is the exact mechanical cause of B1 (confirmed by the
experiment: surfacing the same body under the deriver makes the unchanged detector fire).

**Cross-cutting consumer.** `coverage_manifest.json` is **not** private to this research detector. It is the
denominator for the **Step 3.9 coverage-completeness gate** (which HARD-BLOCKS the review gate until every
in-scope item is dispositioned) and the input for **all Step-2 specialists and recall lenses**. Any change to its
contents propagates pipeline-wide. This single fact dominates the design.

---

## 3. Inheritance Attribution Designs (A–E)

| | Approach | Complexity | Coverage gain | Precision impact | Maintenance | Performance |
|---|---|---|---|---|---|---|
| **A** | **Direct inheritance resolution** — parse `is …`, resolve every base (incl. lib), attribute **all** base methods to derivers | High | High (all inherited surface) | **Negative** at manifest scale (ERC20/Ownable/… everywhere) | High (remappings, multi-base) | Med-High |
| **B** | **Selective inherited-method attribution** — resolve bases, attribute a **curated executor family** (multicall / batch / aggregate / multiDelegatecall) | Medium | Med-High (executor families) | Neutral (executor-shaped only) | Medium | Low-Med |
| **C** | **Multicall-only inherited attribution** — resolve only **multicall-shaped** base executors from a known-base allowlist | **Low-Med** | Medium (the demonstrated need) | **Neutral (0 new FP measured)** | **Low** | **Low** |
| **D** | **General inherited-method graph** — full import+remapping graph, all methods, all contracts | High | Highest (and mostly noise) | **Strongly negative** (manifest explosion, gate denominator blow-up) | **High** | High |
| **E** | **Hybrid** — ship **C** now as an isolated sidecar; keep a documented path to **B**; optional flagged merge into canonical only after gate-impact study | Low-Med | Medium→High over time | Neutral (sidecar isolation) | Low | Low |

A and D operate on the *whole* inherited surface and therefore collide head-on with the coverage-gate denominator;
B and C are scoped to executors (the only thing the detector reasons about). C is the minimal subset of B matching
the **only** demonstrated need.

---

## 4. Coverage Impact

Using the B1 experiment + 20-target evidence (executor = the multicall function; "solved" = becomes detectable
with the **unchanged** detector):

| Target | Inherited multicall? | Form | Effect of C (multicall-only attribution) | Classification |
|---|---|---|---|---|
| Revert Lend | yes (OZ `Multicall`, out-of-scope lib) | Solidity `address(this)` + `for(` | V3Vault + AutoCompound → 2 × `delegatecall_self_context/medium` | **Solved** |
| Panoptic | yes (in-repo `base/Multicall`, not in in-scope set) | Solidity `address(this)` payable + `for(` | PanopticPool + SFPM + PanopticFactory → 3 × `…/high` | **Solved** |
| Maia | yes (solady `Multicallable`) | **assembly** `delegatecall(gas(), address(), …)` | attribution succeeds, but detector still suppresses (no `address(this)`, no paren-loop) | **Partially solved** (visible, not detectable — needs the separate assembly-recognition item) |
| Tokemak | no — `utils/Multicall.sol` is in-scope already | Solidity | already a HIT without attribution | **Unaffected** |
| OZ Multicall (control) | n/a — the base, manifested directly | Solidity | already fires (medium) | **Unaffected** |
| UniV3 Multicall (control) | n/a — the base, manifested directly | Solidity | already fires (high) | **Unaffected** |

**Net:** C converts the inherited-Solidity-level cases (Revert, Panoptic, and by extension any OZ/UniV3 inheritor);
it does not regress the already-covered cases and does not (by itself) solve assembly multicalls.

---

## 5. Precision Impact

- **False positives: ~0.** The B1 run produced exactly one candidate per attributed executor and no spurious
  siblings; the whole-base controls (OZ 6 items→1 candidate, selfpermit 9→1, swaprouter 19→1) show that even
  attributing an *entire* inherited base yields only the multicall. Attribution does not create new noise.
- **Candidate-volume growth: ≈ 1 per inheriting in-scope contract.** This is the true cost. Multicall is widely
  inherited; surfacing it means most protocols gain one (usually benign) `delegatecall_self_context` flag. On the
  3 experiment targets that was +5 candidates; pipeline-wide it scales with the count of contracts inheriting a
  known multicall base.
- **Routing impact:** because these flags are mostly benign executors (the detector flags *opportunity*, not a
  bug), the executor-only candidate **must remain non-routing**. C does not change that; it only widens what the
  research lens can *see*.
- **Would inherited visibility surface substantially more benign executors?** **Yes — by design, and that is
  acceptable for a research lens but unacceptable for a gate.** This is the core reason to keep attribution in an
  isolated sidecar and the executor flag research-only.

---

## 6. Failure Modes

| Failure mode | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Duplicate manifest entries (same base method via multiple paths / re-runs) | Med | Inflated denominator, double candidates | Deterministic IDs keyed on (deriver, base file, line); dedup set; one entry per (deriver, executor) |
| Inherited-noise explosion (attributing whole bases) | High under A/D, **Low under C** | Coverage-gate denominator blow-up; lens noise | Restrict to multicall-shaped executors from an allowlist (C); never attribute non-executor methods |
| Library mis-attribution (wrong base resolved via remappings) | Med | False executor under wrong contract | Allowlist of known base files + verify the resolved file actually defines a `multicall(bytes[])`; skip on ambiguity |
| Abstract-contract handling (executor defined in an abstract base, also re-declared) | Med | Double attribution | Attribute to concrete derivers only; skip if the deriver overrides the method locally (already enumerated) |
| Interface pollution (attributing interface declarations with no body) | Low | Empty bodies → no candidate but denominator noise | Reuse `is_pure_interface` drop (`:343`); require a brace-matched body |
| Proxy inheritance confusion (delegatecall proxies, upgradeable bases) | Low-Med | Mis-attributing proxy/init methods | Allowlist is multicall-only; proxies/initializers excluded by shape |
| Diamond/facet contamination (facets don't inherit a shared base the usual way) | Low | Missed or mis-placed attribution | Out of scope for C (diamonds use `farm`/internal-call batching — a separate detector item, not inheritance) |
| Generated-code artifacts (`out/`, build outputs) | Med | Attributing compiled artifacts | Honor existing exclude-globs; only resolve bases reachable from in-scope `src` imports |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Severity | Mitigation |
|---|---|---|---|---|
| **Polluting canonical `coverage_manifest.json` → Step 3.9 gate denominator changes** | High if merged into canonical | **Critical** (alters production gating + eval reproducibility) | **High** | **Sidecar only**; never write to canonical; if ever merged, tag `inherited:true` and exclude from the blocking denominator |
| Eval-reproducibility drift (frozen snapshots / scorecard recomputation) | Med | High | Med-High | Sidecar is separate file; canonical manifest + frozen `pre_answer_key_snapshot` byte-identical; recompute nothing |
| Candidate-volume increase routed as findings | Med | High | Med | Keep executor flag `research_only` / non-routing (unchanged policy) |
| Remapping/path-resolution fragility | Med | Med | Med | Limit resolution to a small base allowlist; fail safe (skip, log) on unresolved imports |
| Maintenance drift as bases evolve (new multicall variants) | Low-Med | Low-Med | Low | Allowlist + a "resolved a `multicall(bytes[])` body" structural check, not a hard-coded line |

**Headline:** every serious risk is a *manifest-pollution / pipeline-coupling* risk, not a detector-precision
risk. All are neutralized by the sidecar isolation.

---

## 8. Recommended Design

**C — Multicall-only inherited attribution, delivered as a read-only sidecar.**

- **Artifact:** a separate `inherited_executors.json` (sidecar), built by a *new, isolated* pass — **not** a change
  to `build_coverage_manifest.py`'s canonical output. The canonical `coverage_manifest.json` is untouched.
- **What it contains:** for each in-scope contract whose `is …` clause names a **known multicall base**
  (allowlist: OZ `utils/Multicall`, UniV3/periphery `base/Multicall`, in-repo `base/Multicall`, and structurally-
  matching forks), one synthesized item attributing that base's `multicall(bytes[])` to the deriver:
  `{contract: <deriver>, name: "multicall", file: <base file>, source_span: <base method lines>, kind: "function",
  in_scope: true, inherited_from: <base>, synthetic_attribution: true}`.
- **How it's consumed:** research detectors (e.g. `multicall_invariant`) optionally merge the sidecar at
  `--manifest` time (real manifest ∪ sidecar). Production gates and specialists read the canonical manifest **only**
  and never see the sidecar.
- **Why C and not B/A/D:** C matches the *only* demonstrated need (multicall executors), has measured 0-FP impact,
  the lowest path-resolution surface (one method shape, an allowlist of bases), and the smallest denominator
  footprint. B is the documented growth path if other executor families (batch/aggregate) later prove valuable; A
  and D are rejected (manifest explosion + gate destabilization with no precision benefit).
- **Determinism/explainability:** IDs keyed on (deriver, base file, line) like `_short_id`; each entry self-
  documents `inherited_from`; output stable across runs (no LLM, no network).

---

## 9. Alternative Designs

- **B (Selective executor-family attribution):** extend C's allowlist/shape match to `batch*`/`aggregate*`/
  `multiDelegatecall` inherited executors. Natural next step **only if** evidence shows inherited non-multicall
  executors are missed. Keeps the sidecar model; modest extra resolution.
- **A / D (Global / full-graph):** attribute all inherited methods. **Rejected** — manifest explosion, Step 3.9
  denominator blow-up, interface/abstract pollution, high maintenance, and **no measured precision benefit** (the
  detector only ever fires on the multicall anyway).
- **Do-nothing:** acceptable given the detector is research-only and the gap is one architecture; but C is cheap
  and isolated enough that the visibility win is worth capturing as a standalone, non-pipeline-coupled artifact.

---

## 10. Implementation Complexity

For **C (sidecar)** — estimated **Low-Medium**:
1. Parse the `is Base1, Base2, …` clause for in-scope contracts (extend `TYPE_DECL` usage; small regex, no AST).
2. Map a named base → its source file via a **small allowlist + import resolution limited to that allowlist**
   (handle `@openzeppelin/`→`lib/...` and in-repo relative imports only). Fail-safe skip on ambiguity.
3. Locate the base's `multicall(bytes[])` method span (reuse `_signature_block`-style brace matching), and verify a
   real body exists.
4. Synthesize one sidecar item per (deriver, executor); dedup; deterministic ID.
5. Emit `inherited_executors.json`. **No edit to canonical manifest, detector, gates, or routing.**

For **A/D (global)** — **High**: full import graph + Foundry remapping resolution + multi-base linearization +
denominator-impact handling in the Step 3.9 gate. Not recommended.

---

## 11. Expected Validation Plan (executable later WITHOUT modifying the detector)

This plan validates the sidecar with the detector **unchanged** (mirrors the B1 experiment harness):

1. **Build the sidecar** for Revert, Panoptic, Maia, Tokemak + OZ/UniV3 controls (isolated output dir).
2. **Run the unchanged detector** via `documentation/evals/multicall_overnight_targets/_harness.py` against
   `(real manifest ∪ sidecar)` for each target (isolated `get_audit_root`, zero workspace writes).
3. **Assert expected behavior:** Revert → 2 × `delegatecall_self_context/medium`; Panoptic → 3 × `…/high`; Maia →
   0 (assembly, unchanged); Tokemak/OZ/UniV3 → unchanged. **0 new high-confidence false positives.**
4. **Manifest-stability check:** canonical `coverage_manifest.json` files and all frozen `pre_answer_key_snapshot`
   baselines **byte-identical** before/after (`sha256sum -c`); the sidecar is a separate file.
5. **Gate-safety check:** Step 3.9 coverage-completeness denominator **unchanged** (sidecar excluded from the
   blocking set); confirm no routing/gate path reads the sidecar.
6. **Volume measurement:** count the candidate-volume delta across the 20-target set to quantify benign-executor
   growth (the one real cost) and confirm it stays in the non-routing tier.
7. **Pass criteria:** coverage converts as predicted, precision FP-delta ≈ 0, canonical artifacts unchanged,
   detector binary unchanged. Only then consider productizing; an optional canonical-merge would require a separate
   gate-impact study (step 5 expanded).

---

## 12. Final Recommendation

# IMPLEMENT MULTICALL-ONLY ATTRIBUTION

Deliver it as an **isolated, read-only sidecar** (Design C/E), consumed only by research detectors and **never**
written into the canonical coverage manifest. This is the proportionate choice: it captures the demonstrated B1
visibility win (Revert, Panoptic, and any OZ/UniV3 inheritor) with **measured zero false-positive impact**, the
lowest engineering surface, and **no coupling to production gating, routing, or evaluation reproducibility**. Keep
the executor flag research-only (volume, not noise, is the cost). Document **Selective (B)** as the extension path
and **reject Global/Full-graph (A/D)**. The assembly-multicall gap (Maia/solady) is explicitly **out of scope** for
this manifest-layer project and remains a separate detector-implementation item.

---

## Final Output

### 1. Executive summary
Inherited-executor attribution is feasible and precision-safe **only** in a minimal, multicall-only, isolated form;
the real risk is manifest pollution (the canonical manifest feeds the Step 3.9 gate + all lenses), not detector
precision. Recommend a read-only sidecar that research detectors merge at read-time and that never touches the
canonical manifest.

### 2. Recommended design
Multicall-only inherited attribution → `inherited_executors.json` **sidecar**, built by a separate pass from a
known-base allowlist, attributing each inherited `multicall(bytes[])` to its deriving in-scope contract
(`inherited_from`, `synthetic_attribution:true`, deterministic IDs); consumed only by research detectors.

### 3. Estimated coverage gain
Converts inherited Solidity-level multicalls: Revert (+2), Panoptic (+3) demonstrated, plus any OZ/UniV3 inheritor;
category *inherited-library multicall (Solidity-level)* Unsupported → Supported. No gain for assembly multicalls
(Maia) or already-covered Tokemak/OZ/UniV3.

### 4. Estimated precision impact
**~0 new false positives** (B1 + whole-base controls). Cost = candidate-volume growth ≈ 1 benign executor flag per
inheriting contract ⇒ keep the executor flag non-routing.

### 5. Key implementation risks
(1) Canonical-manifest pollution / Step 3.9 denominator change — mitigated by sidecar isolation; (2) eval-
reproducibility drift — mitigated (canonical + frozen snapshots untouched); (3) remapping/path-resolution
fragility — mitigated by base allowlist + fail-safe skip; (4) routing of benign executor flags — mitigated by
research-only policy.

### 6. Final recommendation
**IMPLEMENT MULTICALL-ONLY ATTRIBUTION** as an isolated sidecar, validated later with the detector unchanged per
§11; extend to Selective (B) only on evidence; do not pursue Global/Full-graph; treat assembly-multicall
recognition as a separate detector item.
