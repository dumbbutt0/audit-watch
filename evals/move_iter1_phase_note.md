# Recall-Lab phase note — Move iteration 1

- **Audit added:** Sui-AMM-swap (OmniBTC), MoveBit Nov-2022 · `sui-amm-swap-2022-11-eval`
- **Language:** Move (Sui) · constant-product AMM · 7 in-scope modules (~1.8k LOC) · vulnerable commit `2d33538`
- **Awarded findings:** 7 (6 Medium + 1 Major→High). Source code + public report both public.

## Baseline (honest blind cold pass)
- recall_of_surfaced = **5/7 = 0.714**, 7/7 files examined.
- 2 misses, both **reasoning gaps** (files opened, mechanism not flagged):
  - **M-1** — `swap_out` never re-asserts the constant-product K invariant post-swap (specialists concluded
    "k grows, sound" and didn't flag the *absent* guard).
  - **M-4** — event-emit helpers are `public fun` → anyone forges protocol events (visibility audit covered
    money-movers, skipped side-effecting emitters).
- NOTE: a first contaminated pass (prompts leaked the answer key) was discarded → `output/_contaminated_pass/`.
  The 0.714 number is from a re-run with neutral, generic-checklist-only prompts.

## Logic added (smallest generalizable)
- `agents/move_clmm_math.md` **§7** — "Missing post-mutation conservation-invariant re-check": for every
  state-mutating math path, flag the ABSENCE of a post-state invariant assertion (constant-product K / analogous)
  even when current pricing is conservative. + FP guardrail (Med/Low unless extraction traceable).
- `agents/move_object_capability.md` **§7** — "Side-effecting helper visibility": the visibility audit must
  cover event emitters / log/notify / state-touching helpers, not just balance mutators; a `public` emit =
  forgeable events. + FP guardrail (pure views are fine; only side-effecting helpers).
- `config/mechanism_classes.json` — two classes added, `language:move`, `status:reincorporated`:
  `move-constant-product-invariant-recheck`, `move-public-helper-visibility` (awarded_examples → this eval).
- `tests/coverage/test_sui_amm_swap_reincorporation.py` — locks both §-sections + both class registrations.
- Generalizable beyond this audit (any Move AMM/DEX/protocol with swaps + event emitters); no answer-key strings,
  no hardcoded function names in production prompts.

## Final score (post-fix, neutral blind re-run of the two affected specialists)
- recall_of_surfaced = **7/7 = 1.0**, strong_only = 1.0, 0 misses.
- The improved generic prompts caught M-1 (AR-001, citing §7) and M-4 (AC-001, citing §7) with **no hint** from
  the orchestrator → honest improvement.

## Simple-project 100% gate
- ✅ 100% awarded hit (7/7) · ✅ 0 false READY (extra candidates double-fee + withdraw-AND-gate are Low/Med,
  not submission-ready) · ✅ reportable candidate (fn + mechanism + evidence) for every hit · ✅ change wired into
  the normal `/ite-audit` move branch (prompts + production config), not just the eval script.

## Regression
- `eval-regression`: **PASS** — all 16 protected training catches still recalled (move-only change; no Solidity
  regression).
- `pytest tests/coverage/`: 304 passed, **1 pre-existing unrelated failure** —
  `test_rust_manifest.py::test_rust_manifest_end_to_end` (Rust manifest parser returns 0 items for a Rust sample;
  `build_coverage_manifest.py` has no reference to mechanism classes / move agents → not caused by this change).

## Remaining caveats / carry-forward
1. **Rust-manifest parser is broken in this environment** (`build_coverage_manifest` yields 0 items for `.rs`).
   This BLOCKS the next (Rust) iteration's cold pass and must be fixed/diagnosed first.
2. **Infra gap:** `eval_scoreboard.py` routes Move/Rust out of the Solidity board but never writes
   `evals/move_scoreboard.md` nor aggregates `move-*` per-class recall — the honest Move number currently lives
   only in `adjudication.json`. Candidate generalizable fix (emit per-language scoreboards keyed on adjudication
   `language`).
3. `sandbox_check.py` is Solidity-extension-only (0 `.move` scanned) — used a manual injection sweep here.
4. cutoff=pre (2022 public audit): honest blind measurement for this project, but regression-value not headline
   holdout recall per recall-lab honesty rules. Moved holdout→training (one-way rule: revealed + authored).

## Next target language: **Rust** (prefer Solana/Anchor) — fix caveat #1 first.
