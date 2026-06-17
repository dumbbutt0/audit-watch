# P254 — Held-Out Exploit-Chain Completion Procedure Test — SETUP

## Purpose
P253 (verdict **B**) found that the five chain-completion operations recur across contests, but proved it only
in **hindsight** (reconstructed against known ground truth). P252 separately showed that adding reasoning
*structure* to a prompt (checkpoints) did **not** complete chains blind (recall lift 0 despite firing on the
exact awarded loci). **P254 is the proof step before any scaffold build:** perform the five operations as a
**manual reasoning routine — blind, freeze-before-reveal — on an unseen contest** and measure whether
*performing* them completes awarded-equivalent chains the base hunt missed.

This phase does **not** build the scaffold, wire anything, or modify checkpoints/detectors/prompts/routing/
severity/dashboard/production source. The five operations are executed **by hand in markdown**.

## The five operations (from P253)
1. **STATE_TRANSITION_SIMULATION (STS)** — instantiate pre-state / action / post-state / repetition / edge state; check the invariant.
2. **ADVERSARIAL_ACTOR_SUBSTITUTION (AAS)** — replace the honest actor with an attacker who chooses input / acts on-behalf / splits identity / chooses timing / forces another's state.
3. **TERMINAL_STATE_EVALUATION (TSE)** — where do assets/permissions/state end; recoverable? success-despite-failure? stranded? retry?
4. **INVARIANT_DELTA_COMPUTATION (IDC)** — conserved invariant; before/after delta; who loses; who gains; amplifiable?
5. **CROSS_CALL_IDENTITY_TRACKING (CCIT)** — track msg.sender/receiver/owner/payer/refund/from-to/beneficiary across adapter/router/executor/module layers; checked principal == affected principal?

## Target — `loopfi-2024-07-holdout` (LoopFi, Code4rena 2024-07)
Leverage/CDP looping protocol. Exclusions honored: NOT reNFT/PoolTogether/Salty/Spectra; NOT any P253-design
contest (decent/vultisig/kleidi/centrifuge/munchables); NOT the P249/250/251 dev set.

- **Unseen for awarded-recall:** `audits/loopfi-2024-07-holdout/findings/raw` and `.../findings/validated` are
  **empty** (never hunted). The answer key at `audits/loopfi-2024-07-holdout/reports/` is **SEALED** and is not
  opened until Phases 1–3 are frozen and hashed (see REVEAL_AND_SCORE.md).
- **Checkpoint-ready:** `output/coverage_manifest.json` — 399 in-scope function items, ROOT-relative `file`
  paths resolve, `source_span` present. Both checkpoints ran (BASE_HUNT_FREEZE.md).
- **Surface for the 5 ops:** CDPVault (positions / liquidation — STS/AAS/IDC), AuraVault & PoolV3 & StakingLPEth
  (ERC4626 + reward accounting — IDC/STS/A1), PositionAction*/SwapAction/PoolAction proxy layer (CCIT/AAS),
  Flashlender, quotas (PoolQuotaKeeperV3/GaugeV3).

### Disclosed prior exposure (NOT answer-key contamination)
P147 (`p147_nondup_runtime_poc`) touched loopfi `MultiFeeDistribution.getReward` / `claimFromConverter` **only
as rejected controls** ("control (no bug)" / "control (intended) — pays rewardConverter by NatSpec"), on an
explicit *"no local answer key"* basis. No loopfi awarded chain was ever revealed. The only residual knowledge
is that MFD reward-claim is *not* an award locus — which narrows the surface honestly and is recorded here for
integrity. Nothing about the awarded findings was seen.

## Method (mirrors P250/P252 forward-blind; isolated, no active-audit touch)
- Active audit `size-credit-2024-06-blind` is **not** switched; `output` symlink unchanged.
- Checkpoints run via explicit `--manifest`/`--out` into this phase's `outputs/` (no `audit_path` write):
  - `scripts/accounting_checkpoint_audit.py --manifest audits/loopfi-2024-07-holdout/output/coverage_manifest.json --out .../outputs/loopfi_accounting_checkpoint.json --quiet`
  - `scripts/state_transition_checkpoint_audit.py --manifest <same> --out .../outputs/loopfi_state_transition_checkpoint.json --quiet`
- Base candidates = an isolated/manual blind read = the **frozen base-workflow analogue** for P254 (so it stays
  comparable to the original procedure), NOT an ad hoc hunt. Checkpoint records are advisory inputs.

## Phase order (freeze-before-reveal)
1. **BASE_HUNT_FREEZE.md** — frozen base candidates + checkpoint records + rankings + generation basis +
   three-way state tag per item. Hashed.
2. **SELECTED_LOCI.md** — 2–5 loci picked pre-reveal, each with a no-hindsight lock. Hashed.
3. **PROCEDURE_OUTPUTS.md** — the five-operation routine per locus, op labels + chain status. Hashed.
4. **REVEAL_AND_SCORE.md** — open the sealed key, classify, score (only after 1–3 are hashed).
5. **OPERATION_CONTRIBUTION.md** + **VERDICT.md**.

## Standing caveats
n=1 contest; no PoCs; training-confound (same operator runs base + routine) → the confound-light signal is the
**procedure-completed-not-base** delta, not absolute recall. No softening toward verdict A unless the pre-reveal
routine actually completes a missed chain.
