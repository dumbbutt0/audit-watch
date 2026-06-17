# P199 — severity-gate proposal (DESIGN NOTE ONLY — not implemented)

**Status: proposal.** Nothing here is built, wired, or applied. It is additive to (does not replace) the
`deep_trace.md` threat-ceiling verdict, and would itself require a separate, measured, human-approved phase
(mirroring the P195/P196 burden-of-proof discipline). **Reject-first:** absence of proof of a High dimension →
demote, never promote.

## Where it would sit
A post-verdict **calibration step**: the deep-trace verdict stays a *threat ceiling*; the gate maps
`(ceiling, evidence)` → a *calibrated* severity. It changes no enumeration, routing, or selection — recall is
untouched; only the severity label is calibrated.

## Eight evidence dimensions (each must be explicitly graded)
1. **mechanism-validity** — is the bug real (source-backed, responsive)? [pass/fail]
2. **exploit-reachability** — `executable` (concrete attacker tx) / `theoretical` / `unproven`.
3. **asset/value path** — does value actually leave a victim, or is it liveness/compliance/precision-only?
4. **loss-magnitude** — `> program threshold` / `material` / `dust` / `unproven`.
5. **actor-permissions** — `permissionless` / `needs-allowance` / `trusted/admin prerequisite`.
6. **blast-radius** — `protocol-wide` / `broad user class` / `single user / local`.
7. **permanence** — `permanent` / `recoverable` / `temporary mismatch`.
8. **harness-requirement** — does proving magnitude/reachability require a runtime harness?

## HIGH_THREAD gate (all required — reject-first)
Label HIGH only if **ALL** hold (else demote):
- mechanism-validity = pass, AND
- exploit-reachability = `executable` (not theoretical/unproven), AND
- asset/value path = real value extraction OR protocol-wide insolvency OR permanent fund lock OR unauthorized
  privileged state transition, AND
- loss-magnitude = material / `> threshold` (NOT dust, NOT unproven), AND
- actor-permissions = `permissionless` or `needs-allowance` (NOT trusted/admin prerequisite), AND
- (blast-radius ≥ broad OR magnitude clearly material), AND
- NOT (the impact is solely DoS/griefing/precision/compliance/bounded-local).

## Demotion rules (reject-first)
- DoS / griefing / liveness / compliance / precision-dust / bounded-local mispricing → **Medium** (the CLAUDE.md
  Medium tier), regardless of how valid the mechanism is.
- magnitude OR reachability `unproven`, and a harness would settle it → **NEEDS_HARNESS** (do not grade High on a
  threat ceiling alone — fixes `NEEDS_HARNESS-as-severity-substitute`).
- trusted/admin prerequisite → cap at Medium unless the privileged path is itself the awarded bug.
- temporary mismatch / recoverable → not "permanent loss" → demote.
- access-control claims must check the **public entry layer**, not only an auth-gated callee (addresses P198 FM-2).

## What this would have done on the dataset
- The 8 over-HIGH Medium cases → all demote to Medium (DoS/griefing/precision/compliance/bounded-local; none pass
  the asset/value+magnitude+permanence gate).
- The 12 genuine Highs → all stay High (direct theft / insolvency / permanent loss, permissionless, executable).
- The 1 correct Medium (M-07) → stays Medium.
- Net (on this dataset): over-HIGH 8→0 with **0 genuine-High demotions** — i.e. precision gain at no recall cost.
  (Dataset n=30; a real phase must measure this on fresh corpora before shipping.)

## Explicit non-goals
Not a change to `deep_trace.md`, the checker, routing, selection, or detectors. Not a recall change. Not
auto-applied. The verdict still enumerates aggressively (recall); the gate only calibrates the *grade*.
