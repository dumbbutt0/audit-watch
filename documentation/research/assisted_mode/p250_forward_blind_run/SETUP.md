# P250 — Setup & Frozen-System Attestation

Forward blind run of the frozen post-P249 system on a genuinely unseen target.

## Target (operator decision: fresh + web-fetched key, 1 contest)
`spectra-2024-02-holdout` — ERC5095 PrincipalToken/YieldToken yield-tokenization vault (PT/YT, IBT 4626,
RayMath). 585 manifest items / 111 in-scope / 104 critical. Accounting-rich (token 94, accounting 34,
decimals 9). **Unseen attestation:** no `findings_*.json`, no `_sealed_answer_key`, no `*REVEALED*` marker,
no local key — never hunted or revealed in this program; not in the P246/P240/P241 sets nor the P249 tuning
set (kleidi/centrifuge/munchables). Answer key will be WEB-FETCHED only after both freezes.

## Frozen system (unchanged for the run)
- P245 coverage+reasoning gate ENABLED · accounting checkpoint ENABLED (run via `accounting_checkpoint_audit.py
  --manifest`) · **NO state-transition / cross-contract checkpoint**.
- Forbidden files byte-identical at start (re-verified at end):
  `c1af70e1` dashboard_sync · `c095c426` deep_trace · `2a15169a` min_confirm_gate · `afc481c9` confirm_gate ·
  `ae55eb80` validate_p208. No code/config edits this phase. Active audit `size-credit-2024-06-blind`
  unchanged (no switch).

## Procedure
Blind base hunt (read source, no checkpoint) → freeze+hash → checkpoint pass (run checkpoint, answer the 6
questions, construct candidates) → freeze+hash → reveal (WebFetch) → score base vs +checkpoint → 6 metrics.

## Honesty caveat (stated up front)
spectra is a public Code4rena contest → LLM training exposure is possible, so absolute recall is an UPPER
BOUND. The confound-light signals are the **checkpoint-attributable delta, question-volume, time, and FP** —
those measure the tool's behavior, not my prior knowledge. A carefully-read small contest may mean the base
hunt already catches the main accounting issues, leaving the checkpoint a small marginal contribution — that
is itself an honest forward-blind result and will be reported as-is.
