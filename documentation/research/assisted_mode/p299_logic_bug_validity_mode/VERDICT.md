# P299 — VERDICT

## A — LOGIC_BUG_VALIDITY_MODE_CONFIRMS_LOGIC_LOCI_AT_FP_ZERO

The additive logic_differential mode confirms logic/correctness bugs by a passing bug-vs-corrected-reference
differential (no attacker L1), the exploit track is byte-for-behavior identical, and confirmed-FP stays 0.

### A-criteria — all met
- **3 logic loci confirmed** via the differential: LG-001 (ReseedField loop off-by-var), PC-001 (totalDeltaB one
  well), SN-001 (flood divisor) → `confirmed_by_logic_differential` (validity_confirmed=True, attacker_verified=False).
- **Exploit track byte-for-behavior identical** for all 7 prior PoCs (live + recorded).
- **confirmed-FP = 0** — the three negative guards (no passing control / failing bug test / no assertion_map) all
  block confirmation (proven in test_p299).
- **All prior tests green** after the hash-only verifier-pin bump (a1280b2a→1a005811) across test_p294-298.
- **Cumulative recall-of-confirmed: 15 (arc thru P297) + 5 beanstalk (2 exploit + 3 logic) = 20 loci.**
- P298 snapshot preserved (still 2 exploit confirms); forbidden 5 + symlink unchanged; un-wired from confirm gates.

### What this buys
Validity now covers BOTH attacker-exploit bugs (executed exploit + L1+L2+L3) AND logic/correctness/admin bugs
(executed differential, no attacker), each at confirmed-FP=0. The P298 limitation is closed: LG-001/PC-001/SN-001
move from setup_only → confirmed.

### Next
Re-run the P298 beanstalk validity with the mode for the full updated scorecard; wire the mode into the
verification-agent loop so future logic awarded loci confirm; the 7 needs_execution bundles remain the next wave.
Submission stays human-gated.
