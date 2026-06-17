# Promotion Review — `sibling_function_parity`

Decision document per the research-detector lifecycle
(`documentation/architecture/research_methodology.md`). Evidence:
`documentation/evals/sibling_function_parity_eval/`.

## The six questions

### 1. Did the detector recover evaluation misses?
**Yes — one, cleanly.** Blackhole **M-04** (`RewardsDistributor.claim`~`claim_many`, missing
`avm.getOriginalOwner` recipient resolution) was an out-of-lens-scope MISS in the 20-subject baseline
and is now a **high-confidence HIT** with the exact missing component named. Size **M-02** is surfaced
as a low-tier ADJACENT (validation-parity theme). Size **M-06** (cross-contract) and **M-12**
(wrong-value) are outside this detector's structural model.

### 2. Did it reduce out-of-scope bugs?
**Marginally — by one, plus partial illumination.** The baseline's 24 out-of-lens-scope bugs drop by 1
(M-04 now addressable); M-02's theme is now visible. The detector also produced the important
*diagnostic* that the "validation parity" cluster is **heterogeneous** (missing-component vs wrong-value
vs cross-contract) — only the first sub-shape is deterministically reachable.

### 3. Is the FP rate acceptable?
**Yes — excellent.** **Zero** high/medium false positives across 16 subjects / 8,855 in-scope items,
including the 1,332-item Beanstalk diamond and the sibling-dense ve(3,3) DEXes. Corpus high/medium
route-rate **0.0001** (target < 0.02). Every suppression control is justified by a recurring corpus
pattern, not over-fit to one subject.

### 4. Should it become production (wired/routed)?
**Not yet.** Recommend **RESEARCH-STABLE / NARROW-SCOPE-CONFIRMED**, the same status as
`multicall_invariant`. Rationale: precision is production-grade, but high-confidence recall in this
corpus is a single instance — too thin to justify routing/gating. Promotion to production is a separate,
later human decision and should follow either (a) more high-confidence corpus instances, or (b) the
scope extensions in Q6.

### 5. Should it remain research-only?
**Yes.** It ships with `is_gate:false` / `research_only:true` / `routes_in_production:false` /
`routed_manifest_ids:[]`, un-wired (no routing/gate/run_pipeline/agent_policy reference). It "signals,
does not submit." Keep it there until the platform owner promotes it.

### 6. Which categories benefited most?
**Trading** (the one high-confidence recovery, ve(3,3) reward recipient parity). At the exploratory
(low) tier the lens fires across **Trading, Yield, Lending, Stablecoins** and exercises all seven parity
types — so the *shape* is cross-category, but demonstrated high-confidence value is currently Trading-
only. **Recipient parity** is the highest-precision parity type (it hosts the anchor).

## Recommendation

**Adopt as RESEARCH-STABLE / NARROW-SCOPE-CONFIRMED, un-wired.** It precisely captures the
*missing-component, intra-contract sibling* sub-shape of validation parity with zero corpus FP, and
recovers a real High-area miss the baseline could not. Do **not** route it.

## Concrete follow-on opportunities (separate research, not this detector)

1. **Cross-contract sibling pairing** — ✅ **BUILT (Tier-1B)** as `cross_contract_sibling_parity`
   (`documentation/evals/cross_contract_sibling_parity_eval/`). Recovers Size **M-06** (forSale parity
   between `validateBuyCreditMarket`~`validateSellCreditMarket`) at high confidence, 0 FP on the 15
   non-Size subjects (corpus route-rate 0.0003). Research-only / un-wired. Multi-gate (shared verb +
   module dir + state-struct + object-suffix + ≥2 calls) controlled the initial FP explosion. Confirmed
   pattern added to the KB (`kb/attack_primitives.json` PRIM-021, `data/findings/SFP-BH-M04.json`).
2. **Wrong-value parity** (`value_flow_parity`) — **NEXT, not yet built.** Detect a sibling computing
   against the wrong quantity (Size M-02/M-12); the component is present, so this is value-flow, better
   suited to a deep-pass-style check than a structural missing-component diff.
3. **Promote more corpus instances** — expand the answer-key corpus with more `*_many`/`*For`/`validateX`
   pairs to test whether high-confidence recall generalizes before any production decision.

## Platform-contract checklist (verified)

- [x] `config/sibling_function_parity_patterns.json` carries `research_only:true`.
- [x] Output JSON carries `is_gate:false`, `research_only:true`, `routes_in_production:false`,
      `routed_manifest_ids:[]`.
- [x] Un-wired — no routing/gate/run_pipeline/agent_policy reference (grep-verified).
- [x] Deterministic + reproducible; `tests/sibling_function_parity/` (11) green; existing lens suites
      (136) unchanged.
- [x] No existing detector/config/routing modified.
