# P198 — corpus viability decision

**Awarded set: 8 Medium / 0 High** (canonical, from `report.md` severity headers — count-only unseal).

**Decision: VIABLE — continue with Centrifuge (no fallback to badger).** 8 ≥ the ≥6 H/M viability threshold.

Notes:
- **All-Medium / zero-High** is itself a useful stressor: it targets the *Medium validity/severity adjudication*
  frontier that P186/P187 found model-dependent (the M-02/M-06 reject-first disagreements). A clean codebase with
  only Mediums is a stronger precision/calibration test than a High-heavy one.
- The 8 awarded findings span both the accounting-conservation core (deposit/withdraw rounding, Escrow share
  conservation, restriction logic) and peripheral surfaces (axelar gateway auth, permit/DOMAIN_SEPARATOR, admin) —
  good coverage spread for an adjudication-generalization test.
- No silent continuation: viability is documented and met before proceeding.
