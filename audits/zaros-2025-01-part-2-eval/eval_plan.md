# Zaros Part 2 (CodeHawks 2025-01-zaros-part-2) — Blind Eval Plan

## Purpose
Prove Audit-Watch can go from a single CodeHawks bounty URL to a scored, **blind** eval report:
URL → local scope → deterministic audit target → frozen blind audit result → separately collected
answer key → scored eval report. Recall-first, API-free, advisory-confirm-only.

## Phases
- **Stage 0 — Workspace.** `audits/zaros-2025-01-part-2-eval/` with `contracts/ scope/ output/ answer_key/
  documentation/ logs/`. Record source URL + this plan.
- **Stage 1 — Scope.** From contest overview/scope + repo README only, resolve project, repo URL, commit,
  in/out-of-scope contracts, docs, severities, the selected-for-report + validated answer-key URL (recorded,
  not visited). Write `scope/program_scope.{json,md}`. Hard-stop if repo/commit unresolvable (no guessing).
- **Stage 2 — Download + freeze.** `git clone` the contest repo at the resolved commit, profile
  framework/solc, tag in/out scope, write `scope/contract_source_manifest.json` +
  `output/pre_audit_snapshot/MANIFEST.json` (sha256 of scope + sources + configs + lockfiles).
- **Stage 3 — Blind pipeline (recall-first, API-free).** analyze → /deep-analysis → analyze-resume →
  /ite-audit specialists → /coverage-sweep → deep-pass queue/campaigns → 5 recall lenses (cross-chain
  constants, token-standard, units/decimals, migration-flow, griefing/DoS) → full (gates + /triage) →
  in-session eval-ready root-cause dedup → **confirm-advisory only**. Finding nothing is acceptable; never
  invent findings.
- **Stage 4 — Freeze blind artifacts.** Snapshot + checksum the full blind set into
  `output/eval_ready/pre_answer_key_snapshot/` with `MANIFEST.json`. Flip
  `program_scope.answer_key_access_status`. **PAUSE for user go-ahead.**
- **Stage 5 — Answer key (post-freeze only).** Collect selected-for-report **validated** findings (+ final
  report); normalize/dedup by root cause; keep High/Medium/Low; invalid/non-validated → separate file;
  unclear → flagged for manual review.
- **Stage 6 — Score.** `final_scoring_set.json` = merged ∪ eval_findings. Score in-session:
  HIT / PARTIAL / ADJACENT / MISS / FP (+ side tags). Write scorecard, match matrix, comparison CSV,
  failure analysis. Frozen findings read-only.
- **Stage 7 — Reports.** `documentation/evals/zaros-2025-01-part-2/eval_report.md` (15 sections) +
  `scope_reconstruction.md`.
- **Stage 8 — Health checks.** coverage/min-confirm/confirm(eval)/api-free gates + lens pytest + `bash -n`.

## Blindness rules (non-negotiable)
1. **No answer-key material read before the Stage-4 snapshot exists.** Selected submissions, validated/judged
   issues, and the final report are off-limits in Stages 0–4. `answer_key_access_status` =
   `not_accessed_before_freeze` until then.
2. **Frozen blind findings are never mutated after the snapshot.** Answer-key knowledge is used only to
   *score*, never to edit findings.
3. **No double-counting of duplicate root causes.** Eval layer is root-cause-deduped.
4. **Recall measured honestly.** Advisory confirm only — the blocking submission-confirm is never used in the
   eval path; uncertainty routes DOWN, not out.
5. **API-free preserved.** Every LLM stage runs in-session via skills; `runtime_policy.api_free=true`.
   Network use limited to cloning the public repo + fetching public CodeHawks pages.

## Contamination firewall
The Stage-4 `pre_answer_key_snapshot/MANIFEST.json` (sha256 + mtime per file, note "frozen before
answer-key access") is the proof of blindness: it must predate every `answer_key/` file, and every frozen
artifact's sha256 must be unchanged at the end of the run.
