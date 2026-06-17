# P301 — PRE-HUNT CHECKLIST (the standing recall safety-net)

Run this before every real hunt. It catches awarded-finding classes the pipeline would miss, while the FP gates stay
exactly as tight (the executed-PoC submission filter is unchanged).

## How to run the /loop
The loop is self-paced (ScheduleWakeup). To run it manually / drive iterations:
```
python scripts/research/blind_eval_loop.py next          # the next pending target
python scripts/research/blind_eval_loop.py score  <target>   # mine the recall gap -> staged backlog
python scripts/research/blind_eval_loop.py recover <target>  # verify recall-gap PoCs (gates tight)
python scripts/research/blind_eval_loop.py state         # progress + confirmed-FP (must be 0)
```
Or invoke `/loop` with the task "advance the blind-eval suite" — each iteration does next→score→recover for one
target then ScheduleWakeup's the next (pace = config pace_seconds, default 1200s), resuming from loop_state.json.

## Checklist
1. **Run the suite** (`/loop`) until `state` shows all targets `scored`/`recovered`/`needs_key_ingestion`.
2. **Recall gap** → `data/learning/_proposed/recall_gap_backlog.jsonl` (the missed/under-recalled awarded findings).
   For each, the loop attempts recovery via an executed PoC; build PoCs (spawned subagents, Tier-C; exploit OR
   logic_differential) for `needs_execution` loci across iterations.
3. **Gates tight**: every recovery is verifier-confirmed (executed exploit/logic) and passes the submission filter;
   confirmed-FP must be 0. Nothing auto-submits.
4. **Human-promote** the recovered findings + the staged learning proposals (`promote_learning.py`) so the *surfacing*
   layer catches those classes next time. (AI never writes ground_truth / promotes — human-only.)
5. **kb_assemble targets** (spectra/predy/munchables/vultisig/decent/dittoeth/basin): human-ingest their public
   findings (`ingest_ground_truth.py`) to turn `needs_key_ingestion` into a scoreable key.
6. **Hunt** under the submission filter: surface wide → confirm by executed PoC → submit iff confirmed → everything
   else (incl. high/critical-novel) → human review. Submission stays human-gated.

## Invariant
This loop only ever WIDENS recall and STAGES proposals. It never loosens a gate, writes an answer key, or submits.
