# P132 — Decision

## Decision: **ACCEPT_DEFAULT_ON_TRIMMED**

The two trims reduce obvious mock/trivial boost noise **without losing any of the P130/P131 recall gain**, with
no test regressions and no control regression — meeting every ACCEPT_DEFAULT_ON_TRIMMED criterion.

### Rubric check
- ✅ **All 8 newly-surfaced noya awarded functions remain covered** (awarded boosted 8→8; awarded-function
  deep-pass coverage 74% → 74%).
- ✅ **Obvious mock/trivial noise reduced** (−7: 3 mock `ConnectorMock2.*` + 4 trivial empty-array/empty-body).
- ✅ **No test regressions** beyond the known pre-existing `deep_solidity` snapshot failures (full suite
  1586 passed / 2 pre-existing fails / 4 skipped; +14 new P132 tests pass).
- ✅ **No material control regression** (decent awarded 33%→33%, volume 52→52, no path breakage).

Not ACCEPT_WITH_LIMITS_TRIMMED: recall is preserved and noise reduced cleanly; the only outstanding item
(human-graded FP of the on-class residual) is a pre-existing P131 measurement gap, not a limit introduced by the
trims. Not TUNE_AND_RETEST: no useful class was accidentally removed (body-based rule kept all functions with
real logic, incl. sibling `_getUnderlyingTokens` with non-empty bodies). Not REVERT_TRIMS: zero awarded loss,
no material test regression.

## What was removed and why (exactly 7, all provable noise)
- mock (3): `ConnectorMock2.{_updateTokenInRegistry, getPositionTVL, getUnderlyingTokens}` — a mock contract.
- trivial (4): `Aave/Compound/SNXV3 ._getUnderlyingTokens` (`return new address[](0);`),
  `Watchers.verifyRemoveLiquidity` (trivial/empty body).

## Limits (honest)
- The body-based trivial rule is deliberately conservative (only the enumerated trivial shapes), so some
  lower-value-but-non-trivial getters remain — acceptable, since over-trimming risks the awarded value_exit class.
- Downstream human-graded FP of the remaining on-class residual is still unmeasured (P131 limit), and
  enumeration/scope misses (`SNXConnector._getPositionTVL` absent; `updateTVL` untagged) are outside this
  ranking/trim lever.

## Next recommended phase (P133)
A human-graded specialist run on the (now trimmed) noya boost-delta to convert the 74% recall ceiling + the
on-class residual into measured recall/FP rates; then enumeration/scope + callgraph-reachability work for the
residual non-ranking awarded misses.
