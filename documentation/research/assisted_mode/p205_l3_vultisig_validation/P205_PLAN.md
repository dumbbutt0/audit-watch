# P205 — Second-corpus validation of the L3 realized-impact HIGH standard on vultisig

## Context
P204 showed the L3 realized-impact HIGH standard (HIGH only if an executable harness realizes *material* theft/
insolvency/permanent-loss/unauthorized-priv-control under source-valid honest custody) cleanly separated decent's
genuine High (H-01) from the false-Highs static gates over-confirmed (M-03/06/12) — `L3_STANDARD_PROMISING`. One
corpus is a signal, not a warrant. P205 tests **generalization** on a 2nd fresh positive-control corpus,
**vultisig-2024-06** (PCS-accepted: 3H/3M, 3/3 Highs contract-level+source-reachable, 2 qualifying). Validation +
measurement only; no production change, no gate wiring.

## Method (reuse P204's proven harness approach + a fresh blind run)
Self-contained Foundry project under `documentation/research/assisted_mode/p205_l3_vultisig_validation/pocs/`:
real vultisig contracts imported via a **byte-identical copy** (`realsrc/`, production untouched, hash-verified);
**mock only external deps** (OZ ERC721, Uniswap **v3-core** interfaces/libs `IUniswapV3Pool`/`FixedPoint128`/
`FullMath`, `@uniswap` periphery as needed, a faithful V3 pool/factory where a path requires it); forge-std-free
(reuse the inline `Vm` + assert base pattern from P204). Honest custody; no arbitrary mock behavior to manufacture a High.

## Decisive feasibility note (and fallback)
vultisig is an ILO launchpad: `ILOPool` is ERC721 + Uniswap-V3-position based; `claim`/`launch` touch a V3 pool. So
the **positive-control High harness is V3-entangled** (hard) while the **whitelist/access-bypass High (negative
control) is pure access-control (tractable)**. The raise/`buy` and `claimRefund` fund-custody paths are largely
ERC20 and more harnessable. **Fallback (baked in):** if a faithful source-valid positive-control material-impact
harness cannot be built within prototype scope (V3 dependency web), that control is reported
`HARNESS_INCONCLUSIVE` (honestly, not forced), and the phase decision reflects it (likely `L3_STANDARD_PARTIAL`).
Mocking the V3 pool is permitted only as a **faithful external dep**, never to manufacture impact.

## Contamination note
During PCS the orchestrator was transiently exposed to vultisig High hints (ILOPool fee-collection, ILOManager
single-sided-liquidity DoS, Whitelist bypass). As in P204, **L3 results are objective EVM executions** (contamination-
resistant); target selection + harness setup are pre-registered in `L3_TARGET_MATRIX.md` + source-justified, with the
caveat recorded. Blind subagents are fresh and key-blind.

## Required sequence
1. **Integrity precheck** (`INTEGRITY_PRECHECK.md`): START md5 first-8 `deep_trace.md ef93a6c2`,
   `validate_deep_pass_mechanisms.py 5d2a97f9`, `eval_locus_resolver.py 3b0b2c02`, ledger `e23c5bc9`, vultisig source
   tree, relevant P204 artifacts. Confirm vultisig seal intact; harness artifacts isolated under the p205 dir; no
   production file modified.
2. **Controlled viability boundary** (`CONTROLLED_UNSEAL.md`, `CORPUS_VIABILITY.md`): count-only (confirm 3H/3M, 2
   qualifying contract-Highs); record unseal boundary; do not read finding bodies before target-selection. If too
   thin for a 2-sided test (need ≥1 genuine High + ≥1 Medium/false-High) → flag `DATASET_TOO_THIN`.
3. **Source-only coverage manifest** (`COVERAGE_MANIFEST.md`): files · external entry points · signer/access-control
   surfaces · vault/ILO control · asset-transfer/approval paths · role/admin boundaries · signature/whitelist
   validation · invariant-bearing transitions · fund-custody points. Pre-register a bounded **~8–10 surface** sample
   (ILOPool buy/claim/launch/claimRefund, ILOManager initILOPool/launch/claimRefund/setPlatformFee, ILOWhitelist,
   ILOVest, LiquidityManagement).
4. **Blind threat-ceiling run** (`BLIND_THREAT_CEILING_RESULTS.md`, `blind_prompts/`, `raw_outputs/`): production
   `deep_trace.md` unchanged; one blind Sonnet subagent per surface (frozen prompt = deep_trace.md + verbatim
   source; no key/PCS hints). Token-scan prompts+outputs. **FREEZE 1** (raw-outputs hash).
5. **L3 target selection** (`L3_TARGET_MATRIX.md`): from frozen blind outputs select likely-High / Medium-rated-High
   / static-capability-only / access-or-signature-bypass / direct-theft-or-permanent-loss candidates; record why each.
6. **Controlled answer-key scoring boundary**: after FREEZE 1, open the key only to map blind mechanisms → awarded
   High/Medium/false-positive classes; complete the target matrix; keep mapping separate from harness code.
7. **L3 standard before harness results** (`L3_HIGH_STANDARD_VULTISIG.md`): the P204 L3 HIGH conditions adapted to
   vultisig (attacker-controlled entry · executable tx · source-valid config · concrete asset/vault-control/priv-
   authority · victim/protocol material loss/permanent-lock/insolvency/unauth-priv-transition · material magnitude ·
   no trusted/admin prereq · no arbitrary mock custody · no theoretical-capability-without-realized-impact).
   Non-High: MEDIUM (bounded/reversible/local/access-bypass-only) · NEEDS_HARNESS (plausible-but-unproven) ·
   SOURCE_REFUTED.
8. **Build L3 harnesses** (`POSITIVE_CONTROL_POC.md`, `NEGATIVE_CONTROL_POC.md`, `pocs/.../*.t.sol` + run logs):
   ≥1 positive-control High harness (a qualifying permanent-loss/theft High — measure before/after asset/vault/
   permanent-lock state) and ≥1 negative-control harness (the access/whitelist-bypass High and/or a Medium — show
   capability without realized material impact → demote). Control cases where practical. Per-control
   `HARNESS_INCONCLUSIVE` if a source-valid material harness can't be built (documented, not fabricated).
9. **L3 scoring** (`L3_SCORECARD.md`, `metrics.json`): blind HIGH count · L3 HIGH_CONFIRMED count · awarded Highs
   tested/preserved/demoted · awarded Mediums demoted/still-over-HIGH · false-High before/after · NEEDS_HARNESS ·
   harness-inconclusive · production source changes (must be none).
10. **Failure cases + recommendation + decision** (`FAILURE_CASES.md`, `P205_RECOMMENDATION.md`) + integrity
    re-check + memory.

## Decision space
`L3_STANDARD_VALIDATED_SECOND_CORPUS` (≥1 genuine awarded High preserved by executable material impact · ≥1
Medium/false-High demoted/Needs-Harness · no source-proven genuine High wrongly demoted · production unchanged ·
harnesses source-valid/isolated) · `L3_STANDARD_PARTIAL` · `L3_STANDARD_FAILED_FALSE_HIGH` ·
`L3_STANDARD_FAILED_FALSE_DEMOTION` · `HARNESS_INCONCLUSIVE` · `DATASET_TOO_THIN` · `INVALID_RUN`.

## Acceptance / guardrails
vultisig 2nd positive-control; L3 standard written before harness outcomes; ≥1 positive High + ≥1 negative control
tested; harnesses demonstrate realized impact or its absence (capability-only ≠ High); real contracts imported
byte-identically (only external deps mocked); production hashes byte-identical START==END
(`ef93a6c2`/`5d2a97f9`/`3b0b2c02`/`e23c5bc9`) + vultisig source tree unchanged; seal opened read-only only as
documented; blind firewall (prompts+outputs leak-scan, scorer post-freeze, no backfill); Sonnet; JSON valid;
`fabrication_rate=0` (every L3 verdict backed by a run log or a documented source-valid-setup obstacle); harness
artifacts isolated under the p205 pocs dir.

## Files
- **New:** `documentation/research/assisted_mode/p205_l3_vultisig_validation/` (the 15 docs above + `blind_prompts/`
  + `raw_outputs/` + `pocs/` Foundry project: `foundry.toml`/remappings, `src/mocks/`, `realsrc/` byte-identical
  copy, `test/*.t.sol`, `run_log.txt`); read-only `scripts/validate_p205.py` if a scorer helps.
- **Not touched:** production prompt/checker/router/detector/severity code; `deep_trace.md`; vultisig + other corpora
  source (imported read-only, never edited); P186–P204 + PCS deliverables; ledger/seals (except documented vultisig
  count-only + post-freeze unseal).
- **Memory (on completion):** `project_phase205_l3_vultisig_validation.md` + one-line MEMORY.md pointer.

## Follow-on (NOT this phase)
If validated on 2 corpora: operationalize the L3 HIGH bar (require a passing L1/L2/L3 PoC for HIGH promotion;
auto-scaffold vs human + cost budget) — still pre-wiring. Deep-pass recall + oracle track remain separate.
