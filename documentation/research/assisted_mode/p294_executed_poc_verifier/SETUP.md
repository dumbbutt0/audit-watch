# P294 — SETUP

**Phase:** Executed-PoC Verification Hook — the FP oracle (research-only, advisory, production authority WITHHELD).
**Goal:** invert the FP economics chosen by the user (open recall, confirm by executed proof). A candidate is
"confirmed" ONLY when a declared EXPLOIT test in its `pocs/<id>/` dir actually runs under `forge` and PASSes AND
satisfies L1+L2+L3. Precision comes from proof, not from a fail-closed pattern gate.

## Stance
- Research-only · advisory · no production authority/submission/severity/reportable/confirmed-dashboard.
- The verdict is reproducible from the run + raw log. `ground_truth.jsonl` read-only (never written).
- No auto-submission; un-wired from confirm_gate / min_confirm_gate. Local forge only; no mainnet/keys/broadcast.

## Active audit
`output` → `audits/size-credit-2024-06-blind/output` (unchanged).

## New files (P294 adds ONLY new files — zero edits to existing modules → no hash cascade)
- `scripts/research/executed_poc_verifier.py` — the orchestrator/oracle.
- `config/research_executed_poc_verifier.json` — recall_open (default false), L-level parse config, safety limits.
- `pocs/p294/salty_increaseUserShare/` — a net-new Tier-C PoC for the P293-recovered locus.
- `pocs/p286/poc_manifest.json`, `pocs/p290/.../poc_manifest.json` — author-declared exploit/refutation intent.
- `tests/research/test_p294_executed_poc_verifier.py` + this docs dir + `proof_driver.py`.

## Reused (byte-identical, not edited)
forge 1.5.1 · `collect_poc_results.py` semantics (deterministic forge runner) · `validate_poc.py` / the L3 bar in
`validate_p208_l3_readiness.py` (read-only) · forbidden 5.

## Reproduce
`python3 documentation/research/assisted_mode/p294_executed_poc_verifier/proof_driver.py` (runs real forge over the
proof set) · `python3 scripts/research/executed_poc_verifier.py --poc-dir pocs/p286`.
