---
name: recall-lab
description: "Eval-driven recall improvement against scored projects with known awarded findings. Runs one Recall Lab iteration: pick a sealed holdout, blind cold pass via /ite-audit with full coverage, reveal the answer key, adjudicate cold findings vs awarded by mechanism (STRONG/SAME_AREA/SUBSYSTEM_ONLY/MISSED), reincorporate each miss into the specialist prompts, and prove no regression. Activate when user says: run recall lab, eval against scored projects, improve recall, score a blind target, work on missed findings."
---

# Recall Lab — improve recall against scored projects

Eval-only. Never touches the real-world dashboard. Full reference: `documentation/recall_lab.md`.
Corpus + partition: `evals/corpus.json`. Mechanism taxonomy: `config/mechanism_classes.json`.

## Philosophy
- **Honest recall**: reveal the answer key LAST; adjudicate by mechanism; report holdout (genuine) separately
  from training (regression-only, contamination acknowledged).
- **The lever is the prompt**: misses on files that WERE read are reasoning gaps → fix by authoring a specialist
  agent §-section (research detectors stay advisory/un-wired). Misses on UNREAD files are coverage gaps → fix the
  mandatory sweep.
- **No regression, no circular scoring**: a prompt change may never drop a known training catch; a holdout that
  authored a section moves to training.

## Procedure (one iteration)

### 0. Pick a holdout
`evals/corpus.json` → `sets.holdout` with `scoreable:true` and an UNADJUDICATED `adjudication.json`, OR ingest a
fresh one: `python scripts/ingest_contest.py --help`. Confirm its `_sealed_answer_key/report.md` exists and you
have NOT read it.

### 1. Freeze
`python scripts/sandbox_check.py <source>` on the contracts. Keep the answer key sealed (do not open
`_sealed_answer_key/`).

### 2. Blind cold pass — MUST be full-coverage (not thin)
Run `/ite-audit` on the target with P315 mandatory full coverage. Record the scope denominator
(`audits/<id>/scope.json` — written by `ingest_contest.py --scope-json`, or hand-built) and **examine EVERY
in-scope substantive file** (deep for high value, `depth:"survey"` for low), logging each in
`merged_findings.json` `_coverage[]` (`{file, depth}`, file = contracts-relative). Do not peek at the answer key.
- **Full coverage is AUTO-ENFORCED (no manual step):** `eval-adjudicate`, `eval-loop next`, and `eval-loop done`
  automatically REFUSE on a scoped ingested contest until every substantive in-scope file is examined (recorded
  in `merged_findings._coverage[]`). You cannot reveal/adjudicate/bank a thin pass. Use
  `./run_pipeline.sh eval-loop cold-coverage <id>` only as a read-only progress check (which files remain).
  Rationale: the Cap/Numa experiments proved a thin pass manufactures phantom `read_file=false` "coverage-gap"
  misses and *hides the real reasoning gaps* (Numa fast-forward = recall 0.0, 12/16 in unread files).
- **Override (off by default, logged):** a deliberate fast-forward requires `AUDITWATCH_COVERAGE_OVERRIDE=1` (same
  var as the production gate) — it warns loudly and stamps `coverage_override:true` into `adjudication.json`.

### 3. Reveal + adjudicate
- **Precondition (auto-enforced):** full coverage — the reveal/adjudicate commands block otherwise. Only then reveal.
- `./run_pipeline.sh eval-adjudicate <id>` — scaffolds `output/eval_ready/adjudication.json` (parses awarded
  findings, lists your cold candidates, suggests token-overlap matches).
- NOW read `_sealed_answer_key/report.md`. For each awarded row, set in `adjudication.json`:
  `label` (STRONG/SAME_AREA/SUBSYSTEM_ONLY/MISSED), `matched_candidate_id`, `mechanism_class` (reuse a slug from
  `config/mechanism_classes.json` or add one), and `read_file` (was the bug's locus file examined in the cold
  pass — check coverage dispositions / merged_findings loci). Be rigorous and honest; an honest MISSED is worth
  more than an inflated SAME_AREA.

### 4. Reincorporate each miss
- `read_file=false` (coverage gap) → tighten the mandatory sweep / `generate_context_pack` so that file class is
  examined next time. No prompt section.
- `read_file=true` (reasoning gap) → author a new numbered §N in the correct `agents/<specialist>.md`:
  mechanism class + concrete trace checklist + FP guardrail + "(generalized from <project> miss, <id>)". Add the
  class to `config/mechanism_classes.json` (status `reincorporated`, point `prompt_section` at the new §). Add a
  `tests/<agent>_<class>` regression test. Stage learning via `python scripts/derive_learning.py` →
  `data/learning/_proposed/` (human-promoted; pinned `rejection_rules.jsonl` never auto-mutated).

### 5. Guard + score
- `./run_pipeline.sh eval-regression` — MUST stay green (no training catch dropped by your prompt edit).
- `./run_pipeline.sh eval-scoreboard` → `evals/scoreboard.md`. Report the holdout-recall delta and which
  mechanism classes moved.
- Move the revealed holdout project to `sets.training` in `evals/corpus.json`; if you added training catches, lock
  them in: `./run_pipeline.sh eval-regression --snapshot`.

## Looping protocol (one fire) — walk ALL past contests

To run the lab as a resumable loop over every past contest (autonomous /loop, one contest per fire):
`./run_pipeline.sh eval-loop build` once to build the work queue (`evals/loop_state.json`) — on-disk contests
with a cold pass + an answer key, ordered **highest reasoning-gap-miss-count first** (the prompt-addressable
leverage). Then each fire:

1. `./run_pipeline.sh eval-loop next` — mines the next contest (adjudicate `--auto` + stages reasoning-gap
   reincorporation candidates) and prints the **iteration packet**. It does NOT advance the cursor.
2. **Confirm before authoring.** The heuristic OVER-reports MISSED. For each reasoning-gap row in the packet,
   read the awarded finding text + your cold candidates and confirm it's a genuine miss (file read, mechanism
   missed). The heuristic only prioritizes; it is not ground truth.
3. Author the `agents/<specialist>.md §N` for each confirmed reasoning-gap miss (+ `config/mechanism_classes.json`
   entry + a `tests/` regression test), exactly as in step 4 above. Coverage-gap rows → fix the sweep, no §.
3b. **Work the PARTIALS → STRONG (do this every iteration, including between fires).** For each SAME_AREA /
   SUBSYSTEM_ONLY catch — the cold pass was already in the right function/area but missed the exact mechanism —
   diff your cold candidate against the awarded root cause and author the **completion** reasoning, not a new
   family: the precise step that converts "found the area" → "found the bug." These are the highest-leverage
   edits because the system was already looking at the right code. Tag the section `(… partial->strong)` and add a
   `PARTIAL->STRONG DISCIPLINE:` line stating the habit that would have closed it (e.g. "don't hedge a guard's
   effectiveness — finish the reachability trace"; "in a liquidation fn, scan every subtraction for underflow-DoS
   before down-grading to dust"; "past an accounting-drift observation, ask if any exit path ignores pending
   losses"). Register the class with the awarded example(s) and add a regression test.
3c. **Verify-to-drop discipline (anti over-retraction).** Dropping a flagged candidate as a false positive is as
   error-prone as hedging. When you retract, verify the EXACT mechanism you flagged — not an adjacent sub-aspect.
   (Cap M-5: candidate C-08 "slash uses past-epoch collateral → under-slash" was correct, but I dropped it after
   confirming the USD↔collateral *conversion* was consistent — the wrong thing; the real bug was the gameable
   `slashTimestamp`. The same verify-before-claim rigor that correctly killed C-05 wrongly killed C-08.) Rule:
   a drop requires disproving the specific flagged path, end-to-end.
4. `./run_pipeline.sh eval-regression` — MUST be green.
5. `./run_pipeline.sh eval-loop done <id> --sections "logic.md#17,..." --classes "slug-a,..."` — refuses on a
   red gate; otherwise banks the iteration and advances the cursor.
6. `./run_pipeline.sh eval-scoreboard`, then `ScheduleWakeup` for the next fire.

**Resume:** a fresh-context fire reads `evals/loop_state.json` (cursor + per-contest status) and continues —
re-running `eval-loop next` re-emits the current contest's packet if it was already mined.
**Drain → ingest:** when no on-disk contests remain pending, `./run_pipeline.sh eval-loop enqueue-ingest` prints
the protocol to add fresh past contests (Sherlock/C4 public reports → `ingest_contest.py` → blind cold pass).

## Output (report to the user)
```
Recall Lab — <project> (<set>)
  cold findings: N | awarded: M
  recall_of_surfaced: X.XXX  (strong-only Y.YYY)
  misses: A coverage-gap (unread) / B reasoning-gap (read)
  reincorporated: <agent>.md §N <mechanism-class>  [+ test]
  regression guard: PASS/FAIL | scoreboard: evals/scoreboard.md
```
