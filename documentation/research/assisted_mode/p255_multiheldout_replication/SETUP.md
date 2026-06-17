# P255 — Multi-Heldout Chain-Completion Replication — SETUP

## Purpose
Rerun the **exact P254 five-operation routine, unchanged**, blind + freeze-before-reveal, on 2 more unseen
contests, to answer:

The five operations (identical to P254, no additions): **STATE_TRANSITION_SIMULATION (STS)** ·
**ADVERSARIAL_ACTOR_SUBSTITUTION (AAS)** · **TERMINAL_STATE_EVALUATION (TSE)** ·
**INVARIANT_DELTA_COMPUTATION (IDC)** · **CROSS_CALL_IDENTITY_TRACKING (CCIT)**.

- **Primary:** does the routine *repeatedly* produce procedure-completed-not-base awarded/partial-award chains?
- **Secondary:** is the main failure mode still **mechanism selection** (P254 = 1/4 awarded-mechanism selection)?

No scaffold, no new operations, no procedure tuning from LoopFi mistakes, no production edits.

## Targets (operator-approved: basin + bakerfi)
Architecturally distinct from loopfi-CDP and from each other. Excluded for contamination: P253-design contests,
P246 reveals (+badger), barred (reNFT/PoolTogether/Salty/Spectra), P254 (loopfi), and award-revealed contests
(kelp read-FULL+scored in p241; ecg p152/p153; abracadabra p154–163 campaign; dittoeth P245; predy value_state_recall).

| contest | architecture | in-scope fns | disclosed prior exposure (areas EXCLUDED from selection) |
|---|---|---|---|
| `basin-2024-07-holdout` | AMM "Wells" (Aquifer/Well/Stable2/pumps) | 26 | p160 examined the Well **MEV/donation** finding (`SOURCE_REFUTED`) — that area excluded |
| `bakerfi-2024-05-holdout` | leveraged-ETH vault (Vault/StrategyLeverage/oracle) | 167 | p242 hunted **create-time-reentrancy** + **ERC4626-share-accounting** families — those areas excluded |

Neither has a local answer key (`reports/` empty) → reveal is **post-freeze** via WebFetch/WebSearch of the
verified `code-423n4/2024-07-basin-findings` and `code-423n4/2024-05-bakerfi-findings` issues (WebSearch fallback
if a report page exceeds the 10 MB fetch limit, as in P254/P250).

## Method (identical to P254; isolated; no active-audit touch)
- Active audit `size-credit-2024-06-blind` not switched; checkpoints run via `--manifest`/`--out` into this
  phase's `outputs/` (no `audit_path` write). Invariants re-verified per output (`emits_findings:false`, 0 concluded).
  - basin: accounting 8 recs (Stable2 calc* A5/A1) · state-transition 0.
  - bakerfi: accounting 21 recs (Vault rebalance/deposit/withdraw + StrategyLeverage flashloan/leverage + PythOracle) · state-transition 0.
- Base candidates = isolated/manual blind read = frozen base-workflow analogue (P250/P252/P254 method).
- The five operations are performed **by hand** in `<contest>_PROCEDURE_OUTPUTS.md`.

## Per-contest phase order (freeze-before-reveal)
1. `<contest>_BASE_FREEZE.md` — candidates + checkpoint records + rankings + command basis + **three-way tag**
   (`BASE_COMPLETED_CHAIN`/`BASE_BORN_INCOMPLETE`/`CHECKPOINT_HIT_SUSPICIOUS_LOCUS`).
2. `<contest>_SELECTED_LOCI.md` — 3 loci, each with a **pre-reveal no-hindsight lock**.
3. `<contest>_PROCEDURE_OUTPUTS.md` — 5 ops/locus (PASS/NO_EFFECT/UNCLEAR/CANDIDATE_STRENGTHENED) + chain status
   + **plausible-mechanisms-considered count** (new P255 metric). Hash all three before opening the key.
4. `<contest>_REVEAL_AND_SCORE.md` — classify (AWARDED_EQUIVALENT/PARTIAL_AWARD/SAME_AREA_WRONG_MECHANISM/
   BENIGN/FALSE_POSITIVE) + one of the four **mechanism-selection labels** per locus.

Then `REPLICATION_METRICS.md` (pooled vs LoopFi's 1/4) + `VERDICT.md` (A/B/C/D).

## Standing caveats
n≈3 contests total (incl. P254); no PoCs; training-confound (same operator) → credited signal is the
procedure-completed-not-base delta. No softening toward A.
