# Audit-Watch — Research Detector Registry

All detectors below are **research-only and un-wired**: `is_gate:false`, `research_only:true`,
`routes_in_production:false`, `routed_manifest_ids:[]`. None feeds production routing/gates. Status terms follow
the lifecycle in `research_methodology.md`.

---

## `multicall_invariant_v1`
| Field | Value |
|---|---|
| **Classification** | Batch/multicall cross-call accounting-invariant lens |
| **Status** | **RESEARCH-STABLE** · **NARROW SCOPE CONFIRMED** |
| **Scope** | Manifest-visible `bytes[]` `address(this).delegatecall` multicall executors (OZ/UniV3 `Multicall` shape + direct forks); + the Size M-01 balanceOf-vs-totalSupply before/after invariant on such an executor |
| **Supported architectures** | in-scope `bytes[]` self-delegatecall multicall (Solidity-level). Via the **B1 sidecar**, inherited OZ/UniV3 multicall can be surfaced for the deriving contract |
| **Known blind spots** | inherited-library multicall (visibility — partly addressed by the B1 sidecar) · typed-struct dispatch · internal-call batch (e.g. Ethos `batchLiquidateTroves`) · diamond/`farm` batch · permit/msg.value/ERC2771 mechanisms · **assembly** multicalls (solady `Multicallable`) |
| **Evaluation size** | 20-target overnight campaign: **3 HIT / 2 PARTIAL / 2 ADJACENT / 2 MISS / 2 FP / 9 TRUE-NEG**; all true positives were the one `bytes[]` self-delegatecall shape; 0 high-confidence noise |
| **Validation outcome** | NARROW SCOPE CONFIRMED — detects one architecture precisely; does not generalize to the broader multicall *class* |
| **B1 sidecar** | `build_inherited_multicall_sidecar.py` (research-only): inherited-multicall visibility; experiment verdict **B1 PARTIALLY VISIBILITY ISSUE** (Revert/Panoptic convert; Maia/solady assembly does not). 0 new FP; "volume not noise" cost |
| **Integrity** | detector + patterns 0-drift across all eval phases; un-wired |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/research/multicall_detector_evolution.md`, `documentation/evals/multicall_invariant_final_evaluation_report.md` + integrity review; B1: `documentation/research/b1_*` |

## `permit_asset_binding`
| Field | Value |
|---|---|
| **Classification** | Permit/Permit2 asset-binding lens (Shape A only) |
| **Status** | **RESEARCH-STABLE** · **HIGH PRECISION PROTOTYPE VALIDATED** (validation campaign complete) |
| **Scope** | A permit/Permit2 transfer consumed into a protocol with a **single expected asset**, with **no** `permitted.token == asset` binding (asset/token mismatch). Anchor: Revert Lend H-01 / #368 |
| **Supported architectures** | single-asset vaults / lending consuming `permitTransferFrom` / `permitWitnessTransferFrom` / ERC-2612 `.permit()` |
| **Known blind spots (accepted FNs, by design)** | permit *validation-bypass* (Aave #138) · recipient axis (Permit2 #250) · per-market/computed-asset protocols · routers/aggregators (intentionally suppressed) · assembly permit |
| **Evaluation size** | 7-target prototype (anchor 3× high, 6 negatives quiet, 0 FP) **+ 20-target validation: 1 HIT / 19 TRUE-NEG / 0 FALSE POSITIVE** (0 high-confidence FP; total volume 3, all on the anchor) |
| **Validation outcome** | RESEARCH-STABLE DETECTOR — precision held across diverse permit-heavy/router/ERC4626 stressors |
| **Integrity** | detector + patterns 0-drift across prototype + validation; un-wired |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/research/permit_asset_validation_lens.md`, `documentation/research/permit_asset_binding_prototype.md`, `documentation/evals/permit_asset_binding_validation.md` (+ scorecard / per-target notes) |

## `safe_management_coverage`
| Field | Value |
|---|---|
| **Classification** | Gnosis-Safe self-management selector-coverage + calldata-decode lens (guard-completeness family) |
| **Status** | **PROMISING-BUT-NEEDS-REFINEMENT** · NARROW SCOPE CONFIRMED (single-anchor validated, 0 FP) |
| **Scope** | A guard/policy that filters Safe transactions by selector but (A) decodes a multi-arg Safe self-management selector at the wrong calldata offset (`decode_offset_mismatch`), or (B) covers ≥1 Safe self-management selector yet misses high-impact ones (`incomplete_selector_coverage`: setFallbackHandler/setGuard/enable-disableModule/module-exec/multiSend/owner-mgmt/permit). Anchors: reNFT 2024-01 H-04 (disableModule offset 0x24 reads prevModule not module @0x44), H-02 (setFallbackHandler uncovered), H-05 (fallback/permit basis) |
| **Supported architectures** | Gnosis-Safe guard/`checkTransaction`/`BaseGuard` selector-dispatch integrations (rental, NFT custody, account-abstraction, module-guarded Safes) |
| **Known blind spots (accepted, by design)** | hostile-token / create-time reentrancy / Seaport / economic families (out of scope); guards filtering via non-selector logic; assembly-only decoders without a resolvable offset constant/literal |
| **Evaluation size** | reNFT full-workspace replay (22,345 manifest items, 160 in-scope): **4 candidates, all on the real `Guard`, 0 FP** (Stop/Factory callers + test guards suppressed); recovers H-04 + H-02 directly, H-05 partial. 8 synthetic guard cases + replay test (10 tests). **Single anchor — needs a 15–20 target campaign before RESEARCH-STABLE.** |
| **Validation outcome** | NARROW SCOPE CONFIRMED on the anchor; mechanism-based recovery (offset value, selector-set difference), not answer-key matching |
| **Integrity** | un-wired; 4 research flags on output; recovery deterministic |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/research/safe_management_coverage_research.md`, `documentation/research/assisted_mode/p237_safe_management_lens/REPLAY_REPORT.md` |

## `hostile_token_settlement`
| Field | Value |
|---|---|
| **Classification** | Hostile-token settlement/cleanup DoS lens (must-succeed-transfer family) |
| **Status** | **PROMISING-BUT-NEEDS-REFINEMENT** · NARROW SCOPE CONFIRMED (single-anchor validated, 0 FP) |
| **Scope** | A must-succeed cleanup flow (stop/reclaim/close/settle/liquidate/withdraw/refund/finalize/claim/...) that pushes an attacker-/order-selected token via a revert-on-failure transfer with NO containment (try-catch / pull-payment / allowlist), so a hostile token (revert/blacklist/false-return/reentrancy) blocks cleanup → permanent lock / DoS of another user (`hostile_token_settlement_dos`). Anchors: reNFT 2024-01 H-01 (Stop→PaymentEscrow `_settlePayment` `_safeTransfer` of attacker-tipped consideration token), #64/#605 (blacklisting payment ERC20 / blacklisted lender freeze) |
| **Supported architectures** | order/market/rental settlement + escrow + reclaim flows that transfer user-selected tokens to counterparties (rental, NFT marketplaces, lending liquidation/closeout, escrow) |
| **Known blind spots (accepted, by design)** | Safe-management / create-time reentrancy / Seaport-invariant families (out of scope); cross-contract settle where the transfer is >1 helper hop from the cleanup entrypoint (fires on the contract that holds the transfer, e.g. PaymentEscrow, not the orchestrator Stop); tokens behind an allowlist |
| **Evaluation size** | reNFT full-workspace replay (22,345 manifest items, 160 in-scope): **2 candidates, both HIGH, 0 FP** — `PaymentEscrow._settlePayment` (H-01/#64/#605) + `Reclaimer.reclaimRentalOrder` (reclaim DoS). 8 synthetic fixtures + admin-downgrade + replay test (10 tests). **Single anchor — needs a 15–20 target campaign before RESEARCH-STABLE.** |
| **Validation outcome** | NARROW SCOPE CONFIRMED on the anchor; 5-signal gate (cleanup-verb + must-succeed push + attacker-sourced token + missing containment + counterparty) keeps it off ordinary transfers; mechanism-based, not answer-key matching |
| **Integrity** | un-wired; 4 research flags on output; recovery deterministic |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/research/hostile_token_settlement_research.md`, `documentation/research/assisted_mode/p238_hostile_token_lens/REPLAY_REPORT.md` + `COMBINED_RECALL_LIFT.md` |

## `create_time_reentrancy`
| Field | Value |
|---|---|
| **Classification** | Create/registration-time reentrancy lens (callback-before-commit family) |
| **Status** | **PROMISING / READY-FOR-ADVISORY** · single-anchor, 0 FP |
| **Scope** | A create/mint/register/deposit/stake fn performs a receiver/arbitrary callback (`_safeMint`/`safeBatchTransferFrom`/`onERCxReceived`/`.call{`) BEFORE committing the registration/limit state, no nonReentrant → reentrancy bypasses the invariant. Anchor: nextgen H-01 (`NextGenCore.mint`→`_mintProcessing`→`_safeMint` before `tokensMintedPerAddress += 1`) |
| **Supported architectures** | single-contract callback-before-commit in NFT mint / create flows |
| **Known blind spots** | cross-CONTRACT stale-check + Seaport/conduit-mediated callbacks (reNFT H-03); read-only reentrancy |
| **Evaluation size** | 16-target P242 campaign: **3 candidates (all nextgen, H-01 family), 0 FP, 0 noise** (after dropping ambiguous ERC20 safeTransferFrom that caused deposit FPs); 7 tests incl. NextGenCore.mint replay |
| **Validation outcome** | precision validated (0 high-conf FP across 16 diverse targets); single in-repo anchor, no independent non-anchor TP in corpus |
| **Integrity** | un-wired; 4 research flags on output |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/research/assisted_mode/p242_recall_sprint/FAMILY_A_create_time_reentrancy.md`, `VALIDATION_REPORT.md` |

## `erc4626_share_accounting`
| Field | Value |
|---|---|
| **Classification** | EIP-4626 share-accounting lens (convert-in-max external-wrapper sub-shape; NARROW) |
| **Status** | **PROMISING-BUT-NEEDS-REFINEMENT** · research-only |
| **Scope** | In a 4626 vault, a max/limit/preview fn using the external-max WRAPPER `externalVault.convertToAssets(externalVault.maxRedeem())` where EIP-4626 mandates exact `preview*`. Anchor: PoolTogether M-02 (`PrizeVault._maxYieldVaultWithdraw`) |
| **Supported architectures** | vault-of-vault / wrapper ERC-4626 (PrizeVault, SuperPool) |
| **Known blind spots** | non-wrapper preview/action rounding divergence (M-03/M-06); non-4626; nuanced convertTo-in-max that is actually compliant |
| **Evaluation size** | 16-target P242 campaign: M-02 anchor recovered; 0 high-conf FP after requiring the external-max wrapper (dropped preview-only shape that was broad noise — sentiment 8/concrete 5); residual same-root volume + unverified breadth (sentiment/concrete); 8 tests incl. PrizeVault replay |
| **Validation outcome** | recovers anchor with 0 high-conf FP, but same-root volume + unverified breadth + inherent nuance → KEEP RESEARCH-ONLY |
| **Integrity** | un-wired; 4 research flags |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/research/assisted_mode/p242_recall_sprint/FAMILY_B_erc4626_share_accounting.md`, `VALIDATION_REPORT.md` |

## `sibling_function_parity`
| Field | Value |
|---|---|
| **Classification** | Intra-contract sibling missing-component lens (structural-comparison family) |
| **Status** | **RESEARCH-STABLE** · architecture-narrow |
| **Scope** | Two sibling functions in a contract reach the same state transition but one omits a security-relevant component (validation/recipient/cap/access/registry/pause). Anchor: Blackhole M-04 (`RewardsDistributor.claim_many` omits `avm.getOriginalOwner` that `claim` performs) |
| **Supported architectures** | name-stem / behavioral-kin siblings (Solidity); validated on ve(3,3) (Blackhole) |
| **Evaluation size** | 20-subject baseline: **1 HIT (high)**, 0 corpus high/medium FP across 16 swept subjects (incl. 1,332-item Beanstalk); route-rate ~0 |
| **Validation outcome** | precision validated; recall architecture-narrow (the "validation parity" cluster is heterogeneous — only the missing-component intra-contract sub-shape is here) |
| **Integrity** | un-wired; 0 production wiring |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/evals/sibling_function_parity_eval/`, `documentation/research/sibling_function_parity_promotion_review.md` |

## `cross_contract_sibling_parity`
| Field | Value |
|---|---|
| **Classification** | Cross-contract sibling missing-component lens (structural-comparison family) |
| **Status** | **RESEARCH-STABLE** · architecture-narrow |
| **Scope** | Sibling functions in DIFFERENT contracts of a per-action-library module; one guards an eligibility flag a sibling action omits. Anchor: Size M-06 (`validateBuyCreditMarket` guards `forSale`; `validateSellCreditMarket` omits it) |
| **Supported architectures** | per-action-library protocols (shared state-struct + module dir + object-suffix); validated on Size (lending) |
| **Evaluation size** | 16-subject sweep: **1 HIT (high)** (only Size fires — the architecture is Size-specific), 0 FP on the 15 non-Size subjects; route-rate 0.0003 |
| **Validation outcome** | NARROW SCOPE CONFIRMED — recovers the cross-contract sub-shape the intra-contract lens cannot reach; multi-gate (verb + state-struct + module + object-suffix) controls FP |
| **Integrity** | un-wired; reuses `sibling_function_parity` primitives read-only |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/evals/cross_contract_sibling_parity_eval/` |

## `value_flow_parity`
| Field | Value |
|---|---|
| **Classification** | Wrong-value parity lens (structural-comparison family) · **v2** (Phase-13 generalized) |
| **Status** | **RESEARCH-PROTOTYPE** · architecture-narrow (v2 adds 3 transferable sub-shapes; Holdout Recall 0%) |
| **Scope** | A check/accounting component is present but fed the wrong semantic value (curated identifier alias-pairs / threshold-name mismatch). Anchor: Size M-02 (`validateSellCreditMarket` checks raw `amount` against a credit-named bound) |
| **Supported architectures** | validator-argument mismatch (validate/execute); validated on Size (lending) |
| **Evaluation size** | 16-subject sweep: **1 HIT (medium)**, 0 high/medium FP across 16 subjects; route-rate 0.0002 |
| **Known blind spots (accepted FNs)** | identity check-vs-use (sender/recipient) demoted to LOW (normal ERC20/4626 pattern); net/gross cross-function (Size M-12) out of single-function reach |
| **Validation outcome** | precision validated on the threshold-value-mismatch sub-shape; wrong-value is FP-prone, so deliberately narrow |
| **Integrity** | un-wired; distinct from `asset_source_consistency` (asset-source-family mismatch) — scope test enforces |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/evals/value_flow_parity_eval/` |

## `registry_position_lifecycle`
| Field | Value |
|---|---|
| **Classification** | Lifecycle/registry invariant-omission lens (**distinct family — NOT parity**) |
| **Status** | **RESEARCH-STABLE** · architecture-narrow |
| **Scope** | A positions registry desyncs: a position-mutating function omits the registry update its siblings perform (`missing_registry_update`), or removes an entry without the emptiness guard a sibling remove has (`unguarded_registry_remove`). Anchors: NOYA H-23 (`transferBetweenAccounts` omits `registry.updateHoldingPosition`) + H-18 (`closeBorrowPosition` removes unguarded) |
| **Supported architectures** | position-registry connectors (registry-mutation vocab + subject-proxy); shape present in 11/16 corpus subjects; validated on NOYA (connector-yield) |
| **Evaluation size** | 16-subject sweep: **2 HIT (high + medium)** + 1 same-shape candidate (SNXV3 createAccount), 0 FP on the 15 non-NOYA subjects; route-rate 0.0003 |
| **Known blind spots (accepted FNs)** | H-12 key-mismatch (owned by `connector_position_accounting` Shape C — not duplicated); H-21 incomplete-emptiness predicate (semantic — deferred) |
| **Validation outcome** | precision validated; recovers two structurally-reachable lifecycle bugs generic parity could not pair (cores differ, jaccard < 0.3) |
| **Integrity** | un-wired; reuses `sibling_function_parity` body extractor read-only; generic-collection-method exclude controls the EnumerableSet FP |
| **Routing status** | **NOT ROUTED** (research-only) |
| **Reports** | `documentation/evals/registry_position_lifecycle_eval/`, `documentation/evals/phase11_registry_lifecycle/` |

Family-level promotion status for all of the above: `research_family_promotion_status.md`.

---

## Adding a detector
A new detector enters this registry only after completing the lifecycle in `research_methodology.md` and reaching a
**stability classification**. It must ship research-only/un-wired with the four flags, a registry entry in
`config/research_finding_normalization.json` (so it composes into the normalization layer), and an integrity check
showing 0-drift on the frozen platform. Candidate next families are in `roadmap.md`.


## P311 — Advisory-only promotion (human-gated, 2026-06-10)
The 8 P303/P305/P307 lenses (nonstandard_permit, erc4626_limit_fidelity, eip712_domain_separator_staleness,
beneficiary_guard_parity, admin_capability_parity, crosschain_min_gas_unchecked, crosschain_refund_recipient,
fee_wrapper_bypass) were PROMOTED **advisory-only** by human decision: wired to RUN in run_pipeline.sh
(coverage_review_gate + coverage-gate) and SURFACED in advisory_escalation_gate.json under
`promoted_advisory_lens_hits` (routed_to:advisory_only). They are FP-safe (0 candidates on every unrelated codebase)
but KNOWINGLY OVERRIDE criteria 1/2/5/6 of the promotion bar above (0 proven non-anchor recoveries). Mitigation:
advisory-only — they NEVER apply_update / route / gate / set severity (`promoted_advisory_routed` is always 0). The
strict-escalation upgrade (route → needs_deep_pass) is DEFERRED until each earns >=2 non-anchor recoveries. Reversible:
remove the run_pipeline invocations + the advisory_escalation_gate PROMOTED_ADVISORY_LENSES block + restore the flags.
