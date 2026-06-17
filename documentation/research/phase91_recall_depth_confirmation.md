# Phase 91 — Fifth fresh sealed-key blind run (P90 recall/depth confirmation)

## Goal
Confirm whether the P90 recall/depth policy (top-16 + per-contract top-2 floor + NOT_RUN→0 +
maximal_consequence_check in the deep pass) improves conversion recall + High-labelling while holding the
calibrated **0 severity-FP** (gate frozen at P88 `193abf9f`). Confirmation run, not a repair.

## Subject & sealed-key discipline
- **kleidi-2024-10** (Code4rena), commit `89266a7d…`, **11 in-scope contracts** (~2836 lines; Timelock.sol
  dominates at 1344). Fresh — a Safe-module timelock/guardian system.
- **Sealed-key PRESERVED:** metadata → leads → C-chain bundles → maximal-consequence outputs → adversarial →
  severity outputs → `prekey_freeze.json` (`answer_key_opened=false`) all frozen **before** the findings repo
  was cloned. No web search; `4naly3er-report.md` / README never opened.

## P90 lead policy (applied)
Lens → 28 leads. Selected = **global top-16 ∪ per-in-scope-contract top-2 floor + 3 controls = 22**, each
tagged with `inclusion_source`. **The per-contract floor added 5 leads from contracts the top-16 missed
entirely** (`ConfigurablePause.pause`, `Guard.checkTransaction`, `InstanceDeployer.createSystemInstance`,
`RecoverySpellFactory.createRecoverySpell`, `TimelockFactory.createTimelock`) — the policy worked mechanically.
**NOT_RUN = 0** (every lead dispositioned).

## C-chain result (frozen pre-key)
- **0 kept promotions.** 1 candidate found, demoted; 4 honest abstains; 17 rejected.
  - `RecoverySpellFactory.createRecoverySpell` — a **real** bug (the transient-storage duplicate-owner check
    `tstore(owner,1)` is never cleared, vs the clean loop in `calculateAddress`), so same-tx batch creation of
    spells sharing an owner reverts. The **isolated key-blind adversarial reviewer adjudicated it Low/QA**
    (bounded, self-inflicted, retry-recoverable, no funds at risk); `maximal_consequence_check` correctly did
    **not** escalate; the gate **demoted** it to NEEDS_CONTEXT → **0 severity FP**.
  - NEEDS_CONTEXT abstains (honest, deep/config-dependent): `executeWhitelisted`/`executeWhitelistedBatch`,
    `addCalldataChecks`, `InstanceDeployer.createSystemInstance`.
- Safety: 0 SOURCE_FALSE / unsupported-READY / HARD_FAIL / detector→finding. Controls 3/3 rejected.

## Scoring vs key (0 High + 3 Medium — hardened, low-density, all in Timelock)
| Axis | Result |
|---|---|
| Sealed-key · NOT_RUN | preserved · 0 ✅ |
| Safety (4 axes) | 0/0/0/0 ✅ |
| **Severity FP after gate** | **0** ✅ |
| Controls | 3/3 rejected ✅ |
| Per-contract floor | added 5 contracts ✅ (but 0 hits — see below) |
| **Conversion** | **0 CLEAN_HIT / 0 STRONG_PARTIAL** ⚠ |
| False-demotion of a surfaced true M/H | 0 ✅ |

- **M-02** ("wrong handling of calldata check indices … `endIndex-startIndex` missing `+1` → whitelisted call
  reverts when a param fills all its bytes") → I **localized to the calldata-check** and flagged
  `Timelock.addCalldataChecks` **NEEDS_CONTEXT** (right area) but did **not** trace the off-by-one → near-miss,
  not converted. **Deep-pass DEPTH miss** (P90-B's #1 predicted bucket).
- **M-01** (gas-griefing via creating proposals; requires ≥threshold keys exposed) → rejected `scheduleBatch`
  as standard timelock → MISS (depth, precondition-heavy).
- **M-03** (`updateExpirationPeriod` can't reduce below current in a window) → rank 18, **not selected**
  (below top-16; Timelock's floor-2 already in top-16) + a self-governance setter → selection/control miss.

## Verdict — SAFETY-ONLY PASS
Safety + **0 severity FP** + controls clean + NOT_RUN=0 hold, but **conversion = 0**. Per the rubric this is
exactly Safety-only PASS.

### What this says about P90 — honestly INCONCLUSIVE for the recall claim
- Kleidi is **hardened/low-density** (0 High, only 3 Medium, all concentrated in `Timelock`). Conversion recall
  could not be meaningfully exercised.
- **The per-contract floor was the wrong lever for this subject:** it covered 5 *other* contracts, but every
  awarded finding was in the **dominant top-scoring contract** (`Timelock`). The floor helps when findings sit
  in *low-scoring* contracts; here they didn't.
- **The deep-pass DEPTH gap is reconfirmed as the #1 lever** (P90-B): M-02 was correctly *localized* but not
  *deep-traced*; M-01/M-03 were depth/selection misses.
- **KEY POSITIVE — the 0-severity-FP discipline held under temptation.** A real-but-bounded bug
  (RecoverySpellFactory) was correctly adjudicated Low/QA by the isolated adversarial review +
  maximal_consequence_check + the frozen gate and kept out — and it was indeed **not** in the awarded set. The
  maximal_consequence_check also correctly did **not** over-escalate. So P86/P88 + the new P90-C check are
  jointly robust on fresh hardened material.

Per constraints: no machinery change (gate frozen `193abf9f`; `maximal_consequence_check` unchanged), no
post-key tuning, no retroactive re-score. No promotion → no P84 handoff bundle, no funnel record (accurate).

## Next recommendation
- **P90's recall improvement remains unvalidated** — re-test on a **higher-density subject with findings in
  low-scoring contracts** (to actually exercise both conversion and the per-contract floor's payoff).
- **The real lever is deep-pass DEPTH** (M-02 localized-but-not-traced; M-01 griefing): a P92 **deep-pass depth
  prompt** that, once a lead is localized to a suspicious mechanism (e.g. a calldata index/length computation),
  forces tracing the arithmetic/edge-case to a concrete pass/revert — measured against the frozen corpora —
  is the highest-value next step, not another lead-selection or gate change.
- Consider a `calldata_range_validation` P84 type if the M-02 class recurs (1 instance so far → monitor).
