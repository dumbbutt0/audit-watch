# notional — Phase 4: Ranking ablation (PRE-REVEAL, FROZEN)

Each locus ranked under Profile A (original P256 gate), Profile B (messy-reconciliation weighted), Profile C
(runner-up challenge). Winners committed before reveal.

## N-L1
- **Profile A winner: M1** (virtual-share rounding) — tidy, high award-likeness/simplicity in the P256 scoring.
- **Profile B winner: M2** (escrow-excluded-from-supply-not-balance) — reconciliation mismatch + value
  redistribution + state terminality score highest under B's reweighting; M1 demoted (low delta, tidy).
- **Profile C winner: M2** — A's top (M1) vs runner-up M2: M2 has larger/more-terminal delta, clearer victim
  (escrowed withdrawer), better award explanation (a real value-redistribution), survives refutation (the balance
  genuinely retains escrowed yield tokens). M2 overtakes with source-backed reason (effectiveSupply subtracts
  escrow but balance does not).
- runner-up: M3. why winner beat runner-up: M2 has a concrete invariant comparand + bounded assumptions vs M3's
  time-dependence. falsifier: withdraw request removes yield tokens from balance synchronously.

## N-L2
- **Profile A winner: M1** (Taylor approx error) — tidiest/math-shaped.
- **Profile B winner: M2** (accrue-timing fee dodge) — accounting-intent-violated-despite-locally-plausible-math +
  controllability score highest under B.
- **Profile C winner: M2** — M1 vs M2: M2 has attacker controllability (entry-path ordering) and a real
  value-delta (dodged/duplicated fee) vs M1's bounded dust; M2 wins.
- runner-up: M3. falsifier: every entry path provably `_accrueFees()` first.

## N-L3
- **Profile A winner: M1** (transient stale account) — clean state bug, simple.
- **Profile B winner: M2** (escrow double-count/effectiveSupply desync) — state-machine terminality + delta highest under B.
- **Profile C winner: M2** — M1 vs M2: M2 more terminal (persistent supply desync) and more dangerous if scaled; wins.
- runner-up: M3. falsifier: single-withdraw-request-per-account invariant enforced elsewhere.

## Ablation summary (frozen)
| locus | Profile A | Profile B | Profile C | common top-2 runner-up |
|---|---|---|---|---|
| N-L1 | M1 (tidy virtual-share) | **M2 (escrow recon)** | **M2** | M3 |
| N-L2 | M1 (approx error) | **M2 (fee-accrue dodge)** | **M2** | M3 |
| N-L3 | M1 (transient stale) | **M2 (escrow desync)** | **M2** | M3 |

**Pattern (pre-reveal):** Profile A picks the *tidy* mechanism every time; B and C both pick the *messy* M2. The
reveal tests whether the awarded mechanism is the tidy A-pick or the messy B/C-pick. **FREEZE.**
