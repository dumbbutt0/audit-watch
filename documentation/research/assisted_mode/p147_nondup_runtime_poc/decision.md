# P147 — Decision

## Decision: **RUNTIME_CONFIRMED_NONDUP**

A Foundry test deploys the **real centrifuge `UserEscrow`** (a holdout with no local answer key) and calls its real
`transferIn`/`transferOut`. Funds escrowed for `destination` (0xDDDD) were paid to an unrelated `receiver` (0xBEEF,
1000e18) solely via `destination`'s stale infinite ERC20 allowance (never reduced by the escrow); a corrected
reference (`receiver == destination`) reverts, and a control (`receiver == destination`) matches. This is a
runtime-confirmed value/recipient-provenance divergence with `duplicate_status=duplicate_unknown` — the first
runtime-confirmed panel row that is **not** `duplicate_known`.

### Rubric
- **RUNTIME_CONFIRMED_NONDUP** ✅: real-contract PoC shows the divergence vs corrected + control; non-duplicate
  locally (no answer key).
- Not RUNTIME_PARTIAL_NONDUP: full real-contract deploy was achieved (no wrapper).
- Not RUNTIME_KILLED_NONDUP: the divergence genuinely executes (vulnerable ≠ corrected).
- Not NEEDS_CONTEXT: a source-verifiable, runtime-confirmed divergence was found.
- **Caveat:** intent-dependent (NatSpec "additional protection") ⇒ severity/validity is for human review; this is
  not a submission and not a novelty claim.

## Final response

**What this phase tested** — the runtime-PoC method on a non-duplicate (no local answer key) holdout target:
centrifuge `UserEscrow.transferOut` recipient provenance.

**Harness** — real-contract Foundry PoC (`audits/centrifuge-2023-09-holdout/pocs/p147/`): real `UserEscrow` + mock
ERC20 + a corrected reference (`receiver==destination`) + a non-redirect control.

**Runtime result** — 4/4 pass; escrowed-for-destination funds redirected to an unrelated receiver (1000e18),
corrected reverts, control matches, repeat redirect (2000e18, allowance never reduced).

**Panel integration** — added as a **runtime-only** sidecar row (`H1-centrifuge-userescrow`,
`runtime_confirmed`/high/`duplicate_unknown`/`runtime_only:true`); panel now `{rows:12, runtime_only:1,
runtime_confirmed:3, not_run:9}`; the P138 prompt baseline (`finding 3/needs_human 1/strong_clear 7`, useful_recall
0.80, clean_FP 0.0) is **byte-for-byte unchanged** (`prompt_corpus_unchanged:true`).

**Honesty** — `duplicate_unknown` (no novelty/award claim); intent-dependent → human severity/validity review;
two design-intended loopfi candidates rejected as controls; not submission-ready.

**Tests / integrity** — 24 research tests pass (20 + 4 new); full suite 1661 passed / 2 pre-existing snapshot fails
/ 4 skipped; `UserEscrow.sol` byte-identical; un-wired; active `output/` symlink unchanged.

**Decision** — RUNTIME_CONFIRMED_NONDUP.

**Next recommended phase (P148)** — (a) human reachability/severity review of the centrifuge item (resolve the
intent caveat: is the `allowance==max` proxy an accepted design or a real authorization weakness?), or (b) exercise
the `runtime_refuted`/`partial` panel vocab by taking a candidate that the runtime *kills*, or (c) grow the
non-duplicate runtime set with another holdout to track the method's cross-architecture yield.
