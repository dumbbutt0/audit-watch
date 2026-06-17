# P213 — L3 severity-mapping repair: deterministic core-path DoS carve-out (research-only, validation-first)

## Context
P212 Stage 2 found the top awarded High (SOPH-03 = official 003-H, stETH share-rounding → `depositStEth` deterministic
revert) but the L3 mapping **under-rated it Medium** because it classified the impact as DoS. The L3 impact-measurement
layer works; the severity mapping is too blunt ("DoS → Medium"). P213 adds a **narrow, general** carve-out so a
*deterministic, source-valid, no-workaround DoS of a core supported entry/exit/conversion path* can be High — WITHOUT
reintroducing the P199 over-HIGH problem. Research-only; **do not wire** until it survives regression.

## Recon (read-only) — the exact repair point
- `scripts/validate_p208_l3_readiness.py` `decide()` severity branch: `elif l3=="FAIL": cal = "invalid" if "refut"
  else "medium"` and `elif ic in (dos,griefing,precision,bounded_local,auth_only): cal="medium"`. SOPH-03 hit the
  FAIL→medium path (its FAIL meant "no theft", conflating no-theft with not-High).
- Fix lives in a **NEW research helper** that imports `decide()` read-only for `old_label`, then layers the carve-out
  for `repaired_label`. `decide()` / `validate_p208` stays byte-identical (no production edit; not wired).
- The carve-out reads a NEW evidence block (10 booleans/enums) independent of the old theft-centric `l3_status`.

## Carve-out rule (write BEFORE testing; general, not sophon-specific)
`repaired_label = "high"` iff ALL ten hold; else fall through to `old_label` (and never upgrade a source-refuted/
invalid case):
1. `deterministic_l3_proof` — executed harness shows deterministic revert / permanent blockage / unavoidable failure;
2. `core_path` — entry/exit/redeem/claim/deposit/withdraw/conversion/liquidation/settlement;
3. `supported_asset` — path/asset explicitly supported by the protocol;
4. `not_optional_griefing` — not user-griefs-user via an optional action;
5. `source_valid_token_behavior` — realistic token/protocol behavior;
6. `attacker_model ∈ {permissionless, unavoidable, normal_user_behavior}`;
7. `no_workaround` — no practical workaround for the supported path;
8. `affects_class_or_protocol` — class of users / protocol-wide, not a self-inflicted edge;
9. `control_case_present` — harness control shows the path succeeds absent the bug;
10. `no_admin_prereq`.
Ordinary DoS / optional griefing / bounded-local → Medium (or Low); needs-harness when scope/workaround unclear;
**no broad "DoS == High".** Missing any criterion → Medium / Needs-Harness / invalid, not High.

## Execution (deliverables under `documentation/research/assisted_mode/p213_l3_dos_carveout/`)
1. **INTEGRITY_PRECHECK.md** — START hashes: `deep_trace ef93a6c2`, `min_confirm_gate 41dd3c96`, `confirm_gate
   4fadfc5f`, `submission_readiness_review 7c4b563d`, `dashboard dbed5174`, `validate_p208_l3_readiness 7e148e18`,
   ledger `fc446040`, P208 schema `91c0590f`; confirm api_free=true, no live route, research-only/un-wired.
2. **P212_UNDERRATING_ANALYSIS.md** — official 003-H=High vs system Medium; harness = deterministic DoS; WHY old
   mapping demoted (FAIL→medium + dos→medium conflates no-theft with not-High); why venue treats it High (deposit DoS,
   Lido precedent, escalation accepted); what separates SOPH-03 from ordinary griefing (the 10 criteria).
3. **L3_DOS_CARVEOUT_RULE.md** — the rule above, with the severity ladder (ordinary DoS/griefing/bounded → Medium/Low;
   deterministic core-path DoS → possible High; permanent fund-lock/protocol-wide entry-exit failure → High if
   L3-proven; needs-harness when unclear).
4. **REGRESSION_SET.md + regression_cases.json** — fixtures carrying old P208 fields + the 10 carve-out fields:
   - **positive:** SOPH-03 (all 10 true; expected repaired = High).
   - **negative controls (must stay < High):** decent M-03 (auth-bypass, not core-path DoS), decent-06 (false High,
     no drain), decent-12 (NEEDS_HARNESS), vultisig M-03 (cap-bypass, not DoS), **munchables DoS/griefing Highs
     (permissionless DoS but NO executed deterministic L3 proof → criterion 1 fails → stays Medium/Needs-Harness)**,
     generic static-High-no-PoC (blocked), generic DoS-no-core-path (Medium), precision-no-magnitude (Medium/Needs-
     Harness), source-refuted (invalid).
5. **`validate_p213.py`** (un-wired research helper, under the p213 dir): reads fixtures only; imports `decide()`
   read-only for `old_label`; computes `repaired_label` + per-criterion satisfaction + missing list; never mutates
   artifacts, never imported by production. Emits scorecard + metrics; labels each case `old_l3_label` /
   `repaired_l3_label` / `expected`.
6. **REPAIRED_MAPPING_SCORECARD.md** — per case: id · old · repaired · expected · criteria-satisfied · missing ·
   reason · pass/fail.
7. **HISTORICAL_CONTROL_RESULTS.md** — assert: SOPH-03 medium→High; decent M-03 / vultisig M-03 NOT →High; static-High-
   no-PoC blocked; SOPH-01/02 remain invalid (refuted); Medium path unchanged unless all 10 hold; munchables DoS NOT
   auto-High.
8. **metrics.json** — cases, SOPH-03 fixed (bool), old-false-demotions-fixed, **new-false-Highs (must be 0)**,
   regression failures, High precision/recall before/after, DoS upgraded vs retained-Medium counts, needs-review count.
9. **FAILURE_CASES.md + P213_RECOMMENDATION.md** + integrity re-check + copy plan → P213_PLAN.md + memory.

## Decision space
`DOS_CARVEOUT_VALIDATED_RESEARCH_ONLY` (SOPH-03 → High; 0 new false-Highs; all negative controls stay < High; rule
narrow + written-first) · `DOS_CARVEOUT_PARTIAL` · `DOS_CARVEOUT_FAILED_FALSE_HIGHS` ·
`DOS_CARVEOUT_FAILED_TO_FIX_SOPH03` · `INVALID_RUN`. **Expected:** `VALIDATED_RESEARCH_ONLY` → recommend P214 =
implement behind the existing `AUDITWATCH_L3_READINESS` flag (or one more rehearsal), per regression results.

## Acceptance criteria
Research-only/un-wired; rule written before testing; SOPH-03 explicitly tested → High; decent & vultisig negative
controls stay < High; static-High-no-PoC blocked; **no broad DoS==High**; the 10 criteria explicit + narrow; munchables
DoS does not auto-High (no executed L3 proof); production hashes byte-identical START==END; JSON valid; `validate_p213.py`
not imported by production.

## Verification
`python documentation/research/assisted_mode/p213_l3_dos_carveout/validate_p213.py` → SOPH-03 `repaired=high`
(old=medium), all negative controls `repaired < high` (0 new false-Highs), source-refuted=invalid, static-no-PoC
blocked; `metrics.json`/`regression_cases.json` valid JSON; production hashes unchanged at END; `grep -rl validate_p213
scripts/ run_pipeline.sh config/` returns nothing (un-wired).

## Follow-on (NOT this phase)
P214: wire the carve-out into the L3 mapping behind the flag (after re-validation) + the P212 conversion-family
sibling-parity lens (002-M near-miss) + recall sweep. Do not wire here.
