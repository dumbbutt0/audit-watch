# Audit-Watch Strategic Review — 2026-06 (Next-Focus Decision)

> A point-in-time strategic assessment. Every claim cites documented evidence (evaluation reports, validation
> campaigns, `detector_registry.md`, `roadmap.md`, `research_methodology.md`, `platform_invariants.md`). No
> speculation about future detector performance; no assumption of out-of-scope detector behavior; no
> production-routing recommendation. Supersedes nothing; informs `roadmap.md`.

---

## Section 1 — Current State Assessment

**Strengths (documented):**
- Two RESEARCH-STABLE detectors with **0 high-confidence false positives** on their validation corpora —
  `multicall_invariant_v1` (20-target: 3 HIT / 2 PARTIAL / 2 ADJ / 2 MISS / 2 FP / 9 TN; all FPs `needs_context`;
  NARROW SCOPE CONFIRMED) and `permit_asset_binding` (20-target: 1 HIT / 19 TN / 0 FP; HIGH PRECISION VALIDATED).
- A repeatable, documented **7-stage lifecycle** that both detectors actually passed.
- Three composition layers **built + demonstrated end-to-end** (detectors → normalization → evidence-bundle gate),
  each with an enforced, tested refusal invariant; **56 tests, 9 frozen files 0-drift, fully un-wired**.
- Clean research/production separation; integrity reviews VERIFIED CLEAN.

**Weaknesses (documented):**
- **Composed-output usefulness is unmeasured** — the full chain has only a **6/6 READY demo**
  (`_evidence_demo/evidence_bundles.json`); no measurement that bundles are useful triage units for a human. The
  judge methodology flags its corpus as **"NOT collected."**
- **All detector validation is retrospective** (answer keys known in advance); no forward/blind exposure of the
  assembled platform.
- **Detector coverage is two narrow shapes** — ~8 documented uncovered multicall architectures (B1–B8) + 4 roadmap
  families; permit detector is Shape A only (recall 1/1).

**Maturity level:** **Intermediate research platform** — method proven and layered, end-to-end value not yet
measured on a real corpus.

---

## Section 2 — Information Gain Analysis (highest → lowest)

| Rank | Action | Learning | Risk | Effort |
|---|---|---|---|---|
| **1** | **Expand evaluation corpus** (freeze real READY bundles from detectors → normalization → evidence gate + blind human coherence/effort labels) | **HIGH** — first forward measurement of composed usefulness; tests `review_priority` + READY judgments; prerequisite the judge needs | **LOW** | LOW–MED |
| 2 | Real bug-bounty / live-corpus eval | HIGH | **HIGH** (premature; routing pressure) | HIGH |
| 3 | Research judge prototype | MED — **un-evaluable today** (corpus not collected) | MED (Goodhart) | MED |
| 4 | PoC-feasibility layer | LOW now — consumes nonexistent judge output | MED | MED |
| 5 | Another detector family | LOW–MED — re-confirms a twice-proven method; remaining families low-scored (3/2/1.5) w/ precision traps | MED | MED–HIGH |
| 6 | Bridge research → production | LOW + explicit non-goal | **HIGH** | HIGH |
| 7 | Improve existing detectors | LOW — VERIFIED CLEAN; broadening = non-goal | LOW | LOW |

---

## Section 3 — Strategic Options

**Path A — Detector Expansion** (internal-call state-reuse / ERC2771 / msg.value).
*Benefits:* widens recall toward documented blind spots; tests method on a 3rd family. *Risks:* highest-value
remaining shapes are absence-based/contextual (precision traps); evolution doc scores them 3/2/1.5 and recommends
freezing the core + narrow companions. *Unknowns:* whether any companion clears the 0-high-conf-FP bar (must not
assume). *Likely outcome:* a 3rd narrow detector re-confirming a proven method while the composed-output question
stays open.

**Path B — Platform Expansion** (judge / PoC-feasibility / readiness).
*Benefits:* extends the architecture toward assessment. *Risks:* the judge is designed but **un-evaluable** (corpus
NOT collected); building it now yields an artifact we can't grade, and grading it wrong reopens the Goodhart trap.
*Unknowns:* whether bundles are coherent enough for a judge to add value (never measured). *Likely outcome:*
premature; code ahead of the measurement that justifies it.

**Path C — Real-World Exposure** (shadow-mode / live corpus / controlled deployment).
*Benefits:* the only true external signal. *Risks:* composed usefulness unmeasured beyond a demo; skips the cheap
internal measurement; invites routing pressure (non-goal). *Unknowns:* whether bundles survive un-keyed real
targets. *Likely outcome:* expensive, high-variance learning a corpus step would de-risk first.

---

## Section 4 — Bottleneck Identification

**VALIDATION BOTTLENECK.** Evidence: composed output measured only by a 6/6 demo; the judge is explicitly blocked
on a corpus ("Corpus: Not Collected"); all evidence to date is retrospective per-detector answer-key validation;
the Self-Calibration principle ("a system that cannot measure its own FP/recall cannot be tuned") — the platform
measures per-detector FP but **cannot yet measure triage usefulness**. Not a detector bottleneck (method proven
twice; remaining families low-scored), not a platform-architecture bottleneck (3 layers built), not yet a
real-world bottleneck (premature).

---

## Section 5 — Recommended Next Focus

**EXPAND EVALUATION CORPUS** — freeze a real READY_FOR_REVIEW evidence-bundle corpus by running the two
RESEARCH-STABLE detectors → normalization → evidence-bundle gate over already-examined (retrospective,
source-on-disk) targets, with **blind, human-authored** coherence / worth-PoC-effort labels.

*Justification:* HIGH information gain (first forward measurement; tests `review_priority` + READY judgments);
unblocks and makes-gradable the judge (its documented prerequisite); lowest opportunity cost vs a 3rd detector
(re-confirms a proven method), a judge prototype (un-evaluable today), or live exposure (premature). Labels are
human-authored (AI must not fabricate; separate from production `ground_truth.jsonl`) and scored on coherence/effort,
**never a bug answer-key** (Goodhart trap). Nothing routed; no detector scope broadened.

---

## Section 6 — 30-Day Roadmap

- **Week 1 — Build & freeze the corpus.** Pick already-examined targets (source on disk in `audits/`). Run the two
  detectors → `normalize_research_findings.py` → `evidence_bundle_gate.py`; collect READY_FOR_REVIEW bundles into a
  frozen, content-hashed research corpus (a few dozen). Compute judge-free structural stats (completeness,
  `review_priority` distribution, detector mix). Integrity-check (un-wired, 0-drift). *No judge.*
- **Week 2 — Blind human annotation.** Each bundle labeled: (a) coherence on the judge's ordinal scale, (b) "worth
  PoC effort?", (c) reviewer counter-arguments. Human-authored, separate store; capture inter-rater agreement if
  >1 reviewer.
- **Week 3 — Measure composed-output usefulness.** Answer-key-free: **triage lift** (does `review_priority` order
  surface human-"worth-effort" bundles earlier than random?) + **evidence sufficiency** (did READY bundles give
  enough to judge coherence?). Document honestly, incl. negatives.
- **Week 4 — Decision gate + write-up.** *Are composed outputs human-useful?* If **yes** → judge prototype becomes
  the justified, gradable next step (start with mechanical grounding-fidelity). If **no/partial** → fix
  evidence/normalization first; the corpus says where. Either branch = high-value learning. Update roadmap/registry.

---

## Section 7 — What Not To Do

- Don't build the judge prototype yet (corpus NOT collected → un-evaluable; Goodhart risk).
- Don't build a 3rd narrow detector now (remaining families scored 3/2/1.5 + precision traps; depth, not surface,
  is the bottleneck; re-confirms a proven method).
- Don't broaden either RESEARCH-STABLE detector beyond validated scope (non-goal; breaks the precision claim).
- Don't re-run the multicall/permit validation campaigns (VERIFIED CLEAN; 0 new info).
- Don't jump to live bug-bounty exposure (premature; routing pressure).
- Don't wire anything into production / no routing (non-negotiable).
- Don't evaluate any future judge against bug validity/severity/accepted-outcome/PoC-as-oracle (forbidden eval
  targets).

---

## Final Output

- **Current Platform Maturity:** intermediate research platform
- **Primary Bottleneck:** validation — composed output (detectors → normalization → evidence bundles) never
  measured for human triage usefulness beyond a 6-bundle demo; that missing measurement blocks the judge and any
  real-world step.
- **Highest-Leverage Next Action:** expand the evaluation corpus — freeze a real READY_FOR_REVIEW bundle corpus
  with blind, human-authored coherence / worth-effort labels.
- **Why:** first forward measurement of the assembled platform's value; the documented prerequisite that unblocks
  and grades the judge; lowest-risk action that converts every downstream choice into an evidence-based decision.
- **Expected Information Gain:** high
- **Expected Risk:** low
