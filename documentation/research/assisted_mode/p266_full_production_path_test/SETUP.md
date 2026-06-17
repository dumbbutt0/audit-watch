# P266 — SETUP (Full Production-Path Test)

**RESEARCH-ONLY · production-PATH test, NOT production authority.** Runs the full operational route on one scored
contest: `shadow advisory candidate → standalone advisory dashboard surface → operator triage → B/C ranking →
five-op completion → isolated foundry PoC → sealed-answer-key reveal → strict pre-reveal reportability gate`, with
**exact mechanism recovery** as the primary success criterion. Nothing here auto-submits, sets severity, or marks
confirmed/reportable/submission-ready.

## Target
`phi-2024-08-fresh` (Code4rena 2024-08; Phi protocol — Cred / bonding-curve / ERC1155 art / reward distribution).
9 in-scope contracts, 257 in-scope functions. Answer key = `code-423n4/2024-08-phi-findings` (PUBLIC, sealed until
Phase 8). See TARGET_SCREEN.md for the SELECT/REJECT rationale and disclosed confounds.

## Frozen inputs (verified unchanged pre-run — no tuning)
| artifact | sha256[:16] |
|---|---|
| recall_first_harness.py | `85f9cbe662d2d991` |
| research_recall_first_harness.json | `e9b74687793fd110` |
| recall_first_shape_sweep.py (P262) | `a48336275cb65a4f` |
| research_recall_first_shape_sweep.json (P262) | `62e860199e7c51cd` |
| locus_shape_prioritizer.py (P260) | `d6b494bc3c0cc746` |
| research_locus_shape_prioritizer.json (P260) | `c61da091ad3ed21e` |

Forbidden (byte-identical): dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` ·
confirm_gate `afc481c9` · validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output`
(unchanged; no `switch_audit`).

## Checkpoint generation (deterministic, reused not modified)
phi checkpoints are produced by the existing deterministic, research-only audit scripts
`scripts/accounting_checkpoint_audit.py` and `scripts/state_transition_checkpoint_audit.py`
(`--manifest <phi manifest> --out <P266 outputs>`) — same generators used across P252–P263. No edits to them.

## Tooling
foundry 1.5.1 (`forge`/`anvil`/`cast`) + `solc` available. PoCs isolated under `pocs/p266/<candidate_id>/`.

## Safety rails (held throughout)
No auto-submission; no severity/routing/submission/confirmation-gate/min-confirm/canonical-schema/detector/checkpoint-
behavior/run_pipeline-default edits; no production or contest source edits. Dashboard surface is standalone +
advisory-only (no forbidden-file edits, no canonical-finding writes). Answer key sealed until Phase 8 freeze
artifacts exist + hashed. No answer-key content used to generate candidates. Any leakage into confirmed/reportable/
severity ⇒ immediate abort (verdict G).
