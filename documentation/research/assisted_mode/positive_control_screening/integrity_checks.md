# PCS — integrity checks

## Production hashes byte-identical START == END (md5 first-8)
| artifact | START | END | ok |
|---|---|---|---|
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | 5d2a97f9 | 5d2a97f9 | ✓ |
| `scripts/eval_locus_resolver.py` | 3b0b2c02 | 3b0b2c02 | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | ✓ |

No production prompt/checker/router/ledger/detector/dashboard edit; no `deep_trace.md` patch; no gate application;
no blind eval run; no submit/route/promote/demote. Read-only/metadata phase. No new production code.

## Seals / symlink
- decent / munchables / vultisig `_sealed_answer_key/report.md` all intact (files unchanged). Opened only via the
  documented controlled title/summary-level unseal **performed by firewall screening subagents**, not the orchestrator.
- `output -> audits/quantamm-2024-12-eval/output` symlink unchanged.
- All screening JSON valid. `fabrication_rate=0` (every tally derives from a subagent's read of the sealed report).

## Firewall result — PARTIAL LEAK (recorded, mitigation specified)
The screening subagents were instructed to return ONLY JSON tallies. They complied for the persisted artifacts —
`screening_outputs/*.json` contain **tallies only, no verbatim titles/loci**. However, the subagents' free-text
**reasoning preambles** (before the JSON) named some files and High mechanism hints for all three corpora. The
orchestrator was transiently exposed to those preambles; **only the JSON was persisted** (preambles not written to
any deliverable).
- **Consequence:** the orchestrator holds partial prior knowledge of the candidate corpora's High mechanisms/loci,
  including the recommended corpus (decent).
- **Mitigation (mandatory, carried to `PCS_RECOMMENDATION.md`):** the decent validation phase must (1) author the
  refined-gate calibration via a **fresh firewall subagent** (not the contaminated orchestrator) or treat the
  orchestrator-applied result as an **upper bound**, and (2) re-unseal independently and **freeze blind verdicts +
  calibration before any full answer-key read**, disclosing this prior in that phase's integrity notes.
- **Process fix for future screening:** require subagents to emit JSON-only with no preamble (or route their output
  through a stripper) so the orchestrator never sees reasoning text.

## Deliverables
`PCS_PLAN.md` · `INTEGRITY_PRECHECK.md` · `SCREENING_PROTOCOL.md` · `screening_outputs/{decent,munchables,vultisig}.json`
· `VIABILITY_TABLE.md` · `PCS_RECOMMENDATION.md` · `integrity_checks.md`.

## Decision
`ACCEPT: decent-2024-01-holdout` (4 qualifying contract-level source-reachable Highs · 5 Mediums). Not DATASET_TOO_THIN.
