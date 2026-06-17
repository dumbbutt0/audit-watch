# P294 — IMPLEMENTATION_NOTES

## Files added (no existing module edited → zero hash cascade)
- `scripts/research/executed_poc_verifier.py` — `verify_poc(poc_dir, audit_id, finding_id)`:
  load `poc_manifest.json` → find `.t.sol` (skip lib/forge-std) → for each declared exploit test, structural
  L1/L2/L3 parse of its brace-matched body + `forge test --match-test '^<fn>\b' -vv` (real run, log to
  `output/poc_validation/raw/`) → confirm iff all exploit tests PASS AND L1+L2+L3. Refutation-only PoCs →
  `refuted_by_execution`. Advisory-stamped; safety-checks forge flags.
- `config/research_executed_poc_verifier.json` — recall_open=false, L-level markers, safety limits, verdict enum.
- `pocs/p294/salty_increaseUserShare/` — Tier-C faithful PoC of the P293 locus (verbatim virtualRewards control-flow
  + MockSALT; `lib` symlinked to `pocs/p286/lib`).
- `poc_manifest.json` in pocs/p286 (exploit), pocs/p290/.../Pools_deposit (refutation), pocs/p294/... (exploit).

## Two implementation gotchas (fixed)
- `forge --match-test '^<fn>$'` reports "no tests match" (the `$` excludes the implicit `()`); use `'^<fn>\b'`.
- forge [PASS] alone ≠ confirmed — a refutation test passes too; polarity comes from the manifest's
  exploit/refutation split, and `attacker_verified` additionally requires the L1+L2+L3 structural levels.

## Anti-fabrication
`attacker_verified` is computed from the captured forge run every time; there is no trusted status field. A manifest
that names an exploit test which fails (or doesn't exist) yields `refuted_by_execution` — proven by
`test_fabricated_exploit_not_confirmed_when_test_fails`.
