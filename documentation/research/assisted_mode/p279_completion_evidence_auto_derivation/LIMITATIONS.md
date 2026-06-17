# P279 — LIMITATIONS

- **READY is conservative (3 corpus-wide).** By design: only classes whose anomaly is **manifest-visible**
  (ACCESS no-auth/config, ORDER, external-call) can reach READY. ACCOUNTING / MATH_SHARE / ORACLE / REWARDS / STATE —
  the bulk — stay NEEDS_MORE_EVIDENCE because their anomaly is a value-flow/invariant fact the manifest cannot show.
  Lifting them is the **next repair (value-flow derivation)**, not a fix to this one.
- **Evidence is structural, not proven.** A READY package means "evidence complete + source-grounded enough to attempt
  a PoC", NOT "is a vulnerability". The 3 READY still need a runtime PoC to confirm/refute (poc_tier=partial_runtime).
- **Confidence is heuristic** (manifest-signal rules). Auth detection is modifier-name based (an internal/inherited
  guard not surfaced as a modifier could be missed — mitigated by keeping such cases at MEDIUM/LOW, not HIGH).
- **Class label is the router's** (P273/P277); a mis-routed class feeds the wrong template (still advisory).
- **Supervised, not blind** — calibration on the P276 corpus; generalization needs a fresh blind target.
