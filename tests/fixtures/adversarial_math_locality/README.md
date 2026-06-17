# Synthetic fixtures — adversarial math proofs + dependency locality

Minimal vulnerable/safe Solidity examples illustrating the failure classes the adversarial-math-proof
and dependency-locality rules target (Swan/Dria M-08 getFee + H-02 round-validation). Each fixture is a
reference for the scenario; the deterministic tests in
`tests/coverage/test_adversarial_math_proof.py` and `test_dependency_locality.py` exercise the rules over
manifest/disposition fixtures (the validators operate on dispositions + call graph, not raw source).

| Fixture | Class | What a CONFIRMATORY proof / non-dominant clear misses | Expected pipeline outcome |
|---|---|---|---|
| `getfee_bitshift.sol` | math: shift-scaling | `2 << difficulty` is exponential; intended is linear. A proof that restates `2 << difficulty` as intended never checks the economic direction vs difficulty. | `confirmatory_proof` → `math_estimator_review` |
| `fee_monotonicity.sol` | math: wrong economic direction | fee should rise with risk; code makes it fall. Caught by `monotonicity_and_economic_direction`. | divergence in harness (monotonicity inversion) |
| `precision_loss.sol` | math: rounding | `(a / b) * c` truncates before scaling vs intended `(a * c) / b`. | precision-loss in harness; proof needs rounding analysis |
| `guard_in_caller_missing_in_callee.sol` | locality: missing local check | `vault` is public and callable directly; the round check lives only in `Router.run`. | call-graph disproves dominance → `guard_not_path_dominant` |
| `cross_contract_guard.sol` | locality: cross-contract dominance | sink `_apply` is internal and reachable ONLY through the guard. | dominance holds → `dependency_valid` |
| `proxy_router_bypass.sol` | locality: alternative path | a router reaches the sink on a guard-free path. | call-graph disproves dominance → `guard_not_path_dominant` |
| `missing_round_validation.sol` | locality: Swan/Dria H-02 | `purchase` (public) has no local round check; the phase guard sits in another contract. | call-graph disproves dominance → `guard_not_path_dominant` |

`safe_*` variants show the fixed form that a valid clear/proof would describe.
