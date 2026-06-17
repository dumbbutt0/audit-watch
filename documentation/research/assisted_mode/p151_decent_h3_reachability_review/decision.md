# P151 — Decision

## Verdict: **DESIGN / PRIVILEGED-ONLY — fee-binding mismatch NOT externally reachable** (+ separate replay side finding)

The P150-confirmed mechanism (`UTBFeeCollector.collectFees` executes an unbound `fees`) is **not reachable by an
unprivileged attacker** through the real Decent UTB/router flow: both public entrypoints build the signed
`packedInfo` from the user's own `fees` (`abi.encode(instructions, fees)`, `UTB.sol:115`/`:266`, via
`retrieveAndCollectFees` :228-251 → `collectFees` :248), and take **no user `packedInfo` parameter`. Only the
privileged `onlyUtb` caller could pass a mismatched `packedInfo`. The missing re-bind is **defense-in-depth only**.
A **separate** replay/domain-binding weakness exists (no nonce/chainid/contract/deadline in the signed blob).
`submission_ready=false`.

## Answers to the acceptance questions
- **Can an unprivileged attacker make the real router call `collectFees` with `fees` not bound to the signed
  `packedInfo`?** → **No.** The router derives `packedInfo` from `fees`; no entrypoint accepts an independent
  `packedInfo`.
- **Mechanism vs exploitability separated?** → Yes. Mechanism = `runtime_confirmed` (unchanged); exploitability =
  trusted-router-only / not externally reachable.

## Final response
- **Verdict:** Design/privileged-only (not externally reachable); replay = separate side finding.
- **Call-path:** 2 public entrypoints (`swapAndExecute`, `bridgeAndExecute`), both router-bind `fees`↔`packedInfo`;
  `receiveFromBridge` no fee collection; direct `collectFees` is `onlyUtb`.
- **Signed vs executed:** `feeToken`/`feeAmount` ARE signed (via `fees` ⊂ `packedInfo`); nonce/chainid/contract/
  deadline/payer are NOT.
- **Reachability:** fee-mismatch unreachable by unprivileged/user actors; replay user-influenced but distinct.
- **Severity recommendation:** no Medium/High for the mismatch (defense-in-depth recommendation: re-bind `fees` in
  `collectFees`); replay = separate, severity-undetermined, human review.
- **Duplicate/public-known:** not checked beyond local (`duplicate_unknown` = no local record; no novelty inferred).
- **Integrity:** production `UTB.sol`/`UTBFeeCollector.sol` byte-identical; harness un-wired + unchanged; prompt
  baseline + corpus byte-for-byte unchanged; H3 panel row still `runtime_confirmed`, flags false; active symlink
  unchanged.
- **Tests:** 33 research tests pass (31 + 2); full suite 1670 passed / 2 pre-existing snapshot fails / 4 skipped.
- **submission_ready = false** (explicit; unless a human overrides outside this phase).

## Boundary-stop note
This is the intended outcome of a reject-first review: a runtime-confirmed **mechanism** was correctly **not**
promoted to bounty-grade exploitability because the only reachable caller binds the data. The panel keeps the
mechanism (`runtime_confirmed`) while recording the reachability verdict (`trusted_router_only_not_externally_
reachable`) so the dashboard cannot mistake mechanism confirmation for exploitability.

## Next recommended phase (P152)
A third non-duplicate runtime holdout (continue cross-architecture yield), or a cross-architecture yield/quality
summary now that the panel spans 5 architectures with confirmed + refuted + a reachability-downgraded row.
