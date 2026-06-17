# P133 — FP-tendency & Human-Review Queue

## FP-tendency (not a final FP rate — human-deferred)
Of the 52 non-awarded boosted functions:
- **39 → needs_human** (on-class value/TVL/accounting review targets) — routed to the sanctioned queue, **not
  graded** valid/FP by the AI.
- **13 → clear** (non-on-class low-value helpers).
- **0 → speculative-reject** — no function warranted a fabricated high-severity flag.

**Key result: the boost's speculative-FP rate is 0.** It does not manufacture false positives; the entire
"noise" cost is **reviewer load** (39 queue items). Many of the 39 are the *same* `_getPositionTVL` class as the
awarded bugs (Aave/Camelot/Compound/Curve/Dolomite/Frax/Gearbox/Lido/UNIv3) — i.e. legitimate review targets,
some plausibly valid-unawarded. This is the intended widening, not noise.

`arithmetic`/`economic_attack` over-fire check (P129's concern): **none.** The boosted set is view value-getters;
no speculative arithmetic/economic flag was generated. The boost re-ranks read logic and adds no state-mutating
call paths.

## Human-review queue (sanctioned, audit-local)
Written 39 entries to `audits/noya-2024-04-eval/data/triage/human_review_queue.jsonl`, each with:
`finding_id`, `contract`, `function`, `file`, `reason` ("plausible value/TVL/accounting review target; valid-vs-FP
requires human + protocol depth"), `human_review_required: true`, `ai_verdict: "NONE (routed, not graded)"`.

A real human grading this queue would convert the 39 into measured valid/FP counts — that is the remaining step
to turn FP-tendency into a measured FP rate. The AI explicitly does **not** pre-judge them (non-negotiable:
human-review findings are not submission-ready on AI reasoning alone).

## What this measures vs doesn't
- **Measured here:** speculative-FP rate of the boost = 0; reviewer-load = 39 on-class items; 13 fast clears.
- **Not measured (human-deferred):** the true valid/FP split of the 39 on-class items — requires a human with
  protocol depth. This is the honest boundary of an AI-reviewer phase.
