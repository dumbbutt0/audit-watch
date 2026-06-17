# P220 — Harness feasibility matrix

Common toolchain: `forge 1.5.1`, `solc 0.8.7`. Project `pocs/p220/` (src=realsrc, vendor via remappings, mocks/).
Vendored authentic deps: OpenZeppelin 4.8.1 subset (`security/Pausable`, `token/ERC20/*`, `utils/*`,
`interfaces/IERC20`), Uniswap v3-core + v3-periphery interface trees. All target contracts compiled UNMODIFIED.

| Axis | ZETA-04 | ZETA-10 | ZETA-11 |
|------|---------|---------|---------|
| Real contract | ZetaConnectorNonEth (+base) | ZetaTokenConsumerUniV3 | ZetaTokenConsumerTrident |
| Mocks needed | MintableZetaToken | MockWETH9 + MockUniV3Router (1:1) + AttackerReentrant | MockTridentFactory + MockTridentRouter |
| Mocks create vuln? | No (standard mint/burn ERC20) | No (faithful 1:1 AMM, pays from own reserves) | No (empty/non-empty list is a real factory state) |
| Setup complexity | Low | High (V3 interface surface + reentrancy plumbing) | Low |
| Source-valid assumptions | TSS = caller; pauser pauses | router/WETH external; consumer real | factory external; getPools returns list |
| Dependency risk | none | router-mock fidelity (kept minimal, 1:1, no value created) | none |
| Expected invariant | pause must halt inbound | reentrancy guarded OR no pooled funds to steal | pool index validated before use |
| PASS condition | paused onReceive mints; control onRevert reverts paused | claimed THEFT realized | candidate THEFT mechanism realized |
| FAIL condition | pause blocks onReceive | no value extracted (theft refuted) | mechanism refuted |
| Inconclusive condition | n/a (clean) | router mock cannot be made faithful | n/a (clean) |

**Outcome of the matrix:** all three are harnessable on real source; none required marking
`HARNESS_INCONCLUSIVE`. ZETA-10's heavier V3 mock was built faithfully (constant 1:1, router pays from its own
pre-funded reserves) so any value the attacker gained would have to come from the consumer — exactly the claim
under test — and none did.
