# Human Vulnerability Promotion Checklist

A **human worksheet** for deciding whether a frozen evidence bundle should move from
`READY_FOR_REVIEW` to a promotion outcome. It sits one step after the Human Validation Console
(`human_validation_dashboard.md`, `hv-1` labels) and before any deeper exploit-chain investigation.

> **Invariant: promotion is a human investigation decision, not a verdict.** `PROMOTE_TO_CHAIN_ANALYSIS`
> means *"a human judges this worth investigating as a chain,"* **not** "this is a valid bug." Nothing here
> decides bug validity, final severity, exploitability, submission, or bounty value. This is a worksheet a human
> fills in — **not** an automated gate, and it does not route anything.
>
> This is the **research track's** human investigation step. It is distinct from the production pipeline's wired
> `output/chains.md` / Step-2.5 bug-chain escalation / CHAIN-XXX system — cross-referenced, never merged.

## Inputs
- One `READY_FOR_REVIEW` evidence bundle (from `frozen_corpus.json` / `evidence_bundles.json`).
- Its `hv-1` human-validation label, if one exists.

The reviewer reasons **only over the bundle + label** (code_snippet, evidence_signals, rationale, location,
carried confidence/declared_severity_potential, and the label fields). No new evidence is invented; anything not
present is marked `unknown`.

### How `hv-1` label fields feed the checklist
| hv-1 label field | informs checklist category |
|---|---|
| `coherence` | evidence coherence |
| `investigation_worthiness` | confidence in next-step investigation |
| `poc_followup_worthiness` | PoC feasibility |
| `expected_review_effort` | PoC feasibility · chain completeness |
| `missing_information` | missing validation · → NEEDS_MORE_EVIDENCE |
| `counter_signals` | counter-signals reviewed · duplicate/known-issue risk |
| `reviewer_notes` | concrete impact hypothesis · system understanding |
| `reviewer_confidence` | confidence in next-step investigation |

---

## The 12 checklist categories
Mark each **met / partial / unmet / unknown**, with a one-line evidence reference (a bundle field or label field).
"unknown" is a legitimate, first-class answer — never guess to fill it.

1. **Evidence coherence** — Do the snippet, evidence_signals, and rationale tell one consistent story?
   *Evidence:* `code_snippet` + `rationale` + label `coherence`.
2. **Attacker reachability** — Is the surface plausibly reachable by an external/unprivileged caller (or is reach
   itself an open question)? *Evidence:* `candidate_surface`, function visibility/modifiers in `code_snippet`.
3. **Affected asset / function** — Which concrete asset, balance, or function is at stake? *Evidence:*
   `candidate_surface`, `evidence_signals` (e.g. `expected_asset_source`).
4. **State transition or invariant affected** — What state/invariant could change or break? *Evidence:*
   `evidence_signals`, `code_snippet` (storage writes, supply/balance math).
5. **Missing validation** — What check is absent or wrong that enables the concern? *Evidence:* `rationale`,
   `missing_binding_explanation`, label `missing_information`.
6. **Concrete impact *hypothesis*** — A specific, testable "if X then Y" outcome (stated as a hypothesis, never a
   conclusion). *Evidence:* reviewer's reasoning grounded in the above + label `reviewer_notes`.
7. **Counter-signals reviewed** — Have the reasons it might be benign / a known-safe pattern / suppressed been
   considered? *Evidence:* label `counter_signals`; detector suppression notes.
8. **PoC feasibility** *(estimate, not a promise)* — Could a PoC plausibly be built; what's roughly required?
   *Evidence:* label `poc_followup_worthiness` + `expected_review_effort`; preconditions visible in the snippet.
9. **Scope / program relevance** — Is the affected contract/area in the examined scope of interest? *Evidence:*
   `location.file`, `workspace`/`corpus_source_slug`.
10. **Duplicate / known-issue risk** — Does this resemble an already-known finding or a documented detector FP
    class? *Evidence:* label `counter_signals`, known-FP notes (e.g. the multicall `needs_context` FP pattern).
11. **Confidence in next-step investigation** — How confident is the reviewer that investigating further is
    worthwhile? *Evidence:* label `reviewer_confidence` + `investigation_worthiness`.
12. **Chain completeness** *(structural descriptor — NOT a severity)* — Is the concern `single-step`
    (missing validation → immediate impact), `multi-step` (missing validation → state corruption → privilege gain
    → asset extraction), or `unknown`? *Evidence:* the exploit shape implied by `code_snippet`/`rationale`.
    *Use:* scales how much slide/PoC effort a promotion will require; multi-step chains need the full slide deck,
    single-step ones a short one.

---

## Forbidden in this checklist
This worksheet must **never** record any of:

```
┌──────────────────── FORBIDDEN (belongs to humans + later, separate steps) ────────────────────┐
│  • final severity / severity rating          • valid / invalid / confirmed-bug verdict          │
│  • submit / reject decision                   • bounty / payout value estimate                  │
│  • autonomous exploitability conclusion ("proven exploitable")                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Note: category **6 ("concrete impact *hypothesis*")** and category **8 ("PoC *feasibility*")** are deliberately
hypotheses/estimates, never conclusions. "Chain completeness" describes *structure*, not *severity*. (Mirrors the
forbidden-field discipline of the evidence-bundle gate and the research judge design.)

---

## Promotion outcomes
Choose exactly one. The decision is the human's; the patterns below are guidance, not a formula.

| Outcome | Typical category pattern |
|---|---|
| **PROMOTE_TO_CHAIN_ANALYSIS** | evidence coherence met · reachability met/partial · a concrete impact *hypothesis* exists · counter-signals reviewed (and not fatal) · scope-relevant · confidence in next-step ≥ partial. (Chain completeness single- or multi-step both qualify.) |
| **NEEDS_MORE_EVIDENCE** | the story is plausible but `missing validation` / `missing_information` dominates, or reachability / affected-asset is `unknown`. Specify exactly what evidence is needed. |
| **HOLD_AS_WEAK_SIGNAL** | partial coherence, no fatal counter-signal, but not currently worth chain effort (low next-step confidence, unclear impact). Revisit if new evidence appears. |
| **ARCHIVE_AS_NOISE** | incoherent, or a counter-signal/known-FP/suppressed pattern explains it (e.g. a `needs_context` candidate matching a documented detector FP class), or out of scope. |

---

## Fill-in checklist block (copy per bundle)
```
PROMOTION CHECKLIST — research-only worksheet (routing_allowed:false, research_only:true)
candidate_id:        <from bundle>
source_corpus_hash:  <from corpus>
reviewer_alias:      <human>
date:                <UTC>

[ ] 1  evidence coherence ............ met / partial / unmet / unknown   — evidence: ____
[ ] 2  attacker reachability ......... met / partial / unmet / unknown   — evidence: ____
[ ] 3  affected asset/function ....... met / partial / unmet / unknown   — evidence: ____
[ ] 4  state/invariant affected ...... met / partial / unmet / unknown   — evidence: ____
[ ] 5  missing validation ............ met / partial / unmet / unknown   — evidence: ____
[ ] 6  concrete impact HYPOTHESIS .... met / partial / unmet / unknown   — hypothesis: ____
[ ] 7  counter-signals reviewed ...... met / partial / unmet / unknown   — evidence: ____
[ ] 8  PoC feasibility (estimate) .... met / partial / unmet / unknown   — note: ____
[ ] 9  scope/program relevance ....... met / partial / unmet / unknown   — evidence: ____
[ ] 10 duplicate/known-issue risk .... low / medium / high / unknown     — evidence: ____
[ ] 11 confidence in next-step ....... high / medium / low / unknown     — basis: ____
[ ] 12 chain completeness ............ single-step / multi-step / unknown — basis: ____

OUTCOME: PROMOTE_TO_CHAIN_ANALYSIS | NEEDS_MORE_EVIDENCE | HOLD_AS_WEAK_SIGNAL | ARCHIVE_AS_NOISE
RATIONALE (one paragraph, evidence-grounded, no severity/validity/submit/bounty): ____
```
This is a worksheet recorded by a human. It is not wired into any gate and routes nothing.

---

## Worked micro-examples (illustrative only — no severity/verdict)

**Example A — PROMOTE_TO_CHAIN_ANALYSIS** (permit asset-binding, `V3Vault._deposit`, revert-lend bundle):
coherence **met** (snippet shows `permit2.permitTransferFrom` with no `permitted.token == asset` check);
reachability **partial** (external deposit path); affected asset **met** (`IERC20(asset)`); missing validation
**met** (asset-binding absent); impact *hypothesis* **met** ("if a Permit2 sig for a different ERC-20 is accepted,
it could be credited as the protocol asset — to be tested"); counter-signals **partial** (router suppression
considered, not fatal); scope **met**; chain completeness **single-step**. → **PROMOTE**.

**Example B — ARCHIVE_AS_NOISE** (`needs_context` multicall candidate, beanstalk `balanceOfBatch`):
coherence **partial**; the candidate is a `needs_context` confidence on an ERC1155 batch view-getter — matches a
**documented detector FP class** (batch-getter leak), counter-signal is fatal, no state mutation. → **ARCHIVE_AS_NOISE**
(record the FP pattern in rationale).

---

## 1. Checklist summary
Twelve evidence-grounded categories + four outcomes turn an `hv-1`-labeled `READY_FOR_REVIEW` bundle into a
human decision: promote to chain analysis, gather more evidence, hold, or archive — using met/partial/unmet/unknown
markers tied to bundle/label evidence, never a severity/validity/submit/bounty/exploitability verdict.

## 2. Slide template summary
Bundles that reach `PROMOTE_TO_CHAIN_ANALYSIS` are explained with the reusable outline in
`bug_chain_slide_template.md` (13 sections, evidence-required-before-slide, unknown tags). Chain completeness
(single- vs multi-step) tells you how large that deck needs to be.

## 3. Recommended workflow
`hv-1 human label` → **this checklist** → outcome. If `PROMOTE_TO_CHAIN_ANALYSIS`: clone the slide skeleton from
`bug_chain_slide_template.md`, fill only evidence-backed slides, and let the Open Questions slide drive the PoC plan
/ next investigation. `NEEDS_MORE_EVIDENCE` returns to evidence gathering; `HOLD`/`ARCHIVE` exit the active queue
(with a recorded reason).

## 4. Safety constraints
Research-only; `routing_allowed:false`; assists a human, decides nothing. No final severity, valid/invalid verdict,
submit/reject, bounty estimate, or autonomous exploitability conclusion. Reasons only over existing bundle/label
evidence (no invention; unknowns stay unknown). Modifies no corpus / detector / gate / manifest / answer key /
submission system. Distinct from the production chains/CHAIN-XXX and submission engines.
