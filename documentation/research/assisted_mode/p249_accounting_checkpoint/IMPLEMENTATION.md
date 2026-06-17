# P249 — Part B: Implementation

All additive, research-only, **default-off**, un-wired. No severity/routing/dashboard/prompt edits; forbidden
files byte-identical.

## Files
- `scripts/accounting_checkpoint_taxonomy.py` — pure classifier (no I/O). `classify(contract,name,sig,body,*,
  patterns)` returns a list of interrogative `ACCOUNTING_CHECKPOINT` records (one per matched family).
  Two-signal shape detection per family; never returns severity/confidence/verdict. Constant `QUESTIONS`
  (the six) and `FAMILIES` (exactly five).
- `scripts/accounting_checkpoint_audit.py` — manifest-driven runner (`--manifest`/`--out`/`--no-source`/
  `--quiet`), brace-matches bodies from `source_span`, +1-level same-contract helper resolution, dedups one
  record per (contract, function, family). Emits a report with `is_gate:false research_only:true
  routes_in_production:false emits_findings:false concludes_vulnerability:false output_type:"reasoning_records"`
  and a runtime **assert** that no record carries a conclusion (severity/concluded) — a self-tripwire against
  drifting into detector behavior.
- `config/accounting_checkpoint_patterns.json` — the A1–A5 shape markers + the six questions. `checkpoint_only:
  true`, `emits_findings:false`.
- `config/agent_policy.json` — `"accounting_checkpoint_enabled": false` (default-off; the module is un-wired
  regardless — nothing in run_pipeline/agent routing references it).
- `tests/accounting_checkpoint/test_accounting_checkpoint.py` — 8 unit tests: A1–A5 detection, the
  never-concludes invariant, benign-view→no-record, exactly-five-families.

## The five families (A1–A5) and their shape signals
| Family | Two-signal shape | Example locus |
|---|---|---|
| A1 rounding-direction | conversion/round op (`convertTo*`/`mulDiv`/`Rounding.*`) in a deposit/withdraw/mint/redeem/preview context | centrifuge `_calculateTrancheTokenAmount` |
| A2 conservation | value-create + value-destroy markers (`_mint`/`_burn`/`fee`/`harvest`) | settlement/payout fns |
| A3 double-counting | a quantity marker (`remainder`/`reward`/`balance`) + a reuse marker (`+=`/carried/`lastLockTime`) | munchables `_lock` |
| A4 shared-balance depletion | a shared marker (`escrow`/`pool`/`totalAssets`) + an actor op (`transferFrom`/`claim`/`max*`) | centrifuge `_deposit` |
| A5 index/arithmetic exactness | an index marker (`startIndex`/`slice`/`length`) + arith (`- start`/`- 1`/`% `) | kleidi `sliceBytes` |

## The `ACCOUNTING_CHECKPOINT` record (fields)
`accounting_family` · `value_source` · `value_sink` · `conservation_expected` · `conservation_actual` (empty)
· `affected_actor` · `potential_winner` (empty) · `potential_loser` (empty) · `exploit_hypothesis` (empty) ·
`questions` (the six) · `concluded:false` · `requires_operator_reasoning:true` · `severity:null` ·
`confidence:null`. The shape-derived fields (value_source/sink, conservation_expected, affected_actor) are
*observations that seed reasoning*; the empty fields are filled only by the operator answering the questions.

## The six mandatory questions (constant, family-independent)
Q1 value created? · Q2 value destroyed? · Q3 counted twice? · Q4 another actor deprived? · Q5 rounding favors
wrong side? · Q6 repeated action amplifies? — these are the exploit-chain skeleton; the candidate may only
continue once they are answered.
