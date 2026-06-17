# P133 — Method

## Goal
Convert P131's **74% visibility ceiling** (8 awarded value_exit/oracle functions made deep-pass-visible by the
P130 boost, preserved through the P132 trims) into a **graded recall**, and characterize the **FP/noise** of the
60-fn trimmed boost-delta — using the detailed on-disk noya answer key.

## Honesty model (user-confirmed: AI-reviewer + answer-key recall + human queue)
I am the AI reviewer, so:
- **Recall = answer-key-objective, INFORMED-reviewer grade.** I have read
  `audits/noya-2024-04-eval/output/eval_ready/noya_fresh/answer_key.md` (specific root cause per finding). Grades
  are therefore an **upper bound** on a blind run — HIT/PARTIAL grades especially (a blind specialist would catch
  ≤ these); MISS grades are robust (if even an informed reviewer rates a bug "not surface-catchable," a blind one
  certainly misses). This is stated on every recall number.
- **FP = NOT graded by me.** Non-awarded confirmed-looking findings → the sanctioned `human_review_queue`
  (audit-local). Speculative flags that ICE/reject-first would reject → counted as FP-tendency. No AI valid/FP
  verdict on non-awarded findings (non-negotiable).
- No outcome fabricated; the answer key is the human/contest ground truth (manual_entry).

## Steps
1. Read the answer key + the source of the 8 boost-delta awarded functions (recall arm) and a categorized scan
   of the 52 non-awarded boosted functions (FP arm). Candidate set = P132 `noya_ON_trimmed.json` (boost-on,
   trimmed; 60 boosts = 8 awarded + 52 non-awarded).
2. **Recall arm:** per awarded fn, source-grounded specialist + ICE review → HIT / PARTIAL / MISS vs the specific
   answer-key bug, with rationale. Cross-checked against the answer key's own discoverability hypothesis.
3. **FP arm:** per non-awarded fn, disposition clear / needs_human / speculative-reject. needs_human (on-class
   value/TVL/accounting review targets) written to `audits/noya-2024-04-eval/data/triage/human_review_queue.jsonl`.
4. No production code touched (review/measurement only). Active audit never switched (direct file paths) — remains
   `quantamm-2024-12-eval`.

## Scope limits
- Informed, not blind (answer key read) → recall is an upper bound.
- FP final grade deferred to a human (39 queued).
- noya not pushed into `compute_metrics` recall (P129 showed `recall_on_valid` can't represent discovery recall;
  recall is kept in this grade matrix to avoid a circular/misleading number).
