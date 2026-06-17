# P152 — Runtime Result

| field | value |
|---|---|
| harness_type | real_contract (real `ERC20MultiVotes` logic inherited) |
| tests | 3 passed / 0 failed / 0 skipped |
| suspected mechanism | delegated votes retained/inflated after transferring tokens away |
| real transfer | `getVotes(delegatee)` 1000e18 → **0** (guard `_decrementVotesUntilFree` frees the delegation) |
| vulnerable reference (unguarded) | `getVotes(delegatee)` retains 1000e18 (bug shape the real contract avoids) |
| control (no transfer) | `getVotes(delegatee)` stable at 1000e18 |
| runtime_status | **runtime_refuted** |
| runtime_confidence | high |
| reachability_verdict | unprivileged surface, but mechanism absent |
| severity_class | no_security_impact_shown |
| duplicate_status | duplicate_unknown |

## What this proves
The canonical ERC20MultiVotes "vote retention after transfer" suspicion is **refuted** in the real contract: the
guarded `transfer` decrements the delegatee's checkpointed votes, so a holder cannot keep delegated voting power
after moving their tokens. The vulnerable reference (unguarded transfer) shows what the bug would look like;
the control confirms no spurious change.

## Conversion
- `mechanism_confirmed: false` (suspicion killed), `attacker_reachable: true` (surface is unprivileged, but the
  mechanism is absent), `severity_bearing: false`, `novelty_clear: false`, `reportable: false`,
  `outcome: runtime_refuted`, `blocker: null` (mechanism_absent_guard_present).
- Not submission-ready. `duplicate_unknown` carries no novelty inference.
