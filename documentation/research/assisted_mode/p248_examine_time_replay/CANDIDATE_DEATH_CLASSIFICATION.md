# P248 — Phase B: Candidate Death Classification

One proximate death class per miss (the stage/operation where the candidate disappeared). A second column
gives the **operation cluster** (the reasoning operation that would have birthed *and* completed it) so Phase
D can map deaths → checkpoints. Weights H=3/M=1.

| Finding | Sev | Proximate death class | Operation cluster (→ checkpoint) |
|---|---|---|---|
| decent H-02 | H | NO_CROSS_CONTRACT_TRACE | cross-contract |
| decent H-03 | H | NO_EXPLOIT_CHAIN_CONSTRUCTION | cross-contract |
| decent H-04 | H | NO_EXPLOIT_CHAIN_CONSTRUCTION | state-transition |
| decent M-01 | M | NO_CROSS_CONTRACT_TRACE | cross-contract |
| decent M-02 | M | NO_PERMISSION_CHECK | permission |
| decent M-04 | M | NO_ACTOR_MODEL | economic |
| decent M-05 | M | NO_CROSS_CONTRACT_TRACE | cross-contract |
| vultisig H-02 | H | NO_EXPLOIT_CHAIN_CONSTRUCTION | permission |
| vultisig M-02 | M | LOCAL_REASONING_STOP | economic |
| vultisig M-03 | M | NO_EXPLOIT_CHAIN_CONSTRUCTION | state-transition |
| kleidi M-01 | M | NO_STATE_TRANSITION_TRACE | state-transition |
| kleidi M-02 | M | NO_EXPLOIT_CHAIN_CONSTRUCTION | accounting |
| kleidi M-03 | M | NO_STATE_TRANSITION_TRACE | state-transition |
| centrifuge M-02 | M | NO_CROSS_CONTRACT_TRACE | cross-contract |
| centrifuge M-04 | M | NO_EXPLOIT_CHAIN_CONSTRUCTION | permission |
| centrifuge M-05 | M | NO_EXPLOIT_CHAIN_CONSTRUCTION | accounting |
| centrifuge M-07 | M | NO_EXPLOIT_CHAIN_CONSTRUCTION | accounting |
| munchables H-01 | H | NO_EXPLOIT_CHAIN_CONSTRUCTION | state-transition |
| munchables M-01 | M | NO_STATE_TRANSITION_TRACE | state-transition |
| munchables M-03 | M | NO_EXPLOIT_CHAIN_CONSTRUCTION | accounting |
| munchables M-04 | M | NO_ACCOUNTING_CHECK | accounting |

## Proximate death-class tally (where candidates disappear)
| Death class | count | weighted |
|---|---|---|
| **NO_EXPLOIT_CHAIN_CONSTRUCTION** | **10** | **19** |
| NO_CROSS_CONTRACT_TRACE | 4 | 6 |
| NO_STATE_TRANSITION_TRACE | 3 | 3 |
| NO_PERMISSION_CHECK | 1 | 1 |
| NO_ACTOR_MODEL | 1 | 1 |
| NO_ACCOUNTING_CHECK | 1 | 1 |
| LOCAL_REASONING_STOP | 1 | 1 |
| NO_ACTOR_MODEL/OTHER | 0 | 0 |
| **Total** | **21** | **31** |

## Operation-cluster tally (for checkpoint mapping)
| Operation cluster | count | weighted |
|---|---|---|
| cross-contract | 5 | 9 |
| state-transition (incl 1 lifecycle) | 6 | 10 |
| accounting | 5 | 5 |
| permission | 3 | 5 |
| economic | 2 | 2 |
| **Total** | **21** | **31** |

## Reading
- **The single largest proximate death class is NO_EXPLOIT_CHAIN_CONSTRUCTION (10 findings, 19 weighted,
  incl. 4 of the 5 Highs).** Refining P247: it is not simply that candidates are never born — in *half* the
  cases (and most of the High weight) the system DID birth a related/partial candidate but **failed to
  construct the exploit chain to the awarded impact**. The other half (10 findings, 12 weighted) failed
  earlier, at candidate birth, split across the specific missing traces.
- The **High severity lives at the Exploit-Chain death stage** (decent H-03/H-04, vultisig H-02, munchables
  H-01) — i.e., among candidates that *were* born. Decent H-02 is the only High lost at birth.
- Operation-cluster view (which Phase D uses): state-transition (10wt) and cross-contract (9wt) carry the
  most weight; accounting (5wt) and permission (5wt) are the cheapest/FP-tightest operations.
