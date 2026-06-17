# P256 — Subtle Accounting/State Mechanism-Selection Stress Test — SETUP

## Purpose
P254/P255 validated the five completion operations for **impact completion** but not for **subtle mechanism
selection** (P255 bakerfi reproduced the failure: right function, wrong mechanism). P256 tests whether a
**pre-completion Mechanism Selection Gate** can pick the awarded mechanism among ≥3 plausible mechanisms on
**subtle accounting/state bugs only**. The five completion ops are **unchanged**; the gate is the only addition.
Output diagnoses whether the bottleneck is **discovery**, **ranking**, or **completion** → which harness to build.

## The five completion operations (UNCHANGED from P254/P255)
**STATE_TRANSITION_SIMULATION (STS)** · **ADVERSARIAL_ACTOR_SUBSTITUTION (AAS)** · **TERMINAL_STATE_EVALUATION
(TSE)** · **INVARIANT_DELTA_COMPUTATION (IDC)** · **CROSS_CALL_IDENTITY_TRACKING (CCIT)**.

## Mechanism Selection Gate (NEW; pre-completion) — 8 scoring dimensions
For each locus, enumerate ≥3 plausible mechanisms and score each H/M/L on:
1. **controllability** — can an attacker actually choose the input/state/timing?
2. **value-delta clarity** — is there a measurable asset/debt/share/reward delta?
3. **victim/gainer separation** — can we name who loses and who gains?
4. **protocol comparand** — sibling fn / comment / invariant / formula / reference showing intended behavior?
5. **terminality** — does the bad state persist, strand value, or permit extraction?
6. **amplification** — repeat / lever / flash-loan / loop / scale?
7. **simplicity** — fewer speculative assumptions than competing mechanisms?
8. **award-likeness** — matches known high-signal bug shapes (without the answer key)?
Then per locus: `SELECTED_MECHANISM`, `RUNNER_UP_MECHANISM`, `REFUTED_MECHANISMS`, `AWARDED_LIKENESS_REASON`,
`WHY_SELECTED_OVER_RUNNER_UP`, `WHAT_WOULD_FALSIFY_THE_SELECTED_MECHANISM`.

## Targets (operator-approved: plaza + concrete; subtle-accounting/state; math/typo/mechanical EXCLUDED)
| contest | architecture | in-scope fns | prior exposure (excluded areas) |
|---|---|---|---|
| `plaza-finance-2024-12-fresh` | leveraged bond/leverage-token AMM (Pool/Auction/BondToken/PreDeposit) | ~136 | p196 infra only (cleanest) |
| `concrete-2024-11-fresh` | multi-strategy yield vault (Vault/WithdrawalQueue/RewardManager) | ~293 | p242 Family-A (deposit reentrancy) + Family-B (max*/preview*-convert), **unverified vs key** → those families excluded |

Source under `audits/<id>/_src/…`. No local keys → reveal **post-freeze** via WebFetch/WebSearch of each
contest's published findings (platform-agnostic; WebSearch fallback if a report exceeds 10 MB).

**Hard locus-exclusion (subtle-only):** no obvious copy-paste typos, no missing-revert/silent-zero, no single-line
math errors, no single-plausible-mechanism loci.

## Method (isolated; no active-audit touch)
Active audit `size-credit-2024-06-blind` not switched. Checkpoints run via `--manifest`/`--out` into `outputs/`
(invariants re-verified). Base candidates = isolated/manual blind read. Gate + ops performed by hand.
- plaza checkpoints: accounting 44 recs (Pool _create/_redeem/simulate*, Auction, BondToken, PreDeposit), ST 31.
- concrete checkpoints: accounting 106 recs (Vault deposit/withdraw/convert/fees, WithdrawalQueue, StrategyBase), ST 30.

## Per-contest phase order (freeze-before-reveal)
1. `<contest>_BASE_FREEZE.md` (candidates + checkpoint records + three-way tag + command basis).
2. `<contest>_MECHANISM_GATE.md` (loci + no-hindsight lock + ≥3 mechanisms + 8-dim scoring + selected/runner-up/refuted/why/falsifier).
3. `<contest>_PROCEDURE_OUTPUTS.md` (5 ops on selected AND runner-up + chain status).
4. hash all three before opening the key.
5. `<contest>_REVEAL_AND_SCORE.md` (classify awarded mechanism: NOT_ENUMERATED / ENUMERATED_BUT_RANKED_TOO_LOW /
   RANKED_HIGH_BUT_NOT_COMPLETED / COMPLETED_CORRECTLY).

Then `SELECTION_DIAGNOSIS.md` (discovery vs ranking vs completion) + `VERDICT.md` (A–F).

## Standing caveats
n small; no PoCs; training-confound (same operator) → credited signal = gate-selected-and-completed-pre-reveal
matching the awarded mechanism. No softening toward A.
