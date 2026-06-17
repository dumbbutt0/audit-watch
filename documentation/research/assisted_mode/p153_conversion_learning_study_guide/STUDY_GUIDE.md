# Conversion Learning for Adversarial Security Research: Phase 0 to P152 Study Guide

> **What this is.** A durable, textbook-style study guide for the Audit-Watch project from its
> origins (Phase 0) through P152. It is a *training manual for a low-level precision-AI trainer* —
> not a blog post, not a hype piece, and **not a vulnerability report**. Nothing here is
> submission-ready. Every runtime row referenced remains `routing_allowed=false` and
> `submission_ready=false`.
>
> **How to read it.** Sections 1–9 teach the conceptual arc. Sections 10–11 give the current,
> verbatim cross-architecture data. Sections 12–15 are reusable field instruments (signal
> taxonomies, chokepoints, trainer rules, self-test questions). Section 16 recommends the next
> phase. Section 17 is the one-line principle to remember.
>
> **Honesty rule used throughout.** Where local memory and on-disk artifacts give exact facts, they
> are stated exactly. Where per-phase detail is not locally recoverable, the text says
> **"(reconstructed; exact per-phase detail unknown)."** No exact fact has been invented to fill a
> gap. `duplicate_unknown` everywhere means *"no local duplicate record found,"* **never** "novel."

---

## 1. Executive Learning Thesis

**The goal of this project is not to make the AI more confident. The goal is to make it more
discriminating.**

A confident auditor that promotes every plausible suspicion is worse than useless: it floods the
human reviewer with false positives, burns trust, and risks an unsafe submission. A *discriminating*
researcher does the opposite — it promotes, refutes, downgrades, or stops based on evidence, and it
is willing to say "I confirmed the mechanism but it is not reachable" or "the surface is reachable
but the mechanism is absent."

To make discrimination *learnable*, the project decomposes a finding into a chain of independent
labels. Each link is its own decision with its own evidence and its own failure mode:

```
lead
  → suspicion
    → mechanism hypothesis
      → source evidence
        → runtime proof
          → reachability
            → severity
              → novelty
                → reportability
                  → conversion outcome
```

**Why each stage is a separate learning label.** If you collapse the chain into a single
"is-this-a-bug?" boolean, every failure looks the same and teaches nothing. Separated, each failure
is *diagnostic*:

- A **lead** that never becomes a **suspicion** teaches *target/triage selection*.
- A **suspicion** with no defensible **mechanism hypothesis** teaches *mechanism identification*.
- A **mechanism** unsupported by **source evidence** teaches *reading discipline*.
- **Source evidence** that fails **runtime proof** teaches *real-vs-imagined behavior* (P148, P152).
- A **runtime-proven** mechanism that fails **reachability** teaches *attacker-model discipline*
  (P151).
- A reachable mechanism with no **severity** teaches *impact discipline*.
- A severe, reachable bug with unknown **novelty** teaches *duplicate handling* (duplicate_unknown).
- Everything passing but **reportability** unproven teaches *the submission boundary*.
- The terminal **conversion outcome** is the supervised label a future model would actually learn
  from.

The thesis in one line: **train the chain, not the verdict.**

---

## 2. Phase History Reconstruction (a learning timeline)

The history is grouped into eras. Recent eras are reconstructed in detail from local memory and
on-disk deliverables; early eras are reconstructed **at era level** from `CLAUDE.md`,
`documentation/architecture/*`, and the project's stated framing, with per-phase specifics marked
unknown where not locally recoverable.

### Era I — Phase 0 → ~Phase 17: Initial pipeline, recall expansion, hallucination & depth failures
*(reconstructed at era level; exact per-phase detail unknown)*

- **Trying to improve:** stand up an end-to-end auditor — sandbox → static tooling → specialist
  agents → synthesis → triage — and *widen recall* so real bugs are not missed. The architecture is
  "recall first, precision second" (`CLAUDE.md`: coverage manifest, five read-time lenses).
- **What failed / was risky:** wide recall without depth produced **hallucinated** findings and
  **shallow depth traces** — "an attacker might…" reasoning that never traced a path end-to-end.
- **Structural change introduced:** the **ICE methodology** (Impact / Confidence / Exploitability)
  and the **Level-3 PoC standard** (L1 entry, L2 state flip, L3 outcome) as gating vocabulary.
- **System behavior change:** findings could no longer "advance on a suggestion" — ICE must be
  re-scored from scratch at each stage.
- **Lesson to transfer:** recall without a depth gate manufactures confident noise. Decide *how a
  claim earns advancement* before you widen the funnel.

### Era II — ~Phase 18 → ~Phase 32: Reject-first repair, depth_trace_v2, root-cause discrimination
*(reconstructed at era level; exact per-phase detail unknown)*

- **Trying to improve:** the precision collapse from Era I — too many near-duplicate, shallow
  candidates.
- **What failed / was risky:** many candidates were the *same* root cause wearing different
  function names; scoring recall on them was dishonest.
- **Change introduced:** **reject-unless-proven-exploitable** as the default posture, a **depth
  trace v2** that re-derives the path, and **root-cause deduplication**
  (`build_eval_inventory.py` collapsing candidates to deduped root causes).
- **Behavior change:** honest recall scoring became possible; the system began *discarding* its own
  weak output instead of forwarding it.
- **Lesson:** the first instinct of a disciplined researcher is to try to *kill* the finding. Make
  rejection the cheap default and promotion the thing that must be earned.

### Era III — ~Phase 33 → ~Phase 81: Detectors, gates, invariant mapping, defense mapping, routing discipline
*(reconstructed at era level; exact per-phase detail unknown)*

- **Trying to improve:** repeatable *precision* — turn one-off intuitions into reusable, FP-tight
  detector families.
- **What failed / was risky:** detectors that over-generalize re-introduce the Era I noise.
- **Change introduced:** the **research-only detector platform** (`documentation/architecture/`):
  validated narrow detectors (`sibling_function_parity`, `cross_contract_sibling_parity`,
  `value_flow_parity`, `registry_position_lifecycle`, `permit_asset_binding`,
  `multicall_invariant_v1`), each FP-tight (two-signal / primitive gate, 0 FP on their bug), plus
  **invariant mapping** and **defense mapping** as read-time context, and the platform invariants:
  every research artifact carries `is_gate:false / research_only:true / routes_in_production:false /
  routing_allowed:false` and is **un-wired**.
- **Behavior change:** detectors *"signal, don't submit"*; normalization *"rank, don't relabel"*;
  the evidence gate *"assemble, don't adjudicate."* Promotion to production became an explicit,
  separate, human decision (5-criteria bar, none promoted yet).
- **Lesson:** keep the experimental surface strictly separated from the production surface. A
  detector that can route itself will eventually route a false positive.

### Era IV — ~Phase 81 → ~Phase 138: Selection strategy, dashboard discipline, human-review & submission gates
*(P100–P116 reconstructed from on-disk dirs; P117–P138 detailed from memory)*

- **Trying to improve:** *which* targets to spend effort on, and how to surface results honestly to
  an operator.
- **What was risky:** a dashboard that shows only status (not evidence) silently re-rewards
  confidence; selection that chases easy targets understates real recall.
- **Changes introduced (P100–P116, dashboard/selection/actor-clarity/runtime-prep era):**
  dashboard metrics summaries, post-cleanup integrity checks (`p101_post_cleanup_integrity.md`),
  blind replay (`p102_blind_replay.md`), **selection-recall repair** (`p103_selection_recall_repair.md`),
  PoC handoff format, terminal-distribution and **actor-clarity** fixes
  (`p114`/`p115`/`p116`). *(Per-phase specifics beyond these titles: reconstructed; exact detail
  unknown.)*
- **Changes introduced (P117–P128, first runtime-harness era — iq-ai "frozen-5"):** the runtime-PoC
  method's *ancestor* — real-contract runtime PoCs for PhiDistribute (P117), UnlistVesting (P118),
  FeeCollector (P120), NukeFund (P121), PhiFactory (P122), AgentRouter buy/sell (P123/P124),
  BootstrapPool (P125), a lifecycle-transition study (P126), the **intent-review gate** (P127), and
  a **governance-capture** study (P128). P119 added an actor-clarity gap fix.
- **Changes introduced (P129–P138, measurement & advisory surfacing):** ground-truth measurement
  (P129), candidate-coverage repair (P130), the noya library-boost A/B (P131/P132), an
  answer-key-graded specialist run (P133), measuring the *existing* mechanism layer vs the gap
  (P134 — concluded "routing gap, not detector gap"), advisory surfacing into review as
  `advisory_only` (P135/P136), the blind H-03 value-provenance conversion (P137), and the **blind
  value-provenance corpus** that measured the deep-pass prompt's precision/recall/FP (P138: useful
  recall 4/5, finding precision 3/3, clean-FP 0/5).
- **Behavior change:** results became *labels on a learning surface*, not green ticks. The human
  review gate and the eval-vs-submission split (`CLAUDE.md`: confirm gate "never wired into the
  eval/full scoring paths") hardened.
- **Lesson:** a dashboard must expose *evidence and outcome labels*, or it will quietly retrain the
  system to be confident. Measure your own FP/recall before adding detectors (the Self-Calibration
  Principle).

### Era V — P139 → P152: Runtime confirmation, reachability separation, conversion schema, refutation & boundary-stop
*(detailed from memory + this session)*

- **Trying to improve:** close the gap between *prompt-derived evidence* ("the model says it's a
  bug") and *runtime-proven evidence* ("the real contract does X"), and then separate that from
  *reachability*, *severity*, and *reportability*.
- **What was risky:** treating a runtime confirmation as a finding — the exact over-promotion the
  whole project exists to prevent.
- **Changes introduced:**
  - **P139–P142** built the value-provenance advisory loop (`--ingest-results`), measured it across
    architectures, and froze it as a **standing research-only eval harness** + corpus + scorecard
    (`value_provenance_eval_harness.py`), reusing prior code with zero production lines added.
  - **P143** produced the first **Level-3 real-contract runtime PoC** (Noya `NoyaValueOracle._getValue`),
    recording `runtime_status` in a sidecar kept *strictly separate* from `prompt_decision`.
  - **P144** did a source-only **reachability/severity review** of that item (protocol-config
    reachable, not user-reachable; severity provisional).
  - **P145** pivoted the method to a 2nd architecture/bug-class (Blackhole `claim_many` sibling
    parity).
  - **P146** added the **runtime evidence panel** to the scorecard — supplemental only, proven (by
    an empty-vs-full-sidecar integrity test) to leave the prompt metrics byte-for-byte unchanged.
  - **P147** ran the first **non-duplicate** holdout to runtime confirmation (Centrifuge
    `UserEscrow.transferOut`).
  - **P148** ran a deliberate **negative control** (Velodrome) and exercised `runtime_refuted` — the
    method can *kill* a plausible candidate, not just confirm.
  - **P149** delivered an **intent/severity judgment** on the Centrifuge item
    (GRIEFING_OR_DESIGN_AMBIGUOUS) — establishing that mechanism-confirmed ≠ bounty-grade.
  - **P150** ran a 2nd non-dup holdout (Decent `UTBFeeCollector.collectFees`) → runtime_confirmed
    mechanism.
  - **P151** did the **reject-first reachability review** of Decent: the real UTB router binds the
    `fees` into the signed `packedInfo`, so the mechanism is **not externally reachable** →
    design / privileged-only. This is the project's defining **boundary-stop**.
  - **P152** ran a 3rd non-dup holdout in a new mechanism class (ECG `ERC20MultiVotes`
    vote-accounting) → **runtime_refuted** (the real guard `_decrementVotesUntilFree` works), and
    adopted the **conversion schema** as a first-class dashboard/data rule.
- **Behavior change:** the system now produces a *spectrum* of honest outcomes — confirmed,
  refuted, privileged-only, needs-context — none of which auto-promote.
- **Lesson:** confirmation is a *milestone*, not a verdict. The value of this era is that it learned
  to **stop honestly** in four distinct ways.

---

## 3. Prompting Improvements and Their Effects

| Prompting / system change | Problem it addressed | Behavioral effect | Example phase / outcome | Future-project lesson |
|---|---|---|---|---|
| Reject-unless-proven-exploitable | Confident over-promotion | Default posture flipped to "try to kill it" | Era II reject-first repair | Make rejection cheap, promotion earned |
| Root-cause discrimination | Inflated recall from near-dup candidates | Candidates collapse to deduped root causes | `build_eval_inventory.py`; Era II | Score root causes, not function names |
| Mechanism vs impact separation | "Bug = severity" conflation | Mechanism can be confirmed while severity stays open | P144, P149, P150 | A confirmed mechanism is not a severity |
| Corrected-reference requirement | Persuasive but unproven claims | A one-line-fixed copy must remove the delta | P143 (20e18→6e18), P152 | Prove the *fix* changes behavior |
| Matched-control requirement | Coincidental deltas | A non-triggering control must show no divergence | P143 single-hop, P148, P152 control | Isolate the variable you blame |
| Real-contract harness preference | Mock-shaped artifacts | Deploy real/inherited production code, mock only deps | P143/P145/P147/P150/P152 | Test the real object, not a stand-in |
| Frozen prompt baseline | Drift contaminating measurement | Prompt metrics stay byte-for-byte across phases | P146 integrity test; P148/P150/P152 | Freeze the baseline to keep experiments comparable |
| No production source edits | Accidental capability/severity change | All work in test/sidecar/research files | Every P143–P152 (contracts byte-identical) | Never let an experiment touch the product |
| Un-wired harnesses | Research silently routing | `routes_in_production:false`, grep-clean | Platform invariants; P142–P152 | Experimental code must be unreachable from prod |
| `routing_allowed=false` (forced) | A row promoting itself | Panel forces the flag regardless of input | P146 `build_runtime_panel` | Make the safe value un-overridable in research |
| `submission_ready=false` by default | Accidental submission | Every row ships not-ready | All of Era V | Submission is opt-in by a human, never default |
| Human-review gate | AI self-adjudication of scope/severity | Ambiguous items routed to a human | P127, P144, P149, P151 | Reserve scope/severity calls for humans |
| Reachability before severity | Severity assigned to unreachable bugs | Reachability is checked first and can stop the chain | P151 boundary-stop | Ask "can an attacker reach it?" before "how bad?" |
| `duplicate_unknown` carries no novelty | "No record" misread as "novel" | Unknown stays unknown; no novelty inferred | P147–P152 holdouts | Absence of a record is not evidence of novelty |
| `conversion_outcome` field | One boolean hiding many failures | Terminal outcome is an explicit enum | P152 schema adoption | Label the *kind* of stop, not just pass/fail |
| `primary_blocker` field | "It didn't work" with no cause | The *reason* it stopped is captured | P151 privileged_router_binds_fees; P152 | Record the blocker so selection improves |
| Backfilled conversion schema | Old rows unlabeled vs new schema | B-rows/H-rows get consistent fields (data only) | P152 backfill onto H1–H3 | Retrofit labels so the dataset is uniform |
| Dashboard panel summaries | Status board ≠ learning surface | Panel shows runtime_status + conversion side-by-side | P146 panel; P152 conversion | A dashboard should teach, not just report |
| Negative labels treated as useful | "Refuted = wasted effort" | `runtime_refuted` / `needs_context` are first-class | P148, P149, P152 | A clean refutation is a successful experiment |

---

## 4. Runtime Confirmation Lessons

Each entry below states the architecture, the mechanism as proven, and the **training labels** that
the experiment produced. These are *learning records*, not findings.

### Noya — oracle / valuation
- **Architecture class:** oracle / valuation.
- **Mechanism:** a multi-hop valuation loop used the static *start* `asset` instead of the
  **loop-carried quoting token**, over-valuing a 2-hop route (real `getValue` = 20e18 vs a
  corrected one-line copy = 6e18, a 3.33× over-valuation); a single-hop control and an
  equal-per-hop-price control showed *no* divergence, isolating the static-`asset` hop.
- **Lesson:** a **corrected-reference valuation delta** is a strong proof of a value-provenance
  defect — but it proves the *mechanism*, not severity or production-route reachability.
- **Training labels:** `runtime_status=runtime_confirmed`, `runtime_confidence=high`,
  `duplicate_status=duplicate_known` (corpus item, outside the conversion funnel).

### Blackhole — rewards / NFT ownership
- **Architecture class:** rewards / NFT ownership.
- **Mechanism:** the single `claim` resolved the correct recipient via the AVM
  `getOriginalOwner` correction; the batch sibling `claim_many` **omitted** that correction and
  mis-routed an AVM-managed reward to `ownerOf` (the AVM manager). A non-AVM control matched.
- **Lesson:** **sibling-function comparands** and **batch-path parity** are strong signals — the
  defended single function vs the undefended batch sibling is a high-yield place to test at runtime.
- **Training labels:** `runtime_status=runtime_confirmed`, `runtime_confidence=high`,
  `duplicate_status=duplicate_known` (Blackhole M-04; method validation, not a submission).

### Decent P150 — cross-chain router / fee authorization
- **Architecture class:** cross-chain router / fee authorization.
- **Mechanism:** `collectFees` verified a signature over `packedInfo` but executed the transfer
  using a **separate, unbound `fees` struct** — the signer authorized `feeAmount=1e18` while the
  real contract charged the unsigned `1000e18`; a corrected reference
  (`require keccak256(packedInfo)==keccak256(abi.encode(fees))`) reverts; a matched-fees control
  shows no divergence.
- **Lesson:** contract-level runtime confirmation is **real but incomplete** — it proves the
  binding failure at the function boundary, not that an external attacker can trigger it.
- **Training labels (P150):** `runtime_status=runtime_confirmed`, reachability/severity *deferred*.

### Decent P151 — the boundary-stop
- **Result:** **design / privileged-only.**
- **Lesson:** the real UTB router builds `packedInfo = abi.encode(instructions, fees)` from the
  user's *own* `fees` at both public entrypoints (`swapAndExecute`, `bridgeAndExecute`), which take
  **no user `packedInfo` parameter**; `collectFees` is `onlyUtb`. So an unprivileged attacker cannot
  make the executed `fees` differ from the signed subject — the missing re-bind is **defense-in-depth
  only, not externally reachable**.
- **Key training labels:** `mechanism_confirmed=true`, `attacker_reachable=false`,
  `reportable=false`, `outcome=runtime_confirmed_but_privileged_only`,
  `blocker=privileged_router_binds_fees`.
- **Why it matters:** this is the canonical demonstration that *mechanism-confirmed ≠ reportable*.
  The runtime fact was preserved (still `runtime_confirmed`); only the **conversion** stopped.

### ECG P152 — governance / credit-guild
- **Architecture class:** governance / credit-guild.
- **Mechanism hypothesis:** governance vote-accounting on transfer — delegated voting power retained
  (inflated) after the holder transfers tokens away.
- **Result:** **runtime_refuted.**
- **Lesson:** the **reachable surface existed** (an unprivileged `transfer`), but the **mechanism was
  absent**: the real `transfer` calls `_decrementVotesUntilFree`, which frees delegated votes before
  the transfer, so `getVotes(delegatee)` drops `1000e18 → 0`. A *vulnerable reference* (unguarded
  transfer) retained `1000e18`, showing the bug shape the real contract avoids; a no-transfer control
  was stable.
- **Key training labels:** `mechanism_confirmed=false`, `attacker_reachable=true`,
  `reportable=false`, `outcome=runtime_refuted`,
  `primary_blocker_if_not_reportable=mechanism_absent_guard_present`.

**The pair P151/P152 is the heart of the runtime era:** one says *mechanism real, reachability
fails*; the other says *reachability real, mechanism fails*. Both are honest stops, and both are
*useful negative labels*.

---

## 5. Conversion Learning Schema (as a training system)

The conversion object is the supervised label set. It is recorded **per candidate**, in the sidecar,
*separately* from `runtime_status`:

```yaml
conversion:
  mechanism_confirmed: true | false | unknown
  attacker_reachable:  true | false | unknown
  severity_bearing:    true | false | unknown
  novelty_clear:       true | false | unknown
  reportable:          true | false | unknown
  outcome:             <enum>
  blocker:             <enum> | null
```

**`outcome` enum (observed/defined in the project):**
`reportable_candidate_needs_human_review` · `runtime_confirmed_but_reachability_unknown` ·
`runtime_confirmed_but_privileged_only` · `runtime_confirmed_but_severity_too_low` ·
`runtime_confirmed_but_duplicate_unknown` · `runtime_refuted` · `not_run_too_heavy` ·
`static_false_positive` · `needs_context`.

### Why `runtime_status` and `conversion_outcome` are different

- **`runtime_status`** answers *"what does the real contract actually do?"* It is a property of the
  **code under test** (`not_run / partial / runtime_confirmed / runtime_refuted / inconclusive`).
- **`conversion_outcome`** answers *"did this lead convert into a reportable, severity-bearing
  finding — and if not, why?"* It is a property of the **whole funnel** (mechanism + reachability +
  severity + novelty + reportability).

A single `runtime_status` can map to many `conversion_outcome`s. Keeping them separate prevents the
classic error of letting "the test passed" mean "the bug is real and reportable."

### Worked examples (all from the current sidecar)

- **runtime_confirmed, reportable unknown** → H1 Centrifuge: mechanism proven, but intent ambiguity
  leaves reachability/severity open → `outcome=needs_context`.
- **runtime_confirmed but privileged-only** → H3 Decent: mechanism proven, but only a privileged
  router could trigger it → `outcome=runtime_confirmed_but_privileged_only`.
- **runtime_refuted** → H2 Velodrome and H4 ECG: the suspected mechanism does not exist in the real
  contract → `outcome=runtime_refuted`.
- **needs_context** → H1 Centrifuge: severity depends on undocumented business intent (in-scope
  malicious ward? functional ERC4626 revert?).
- **static false positive** → *(defined in the enum; not currently instantiated in the sidecar —
  the place a similarity-only suspicion with no runtime delta would land.)*
- **reportable_candidate_needs_human_review** → *(the target outcome; **0 rows currently** — see
  §11.)*

---

## 6. Blocker Taxonomy

A *blocker* is the single reason a runtime-true (or plausible) candidate did **not** become
reportable. Capturing it is what lets future selection avoid the same dead end.

| Blocker | Definition | How it shows up in research | Pre-check that catches it earlier | Effect on future selection |
|---|---|---|---|---|
| `mechanism_absent_guard_present` | The suspected flaw is prevented by an existing guard | Refutation: real contract restores the invariant before state movement (P152 `_decrementVotesUntilFree`) | Read the function's *full* body and its internal calls before harnessing | Deprioritize targets whose guard you have not actually read |
| `privileged_router_binds_fees` | The only caller binds the user input into the signed/authorized subject | P151: UTB encodes `fees` into `packedInfo`; no user `packedInfo` param | Trace the *sole production caller's* argument construction first | Require an independent attacker-controlled input before promoting |
| `intent_ambiguous` | Severity hinges on undocumented business intent | P149 Centrifuge: NatSpec frames the gap as "additional protection" | Look for NatSpec / spec that frames the behavior as intended | Route to human; do not self-adjudicate scope |
| `runtime_refuted` | The real contract does not exhibit the mechanism | P148, P152 negative controls | Build a corrected-reference + control *before* claiming | Treat as a successful experiment; mine the family for true variants |
| `deploy_too_heavy` | Dependencies make a faithful harness impractical | P150 rejected vultisig ILOPool / kelp LRTDepositPool | Estimate mock surface (oracles, routers, libs) at selection | Prefer deploy-light targets; defer heavy ones explicitly |
| `reachability_unknown` | Mechanism proven but the production path is untraced | P144/P150 before their reviews | Plan the upstream call-path trace as part of the PoC | Keep `submission_ready=false`; schedule a reachability review |
| `severity_too_low` | Reachable + real but no meaningful impact | (defined; e.g. a confirmed delta with no economic/security consequence) | State the L3 outcome you expect before testing | Deprioritize; record so the family is not re-mined blindly |
| `duplicate_unknown` | No local duplicate record (NOT novelty) | All P147–P152 holdouts | Check local answer keys / KB at selection | Never infer novelty; a human/KB check gates novelty |
| `wrong_mechanism` | The named mechanism is not what the code does | Refutation where the hypothesis mis-described the code | Re-derive the mechanism from source (no-trust validation) | Tighten mechanism identification before harnessing |
| `wrong_impact` | The impact claimed does not follow from the mechanism | Mechanism real, asserted consequence does not occur | Trace the consequence to an asserted state/balance delta | Require an L3 outcome assertion, not an inferred one |
| `business_logic_unclear` | Correct behavior cannot be determined from available material | Some holdouts without spec | Acquire spec/docs or mark needs_context | Route to human; do not guess intended behavior |
| `privileged_only` | Only a privileged actor can trigger it | P151 (router-only) | Identify the caller's auth modifier early (`onlyUtb`) | Promote only if a malicious-privileged actor is in scope |
| `unreachable` | No production path reaches the vulnerable state | General terminal case of reachability failure | Trace EOA → entrypoint → vulnerable state before promotion | Stop; record the missing edge for future targets |

---

## 7. Chokepoint Guide for Future Projects

Each chokepoint is a place where a disciplined researcher must pause. *Symptom* = what you notice;
*Risk* = what goes wrong if you rush; *Required question* = the one to answer; *Evidence needed* =
what answers it; *Stop condition* = when to abandon; *Promotion condition* = when to advance.

1. **Target selection** — *Symptom:* many candidate audits. *Risk:* chasing easy/known targets.
   *Question:* is this deploy-light with a crisp, isolatable delta? *Evidence:* dependency estimate,
   line count. *Stop:* heavy deps with no crisp delta (`deploy_too_heavy`). *Promote:* deploy-light +
   a value/state-bearing function.
2. **Static suspicion** — *Symptom:* a pattern matches a detector. *Risk:* similarity ≠ behavior.
   *Question:* is there a *state delta*, not just a shape? *Evidence:* the storage/balance that would
   move. *Stop:* shape only. *Promote:* a nameable state/value delta.
3. **Mechanism identification** — *Symptom:* "this looks wrong." *Risk:* wrong_mechanism. *Question:*
   can I state the mechanism in one sentence from source? *Evidence:* the exact lines. *Stop:* cannot
   re-derive from source. *Promote:* a one-sentence, line-anchored mechanism.
4. **Sibling comparand** — *Symptom:* two near-identical functions. *Risk:* missing the defended/
   undefended split. *Question:* does one sibling have a guard the other omits? *Evidence:* both
   bodies side-by-side. *Stop:* siblings identical (P148). *Promote:* a genuine parity gap (P145).
5. **Invariant mapping** — *Symptom:* a value/accounting function. *Risk:* not knowing what *should*
   hold. *Question:* what invariant must hold before/after? *Evidence:* the conservation/parity rule.
   *Stop:* no statable invariant. *Promote:* a precise invariant to violate.
6. **Defense mapping** — *Symptom:* a tempting unguarded-looking path. *Risk:* missing an internal
   guard (P152). *Question:* what guard is *supposed* to stop this, and have I read it? *Evidence:*
   the guard's body. *Stop:* the guard restores the invariant (`mechanism_absent_guard_present`).
   *Promote:* the guard is genuinely absent on the path.
7. **Harness design** — *Symptom:* ready to test. *Risk:* mock-shaped artifact. *Question:* am I
   deploying the *real* contract and mocking only deps? *Evidence:* real/inherited production code in
   the harness. *Stop:* the behavior under test lives in a mock. *Promote:* real object + minimal
   mocks.
8. **Corrected reference** — *Symptom:* the real contract produces the delta. *Risk:* coincidence.
   *Question:* does a one-line fix remove the delta? *Evidence:* corrected copy reverts/changes.
   *Stop:* corrected copy still shows the delta. *Promote:* the fix removes it (P143).
9. **Matched control** — *Symptom:* a positive result. *Risk:* the delta came from something else.
   *Question:* does a non-triggering control show no divergence? *Evidence:* the control path stable.
   *Stop:* the control also diverges. *Promote:* control stable, only the suspect path diverges.
10. **Reachability** — *Symptom:* mechanism confirmed. *Risk:* unreachable/privileged_only.
    *Question:* can an *unprivileged* actor reach the vulnerable state via production flow?
    *Evidence:* an EOA → entrypoint → state-delta trace. *Stop:* only a privileged caller can trigger
    it (P151). *Promote:* a traced unprivileged path.
11. **Severity** — *Symptom:* reachable mechanism. *Risk:* severity_too_low. *Question:* what is the
    severity-bearing L3 outcome? *Evidence:* an asserted economic/security consequence. *Stop:* no
    meaningful impact. *Promote:* a named, asserted consequence.
12. **Novelty** — *Symptom:* a real, reachable, severe bug. *Risk:* inferring novelty from
    `duplicate_unknown`. *Question:* is there a local/KB duplicate? *Evidence:* answer-key/KB check.
    *Stop:* known duplicate (for submission). *Promote:* a confirmed-novel item — but only a human/KB
    check sets `novelty_clear`.
13. **Submission readiness** — *Symptom:* all prior links pass. *Risk:* accidental submission.
    *Question:* has a *human* approved promotion? *Evidence:* an explicit override outside the phase.
    *Stop:* default — `submission_ready=false`. *Promote:* never automatically.
14. **Human review** — *Symptom:* intent/scope ambiguity. *Risk:* AI self-adjudication. *Question:*
    is this a scope/severity/intent call? *Evidence:* the ambiguous artifact. *Stop:* route to human
    (P149). *Promote:* only after a human decision.
15. **Dashboard routing** — *Symptom:* results to surface. *Risk:* a status board that rewards
    confidence. *Question:* does the surface expose evidence + conversion labels (not just status)?
    *Evidence:* the panel forces `routing_allowed=false` and shows the conversion object. *Stop:* a
    row could route itself. *Promote:* labels visible, routing forced off.

---

## 8. Adversarial Reasoning as a Training Skill

Adversarial reasoning became useful **only when constrained by evidence**. Imagination is the input;
evidence is the gate.

**Weak reasoning (rejected by the system):**
> "An attacker might abuse this."

**Strong reasoning (the chain that earns advancement):**
- The attacker controls field **X**.
- Field **X** reaches function **Y** through a production path.
- Defense **Z** that should stop it is **absent** on that path.
- A **corrected reference** rejects the input (proving the defense matters).
- The **real contract** allows the state/value delta (not a mock).
- The **upstream call path is attacker-reachable** by an unprivileged actor.
- The impact is **severity-bearing** (an asserted L3 outcome).

**The reverse cases are equally valuable — and both are negative labels:**

- **Mechanism exists but reachability fails → P151 (Decent).** The binding failure is real at the
  function boundary, but the only production caller binds `fees` into the signed `packedInfo`, so no
  unprivileged attacker can reach the divergence. Label: `mechanism_confirmed=true`,
  `attacker_reachable=false`, `reportable=false`, `outcome=runtime_confirmed_but_privileged_only`.
- **Reachability exists but mechanism fails → P152 (ECG).** The `transfer` surface is unprivileged
  and reachable, but the guard `_decrementVotesUntilFree` removes the suspected vote-retention before
  the transfer. Label: `mechanism_confirmed=false`, `attacker_reachable=true`, `reportable=false`,
  `outcome=runtime_refuted`.

Teaching point: a trainer should reward the *production of either negative label* exactly as much as
a confirmation, because each one removes a whole class of future wasted effort.

---

## 9. How Prompting Changed Outcomes

A direct answer to *"how did the prompting suggestions affect the full project?"*

- **They forced the system to stop over-promoting.** Reject-first + `submission_ready=false` by
  default turned "plausible" into "not yet earned."
- **They turned failures into labels.** `conversion_outcome` + `primary_blocker` mean a refutation or
  a privileged-only stop is *recorded data*, not a dead end (P148, P151, P152).
- **They separated mechanism, reachability, severity, and reportability.** Four independent labels
  instead of one boolean made each failure diagnostic (P144, P149, P151).
- **They made negative results valuable.** `runtime_refuted` and `needs_context` are first-class
  outcomes; the negative-control phase (P148) exists *to* exercise a kill.
- **They prevented accidental submissions.** Forced `routing_allowed=false`, un-wired harnesses, and
  a human-review gate make submission an explicit human act.
- **They created stable experiments by freezing baselines.** The prompt baseline stays byte-for-byte
  across phases; the panel was *proven* not to perturb it (P146 integrity test), so cross-phase
  comparison is honest.
- **They required real evidence instead of persuasive explanations.** Corrected-reference + matched
  control + real-contract harness mean a claim is judged by behavior, not prose.
- **They made the dashboard a learning surface rather than a status board.** The panel surfaces
  `runtime_status` *and* the conversion object side-by-side, so the operator reads evidence and
  outcome, not green ticks.
- **They turned each phase into a data point for future selection.** Every holdout adds a labeled row
  (architecture, mechanism class, runtime_status, blocker), building the dataset a future model could
  actually learn selection from.

---

## 10. Cross-Architecture Conversion Table

Verbatim from `output_research/value_provenance_eval/runtime_status.jsonl` (the 6 sidecar rows). The
`conversion` object lives in the sidecar JSONL; the fixed-field panel renderer does not surface it,
so B1/B5 (corpus, duplicate-known) carry **no** conversion object and sit *outside* the conversion
funnel — their conversion cells are marked `n/a (corpus)`.

| candidate_id | audit | architecture_class | mechanism_class | runtime_status | mechanism_confirmed | attacker_reachable | severity_bearing | conversion_outcome | primary_blocker | submission_ready |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | noya-2024-04 | oracle / valuation | stale_loop_variable | runtime_confirmed | n/a (corpus) | n/a (corpus) | n/a (corpus) | n/a (corpus; duplicate_known) | n/a (corpus) | false |
| B5 | blackhole-2025-05 | rewards / NFT ownership | wrong_recipient_resolution | runtime_confirmed | n/a (corpus) | n/a (corpus) | n/a (corpus) | n/a (corpus; duplicate_known) | n/a (corpus) | false |
| H1-centrifuge-userescrow | centrifuge-2023-09 | escrow / recipient-provenance | recipient_provenance_weak_allowance_proxy | runtime_confirmed | true | unknown | unknown | needs_context | intent_ambiguous | false |
| H2-velodrome-rewardsdist-parity | velodrome-2022-05 | rewards distributor | sibling_recipient_parity_suspected | runtime_refuted | false | false | false | runtime_refuted | null | false |
| H3-decent-utbfeecollector-sigbind | decent-2024-01 | cross-chain router / fee auth | authorization_subject_mismatch_signature_not_bound | runtime_confirmed | true | false | false | runtime_confirmed_but_privileged_only | privileged_router_binds_fees | false |
| H4-ecg-multivotes-accounting | ecg-2023-12 | governance / credit-guild | governance_vote_accounting_on_transfer | runtime_refuted | false | true | false | runtime_refuted | mechanism_absent_guard_present | false |

> **Note on H4's blocker.** In the conversion object, `conversion.blocker` is `null` (consistent with
> H2, where a clean refutation carries a null in-object blocker); the *reason* is recorded in the
> sibling field `primary_blocker_if_not_reportable = mechanism_absent_guard_present`. The table shows
> that more informative value, with this caveat noted to preserve fidelity to the sidecar.

---

## 11. Conversion Funnel

Current state, derived from the sidecar + the runtime panel (panel = 11 corpus rows overlaid + 4
runtime-only rows):

| Funnel metric | Count |
|---|---|
| Total panel rows | **15** |
| Runtime-only rows (H1–H4) | **4** |
| `runtime_confirmed` | **4** (B1, B5, H1, H3) |
| `runtime_refuted` | **2** (H2, H4) |
| `not_run` | **9** (remaining corpus items) |
| `needs_context` | **1** (H1) |
| Privileged-only (`runtime_confirmed_but_privileged_only`) | **1** (H3) |
| `reportable_candidate_needs_human_review` | **0** |
| `submission_ready` | **0** |

**Why 0 reportable candidates is not automatically bad.** The runtime era was deliberately spent
learning **honest boundary detection** *before* any submission automation. A system that produced a
"reportable" row before it could reliably *refute* (P148, P152) and *downgrade* (P151) would be
exactly the over-confident auditor this project exists to avoid. Zero reportable, with four distinct
honest stop-types demonstrated, is the *intended* state of a system that has learned to discriminate
but has not yet been pointed at a target chosen to maximize a reachable, severity-bearing finding.
The next phase (§16) addresses that on purpose.

---

## 12. Positive Signal Taxonomy

The strongest signals learned so far. *Why useful* / *residual FP risk* / *what upgrades it*.

- **Corrected-reference delta** — *Useful:* proves the named flaw causes the delta (P143).
  *FP risk:* the "fix" might change behavior for an unrelated reason. *Upgrade:* pair with a matched
  control that stays stable.
- **Sibling-function comparand** — *Useful:* the defended/undefended split localizes the bug (P145).
  *FP risk:* siblings may legitimately differ (P148). *Upgrade:* confirm the omitted component is a
  *guard*, not a deliberate behavioral difference.
- **Batch-path parity failure** — *Useful:* batch wrappers often skip a per-item correction (P145).
  *FP risk:* the batch path may handle it elsewhere. *Upgrade:* trace the batch path end-to-end.
- **Loop-carried variable mismatch** — *Useful:* using a static start value instead of the updated
  loop variable is a classic value-provenance bug (P143). *FP risk:* the static value may be correct
  by design. *Upgrade:* corrected copy + multi-hop vs single-hop control.
- **Real-contract runtime delta** — *Useful:* behavior of the real object, not a mock. *FP risk:*
  mock dependencies could shape the result. *Upgrade:* minimize mocks; assert specific state.
- **Control-path stability** — *Useful:* shows the delta is specific to the suspect path. *FP risk:*
  a too-similar control may hide the variable. *Upgrade:* choose a control that differs *only* in the
  suspected variable.
- **Deploy-light harness** — *Useful:* a faithful harness is achievable, so results are trustworthy.
  *FP risk:* light deps may omit a real constraint. *Upgrade:* confirm omitted deps cannot prevent
  the path.
- **Unprivileged reachability with state delta** — *Useful:* the strongest reachability evidence — an
  EOA causes a state change. *FP risk:* the entrypoint may have an unmodeled guard. *Upgrade:* trace
  from a real public entrypoint with no privileged setup.
- **Signed-subject vs executed-subject mismatch** — *Useful only if upstream control is proven:* a
  signature not binding the executed value is a real class (P150). *FP risk:* the sole caller may bind
  it (P151!). *Upgrade:* prove an *independent* attacker-controlled input reaches the executed
  subject — without that, this is a negative signal (see §13).

---

## 13. Negative Signal Taxonomy

Misleading signals. *Why it misleads* / *pre-check to add* / *reject, deprioritize, or route?*

- **Suspicious isolated function without upstream reachability** — *Misleads:* looks exploitable in
  isolation. *Pre-check:* trace the sole production caller's argument construction. *Disposition:*
  deprioritize until a reachable path exists.
- **Public surface where a guard prevents the mechanism** — *Misleads:* the entrypoint is
  unprivileged, so it *seems* reachable. *Pre-check:* read the internal guard's body (P152). *
  Disposition:* reject the mechanism (refuted) once the guard is confirmed.
- **Intent ambiguity without docs** — *Misleads:* an apparent flaw may be documented defense-in-depth
  (P149). *Pre-check:* search NatSpec/spec for framing. *Disposition:* route to human (`needs_context`).
- **Heavy deploy dependencies** — *Misleads:* tempting target, but a faithful harness is
  impractical, inviting mock-shaped "confirmations." *Pre-check:* estimate the mock surface at
  selection. *Disposition:* deprioritize (`deploy_too_heavy`).
- **Static similarity without a state delta** — *Misleads:* a detector match feels like a finding.
  *Pre-check:* name the storage/balance that would move. *Disposition:* reject (would be
  `static_false_positive`).
- **Signature mismatch without independent attacker-controlled fields** — *Misleads:* a real bug
  class, but inert if the caller binds the field (P151). *Pre-check:* confirm an independent
  user-supplied input reaches the executed subject. *Disposition:* deprioritize / route until proven.
- **Governance/accounting suspicion without a post-state violation** — *Misleads:* accounting code
  feels risky. *Pre-check:* assert the post-state invariant the bug would violate (P152 votes→0).
  *Disposition:* reject if the invariant holds at runtime.

---

## 14. Trainer Rules (if / then)

Concrete rules the future system should follow:

1. **If** a mechanism is only observable through a privileged direct call, **then** do not promote
   until a real *upstream attacker-controlled* path is proven. *(P151)*
2. **If** a reachable function has a guard that restores the invariant before state movement,
   **then** refute the mechanism (`mechanism_absent_guard_present`). *(P152)*
3. **If** a single function has a defense and its batch sibling omits it, **then** prioritize runtime
   testing of the batch path. *(P145)*
4. **If** a corrected reference removes the delta while the real contract produces it, **then**
   mechanism confidence increases — record the delta and the control. *(P143)*
5. **If** severity depends on undocumented business intent, **then** classify `needs_context` and
   route to human; do not assign severity. *(P149)*
6. **If** duplicate status is unknown, **then** do not infer novelty; leave `novelty_clear=false/
   unknown` until a human/KB check.
7. **If** runtime is confirmed but reachability is unknown, **then** keep `submission_ready=false`
   and schedule a reachability review. *(P144/P150)*
8. **If** reportability is not proven, **then** route to human review or stop — never auto-promote.
9. **If** a candidate's faithful harness needs heavy/oracle/router deps, **then** deprioritize it
   (`deploy_too_heavy`) and record the reason rather than building a mock-shaped test. *(P150)*
10. **If** a panel/dashboard row carries `routing_allowed=true` or `submission_ready=true` from any
    input, **then** force both to false (research invariant). *(P146)*
11. **If** a negative control kills the suspicion, **then** record `runtime_refuted` as a successful
    experiment and mine the family for genuine variants. *(P148)*
12. **If** an experiment would require editing production source/harness/prompt/corpus, **then** stop
    — do it in a test/sidecar/research file or not at all.

---

## 15. Study Questions for Me

Answer these for every candidate when reviewing a future project:

1. What is the **mechanism**, in one sentence?
2. What would **refute** this mechanism?
3. Who **controls the critical input**?
4. Is the **vulnerable state reached** through production flow?
5. What **defense** is supposed to stop it — and have I read its body?
6. Is there a **sibling comparand** (defended vs undefended)?
7. Is there a **corrected reference** that removes the delta?
8. What is the **state or value delta** (named, asserted)?
9. Is the issue **reachable by an unprivileged actor**?
10. What is the **severity-bearing impact** (the L3 outcome)?
11. What is the **primary blocker** if it is not reportable?
12. What did this candidate **teach the system** (which label, which family)?

---

## 16. P154 Strategy

**Options considered:** A — maximize chance of `reportable_candidate_needs_human_review`; B —
maximize architecture diversity; C — stress-test a blocker class; D — improve dashboard scoring.

**Recommendation: Option A — maximize the chance of an honest
`reportable_candidate_needs_human_review`.**

The user's stated preference is A *unless the data shows the dashboard scoring is too weak to support
it.* Reviewing the data: the dashboard/conversion scoring is **strong enough** to support a promotion
attempt. The schema already distinguishes mechanism/reachability/severity/novelty/reportability, the
panel forces the safe flags, the funnel cleanly classifies four distinct honest stops (confirmed,
refuted, privileged-only, needs-context), and §11 shows the missing class is *only* a deliberately
not-yet-targeted reachable+severe item. The scoring is therefore **not** too weak; we do **not** fall
back to D.

**Reason.** The runtime era proved every *defensive* skill (refute, downgrade, defer, stop). The one
outcome never produced is the *positive* terminal — a reachable, severity-bearing, human-reviewable
candidate. Producing exactly one honest such row (or an honest stop while trying) is the natural next
data point and the most informative test of the whole funnel.

**Candidate-selection rules for P154:**
- An **unprivileged public entrypoint** (no privileged setup to reach it).
- An **attacker-controlled input** that reaches a **value-bearing state delta**.
- A guard that is **plausibly absent on that path** (and whose body you have read — apply Rule 2/§6
  `mechanism_absent_guard_present` first).
- **Deploy-light** enough for a faithful real-contract harness (avoid `deploy_too_heavy`).
- `duplicate_unknown` is acceptable (novelty is a later human/KB check, not a selection gate).

**Fields that must be captured:** the full conversion schema —
`mechanism_confirmed / attacker_reachable / severity_bearing / novelty_clear / reportable / outcome /
blocker` — plus `runtime_status`, `runtime_confidence`, the corrected-reference and control records,
and an explicit **L3 outcome** assertion.

**What counts as success:** *either* one honest `reportable_candidate_needs_human_review` row (all of
mechanism_confirmed + attacker_reachable + severity_bearing true, routed to human, still
`submission_ready=false`), **or** an honest stop with a recorded blocker (e.g. reachability fails →
privileged_only, or the guard holds → runtime_refuted). Both are wins.

**What counts as an honest stop:** any candidate that, on faithful runtime testing, is refuted,
privileged-only, severity-too-low, intent-ambiguous, or too heavy — recorded with its blocker and
left `submission_ready=false`. Reaching the boundary and stopping cleanly is a success, not a failure.

---

## 17. Final Lesson

**The project is not training an AI to *sound* like an auditor. It is training an AI to *behave* like
a disciplined researcher — one that can promote, refute, downgrade, or stop based on evidence.**
Confidence is cheap; discrimination is the product.

---

*This guide is a learning artifact only. It introduces no new vulnerability candidate, changes no
production source / harness / prompt baseline / detector / gate / routing / severity policy /
submission policy / corpus / active-audit symlink, and asserts no submission readiness. All
referenced rows remain `routing_allowed=false` and `submission_ready=false`. Unknowns are marked
unknown; no exact per-phase fact has been invented.*
