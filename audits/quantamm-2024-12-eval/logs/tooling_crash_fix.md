# Hard tooling-crash fix during QuantAMM eval

**Script:** scripts/min_confirm_gate.py (Step 3.9 gate)
**Symptom:** `AttributeError: 'str' object has no attribute 'get'` at check_finding — the script does
`ice = f.get("ice_chain", {}) or {}` then calls `ice.get("exploit_path")`. In the standard finding
schema `ice_chain` is a human-readable STRING (e.g. "I=High · C=High · E=Permissionless"), so a
non-empty string stays a string and `.get()` crashes. The crash occurs before the
AUDITWATCH_MINCONFIRM_OVERRIDE check, so the documented override could not bypass it.
**Fix:** defensive type-guard — coerce `ice`/`tice` to `{}` when they are not dicts. No gate LOGIC
changed; for the common string case the structured ice fields are simply treated as absent and the
gate falls back to the other signals (severity, follow_up_packet, location, impact) it already checks.
**Justification:** permitted "hard tooling crash" exception. The fix is in shared scripts/ (NOT a
frozen eval artifact) and does not alter recall or scoring.

## Second crash (same root cause)
**Script:** scripts/confirm_inventory.py — identical `ice = f.get("ice_chain") or {}` then `ice.get(...)`
crash on the string ice_chain. Same defensive type-guard applied (coerce non-dict ice/ite to {}).
No logic change; advisory inventory only.

## Third crash (same root cause, main() scope)
**Script:** scripts/confirm_inventory.py main() line ~83 — second `ice`/`ite` binding also needed the
type-guard. Applied. Advisory inventory now runs clean.
