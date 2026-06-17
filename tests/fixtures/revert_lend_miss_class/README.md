# Revert Lend miss-class fixtures (reconstructed)

Minimal reconstructed Solidity for the Revert Lend misses the adversarial-review-quality upgrade targets,
plus safe equivalents for FP control. Shapes are derived from the eval `failure_analysis.md` (no answer-key
text copied). Illustrative; the enforced regression is the disposition-level routing tests
(`tests/coverage/test_waiver_discipline.py`, `tests/deep_solidity/test_spec_checklists.py`,
`tests/coverage/test_specialist_density.py`) + the read-only replay.

| Miss | File | Shape | New control that catches it |
|---|---|---|---|
| H-01 | `h01_permit_token_substitution.sol` | permit accepts a substituted received token | **permit spec checklist** (`received_vs_paid_token`, `no_unintended_asset_movement`) |
| H-02 | `h02_onreceived_collateral_reentrancy.sol` | NFT sent before collateral-config finalized | **callback checklist** + reentrancy-trace prompt (`state_before_during_after`, `collateral_config_mutation`) |
| H-04 | `h04_transformer_caller_validation.sol` | `V3Utils.execute` no caller validation | **waiver discipline** (this external-call entrypoint cannot be cluster-waived) + transformer_external_call specialist |
| H-05 | `h05_negative_tick_rounding.sol` | negative-tick rounding inflates price | **oracle/liquidation checklist** (`negative_tick_rounding`, `reference_pool_rounding`) |
| H-06 | `h06_callback_liquidation_prevention.sol` | owner callback reverts liquidation | **callback checklist** (`liquidation_prevention`, `debt_collateral_share_liquidation_impact`) |
| M-04 | `m04_once_per_block_interest.sol` | once-per-block interest → interest-free loan | **oracle/liquidation + erc4626 review depth** (flagged via density swarm) |
| M-14 | `m14_erc4626_false_compliance.sol` | false ERC4626 "compliant" clear | **erc4626 spec checklist** (`max_funcs_respected`, `preview_consistency`, `rounding_direction`) |

Plus the **waiver-cluster-hiding-external-call** scenario (a cluster waiver covering `V3Utils.execute`) is
proven blocked in `test_waiver_discipline.py::test_cluster_waiver_of_high_risk_blocks`.
