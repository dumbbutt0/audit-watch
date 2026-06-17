# P152 — Problem Statement

Third non-duplicate runtime holdout, **conversion-labeled**, from a **distinct mechanism class** vs the prior
phases (value-loop / recipient-provenance / sibling-parity / signature-binding). Reject-first; not biased toward
confirmation; sidecar/runtime-only only; baseline preserved. Also adopts the new dashboard `conversion` schema.

## Candidate & result
**`ecg-2023-12-holdout` (Credit Guild) `ERC20MultiVotes`** — mechanism class **governance vote-accounting on token
movement** (new). No local answer key → `duplicate_unknown`. Fully **unprivileged** surface (any holder
`delegate`/`transfer`), so reachability is answerable by construction.

- **Suspected mechanism:** can a holder retain/inflate delegated voting power by transferring tokens away (votes
  not decremented)?
- **Runtime result: RUNTIME_REFUTED.** The real `transfer`/`transferFrom` call `_decrementVotesUntilFree` before
  moving tokens; the real `getVotes(delegatee)` drops 1000e18 → **0** on transfer. A vulnerable reference
  (unguarded transfer) retains 1000e18 (the bug shape the real contract avoids); the matched control is stable.

## Conversion outcome: `runtime_refuted`
`conversion = {mechanism_confirmed:false, attacker_reachable:true, severity_bearing:false, novelty_clear:false,
reportable:false, outcome:runtime_refuted, blocker:null}`. The suspicion was **killed** by the real guard;
reachability was fully answered (unprivileged, but the mechanism is absent). This is the intended conversion-learning
value: the funnel refutes a **new mechanism class**, not merely confirms — and answers reachability regardless of
outcome.

## Why this satisfies the acceptance criteria
- Not "merely another runtime_confirmed row" — it is a distinct-class **refutation**.
- Explains non-conversion: the real contract's `_decrementVotesUntilFree` guard makes the suspected retention
  impossible (`mechanism_absent_guard_present`).
- Reachability answered (unprivileged surface); blocker explicit.
- All P151 integrity checks preserved; `submission_ready=false`.
