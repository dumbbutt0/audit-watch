# PCS — recommendation

## Decision: `ACCEPT: decent-2024-01-holdout` (4 qualifying contract-level Highs · 5 Mediums)

decent is the best positive-control corpus for testing whether the refined severity gate **confirms** genuine
contract-level Highs (the axis P200/P201 never validated):
- **4 / 4 Highs are contract-level, Solidity-source-reachable, permissionless/attacker-controlled** with qualifying
  impact (≥1 clean permissionless theft via missing access control; the others permanent-loss/fund-misrouting in
  the cross-chain bridge value-flow). This is the richest matched-High set of the three.
- **5 Mediums** → enough to keep measuring over-HIGH demotion in the same run (preservation *and* demotion together).
- Cross-chain bridge swap/execute domain (UTB / executor / swapper / bridge-router + the audited
  `lib/decent-bridge/src` contracts) — direct user-fund flow, exactly the surface a severity gate must grade High.

Not `DATASET_TOO_THIN`: decent clears the ≥2–3 qualifying-Highs bar with margin (4). vultisig (2 qualifying, 3 Med)
and munchables (2 qualifying, 2 High) are viable fallbacks if decent is disqualified, but both are thinner on one
axis (vultisig Mediums; munchables total Highs).

## Why this matters
P201 left the gate's High-confirming path **unexercised** (0 HIGH_CONFIRMED, 0 matched Highs). decent provides the
**positive control**: a corpus where, if the refined gate is correctly calibrated, it should produce
HIGH_CONFIRMED on the qualifying contract-Highs while still demoting the Mediums. A run that confirms the Highs and
demotes the Mediums would be the first two-sided out-of-sample validation; a run that demotes the genuine Highs
would show the reject-first bar is too aggressive.

## IMPORTANT — firewall/contamination caveat (must carry into the validation phase)
The screening subagents **over-returned**: their free-text reasoning preambles named some files/mechanisms before
the JSON (e.g., bridge contract names and High mechanism hints for all three corpora). Only the JSON tallies were
persisted to `screening_outputs/`, but the **orchestrator was transiently exposed** to those preambles. Therefore
the orchestrator now holds partial prior knowledge of decent's High mechanisms/loci.

Mitigation for the decent validation phase (mandatory):
1. The refined gate's per-mechanism calibration on decent must be authored by a **fresh firewall subagent** (not the
   contaminated orchestrator), OR
2. apply the gate via a deterministic procedure with the contamination explicitly disclosed and the result treated
   as an **upper bound** on the gate's High-confirm ability,
and in all cases **re-unseal independently and freeze both blind verdicts and calibration before any full
answer-key read**, disclosing this prior in that phase's integrity notes.

## Next (separate phases)
- **Positive-control validation run on decent**: blind campaign (sample the bridge value-flow + access-control +
  refund/executor surfaces) → refined mechanism-level gate (firewall-applied) → score High-confirmation AND
  Medium-demotion. Decision target: does the gate confirm genuine contract-Highs?
- Unchanged separate track: **P202** oracle-rich corpus search → **P203** oracle gate validation.
