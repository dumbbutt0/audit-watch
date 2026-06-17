# Recall Lab — eval-driven recall improvement against scored projects

The Recall Lab measures the pipeline's **blind recall** against projects with known ground-truth findings
(public audit reports) and turns every miss into a durable improvement to the specialist prompts. It is
**eval-only**: nothing here affects the real-world dashboard (`documentation/real_world_results.json`,
`compute_metrics.py` default) — all eval artifacts live under `evals/`.

## Why
Real-world hunting yields mostly honest negatives (reputable targets are well-built), so it rarely exercises
the system's bug-finding ceiling. Scoring cold passes against *awarded* findings does — and lets us prove that
a prompt change actually raises recall without regressing what we already catch.

## The corpus (`evals/corpus.json`)
- **TRAINING** — pre-cutoff scored projects. Prior-knowledge contamination is acknowledged, so these are used
  **only for the regression guard** (don't break a known catch). They do NOT count as genuine recall.
- **HOLDOUT** — genuinely post-cutoff blind targets. This is the **honest** recall number (the headline).
- **One-way rule:** once a holdout project's report has been revealed and used to author a prompt section, move
  it to `training` in `corpus.json`. Never score a prompt on the project that authored it (anti-circular).

## Metrics
- `recall_of_surfaced` = (STRONG + SAME_AREA + SUBSYSTEM_ONLY) / awarded — the gate metric.
- `strong_only` = STRONG / awarded — reported alongside (genuine, root-cause-matching catches).
- **Per-mechanism-class recall** (`config/mechanism_classes.json`) — which expert-bug *families* we
  systematically miss, across projects. The real target for prompt work.
- **Miss split**: `read_file=false` = coverage gap (file unread → tighten the mandatory sweep);
  `read_file=true` = reasoning gap (file read, mechanism missed → author a prompt section). This split is the
  single most important triage.

## Adjudication taxonomy (scored in-session, by mechanism)
- **STRONG** — same root cause, mechanism, AND impact as the awarded finding.
- **SAME_AREA** — same component/region, different or partial mechanism.
- **SUBSYSTEM_ONLY** — touched the subsystem/concept but not the specific mechanism.
- **MISSED** — not surfaced. (`read_file` distinguishes coverage vs reasoning.)

## One iteration (the loop)
1. **Pick a holdout** target (sealed answer key not yet read). Grow the pool via `scripts/ingest_contest.py`.
2. **Freeze**: `sandbox_check.py` the source; keep the report sealed under `audits/<id>/_sealed_answer_key/`.
   Then **mechanically blind it** (T4): `./run_pipeline.sh eval-seal <id>` moves the sealed key OUT of the repo
   (to `~/.audit_watch_keyvault/`) so the cold-pass agents physically cannot read it; `assert_blind.py check <id>`
   exit 0 confirms blind. `eval-adjudicate` auto-`reveal`s the key and runs a leakage backstop before scoring.
3. **Blind cold pass** via `/ite-audit` with P315 mandatory full coverage (`build_coverage_manifest` +
   `/coverage-sweep`). Writes `output/merged_findings.json`. Do NOT read the answer key first.
4. **Reveal + adjudicate** (in-session, by mechanism): `run_pipeline.sh eval-adjudicate <id>` scaffolds
   `output/eval_ready/adjudication.json` (parses awarded findings, lists candidates, suggests matches). Fill each
   awarded row's `label`, `matched_candidate_id`, `mechanism_class`, and `read_file`.
5. **Reincorporate each miss:**
   - `read_file=false` (coverage gap) → tighten the mandatory sweep / context-pack so the file is examined.
   - `read_file=true` (reasoning gap) → author a new numbered §N in the right `agents/<specialist>.md`
     (pattern: mechanism class + concrete trace checklist + FP guardrail + "(generalized from <project> miss,
     <id>)"), add the class to `config/mechanism_classes.json`, and add a `tests/<agent>_<class>` regression
     test. Stage learning artifacts via `scripts/derive_learning.py` → `data/learning/_proposed/` (human-promoted;
     pinned `rejection_rules.jsonl` never auto-mutated).
6. **Guard regressions:** `run_pipeline.sh eval-regression` — must stay green (no training catch dropped). When a
   change adds new training catches, lock them in with `eval-regression --snapshot`.
7. **Update the scoreboard:** `run_pipeline.sh eval-scoreboard` → `evals/scoreboard.md`; record the holdout-recall
   delta and per-mechanism-class movement. Move the revealed holdout project to `training`.

## Honesty invariants
- The real-world dashboard stays real-world-only and byte-behavior-identical; eval numbers live only in `evals/`.
- `ground_truth.jsonl` is human-only with provenance (`ingest_ground_truth.py`); AI never writes outcomes.
- `auto_promote_learning` stays `disable_in_eval: true`; prompt §-sections are human-reviewed before they count.
- Reveal-last + holdout→training one-way = no circular scoring. Training is regression-only, never genuine recall.

## Detecting misses in ALREADY-EVALUATED contests
`adjudicate.py` loads the awarded set from whatever artifact a contest has — `_sealed_answer_key/report.md`
(C4/Sherlock), or `output/eval_ready/answer_key_normalization.json` (prior-eval format), or
`data/evaluation/ground_truth.jsonl` — so any contest with a cold pass (`output/merged_findings.json`) can be
scored. `--auto` runs a CONSERVATIVE heuristic miss-detector (function + mechanism evidence required for recall
credit; file/contract overlap alone only sets `read_file`; biased toward MISSED). Auto labels are advisory:
`source: "auto-heuristic"`, confidence-tagged, **excluded from the confirmed headline and never protected by the
regression gate**; they persist across plain re-runs and are overridden by any human/seed label. The scoreboard
surfaces them in a dedicated "Auto-detected misses" section.
```
run_pipeline.sh eval-detect-misses <id>            # heuristic miss-detection for one already-evaluated contest
run_pipeline.sh eval-detect-misses --all-evaluated # batch over every contest with a cold pass + an answer key
```

## Looping protocol over ALL past contests (resumable; one contest per /loop fire)
`scripts/recall_lab_loop.py` (`run_pipeline.sh eval-loop ...`) walks every past contest, runs the methodology on
each, and turns its misses into prompt improvements one contest at a time. State: `evals/loop_state.json`
(`{cursor, stats, queue:[{id, status, misses, reasoning_misses, awarded, sections_authored, mechanism_classes}]}`;
status `pending → mined → reincorporated`).

- `eval-loop build` — (re)build the queue from on-disk contests with a cold pass + an answer key (any format),
  ordered **highest reasoning-gap-miss-count first** (prompt-addressable leverage; coverage-gap misses are a
  sweep fix, not a prompt fix). Idempotent — preserves status + authored work.
- `eval-loop next` — mine the next contest (`adjudicate --auto` + `derive_learning --from-adjudication`) and emit
  the **iteration packet** (reasoning-gap misses by mechanism class → target `agents/<specialist>.md §`). Does
  NOT advance the cursor. The heuristic OVER-reports MISSED → **confirm each against the awarded text before
  authoring** (it prioritizes, it is not ground truth).
- author the §s in-session → `eval-regression` (must be green) →
  `eval-loop done <id> --sections ... --classes ...` (refuses on a red gate; banks + advances).
- `eval-loop status` — queue + cursor + progress. `eval-loop enqueue-ingest` — when the on-disk backlog is
  drained, print the protocol to ingest fresh past contests (Sherlock/C4 public reports → `ingest_contest.py` →
  blind cold pass → re-`build`).
- **Full coverage is AUTO-ENFORCED on the ingestion path (always).** `eval-adjudicate <id>`, `eval-loop next`,
  and `eval-loop done` automatically REFUSE to reveal/adjudicate/bank a SCOPED ingested contest (one with
  `audits/<id>/scope.json`, written by `ingest_contest.py --scope-json`) until every substantive in-scope file is
  examined and logged in `merged_findings._coverage[]` (`require_full_coverage` in `recall_lab_loop.py`). Archived
  on-disk heuristic contests (no scope.json) are NOT gated — their `--auto` miss-detection is unaffected.
  - Override (off by default, identical to the production gate): `AUDITWATCH_COVERAGE_OVERRIDE=1` — warns loudly
    and stamps `coverage_override:true` + the examined/total counts into `adjudication.json` (auditable, not silent).
  - `eval-loop cold-coverage <id>` remains as a **read-only progress check** (lists unexamined files); it is no
    longer the enforcement mechanism. Rationale: the Cap/Numa experiments proved a thin pass manufactures phantom
    `read_file=false` coverage-gap misses and hides reasoning gaps (Numa fast-forward = recall 0.0, 12/16 in
    unread files). Cold passes MUST be full-coverage, never thin.

Drive it as an autonomous /loop: each fire runs `eval-loop next`, authors, guards, `eval-loop done`, then
`ScheduleWakeup` for the next; a fresh-context fire resumes from `loop_state.json`.

## Commands
```
run_pipeline.sh eval-loop build|status|next|done <id>|enqueue-ingest  # resumable loop over ALL past contests
run_pipeline.sh eval-adjudicate <id>|--all   # build/refresh adjudication.json (human/seed labels)
run_pipeline.sh eval-detect-misses <id>|--all-evaluated  # heuristic miss-detection (any answer-key format)
run_pipeline.sh eval-scoreboard              # honest recall scoreboard (+ auto-detected-misses rollup)
run_pipeline.sh eval-regression [--snapshot] # regression guard / re-baseline (protects confirmed catches only)
python scripts/ingest_contest.py ...         # add a fresh holdout (see --help)
```
