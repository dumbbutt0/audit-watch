# P148 — Problem Statement

P143/P145/P147 produced `runtime_confirmed` rows; P146 built the panel. The panel vocab also defines
`runtime_refuted` / `partial` / `runtime_blocked`, but **none had been exercised** — so the dashboard could show
confirmations but had never shown a promising candidate **dying cleanly at runtime**, with evidence, without
baseline contamination or "almost-bug" noise.

**P148 is a negative-control phase.** Goal: prove the same runtime process can classify a killed candidate as
`runtime_refuted` (panel/sidecar only, baseline preserved) — a negative-control *success*, not a failed phase.
Explicitly **not** hunting for another confirmed bug.

## Candidate & result
**`velodrome-2022-05-bench` `RewardsDistributor`** (claim vs claim_many) — the **ancestor** of blackhole's
distributor where B5 (a real recipient-parity bug) lives. No local answer key (`duplicate_unknown`); not in the
corpus; not runtime-confirmed.

- **Plausible suspicion:** does the B5-style `claim`/`claim_many` recipient-parity divergence exist here too?
- **Runtime answer: REFUTED.** The real contract's `claim` and `claim_many` route **only** via
  `deposit_for(_tokenId, amount)` to their own tokenId — there is **no** `ownerOf` / AVM / expired-lock
  external-transfer branch (the exact code B5's divergence lives in). The PoC drove a nonzero claim and showed both
  siblings credit their own tokenId (1e18 each) with **zero** external-recipient transfer.

## Panel outcome
The panel now exercises the full negative→positive vocabulary: `runtime_confirmed: 3` (B1, B5, H1-centrifuge),
`runtime_refuted: 1` (H2-velodrome), `not_run: 9` — with the P138 prompt baseline (`finding 3 / needs_human 1 /
strong_clear 7`, useful_recall 0.80, clean_FP 0.0) **byte-for-byte unchanged**. The refuted row is `runtime_only`,
`duplicate_unknown`, `routing_allowed=false`, `submission_ready=false`. Not submission-ready.
