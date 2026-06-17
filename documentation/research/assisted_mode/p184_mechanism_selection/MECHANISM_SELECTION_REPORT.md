# P184 — Deep-pass mechanism SELECTION after P183 (blind-subagent measurement)

**Question:** does the P183 enumeration prompt actually make deep-trace SELECT the awarded 2nd/3rd mechanism on
already-reached functions — not just enumerate it? **Headline metric: `awarded_mechanism_selected`, not coverage.**

**Method (decontaminated):** one **blind subagent per function** (5 total) received ONLY the function source +
the P183 `deep_trace.md` prompt — no answer key, no finding IDs, no phase context. Each emitted the structured
deep-trace output (inventory / rejection table / chosen mechanisms / impact / stop). I (answer-aware) then scored
its chosen mechanisms against the key. Raw outputs preserved verbatim in `mechanism_selection_trace.json`.

## Result
```
awarded_mechanism_SELECTED:  7/9   (conservative 6/9, excluding the loose H-03 near-duplicate)
awarded_mechanism_enumerated: 8/9
baseline (these losses, at eval time): 0/9   ← the original deep-trace took the FIRST mechanism and stopped
```

| finding | function | awarded mechanism | enumerated | **selected** | note |
|---|---|---|--:|--:|---|
| H-07 | onAfterRemoveLiquidity | unauthorized deletion via userData | yes | **yes** | EXACT (blind chose userData identity spoofing → burn/delete victim positions) |
| M-03 | afterUpdate | 100-cap not checked on transfer | yes | **yes** | EXACT |
| M-10 | afterUpdate | victim DoS via malicious NFT transfer | yes | **yes** | EXACT (unbounded array growth → gas DoS) |
| L-01 | afterUpdate | block.number vs block.timestamp | yes | **yes** | EXACT |
| M-06 | _getData | unhandled Chainlink revert locks oracle | yes | **yes** | EXACT (no try/catch → all consumers revert) |
| L-02 | MultiHopOracle._getData | precision loss | yes | **yes** | EXACT (compounded integer-division truncation) |
| H-03 | onAfterSwap | improper fee application / admin overcharge | yes | **yes*** | LOOSE — same admin-fee region as already-found PARTIAL H-02; conservative scoring excludes it |
| M-02 | onAfterRemoveLiquidity | lpTokenDepositValueChange underflow | yes | **no** | enumerated but FOLDED into the rejection table as an amplifier, not carried as a standalone chosen finding |
| M-17 | onAfterRemoveLiquidity | feePerLP can exceed 100% | **no** | no | MISS — blind enumerated a different "fee truncation" (rejected as dust); the >100% bound mechanism never surfaced |

**`wrong_mechanism_reduced`: yes.** Every function carried MULTIPLE mechanisms (vs the original single).
`afterUpdate` is the clearest win: the blind trace carried **all three** awarded 2nd/3rd mechanisms (M-03, M-10,
L-01) beyond the original H-01 fee-bypass, and its `stop_condition` fired `more_mechanisms_pending` ("distinct
state vars + distinct actors"). `onAfterRemoveLiquidity` carried H-07 plus an (unawarded but source-grounded)
reverse-loop underflow.

**Noise: low.** Extra unawarded mechanisms (reverse-loop underflow, int216 overflow, div-by-zero, upliftFeeBps
re-stamp, backup-loop off-by-one) are **source-grounded**, not generic spam — each carries a cited source fact
in the rejection table. Some may be real unawarded issues or FPs; a real run would triage them.

## Why this is credible despite same-model contamination
The blind subagent shares the model family, so faint QuantAMM training priors can't be fully excluded. Evidence
the run was genuinely blind, not omniscient:
- it **missed 2/9** (M-17 not enumerated; M-02 folded not selected) — an answer-aware evaluator would not miss;
- every chosen mechanism cites **exact source facts** (`userAddress=address(bytes20(userData))`, `i=length-1`
  unsigned loop, `uint32(block.number)`, `push` with no `>100` cap, `latestRoundData` no try/catch);
- no output cited any answer-key ID.
Caveat retained: this is one in-session run, n=9; the gold standard remains a firewall-sealed fresh-model run.

## Secondary finding (flagged, NOT fixed — P184 is measurement-only)
The P183 advisory checker marked all 5 outputs `mechanism_incomplete` — but on **schema format only**: the blind
agents returned `chosen_mechanism` as a **list** (multi-mechanism carry-forward — exactly the intent) and
`impact_direction` as **prose**. The reasoning fields are all present. → **P185 should update the checker/prompt
schema to accept `chosen_mechanism` as a list.** Flagged, not silently fixed (per scope).

## Decision: KEEP P183 PROMOTED
Per the rule "if awarded mechanisms are selected materially more often, keep P183 promoted": selection went
**0/9 → 7/9 (conservative 6/9)** on these exact losses, with enumeration+stop-condition demonstrably surfacing
the 2nd/3rd mechanisms. Two follow-ups, both narrow:
- **M-02 (enumerated-not-selected)** → next fix is the one you predicted: mechanism **ranking / comparand
  scoring** so a real (carried) mechanism isn't demoted into the rejection table (a P185 candidate).
- **M-17 (not enumerated)** → a small inventory-menu gap (a "value exceeds a logical bound / >100%" mechanism).
- **checker schema** → accept `chosen_mechanism` list (P185).
No prompt edits were made during this run; no recall number is claimed beyond this blind n=9 measurement.
