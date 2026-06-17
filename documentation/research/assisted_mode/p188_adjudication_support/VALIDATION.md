# P188 — Production adjudication calibration: validation

Implements P187's three recommendations as a **production** change, all **advisory** (no block, no
severity/routing/submission/finding write). Edits: `prompts/deep_trace.md` (Parts C/D + schema) and
`scripts/validate_deep_pass_mechanisms.py` (Parts A/B detectors). The research module
`scripts/research/adjudication_rubric.py` stays **un-wired** — its logic was ported natively into the checker, not
imported.

## What was added
- **Part A — `non_responsive_rejection`** (`detect_non_responsive_rejection`): flags a rejection whose alleged
  locus is absent from the entire rejection row. Locus = explicit `claimed_locus` field if present, else derived
  from the **best-matching inventory entry's distinctive identifiers** (strong match only: word-set Jaccard ≥ 0.6
  or substring containment; identifiers are camelCase / snake_case / dotted, length ≥ 6, prose words excluded).
- **Part B — `severity_floor_misrejection`** (`detect_severity_floor_misrejection`): flags a rejection that
  invokes a fund-loss/High bar (`not fund-loss`, `no funds`, `not theft`, …) while a genuine Medium-class impact
  (DoS / lockout / griefing / unavailability / permanent block) is present. A no-impact rejection (dust /
  self-funded, no victim) does **not** flag — reject-first preserved.
- **Part C — harness escalation** (prompt): a source-evidenced, plausible, not-disproven mechanism whose only
  rejection basis is **runtime behavior** goes to `unresolved_mechanisms` with `status:"NEEDS_HARNESS"`. The
  checker recognizes/counts it and never flags carried mechanisms.
- **Part D — reject-first preservation** (prompt): explicit list of when a rejection is still valid (source
  disproves / impact impossible / assumption contradicted / guard proven / invariant proven) + "not a carry-
  everything change."

## (1) Frozen P186 replay — `scripts/validate_p188.py` → `before_after_matrix.json` / `metrics.json`
The 5 frozen P186 deep-trace outputs replayed through the updated `check_output()` (read-only; in-memory copies):

| function | awarded | flags before | flags after |
|---|---|---|---|
| onAfterRemoveLiquidity | **M-02** | (none) | **`non_responsive_rejection`** — claimed_locus `lpTokenDepositValueChange`, rejection_locus `feePerLP, feeAmount, mulDown` |
| UpdateWeightRunner._getData | **M-06** | (none) | **`severity_floor_misrejection`** — impact_type `dos`, severity_floor `Medium` |
| afterUpdate | M-03/M-10/L-01 (stable) | (none) | (none) |
| onAfterSwap | H-03 (stable) | (none) | (none) |
| MultiHopOracle._getData | L-02 (stable) | (none) | (none) |

`metrics.json`: `m02_non_responsive_flagged=true`, `m02_claimed_locus="lpTokenDepositValueChange"`,
`m06_severity_floor_flagged=true`, `stable_selection_false_positives=0`, `acceptance_pass=true`.

## (2) Checker remains advisory
- No `severity` / `submission` / `routing_allowed` / `submission_ready` / `"status":"finding"` writes (grep: only
  descriptive comments mention severity/submission — no assignment). `main()` always `return 0` — never blocks.
- Detectors run **only** over `rejected_mechanisms` rows, so `selected`/`unresolved` (carried) mechanisms are never
  flagged. No mechanism is ever upgraded to a finding — outputs are advisory flags only.

## (3) Frozen traces byte-identical (md5 first-8)
P186 `raw_outputs/*.json` unchanged: `onAfterRemoveLiquidity 3a37b556`, `UpdateWeightRunner__getData c4e979f7`,
`afterUpdate 43060330`, `onAfterSwap 86c8993f`, `MultiHopOracle__getData 7015fead`; P186 `metrics.json eacfdbde`.
The replay operates on in-memory copies and never writes the frozen files.

## (4) Prompt still well-formed
`prompts/deep_trace.md` retains: mechanism inventory · rejection table · stop condition · selected_mechanisms ·
unresolved_mechanisms — and now adds REJECTION RESPONSIVENESS (`claimed_locus`), SEVERITY FLOOR, HARNESS
ESCALATION (`status:"NEEDS_HARNESS"`), and REJECT-FIRST preservation.

## Tests — `tests/deep_solidity/test_adjudication_support.py` (10 passed)
responsive rejection passes · non-responsive rejection flagged · severity-floor misrejection flagged · valid
(dust/self-funded) severity rejection not flagged · source-disproven rejection allowed · NEEDS_HARNESS recognized
& not flagged · frozen M-02 / M-06 / zero stable false-positives · checker-advisory. Existing
`test_deep_pass_mechanism_checker.py` (8) still green. Full `tests/deep_solidity` = 127 passed, 2 failed — the
2 failures are the **pre-existing** frozen-snapshot drifts (`cross_artifact_lifecycle*`, `recipient_custody*`;
failing since before this session, no P188 import), unrelated to this change.

## Acceptance criteria — ALL MET
- M-02 flagged `non_responsive_rejection` ✓
- M-06 flagged `severity_floor_misrejection` ✓
- stable-selection false-positive count = **0** ✓
- checker remains advisory ✓
- no routing / severity / submission change ✓
- reject-first rejection paths intact (Part D + `test_source_disproven_rejection_allowed`,
  `test_valid_severity_rejection_not_flagged`) ✓
