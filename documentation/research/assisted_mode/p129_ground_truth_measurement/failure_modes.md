# P129 — Failure Modes (from measured data)

All evidence below is from `evals/beanstalk_finale/match_matrix.json` (38 MISS rows with
`failure_reason` + `correct_contract`) and the 15-record ground truth (FP autopsy).

## Misses (38/81) — dominated by source-resolution, not reasoning depth
**Headline: `correct_contract = "no"` for ALL 38 misses.** The pipeline never inspected the right
contract for a single missed bug — so depth/reasoning improvements cannot recover them; the candidate
set never reached the right surface.

| Measured `failure_reason` | n | Mapped category |
|---|---|---|
| wrong contract inspected | 12 | **source-resolution failure / candidate-generation miss** |
| missed accounting invariant | 4 | invariant-context miss |
| missing domain knowledge | 4 | candidate-generation miss (domain) |
| weak invariant extraction | 3 | invariant-context miss |
| missed attacker input | 3 | candidate-generation miss |
| architecture mapping failure | 2 | source-resolution failure |
| missed reward accounting edge | 2 | invariant-context miss |
| missed oracle/heartbeat | 2 | invariant-context miss |
| missed cross-chain/migration edge | 2 | invariant-context miss |
| missed state transition | 1 | invariant-context miss |
| found-but-not-escalated | 1 | human-review ambiguity |
| missed oracle/precision | 1 | invariant-context miss |
| missed lifecycle edge | 1 | invariant-context miss |

Rollup: **source-resolution/coverage ≈ 14/38 (37%)**, invariant-context ≈ 19/38 (50%),
domain/attacker-input ≈ 7/38 — but *gated by* the universal `correct_contract=no`, i.e. coverage is the
first-order bottleneck; invariant depth is second-order (only reachable once the right contract is in scope).

## False positives (2/14 promoted, FP rate 0.143)
| FP | agent | bug class | measured cause | category |
|---|---|---|---|---|
| AR-001 | arithmetic | price/arithmetic | "speculative-reachability" (scorecard `most_wasteful_fp_source`) | **exploitability overclaim** |
| EA-002 | economic_attack | economic | promoted lead with no awarded counterpart | candidate overclaim |

Per-agent: `arithmetic 0/2` and `economic_attack 0.5` are the only sub-1.0 reliabilities → FP risk is
**concentrated in the arithmetic + economic_attack specialists**, driven by speculative reachability.
(scorecard also names BSA-005 / DT-011 / SG-004 as privileged/lifecycle-misread FPs in the broader
pre-merge set — same overclaim family.)

## Severity errors
- **Over-severity 0.267 (4/15):** US-001 Critical→High, BSA-001 High→Medium, plus the 2 FPs High/Medium→invalid.
- **Under-severity (not penalised by downgrade metric):** BSA-003 & CC-002 Medium→High, AC-003 & DS-003
  Low→Medium, PC-001 Low→High — i.e. the pipeline also *under-rated* several real findings. Severity
  calibration error is **bidirectional**, not a one-way inflation.

## Categories observed vs not
- **Observed:** source-resolution failure (dominant), candidate-generation miss, wrong/uninspected
  contract, invariant-context miss, exploitability overclaim, severity over- and under-claim,
  human-review ambiguity (1 found-but-not-escalated).
- **Not measurable here:** duplicate/public-known rate (no live dup data), PoC failure (run stopped at
  review gate; PoC corpus is the separate n=14), impact-chain miss (not separable in these artifacts).
