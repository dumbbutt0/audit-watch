# P152 — Candidate Selection

Requirements: `duplicate_unknown` (no local answer key); deploy-light real-contract harness; not heavy oracle/RPC/
bridge; crisp state delta; **distinct mechanism class**; unprivileged surface (so reachability is answerable);
useful for conversion learning (not merely easy to confirm).

| audit | target | mechanism class | deploy | verdict |
|---|---|---|---|---|
| **ecg-2023-12-holdout** | **`ERC20MultiVotes` (delegate/transfer)** | **governance vote-accounting** (new) | moderate (OZ v4.9 ERC20Permit/EnumerableSet + local SafeCastLib) | **SELECTED** — distinct class, unprivileged, crisp `getVotes` delta, conversion-learning (likely refute) |
| pooltogether-2024-03 | `PrizeVault` preview/redeem | preview/execute (ERC4626) | heavy (underlying + yield vault + TWAB controller mocks) | REJECTED (deploy-heavy) |
| munchables-2024-05 | distributors/managers claim/lock | claim accounting | large multi-manager surface | REJECTED (not deploy-light) |
| kelp-2023-11 | `LRTDepositPool` | deposit accounting | oracle/RSETH deps | REJECTED (already rejected P150) |

## Why ecg ERC20MultiVotes
- **Distinct mechanism class** vs P143/P145/P147/P148/P150 (vote-accounting/checkpoint, not value/recipient/sig).
- **Unprivileged**: any holder can `delegate`/`transfer` → the phase can answer **both** mechanism and reachability
  (the user's preference), not isolated contract behavior.
- **Crisp delta**: `getVotes(delegatee)` before/after a transfer.
- **Conversion learning**: the canonical "votes retained after transfer" suspicion is exactly the ERC20MultiVotes
  risk; testing it on the real (guarded) contract most likely **refutes** — a valuable, honest, non-confirm result.
- **Real surface, no source edit**: `ERC20MultiVotes` is abstract; a minimal concrete subclass inherits the real
  delegate/transfer/`_decrementVotesUntilFree`/`getVotes` logic unmodified, adding only `mint`/`setMaxDelegates`
  (the documented "parent adds permissioned public functions" pattern).
