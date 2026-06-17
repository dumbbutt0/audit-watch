# P148 — Decision

## Decision: **RUNTIME_REFUTED** (negative-control success)

A Foundry test deploys the **real velodrome `RewardsDistributor`** (a holdout, no local answer key) and calls its
real `claim`/`claim_many`. Both route **only** via `deposit_for(_tokenId, amount)` to their own tokenId (1e18
each); the external recipient (0xBEEF) received **0**; there is no `ownerOf`/AVM/expired-lock external-transfer
branch. The suspected B5-style recipient-parity divergence is **architecturally absent** and refuted at runtime.

### Rubric
- **RUNTIME_REFUTED** ✅: real runtime kills the suspected recipient divergence with positive evidence.
- Not RUNTIME_PARTIAL: a nonzero `_claim` was driven and both siblings executed end-to-end.
- Not RUNTIME_BLOCKED: compiled + executed with mocks only.
- Not RUNTIME_CONFIRMED: there is no divergence to confirm (and confirmation was forbidden this phase).

## Final response

**Candidate & why** — velodrome `RewardsDistributor` (claim vs claim_many): the ancestor of blackhole's
distributor where B5 (a real recipient-parity bug) lives, so "does the same divergence exist?" is a plausible
same-family suspicion — a true negative control, not a strawman.

**Runtime result** — 3/3 pass; both siblings `deposit_for` their own tokenId (1e18), external recipient 0,
`depositForCount == 2` → suspected divergence refuted.

**Final classification** — `runtime_refuted` (high). The axis refuted: **recipient-divergence**.

**Panel** — added as a runtime-only row `H2-velodrome-rewardsdist-parity` (`duplicate_unknown`, `runtime_only`,
routing/submission false). Panel now `{rows: 13, runtime_only: 2, by_status: {runtime_confirmed: 3, not_run: 9,
runtime_refuted: 1}}` — the full negative→positive vocabulary, exercised.

**Integrity** — prompt unchanged (`totals` == P138 baseline, byte-for-byte; `prompt_corpus_unchanged: true`);
corpus unchanged; production source unchanged (`RewardsDistributor.sol` byte-identical); no detector/gate/severity/
submission/routing changes; active `output/` symlink unchanged; un-wired (grep-clean).

**Tests** — 27 research tests pass (24 + 3 new); full suite 1664 passed / 2 pre-existing snapshot fails / 4
skipped.

**Not submission-ready.** This is a refutation, not a finding.

**Decision** — RUNTIME_REFUTED.

**Next recommended phase (P149)** — human intent/severity review of `H1-centrifuge-userescrow` (resolve the
`allowance==max` delegation-vs-weakness intent caveat), now that the panel vocabulary is complete (confirmed +
refuted both demonstrated); then P150 = a second non-duplicate runtime holdout to grow cross-architecture yield.
