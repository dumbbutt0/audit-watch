# P146 — Runtime Panel Schema

## Vocab (requirements 1–2)
- `runtime_status` ∈ `{not_run, partial, runtime_confirmed, runtime_refuted, inconclusive}` (out-of-vocab →
  `inconclusive`).
- `runtime_confidence` ∈ `{none, low, medium, high}` (out-of-vocab → `none`).

## Per-row fields (requirement 3)
| field | source | notes |
|---|---|---|
| `bug_id` | corpus `item_id` | |
| `architecture` | sidecar / corpus `arch` | |
| `bug_class` | sidecar / corpus `expected_shape` | |
| `harness_path` | sidecar `harness_path`/`test_path` | null when not_run |
| `real_contract_deployed` | sidecar (or derived from `runtime_harness_type=="real_contract"`) | |
| `production_source_modified` | sidecar (default false) | |
| `corrected_reference_type` | sidecar | e.g. `one_line_fixed_copy`, `protocol_sibling_claim` |
| `control_case` | sidecar | e.g. `single_hop+equal_price`, `non_avm` |
| `vulnerable_output` | sidecar | |
| `corrected_output` | sidecar | |
| `divergence_summary` | sidecar | |
| `limitations` | sidecar | |
| `duplicate_status` | sidecar | e.g. `duplicate_known` |
| `runtime_status` | sidecar (default `not_run`) | vocab-validated |
| `runtime_confidence` | sidecar (default `none`) | vocab-validated |
| `routing_allowed` | **forced false** | research invariant |
| `submission_ready` | **forced false** | research invariant |

## Panel envelope
`{generated_at, is_gate:false, research_only:true, routes_in_production:false, routed_manifest_ids:[],
routing_allowed:false, summary:{rows, by_status}, integrity:{...}, rows:[...]}`.

## Backfill (requirements 4–5)
| bug_id | runtime_status | runtime_confidence | duplicate_status |
|---|---|---|---|
| B1 (noya, NoyaValueOracle._getValue) | runtime_confirmed | high | duplicate_known (H-03) |
| B5 (blackhole, RewardsDistributor.claim_many) | runtime_confirmed | high | duplicate_known (M-04) |
| B2,B3,B4,C1,C2,C3,C4,C5,P141-SOLV (9) | not_run | none | — |
