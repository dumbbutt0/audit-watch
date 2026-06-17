# P198 — recommendation

## Final decision: `PARTIAL_GENERALIZATION`

The P183–P188 adjudication stack **partially generalizes** to the structurally-new Centrifuge RWA architecture
(tranches · epochs · escrow · ERC4626):

- **Adjudication recall generalizes (the win).** On the 4 awarded findings the bounded 12-surface sample actually
  covered, the blind stack scored **2 exact HITs + 1 PARTIAL + 1 wrong-mechanism**. Critically, with **no answer-key
  exposure**, Sonnet subagents independently re-derived two awarded RWA mechanisms verbatim on the exact functions:
  **M-08** (`RestrictionManager.detectTransferRestriction` checks receiver but not sender) and **M-07**
  (`_calculateTrancheTokenAmount` rounding direction). Mechanism enumeration, carry-forward, and NEEDS_HARNESS
  escalation transferred intact. This is genuine, non-overfit generalization to RWA accounting invariants.
- **Precision & severity-calibration do NOT generalize cleanly (the weakness).** 11/12 verdicts were `HIGH_THREAD`
  against an **all-Medium / 0-High** reality (FM-1); the run over-enumerated (24+ selected mechanisms, ~3 awarded)
  (FM-3); and M-04 was a wrong-layer non-responsive rejection (FM-2).
- **4/8 awarded were outside the bounded sample** (axelar gateway, permit, DOMAIN_SEPARATOR, admin) — a coverage/
  sampling outcome by design, **not** an adjudication failure.

## What this means
The campaign's durable production win (P183–P188 mechanism adjudication) **carries to a new architecture for
recall** — it finds the right RWA mechanisms blind. The honest residual is **severity/precision calibration on
clean, Medium-dominated codebases** (the same Medium-validity frontier P186/P187 flagged), now reproduced on RWA.

## Recommended next (each needs explicit go — NOT actioned here)
1. **Severity-calibration study** (read-only first): does the over-HIGH skew (FM-1) hold across corpora? If so, a
   future deep_trace severity-grading calibration (Medium-class examples), echoing P187 — but only after measurement.
2. **Wrong-layer rejection** (FM-2): a small extension so a function trace flags "caller-side access-control
   unverified" when an auth-gated callee is reached from a public wrapper — candidate for the P188 checker family.
3. Do **not** widen the bounded sample into exhaustive sweeping (it would become recall-counting); if more coverage
   is wanted, sample the peripheral surfaces (gateway/permit/admin) that held M-01/02/03/06.

## Acceptance criteria — met
Answer-key access controlled & documented (count-only at viability; full only post-freeze) ✓ · no production/tooling
optimization (deep_trace.md + checker read-only; nothing patched mid-run) ✓ · tested P183–P188 on a structurally
new architecture ✓ · results distinguish adjudication quality from routing/execution artifacts (P195/P196) ✓ ·
failure modes described honestly, not patched ✓ · JSON valid ✓ · production hashes recorded start & end (byte-
identical) ✓.
