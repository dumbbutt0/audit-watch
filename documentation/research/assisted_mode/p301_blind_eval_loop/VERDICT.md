# P301 — VERDICT

## A — STANDING_BLIND_EVAL_RECALL_GAP_LOOP_BUILT_AND_VALIDATED

A self-paced `/loop` that discovers the pipeline's missed awarded findings and recovers them at gates-tight is built,
state-driven, and validated end-to-end.

### A-criteria — all met
- **Standing 20-target queue + resumable loop** (`blind_eval_loop.py` + `research_blind_eval_suite.json` +
  `loop_state.json`): next → score → recover → ScheduleWakeup.
- **Iteration 1 ran end-to-end** on real targets: **mined 58 missed/under-recalled awarded findings** (revert-lend
  31, panoptic 22, silo 5) into the staged backlog, **recovered 2** (panoptic M-01, silo M-06) via executed PoC at
  **confirmed-FP = 0**, submission filter 0 leaks.
- **Gate-tight wiring**: recoveries confirmed only by executed PoC; recall gap + recoveries STAGED to
  `_proposed/` (promoted=false) for human promotion; nothing auto-submitted; ground_truth + promoted rules + answer
  keys + contest source unchanged; verifier + forbidden 5 byte-identical; symlink unchanged.
- **Pre-hunt checklist** documents the standing procedure (run /loop → clear backlog → human-promote → hunt under the
  filter).

### What this gives the workflow
A repeatable recall safety-net: before each hunt, the /loop surfaces what the pipeline would miss (mined from answer
keys), recovers what it can by executed PoC, and stages the rest for human promotion — recall widens over time, the
FP gates never loosen.

### Next
Run `/loop` to grind the full queue (build PoCs for the 56 needs_execution gap loci over iterations); human-ingest
the 7 kb_assemble keys; human-promote recoveries + proposals; re-run before each hunt. Submission human-gated.
