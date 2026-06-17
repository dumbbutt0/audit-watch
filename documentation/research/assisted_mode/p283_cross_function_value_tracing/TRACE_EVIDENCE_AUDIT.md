# P283 — TRACE_EVIDENCE_AUDIT

Manual audit of trace evidence: the newly-READY set (0), 5 TRACE_FOUND-not-READY, 3 unresolved-wrapper cases, the two
MEDIUM "anomaly" near-misses, and the L2Governor.execute regression. Question per item: is the trace path real? callee
resolution correct? value-flow link real? invariant specific? assertion implementable? any hallucinated core or generic
over-inference? is the status correct?

## A. Newly-READY (0)
None. Nothing to audit — the gate created no new READY. This is the honest, expected outcome (verdict B).

## B. TRACE_FOUND-not-READY (evidence deepened, correctly NOT lifted) — 5 audited
1. **GaugeCL.claimFees → GaugeCL._claimFees** (ACCOUNTING). Resolution correct (same-contract internal). Callee does a
   state write, no anomaly → LOW. value_flow_path invariant = "generic (needs corrected-reference)", assertion = null.
   Status NEEDS_VALUE_FLOW_EVIDENCE. **Correct**: real cross-function value-flow, no liftable violation.
2. **Pair._mint → Pair._updateFor** (SHARE_ROUNDING). Resolution correct. Callee writes accumulators, no div-before-mul
   in code → LOW, no assertion. **Correct** — the share-accounting bug (if any) is a relationship, not a lexical anomaly.
3. **GaugeV2.withdrawAllAndHarvest → internal harvest** (REWARDS). Resolved, value-flow present, no anomaly → LOW.
   **Correct** not-READY.
4. **VotingEscrow.withdraw → _checkpoint** (STATE_MACHINE, MEDIUM anomaly). The `_checkpoint` "anomaly" is
   `(last_checkpoint / WEEK) * WEEK` — **a false anomaly** (week rounding). Status INLINE_GUARD_REFUTED (D1
   `_isApprovedOrOwner` guard takes precedence) AND it is a state-machine class, so the V2 value-lift never applies.
   **Correct** — two independent defenses prevented any false READY; the audit confirms the anomaly itself is benign.
5. **Black.initialMint / HYBR.initialMint** (SHARE_ROUNDING). Resolved to mint helpers; value-flow present, no anomaly.
   **Correct** not-READY.

## C. Unresolved / wrapper cases — 3 audited
1. **L2Governor.execute** → TRACE_PARTIAL (callees `hashProposal`, `state` resolve but reach no value anomaly). Correct
   — execute is access/state-machine, not a value path; tracer rightly finds nothing to lift on.
2. **`that._consumeMessageAutoWithdraw`** → TRACE_UNRESOLVED (callee bodies not in manifest / external). Correct
   fail-closed; no over-reach.
3. **LibConvert._withdrawTokens** → unresolved/too_dynamic (external token dispatch). Correct fail-closed.

## D. The two MEDIUM near-misses (precision integrity)
- **PanopticPool._burnOptions → _getPremia** (ACCOUNTING/value class). Pre-fix: `_getPremia` `/ 2 ** 64` matched as a
  div-before-mul → MEDIUM → it PASSED the value-flow gate (then blocked at NEEDS_MORE_EVIDENCE by missing core fields).
  This is the one place a *false* anomaly reached the value-flow gate. The `**` exclusion fix removes it; post-fix it is
  NEEDS_VALUE_FLOW_EVIDENCE. **Lesson logged in REPAIR_BACKLOG:** the div-before-mul lexeme is an unreliable bug signal;
  even comment-stripped real code, `(x/U)*U` rounding and `**` scaling are benign. A lift must never rest on it alone.
- **VotingEscrow._checkpoint** — see B.4; benign, double-guarded.

## E. Hallucinated-core / over-inference check
None found. Every `value_flow_path` with `anomaly == null` carries invariant "generic (needs corrected-reference)" and a
null poc_assertion — i.e. the system explicitly refuses to invent a specific bug from generic movement. No candidate was
described with a fabricated attacker path or a specific invariant it could not source.

## F. Verdict on the audit
Trace paths are real and resolution is correct; the tracer **deepens evidence** (35 TRACE_FOUND) and **sharpens the
backlog** without inventing bugs. The only anomalies it found were false and were caught by layered defenses (and one
removed by the `**` fix). Statuses are correct. **Severe FP = 0.** Consistent with verdict B.
