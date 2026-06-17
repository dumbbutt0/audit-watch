# P204 — L3 PoC/harness magnitude HIGH standard (pre-specified)

**Status: standard pre-specified in the approved P204 brief; encoded as harness assertions before results were
interpreted.** Replaces the static v1/v2 precondition (which P203 showed is gameable by arbitrary-call capability).
Design/prototype only — not wired.

## New severity principle
A candidate may be `HIGH_CONFIRMED` only if there is a **concrete attacker-controlled transaction sequence, under
the deployed/source-valid configuration, that realizes material theft, insolvency, permanent loss, or unauthorized
privileged control.** Static capability alone is NOT enough.

## HIGH_CONFIRMED requires ALL of (demonstrated by an executable harness)
1. attacker-controlled entry path;
2. executable transaction sequence (runs to completion in the harness);
3. source-valid deployed configuration (real contracts; only external deps mocked; honest custody);
4. concrete affected asset, accounting balance, or privileged control;
5. victim/protocol value loss, insolvency, permanent lock, or unauthorized privileged transition — **measured**;
6. material magnitude demonstrated or clearly scalable;
7. no trusted/admin/TSS prerequisite;
8. no reliance on hypothetical contract custody unless the harness **initializes custody in a source-valid way** and
   proves the vulnerable path drains/corrupts it.

## Demote or withhold HIGH if
- the candidate only proves **unauthorized-call capability**;
- it only bypasses a **fee / signature / check**;
- it requires the contract to **hold funds in a way not supported by source flow**;
- it depends on **arbitrary mock behavior** not present in the protocol;
- it causes only **recoverable griefing or bounded local loss**;
- it requires a **privileged actor**.
Routing: bounded/reversible/local → `MEDIUM_OR_LOWER_CALIBRATED`; material-but-not-source-validly-realizable (needs
unsourced custody) → `NEEDS_HARNESS_FOR_SEVERITY`.

## Why this beats static gates (P203 lesson)
P203's static "source-proven custody/value-flow" precondition was satisfied by an independent reviewer treating
*arbitrary-execution capability* / *existence of a balance variable* as material. The L3 standard removes that
loophole: it requires an **executed** tx that **moves measured material value** under honest custody. Capability
that cannot move value under source-valid setup does not pass.
