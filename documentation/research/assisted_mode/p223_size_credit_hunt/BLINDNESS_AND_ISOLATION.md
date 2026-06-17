# P223 — Blindness & isolation (fork + seal proof)

## Why a fork was required
The existing `size-credit-2024-06` workspace was already eval'd **with** the answer key. Its `output/`
contains post-key artifacts that would contaminate a "blind" run: `coverage_dispositions.json` (prior
assignments), `deep_pass/candidate_queue.json` (prior specialist selections), `eval_ready/size_fresh/`
(answer key + `route_scorecard.json` + `candidate_H-03.json`), and `pre_answer_key_snapshot/`. Reusing any of
these would leak the answers.

## Fork (pristine workspace)
- `python scripts/audit_manager.py new size-credit-2024-06-blind --no-switch` → empty `output/` + `data/`.
- Source-only copy: `audits/size-credit-2024-06/contracts/2024-06-size/` →
  `audits/size-credit-2024-06-blind/contracts/2024-06-size/`. **39 `.sol`, 4431 LOC.**
  - Verified: 0 files matching `*answer_key* / *scorecard* / *finding_matches* / *candidate_H-* / *eval*`
    were copied.
- `meta.json.contract_path = contracts/2024-06-size` (matches original layout so the pipeline resolves source).
- `audit_manager.py switch size-credit-2024-06-blind` → active; `output` symlink → blind workspace;
  `output/` and `data/` confirmed **empty** (0 files) at hunt start.

## Seal (answer key never read until scoring)
- Answer key remains only in the original `size-credit-2024-06` workspace, witnessed at
  `sha256 8eacd80…a9c23` (see INTEGRITY_PRECHECK.md). It is opened only at Step 9 (post-freeze scoring), and
  the hash is re-checked then to prove it was unchanged/unread.
- Sealed paths (forbidden to read during Steps 2–8) enumerated in INTEGRITY_PRECHECK.md.
- Every discovery subagent is instructed to read only the blind workspace `contracts/` + freshly built
  coverage manifest, and explicitly forbidden from reading any sealed path or the original workspace.

## Isolation guarantees
- All hunt outputs land in the **blind** workspace (`output/` symlink) + the research namespaces
  (`output_research/`, `documentation/research/assisted_mode/p223_size_credit_hunt/`, `pocs/p223/`).
- The original `size-credit-2024-06/output/` (fingerprint `62901f774f9e`, 65 files) is **never written** and
  is re-checked byte-identical at END.
