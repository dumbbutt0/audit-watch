# P279 — FP_AND_NOISE_REPORT

## Severe concluded/reportable FP: **0**
The deriver + gate are advisory-only; READY_FOR_POC_INTENT means "evidence complete enough to attempt a PoC", never
confirmed/reportable/severity. Every package carries the advisory contract; guard PASS; fail-closed verified.

## Moved to READY: 3 (from 0)
All manifest-true, unguarded, real-anomaly (ORDER cancel, ACCESS ungated governance execute, ACCESS external-call
transform). Low-noise by design (anomaly-gated).

## Blocked and why (81 NEEDS_MORE_EVIDENCE)
- auth-guarded functions ⇒ LOW attacker_path (bypass would be the core claim).
- internal/underscore helpers / view-pure ⇒ not a clean external entry.
- ACCOUNTING / MATH_SHARE / ORACLE / REWARDS / STATE ⇒ anomaly is a value-flow/invariant fact not in the manifest ⇒
  LOW + core-carrying unresolved assumption. **This is the next repair (value-flow derivation), not a defect.**

## Noise control that fired
The evidence audit caught a substring false-match ('fill' in 'fulfill') on a guarded function; the auth-guard global
override removed it. No remaining unsupported READY.

## Taxonomy
non-awarded TP / same-area-wrong / benign: not adjudicated here (needs runtime; the 3 READY are the PoC-sweep queue).
**severe concluded/reportable FP: 0.**
