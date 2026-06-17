# P299 — DESIGN

## Problem (from P298)
The executed-PoC verifier is EXPLOIT-SHAPED: confirmation requires L1 (attacker EOA entry), so logic/correctness/admin
bugs proven by a passing differential test (verbatim source) scored `setup_only` (LG-001 off-by-loop-var, PC-001
wrong getter total, SN-001 flood divisor). Real bugs, no attacker to assert.

## The logic_differential mode (additive; exploit track unchanged)
Manifest field `validity_mode` (default `exploit`). When `logic_differential`, confirm iff:
- every declared **bug test** (`exploit_tests`) PASSES (the failing-bug case already returned `refuted` upstream, so
  logic mode can NEVER rescue a failing bug test),
- every declared **corrected-control test** (`control_tests`) PASSES and is non-empty (the differential),
- **L3** (an outcome assertion in the bug test) is present,
- a manifest **`assertion_map`** ties the bug-vs-control divergence to the awarded bug.
→ status `confirmed_by_logic_differential`; `validity_confirmed=True`, `logic_verified=True`; `attacker_verified=False`.
**L1 is NOT required, and L2 (before/after state flip) is NOT required** — for a value-correctness bug the divergence
IS the named-value evidence (the bug test's asserted value vs the corrected control's). Missing control / map / L3 →
`setup_only` (never a silent confirm).

`validity_confirmed` is the unified "confirmed" signal (True for exploit OR logic track); `attacker_verified` stays
exploit-only. Every prior manifest lacks `validity_mode`, so the exploit track is byte-for-behavior identical.

## Why FP stays 0
A logic confirmation needs a passing bug test on verbatim source AND a passing corrected-control that diverges AND the
assertion_map. A non-bug has no real divergence — a control cannot both PASS and diverge from a correct path. The
failing-bug case refutes first. confirmed_by_logic_differential is MEDIUM-confidence and carries the same
fidelity/human-review status as exploit confirmations. The verifier remains the SOLE judge.
