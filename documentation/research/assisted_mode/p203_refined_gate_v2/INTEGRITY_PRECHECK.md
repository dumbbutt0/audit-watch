# P203 — integrity precheck

## START hashes (md5sum first-8)
| artifact | START | expected | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |
| P202 raw blind outputs (FREEZE 1, concat) | `54abf9ca` | `54abf9ca` | ✓ |
| P202 v1 calibration (FREEZE 2) | `90cf2a4f` | `90cf2a4f` | ✓ |
| decent in-scope source tree (concat) | `623aedd6` | — (record) | n/a |

No production artifact is run or modified (deep_trace/checker recorded for discipline only).

## Reuse of frozen P202 blind outputs (no rerun)
This phase **reuses** the 14 frozen P202 raw blind outputs (`54abf9ca`) and the frozen v1 calibration (`90cf2a4f`).
No blind agents are rerun. The v2 regrade is an offline re-application of a new rule to the same frozen mechanisms.

## Backfit firewall
The orchestrator is **doubly answer-aware** (PCS contamination + read the P202 key during P202 scoring). Therefore
the v2 regrade is applied by a **fresh cold-start key-blind firewall subagent** (see `REFINED_GATE_V2_RULE.md` +
the regrade protocol). The v2 rule is **general and written before application** (`REFINED_GATE_V2_RULE.md`, authored
in Step 2, verbatim from the phase spec — not derived from the answer key). The orchestrator performs only the
post-regrade v1-vs-v2 scoring (legitimately answer-aware).

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact.

## END re-check
Recorded in `integrity_checks.md` — START==END required for the four production artifacts; frozen P202 artifacts
must remain `54abf9ca` / `90cf2a4f`.
