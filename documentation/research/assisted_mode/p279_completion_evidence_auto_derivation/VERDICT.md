# P279 — VERDICT

## Verdict: **B — EVIDENCE_DERIVER_PROMISING_NEEDS_REFINEMENT**

### Why B
The deriver works and is clean:
- **Auto READY_FOR_POC_INTENT moved from 0 → 3** corpus-wide (cancelPodListing/ORDER, L2Governor.execute/ACCESS,
  V3Vault.transform/ACCESS) — the operator-to-derive wall is broken for the manifest-visible-anomaly classes.
- **Evidence audit clean**: all 3 READY are manifest-true (source_basis cites exact manifest fields), **no hallucinated
  core evidence, no placeholder leaked**, PoC assertions implementable.
- **severe concluded/reportable FP = 0**; advisory-only; gate stays strict (auth-guarded + value-flow-invisible classes
  correctly blocked); the audit caught and fixed one substring false-match (auth-guard override).

But not **A**, because corpus-wide READY is **low (3 / 144)**: the deriver only unlocks classes whose anomaly is
**manifest-visible** (ACCESS/ORDER/external-call). The bulk — ACCOUNTING/MATH/ORACLE/REWARDS/STATE — stay
NEEDS_MORE_EVIDENCE because their anomaly is a value-flow/invariant fact the manifest cannot show. Calling the deriver
"ready for the PoC sweep" broadly would overclaim; it is ready for a **small targeted sweep on the 3 clean READY**, and
needs the next refinement (value-flow evidence derivation) to lift the accounting/math/oracle bulk.

### Not C / D
- Not **C** (TOO_NOISY): READY is anomaly-gated and clean (0 hallucination, 0 FP, guarded/invisible classes blocked).
- Not **D** (ABORTED): research-only; only the new deriver/config + P278 glue + test/docs changed; P260/P262/P264/P267/
  P273 router code+config/P269 + P271 + forbidden 5 byte-identical; active audit unchanged.

### Next
1. Small **PoC sweep** on the 3 READY (runtime, confirm/refute) — the verdict-A path for these.
2. **Value-flow evidence derivation** (next repair) to lift ACCOUNTING/MATH/ORACLE/REWARDS from NEEDS_MORE_EVIDENCE.
3. Re-run the map; then a fresh **blind** target. Production authority WITHHELD.
