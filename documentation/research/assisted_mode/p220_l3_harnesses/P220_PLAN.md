# P220 — Build L3 harnesses for ZETA-04, ZETA-10, ZETA-11

**Objective.** Generate *executed* L3 evidence for the three remaining Zeta High-ceiling candidates so their
`/candidates` dashboard cards populate PoC actual / expected / control / value-delta from real harness artifacts,
not guesses. Evidence GENERATION (build + run harnesses), not the P219 extraction pass.

**Mode.** Research-only. No external submission, no platform routing, no submit/promote/demote. Production Zeta
source, `deep_trace.md`, `min_confirm_gate.py`, `confirm_gate.py`, `run_pipeline.sh` and the P216–P219 scripts stay
byte-identical. Harnesses isolated under `pocs/p220/`. Answer-key text only in `scoring_note`/`last_reviewer_note`.

**Hard rule.** A populated L3 field must trace to a real run artifact (test file + run log); otherwise it stays empty
/ `NEEDS_HARNESS` / refuted. No fabricated actual/expected/control.

## Targets and the question each harness must answer
| ID | Source | Claim | L3 question |
|----|--------|-------|-------------|
| ZETA-04 | `ZetaConnector.non-eth.sol:61` `onReceive` | onReceive lacks `whenNotPaused` (onRevert/send have it) | Does a paused connector still execute inbound minting? |
| ZETA-10 | `ZetaTokenConsumerUniV3.strategy.sol:124` `getEthFromZeta` | missing `nonReentrant` → cross-fn reentrancy theft | Is the reentrancy reachable, and does it realize theft? |
| ZETA-11 | `ZetaTokenConsumerTrident.strategy.sol:82` `getZetaFromEth` | unvalidated `getPools(...)[0]` → theft/DoS | Does the harness reproduce the impact, and which mechanism? |

## Method
1. Integrity precheck (START hashes; `api_free=true`).
2. Evidence review + feasibility matrix per target.
3. Isolated Foundry project `pocs/p220/`: real unmodified target contracts under `realsrc/`, authentic OZ 4.8.1 +
   Uniswap v3 interfaces under `vendor/`, minimal mocks under `mocks/` (mocks must not create the vulnerability).
4. One `.t.sol` per target with actual-vs-control; run with `forge test`; save logs under `pocs/p220/logs/`.
5. Rewrite `output_research/l3_readiness/ZETA-0{4,10,11}.json` from run artifacts only.
6. Re-run `run_hunt_sync_hook.py` (sync + completion guard `--strict`); verify cards update + safety flags.
7. Tests, scorecard, END integrity.

## Decision space
`ZETA_L3_EVIDENCE_READY` · `ZETA_L3_PARTIAL` · `ZETA_L3_FAILED_REFUTED` · `ZETA_L3_BLOCKED_BY_HARNESS_COMPLEXITY`
· `INVALID_RUN`. A clean refutation or a precise INCONCLUSIVE is a valid outcome; three PASSes are not required.
Severity calibration is `validate_p208_l3_readiness.decide()`'s job, never the harness author's or the answer key's.
