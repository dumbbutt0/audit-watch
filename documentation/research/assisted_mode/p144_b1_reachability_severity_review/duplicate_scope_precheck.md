# P144 — Duplicate & Scope Pre-check (local artifacts only)

## Evidence
- **Answer key** `audits/noya-2024-04-eval/output/eval_ready/noya_fresh/answer_key.md:15`:
  > `| H-03 | NoyaValueOracle::_getValue | oracle multi-hop | loop reuses static `asset` instead of advancing
  > `quotingToken` → wrong sequential conversion | oracle_liquidation / cross_function_invariant | _getValue |`
  Listed among the **19 primary Highs** (`:5-6`); also grouped under "Oracle/decimals valuation: H-01, H-02, H-03"
  (`:35`).
- **Scope** `answer_key.md:4`: NoyaValueOracle is part of the reviewed in-scope set
  ("…NoyaValueOracle/Chainlink…").
- **Prior deliverables** confirm the same item: `p137_h03_value_provenance_conversion/` (blind discovery),
  `p133_noya_human_graded_run/` (graded run), `p143_b1_runtime_poc/` (runtime PoC). All reference the identical
  `NoyaValueOracle._getValue` static-`asset` mechanism.

## Classification
- **Scope:** **IN_SCOPE_LIKELY** — NoyaValueOracle is explicitly in the reviewed in-scope set.
- **Duplicate:** **DUPLICATE_KNOWN_LOCALLY** — this is the awarded/known **noya H-03**; it is recorded in the local
  answer key and across prior P133/P137/P143 deliverables. It is **not novel** for this eval.

## Consequence
For submission purposes the duplicate gate **blocks novelty**: B1 must not be submitted as a new finding. It may be
routed to **human review as confirmation of the known H-03** (mechanism + runtime evidence), but the human owns the
duplicate ruling and the final severity. This keeps `submission_ready=false` regardless of the strong technical
case.
