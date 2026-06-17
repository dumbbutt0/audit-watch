# Panoptic miss-class fixtures (reconstructed)

Minimal reconstructed Solidity for the Panoptic miss classes the conversion-engine upgrade targets, plus
safe equivalents for FP control. Shapes are derived from the eval `failure_analysis.md` (no answer-key
text copied). These are illustrative shapes for future detector work and documentation; the enforced
regression for this upgrade is the disposition-level routing/ledger/specialist/gate-vs-DoS tests under
`tests/coverage/` and `tests/deep_solidity/`.

| Miss | File | Shape | Specialist that should catch it | Safe equivalent |
|---|---|---|---|---|
| H-01 | `h01_builderwallet_init_reinit.sol` | unguarded `init()` re-initialization → admin overwrite + drain | access_control / initialization | `*_safe.sol`: init-once guard + onlyOwner |
| H-02 | `h02_liquidation_cross_contract_reentrancy.sol` | ETH refund before settlement completes → cross-contract reentrancy | reentrancy | `*_safe.sol`: effects-before-interaction + nonReentrant |
| M-01 | `m01_intended_gate_vs_liquidation_dos.sol` | `threshold - balance` underflow framed as a "gate" but blocks legitimate liquidation | gate-vs-DoS (liveness disproof) | `*_safe.sol`: signed/clamped check, no liveness block |

The H-01/H-02 shapes are why the **mandatory specialist coverage gate** exists (both Highs were the
reentrancy + access-control specialists' targets and those specialists were skipped). The M-01 shape is
why the **gate-vs-DoS validator** exists (the underflow was cleared as an "intended gate" without testing
whether it blocks a legitimate insolvent account's liquidation).
