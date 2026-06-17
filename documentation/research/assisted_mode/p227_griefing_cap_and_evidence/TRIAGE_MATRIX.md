# P227 — Part B triage matrix (11 WARNING_LOW_EVIDENCE_DEPTH cards)

Pre-harness triage of every candidate. "Disposition" = what was done this phase. All records:
`output_research/l3_readiness/<ID>.json`. Severity is `decide()`'s calibrated value (0 false-Highs).

| ID | mechanism | impact_class | bounded | disposition (this phase) | l3_status | decide |
|----|-----------|--------------|---------|--------------------------|-----------|--------|
| SC-05 | scaled-token double-mulDivDown rounding under-credit | precision | yes | **HARNESSED → executed L3 PASS** (`SC05_scaled_dust.t.sol`, 2/2) | PASS | medium |
| SC-08 | borrowATokenCap bypassed in multicall boundary | dos | yes | **HARNESSED → executed L3 PASS** (`SC08_cap_bypass.t.sol`, 2/2; validates the P227 cap) | PASS | medium |
| SC-06 | getCreditAmountIn no-trade gap band | dos | yes | L1 source-backed record (design boundary; trivial workaround) | NEEDS_HARNESS (L1) | needs_harness_for_severity |
| SC-07 | selfLiquidate CR-band optionality gap | other | no | L1 source-backed record (position still liquidatable elsewhere) | NEEDS_HARNESS (L1) | needs_harness_for_severity |
| SC-09 | withdraw silent Math.min clamp | other | no | L1 source-backed record (integrator footgun, Low) | NEEDS_HARNESS (L1) | needs_harness_for_severity |
| SC-10 | SellCreditMarket cash-vs-credit dead guard | other | no | **DEFER/QA** (no exploit; route to human review) | NOT_ATTEMPTED | medium |
| SC-11 | LiquidateWithReplacement transient REPAID event | other | yes | NEEDS_HARNESS + plan (integration + event-ordering DEFERRED) | NEEDS_HARNESS | needs_harness_for_severity |
| SC-12 | Claim sequential-index rounding (SC-05 family) | precision | yes | NEEDS_HARNESS + plan (integration DEFERRED) | NEEDS_HARNESS | needs_harness_for_severity |
| ZETA-02 | ERC20Custody FoT fee-accounting drift | other | yes | NEEDS_HARNESS + plan (light; pocs/p220 + FoT mock DEFERRED) | NEEDS_HARNESS | needs_harness_for_severity |
| ZETA-09 | connector ctor no FUNGIBLE_MODULE guard | auth_only | no | L1 source-backed record (event-spoofing surface, Low/Info) | NEEDS_HARNESS (L1) | needs_harness_for_severity |
| ZETA-12 | timestamp-deadline weak MEV | griefing | yes | **REFUTE/DEFER** (runtime/mempool property; not on-chain harnessable) | NOT_ATTEMPTED | invalid |

## This phase
- **Harnessed → executed L3 PASS (2):** SC-05, SC-08 (real source; external-only mocks; actual+control+command+output).
- **L1 source-backed records (4):** SC-06, SC-07, SC-09, ZETA-09 (source-confirmed; not executed).
- **Defer / refute (2):** SC-10 (QA, no exploit), ZETA-12 (MEV runtime property).
- **NEEDS_HARNESS + precise plan (3, deferred for integration cost):** SC-11, SC-12, ZETA-02.
- **0 false-Highs:** every candidate decides Medium / needs_harness / invalid (never High).

## Notes / known limitations
- ZETA-02/09/12 L3 records improve `decide()` + disposition, but surfacing them on the dashboard cards needs a
  **zeta-adapter re-sync** (deferred — avoids mutating the frozen P215/P220 ZETA mirror records this phase).
- Six pre-existing ZETA-01/03/05/06/07/08 + SOPH-05 records use non-enum `poc_tier=STATIC_ONLY` /
  `impact_class=accounting` / `attacker_model=privileged` (authored pre-P227; not introduced or modified here).
- SC-11/SC-12/ZETA-02 are the recommended next harnesses (queued with plans in their L3 records).
