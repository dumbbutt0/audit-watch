# Bug-Chain Slide Planning Template

A **reusable slide-outline template** for explaining a promoted bug chain step-by-step. This is a planning
scaffold — **not** a set of finished slides, and **not** a submission artifact.

> **When to use:** only for a bundle already at `PROMOTE_TO_CHAIN_ANALYSIS` (see
> `human_vuln_promotion_checklist.md`). It organizes a human's explanation of a *hypothesised* chain; it asserts
> **hypotheses + evidence + open questions**, never a verdict.
>
> **Invariant (mirrors the rest of the research track):** slides do not state a final severity, a confirmed-bug
> verdict, a submission/bounty framing, or "exploit proven" (unless an actual PoC result is attached). Research-only;
> `routing_allowed:false`. Distinct from the production submission/report renderers.

---

## The 13 slide sections
For each: **(a)** what the slide contains · **(b)** which screenshots/code snippets belong on it · **(c)** the
evidence required before the slide may be made (if absent → leave it a marked placeholder, never fabricate).

**1. Title / finding hypothesis**
- (a) One-line hypothesis in *could/if* language (e.g. "If a Permit2 signature for a non-asset token is accepted,
  it could be credited as the protocol asset"). (b) none (or a single context diagram). (c) requires a coherent
  `rationale` from the bundle. No severity word in the title.

**2. System context**
- (a) The component(s) involved and what they're supposed to do. (b) an architecture/box diagram; the contract
  name(s) from `location.file`. (c) requires the affected contract/function be identified.

**3. Attacker preconditions** *(what must already be true for the attack to start)*
- (a) The starting world-state the attacker needs: funds held/approved, roles owned, prior protocol state, timing/
  ordering, external dependencies. The slide whose absence most often sinks PoCs — list them explicitly. (b) the
  relevant modifiers / access checks / required approvals from `code_snippet`. (c) each precondition marked
  **confirmed-from-evidence** (cite file:line) or `⟦UNKNOWN⟧`. An empty/unknown preconditions slide is itself a
  finding about investigation readiness, not something to skip.

**4. Entry point**
- (a) The exact externally-callable function where the attacker begins. (b) the function signature + visibility/
  modifiers + call site from the bundle's `code_snippet` / `candidate_surface`. (c) requires `candidate_surface`
  and a resolvable `location`.

**5. Trust / validation assumption**
- (a) The assumption the code makes that the attacker will violate. (b) the line(s) embodying the assumption
  (e.g. "assumes `permit.token` is the protocol asset"). (c) requires the assumption be visible in evidence;
  otherwise `⟦UNKNOWN⟧`.

**6. Broken check**
- (a) The specific missing or incorrect validation. (b) the exact missing/incorrect lines, or the absence shown in
  context (highlight where the check *should* be). (c) requires `rationale` / `missing_binding_explanation` or a
  cited code location.

**7. Exploit path step-by-step**
- (a) Ordered steps from entry to impact, each step a discrete action. (b) per-step code refs; a sequence diagram.
  (c) each step cited to evidence or tagged `⟦TO CONFIRM VIA PoC⟧`. Do not present unconfirmed steps as fact.

**8. State change**
- (a) The concrete storage/balance/accounting change the chain causes. (b) before/after of the named slot or
  balance, each tagged `⟦TO CONFIRM VIA PoC⟧` until a PoC shows it. (c) requires a named state variable from
  `evidence_signals`/`code_snippet`; if only hypothesised, mark it.

**9. Impact hypothesis**
- (a) The economic/security consequence **as a hypothesis** ("could lead to …, if reachable"). (b) optional impact
  diagram. (c) requires steps 6–8 to at least be hypothesised with evidence. **No severity rating here** — impact
  is a hypothesis to be tested, not a graded outcome.

**10. PoC plan**
- (a) What a PoC would need to set up (preconditions from slide 3), call (entry from slide 4), and assert (state
  from slide 8) to confirm/refute the chain. (b) a skeleton test outline. (c) requires slides 3/4/8 populated;
  drives directly from the Open Questions slide.

**11. Counter-signals / limitations**
- (a) Why this might be benign / a known-safe pattern / a detector FP / unreachable. (b) the suppression or
  guard code if any. (c) requires the promotion checklist's "counter-signals reviewed" content + label
  `counter_signals`. A chain with no honestly-listed limitations is under-analysed.

**12. Evidence inventory**
- (a) Every piece of evidence backing the deck, each with a source ref (file:line / bundle `candidate_id` /
  `source_audit_path` / label). (b) the snippet/screenshot list. (c) **no claim elsewhere in the deck may exist
  without an entry here or an `⟦UNKNOWN⟧` tag.**

**13. Open questions**
- (a) Everything still unknown — reachability gaps, unconfirmed state changes, missing preconditions. (b) none.
  (c) **mandatory slide**; it is the to-do list that the PoC plan (slide 10) executes against.

---

## Cross-cutting authoring rules

### How to avoid overstating severity
- Use hypothesis language throughout: *could*, *may*, *if reachable*, *to be confirmed*. Never write a severity
  rating (no "critical"/"high"/"medium") and never call it a "valid"/"confirmed" bug. Impact (slide 9) is always a
  *hypothesis to be tested*. Every causal claim either cites an evidence inventory entry or carries an unknown tag.

### How to mark unknowns clearly
- Two standard tags, used inline and never silently resolved:
  - `⟦UNKNOWN⟧` — not yet established from evidence.
  - `⟦TO CONFIRM VIA PoC⟧` — believed but requires a PoC to prove (esp. slides 7 and 8).
- Unknowns are first-class content. The **Open Questions** slide (13) is mandatory and aggregates them.

### Evidence inventory discipline
- Every snippet/screenshot carries a provenance ref (file:line, bundle `candidate_id`, `source_audit_path`, or the
  `hv-1` label). No claim without provenance — the same grounding rule as the research judge's `evidence_refs`.
  If you cannot cite it, it is an `⟦UNKNOWN⟧`, not a statement.

---

## Forbidden on slides
```
• final severity rating        • "valid bug" / "confirmed vulnerability" language
• submission / bounty framing   • "exploit proven" without an attached, actually-run PoC result
```
Slides present **hypotheses + evidence + open questions**. Confirmation comes later, from a real PoC, recorded
separately.

---

## Blank slide-outline skeleton (clone per promoted chain)
```
BUG-CHAIN OUTLINE — research-only (routing_allowed:false, research_only:true)
candidate_id: ____   source_corpus_hash: ____   chain_completeness: single-step / multi-step / unknown

01 Title / finding hypothesis ......... [ ] evidence attached   <could/if one-liner>
02 System context ..................... [ ] evidence attached
03 Attacker preconditions ............. [ ] evidence attached   (each: confirmed | ⟦UNKNOWN⟧)
04 Entry point ........................ [ ] evidence attached
05 Trust / validation assumption ...... [ ] evidence attached
06 Broken check ....................... [ ] evidence attached
07 Exploit path step-by-step .......... [ ] evidence attached   (steps: cited | ⟦TO CONFIRM VIA PoC⟧)
08 State change ....................... [ ] evidence attached   (before/after | ⟦TO CONFIRM VIA PoC⟧)
09 Impact hypothesis .................. [ ] evidence attached   (hypothesis only — NO severity)
10 PoC plan ........................... [ ] evidence attached
11 Counter-signals / limitations ...... [ ] evidence attached
12 Evidence inventory ................. [ ] complete (every claim has a ref)
13 Open questions ..................... [ ] MANDATORY — lists all ⟦UNKNOWN⟧ / ⟦TO CONFIRM VIA PoC⟧
```
A slide whose "evidence attached" box is unchecked stays a placeholder — it is not presented as fact.

---

## 1. Checklist summary
The promotion decision (`human_vuln_promotion_checklist.md`) gates entry: only `PROMOTE_TO_CHAIN_ANALYSIS` bundles
get a deck, and their `chain completeness` (single- vs multi-step) sets the depth.

## 2. Slide template summary
Thirteen ordered sections (Title → System context → **Attacker preconditions** → Entry → Assumption → Broken check
→ Exploit path → State change → Impact hypothesis → PoC plan → Counter-signals → Evidence inventory → Open
questions), each with required content, the snippet/screenshot it carries, and the evidence that must exist before
it can be drawn. Unknowns are tagged; severity is never asserted.

## 3. Recommended workflow
`hv-1 human label` → promotion checklist → (if `PROMOTE_TO_CHAIN_ANALYSIS`) clone this skeleton → fill **only**
evidence-backed slides, tag the rest `⟦UNKNOWN⟧` → the **Open Questions** slide becomes the **PoC plan**'s to-do
list → a real PoC (run separately) is what later upgrades `⟦TO CONFIRM VIA PoC⟧` claims to confirmed.

## 4. Safety constraints
Research-only; `routing_allowed:false`; a planning scaffold, not a submission. No final severity, valid/confirmed
verdict, submission/bounty framing, or "exploit proven" without an attached PoC result. Every claim is cited or
marked unknown. Modifies no corpus / detector / gate / manifest / answer key / submission system. Distinct from the
production report/submission renderers and the production `chains.md`/CHAIN-XXX system.
