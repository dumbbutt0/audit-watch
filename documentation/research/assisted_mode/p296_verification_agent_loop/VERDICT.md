# P296 — VERDICT

## A — VERIFICATION_AGENT_LOOP_CONFIRMS_NEW_LOCI_AT_FP_ZERO

The loop emits specs, builders produce PoCs, and the verifier (sole judge) confirmed new awarded loci — recall-of-
confirmed climbed at confirmed-FP = 0.

### A-criteria — all met
- **Loop ran end-to-end** (emit → build → judge); **3 loci attempted** (≥3), all via spawned subagents.
- **3 new verifier confirmations** (≥1): ecg H-03 (onBid bad-debt cascade), ecg H-02 (rebase-transfer reward theft),
  kelp H-02 (deposit-before-calc under-mint) — each a real forge exploit PASS (L1+L2+L3) with an assertion_map.
- **recall-of-confirmed climbed 6 → 9 loci** (cumulative, locally-answer-keyed subset).
- **confirmed-FP = 0** — verifier is the sole confirmer; builder self-reports advisory; the refutation control stays
  refuted; no confirmed_but_unmapped.
- **Judge-not-the-builder + assertion_map guards proven** by synthetic tests (a failing-exploit "confirmed" claim is
  overridden; a verifier-PASS without an assertion_map is flagged unmapped).
- Funnel + re-ranked backlog updated; new files only (zero cascade).

### What this buys
The climb to 100% recall-of-confirmed is now an automatable loop: spawn builders at the surfaced backlog, let the
verifier judge. Cold-start only costs recall (refutes), never precision — exactly the property that makes opening
recall safe.

### Next
Run the next waves (remaining 6 tractable loci, then beanstalk-12, then strict-eval once answer keys are available);
a surfacing pass for the 4 missed; re-blind once recall-of-confirmed holds at confirmed-FP=0. Submission human-gated.
