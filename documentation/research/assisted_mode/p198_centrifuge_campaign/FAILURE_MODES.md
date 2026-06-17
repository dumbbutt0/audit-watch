# P198 — failure modes (described, NOT patched mid-run)

Distinguished from routing/execution artifacts (P195/P196): the deep-pass auto-executor is an api-free no-op; this
run used the in-session blind path, so all observations below are **adjudication-quality** observations on the RWA
architecture, not routing/execution.

## FM-1 — Severity over-calibration on a clean codebase
11/12 blind verdicts were `HIGH_THREAD`; the awarded reality is **0 High / 8 Medium**. The stack grades nearly
every accounting/escrow/restriction surface as High. This is the **Medium validity/severity adjudication frontier**
(P186/P187 M-02/M-06) recurring on a new architecture: the stack reliably *enumerates* the mechanism but
*over-rates* its severity when the true impact is Medium / conditional / unconfirmed. **Architecture-stressed
weakness, not an enumeration failure.**

## FM-2 — Wrong-layer / non-responsive rejection (M-04)
For the public-`deposit` griefing (M-04), IM-04 traced the **auth-gated callee** `processDeposit`, enumerated
other mechanisms (maxDeposit accounting, stale price), and **rejected** the access-control angle because
`processDeposit` is `auth`-gated — missing that the **public `LiquidityPool.deposit` wrapper** has no access
control. The rejection was *responsive to the callee's guard but not to the caller's gap*. This is the
non-responsive-rejection class P188's detector targets, here manifesting as **analyzing the wrong layer** (callee
vs the unguarded public entrypoint). A bounded single-function trace can miss a caller-side access-control gap.

## FM-3 — Over-enumeration / low precision on a low-bug-density corpus
24+ selected mechanisms across 12 surfaces; only ~3 map to awarded findings. Most extras are hedged on
"compromised Gateway/auth" or routed to `NEEDS_HARNESS`. On a clean codebase this is a **candidate-volume /
precision** problem: the enumerate-aggressively design (good for recall) produces many unconfirmed High-flavoured
candidates a human must triage. (Not necessarily false — some may be genuine-unsubmitted — but unconfirmed.)

## What did NOT fail (transferred intact)
- Mechanism **enumeration** + **carry-forward** fired strongly on tranche/epoch/escrow/ERC4626 surfaces.
- **NEEDS_HARNESS escalation** correctly captured runtime-dependent disputes (price internals, reentrancy, token
  behaviour) instead of false-rejecting them.
- **Reject-first** produced source-backed rejections (EVM-atomicity on decrement-before-transfer; `onlyGateway`/
  `auth` on direct-EOA paths) — except the wrong-layer M-04 case (FM-2).
- The two clearest awarded RWA mechanisms (restriction sender-check, withdrawal rounding direction) were
  independently re-derived **blind** on the exact functions.

## Honesty
No mechanism was patched, no prompt/checker changed mid-run (the FM-2 wrong-layer issue is documented here, not
fixed). Severity-calibration (FM-1) and wrong-layer rejection (FM-2) are candidate inputs for a *future,
separately-approved* phase — not actioned in P198.
