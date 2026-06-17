# P294 — DESIGN

## The inversion
The P287→P293 arc bought FP=0 with fail-closed static gates → recall was bounded by pre-built lens coverage (one
bug per phase). P294 makes the FP control an **executed L3 PoC** instead of a pattern: a candidate is confirmed iff
its declared exploit test actually runs under `forge` and PASSes with L1+L2+L3. This lets recall open wide (verify
everything) while confirmed-FP stays ≈0 **by construction** (a confirmation is a passing executed proof), and it
generalizes (execution is ground truth, not an answer-key-shaped pattern).

## Why forge [PASS] alone is NOT "confirmed" (the polarity problem)
A refutation PoC also PASSes — it proves the bug is ABSENT (salty `Pools.deposit`: the test asserts no corruption).
So confirmation requires a test that DEMONSTRATES the exploit, not one that demonstrates safety. Polarity is
**author-declared** in `pocs/<id>/poc_manifest.json` (`exploit_tests` / `refutation_tests` / `control_tests`) — NOT
inferred from assertion-string scans. Confirmed iff the declared EXPLOIT test(s) PASS.

## L1/L2/L3 parse contract (reuses the validated L3 standard)
Mirrors the L3 realized-impact bar (`validate_poc.py` / `validate_p208_l3_readiness.py`, read-only):
- **L1** — attacker EOA entry + a real call (vm.prank/makeAddr/vm.deal + `(`), not copied/inlined logic.
- **L2** — a named state flip: `vm.load` or a balance/before/after read, AND an assertion present.
- **L3** — an outcome assertion present in the test (assertEq/assertGt/…) on the claimed impact.
`attacker_verified = forge PASS(exploit test) AND L1 AND L2 AND L3` — derived from the real run + a deterministic
structural parse of the test source. There is NO self-asserted "proved" field and NO assertion-string shortcut.

## Verdict statuses
`confirmed_by_execution` (attacker_verified=True) · `refuted_by_execution` (exploit test fails, or only a
refutation test passes) · `setup_only` (exploit passes but L-levels incomplete) · `no_exploit_test` · `inconclusive`.

## recall_open flag (default OFF; additive)
When ON (a later phase) the static lenses/gates emit advisory candidates that all route to this verifier (sole
confirmer). OFF preserves every existing gate byte-for-byte. This phase demonstrates the flow by invoking the
verifier over a candidate list directly (the proof driver) — **no edit to any existing module**.

## Authority wall
The verifier confirms FOR MEASUREMENT. It sets no severity/submission_ready, performs no auto-submission, and is
un-wired from confirm_gate/min_confirm_gate (asserted by test). Submission still requires the existing gates + a
human. This is the safe boundary: proof raises confidence; it does not grant authority.
