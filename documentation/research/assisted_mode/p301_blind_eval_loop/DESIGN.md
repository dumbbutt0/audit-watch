# P301 — DESIGN

## Goal
A standing **`/loop`** that grinds a 20-target queue one target per iteration to DISCOVER awarded findings the
pipeline MISSES, RECOVER them through the executed-PoC verifier (gates tight), and STAGE them so future runs catch
them — re-invokable before every real hunt.

## The loop (blind_eval_loop.py + ScheduleWakeup)
Per iteration: `next` (pick pending target) → `score` (mine the recall gap) → `recover` (a bounded batch) → advance
state → **ScheduleWakeup** (pace ~1 target/iter via config `pace_seconds`) until the queue is exhausted. State in
`outputs/loop_state.json` makes it resumable; re-running `/loop` continues where it left off.

- **score**: load the answer key per `key_source` — match_matrix (MISS/ADJACENT/PARTIAL rows = the recall gap),
  reveal_doc (kelp/ecg/salty reveal_score.json), or kb_assemble (holdouts → `needs_key_ingestion`, human ingests via
  ingest_ground_truth.py). The missed/under-recalled awarded findings are appended to
  `data/learning/_proposed/recall_gap_backlog.jsonl` (STAGED, promoted=false). For unrevealed holdouts the protocol
  is true-blind: run the frozen `p276_corpus_replay` surface, freeze+hash, THEN reveal+score.
- **recover**: for recall-gap loci with a `pocs/p301/<slug>__<id>/` PoC, run the P294 verifier (exploit OR
  logic_differential) → the **submission filter** (`submit` iff `validity_confirmed`). Record recovered /
  needs_execution.

## Why gates stay tight (the durable wiring)
- A recovered miss is only ever **confirmed by an executed PoC** (verifier = sole judge; submission filter); nothing
  auto-submits → confirmed-FP = 0 by proof. Recall widens; the FP gate is unchanged.
- The recall gap + every confirmed recovery is **STAGED** to `data/learning/_proposed/` (a surfacing-lens / pattern
  proposal) for **human promotion** (promote_learning.py). That is how a found miss stops being missed in future —
  the *discovery* layer learns it, the *gate* does not loosen.
- `ground_truth.jsonl` / promoted rules are never written by the loop (human-only).

## Pre-hunt use
The loop IS the standing recall safety-net: run `/loop` over the suite → clear the recall-gap backlog (recover /
needs_execution) → human-promote the proposals → then hunt under the submission filter (see PRE_HUNT_CHECKLIST.md).
