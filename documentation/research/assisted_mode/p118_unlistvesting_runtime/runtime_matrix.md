# P118 — Runtime matrix (forge, local, no fork)

Command (from `/tmp/p97-secondswap`): `forge test --match-contract UnlistVestingRuntime -vv` → **4 passed**.
Full log: `execution_output.txt`.

| Case | Caller / action | Expected | Result |
|---|---|---|---|
| A | `attacker` (non-seller, non-admin) calls `unlistVesting` | revert "SS_Marketplace: Not the seller" | **PASS** (reverted) |
| B | `holder` unlists once, then again (warp +121s) | 1st ok; 2nd revert "Listing not active" | **PASS** (no double-unlist) |
| C | `holder` unlists own active listing once | success | **PASS** |
| D | `admin` (s2Admin) unlists | success (privileged branch) | **PASS** |

- Access control (`seller==msg.sender || s2Admin`) blocks the unauthorized caller (A).
- Status guard + `status→DELIST` + `balance→0` prevent a second unlist / double balance-return (B).
- Legitimate seller (C) and admin (D) paths work exactly once.
