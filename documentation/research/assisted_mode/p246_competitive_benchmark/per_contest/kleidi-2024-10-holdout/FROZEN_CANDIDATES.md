# kleidi-2024-10-holdout — FROZEN CANDIDATES (blind, pre-reveal)

Architecture: Gnosis-Safe + self-administered Timelock + Guard + RecoverySpell (Solidity-Labs-authored,
hardened, heavily-commented with stated invariants/known-issues). Sealed-key hash 1deef6f39536eb73 (not
opened). Read in full: Timelock, Guard, RecoverySpell, RecoverySpellFactory, InstanceDeployer, BytesHelper,
ConfigurablePause (skim). Advisory lenses: safe_management 0, hostile_token 0, create_time **2** (advisory,
on create/deploy flow — to be classified; expected benign).

## Candidates (base hunt) — note: hardened target, low-confidence set
| id | sev | locus | mechanism |
|---|---|---|---|
| K-M1 | Medium | RecoverySpellFactory._paramChecks / RecoverySpell.executeRecovery | `recoveryThreshold == 0` is permitted (only `threshold != 0` enforced); with `delay == 0` a recovery spell rotates all safe owners with ZERO signatures, instantly — any party can cast it once the spell is a module. Operator-config risk / footgun escalating to takeover. |
| K-M2 | Medium | Timelock.checkCalldata / _addCalldataCheck (wildcard) | A wildcard check (`startIndex == endIndex == 4`) makes `checkCalldata` `return` early → any calldata for that selector passes. Add/remove ordering around the "wildcard only if no other checks" guard may allow a wildcard to coexist/bypass concrete checks → hot signer executes arbitrary params. |
| K-M3 | Medium | Timelock._removeCalldataCheck / removeCalldataCheckDatahash | swap-and-pop over `Index[]` whose elements contain `EnumerableSet` (dataHashes) manually copies set members between structs; risk of corrupting/duplicating remaining checks (storage-pointer aliasing) → stale or missing calldata checks. |
| K-L1 | Low | Timelock.initialize | no access control (`require(!initialized)` only); mitigated because InstanceDeployer initializes atomically, residual if ever deployed manually. |
| K-L2 | Low | RecoverySpellFactory | `createRecoverySpell` (transient-storage) vs `calculateAddress` (nested-loop) use different duplicate-owner checks → consistency/clone-mismatch risk. |

## Gate / proof status
P245 gate: would block until 64 critical READ_FULL (all read). Proof: BLOCKED_BY_BUILD. Honest note: this is a
hardened, formally-reasoned codebase; the base hunt produced no high-confidence High and may miss the awarded
set — recorded without optimism.
FREEZE: final pre-reveal.
