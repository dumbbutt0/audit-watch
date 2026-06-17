# P141 — Completion Artifacts

Each completed job has a P140-schema artifact under `<audit>/output/value_provenance_manual_results/<job_id>.json`
(written during measurement, removed on restore — copies of the resulting merged records are in
`{noya,blackhole,size}_results.json` here). All artifacts share:
`execution_mode=manual_in_session`, `advisory_only=true`, `submission_ready=false`, `requires_human_review=true`,
`prompt_name=deep_pass_value_provenance`, `source_result_path` → the P137/P138/P141 deliverable; **no answer-key
issue IDs**; `reviewer_or_runner` names the exact blind subagent id.

| job_id | decision | confidence | recommended_next_step | reviewer_or_runner |
|---|---|---|---|---|
| VP-SolvencyV2.convertAmountsToValues | strong_clear | high | keep_advisory | P141 fresh blind `aa6d4aac2a89ed1b9` |
| VP-NoyaValueOracle._getValue | finding | high | build_poc | P137 blind subagent |
| VP-RewardsDistributor.claim_many | finding | high | build_poc | P138 blind `a67fb918317d02d07` |
| VP-RewardsDistributor.claim | strong_clear | high | keep_advisory | P138 blind `a8b0c3cd763de3d36` |
| VP-RewardsDistributor.claimable | strong_clear | high | keep_advisory | P138 blind `af34d02a9bfb2d68a` |
| VP-SellCreditMarket.validateSellCreditMarket | needs_human | medium | human_review | P138 blind `a281e3db7ab349438` |
| VP-AccountingLibrary.debtTokenAmountToCollateralTokenAmount | strong_clear | high | keep_advisory | P138 blind `a403bf1955e6383ae` |

## Provenance separation (constraint 13)
- **Prompt-derived (all 7):** advisory review evidence only.
- **Runtime-confirmed (0):** none. No PoC was run; the two `finding` rows remain hypotheses requiring PoC + human
  review before any severity/submission. `needs_human` is explicit uncertainty.

## Forbidden-field discipline
No artifact carries `confirmed:true`, `submission_ready:true`, `advisory_only:false`, or a bare `final_severity` —
so none were quarantined (0 rejected across all 7). The ingester additionally **forces** the advisory triplet on
every merged entry regardless of artifact contents (defense-in-depth).
