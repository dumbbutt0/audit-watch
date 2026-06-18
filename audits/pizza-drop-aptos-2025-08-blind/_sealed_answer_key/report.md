# Pizza Drop (CodeHawks 2025-08-aptos-pizza-drop) — AWARDED FINDINGS (revealed post-blind-pass)

Counts confirmed from the CodeHawks results page: High = 2, Medium = 1.
Titles reconstructed from the public submissions list at
https://codehawks.cyfrin.io/c/2025-08-aptos-pizza-drop/submissions
(deduped to the awarded root causes; the detailed awarded report PDF is not web-accessible, so the
exact awarded-severity split is the best reconstruction from the clustered public submissions —
the orchestrator stayed BLIND on titles until after the cold pass).

## High Risk Findings

- H-01 | Access-control bypass: anyone can self-register and drain the pool — `get_random_slice` is a public `entry` with no owner check, so any account registers itself (or arbitrary addresses) for a claimable amount, bypassing the owner-only `register_pizza_lover` gate, then calls `claim_pizza_slice` to drain the resource account. (Submissions: "Anyone can self-register and set a claimable amount (owner bypass)", "Ability to Self-Register and Drain the Pizza Drop Pool", "Authorization Bypass Allows Unlimited Reward Registration", "Access Control Bypass Vulnerability".)

- H-02 | Reward denominated in Octas instead of APT (units/documentation mismatch) — `random_amount = 100 + random_val` is treated as raw Octas (10^-8 APT) while the intent/comment is "100-500 APT", so recipients receive dust instead of the documented amount. (Submissions: "Invalid reward set in Octas not in APT", "Mismatch Between Documentation and Implementation Causes Users to Receive Incorrect APT Values".)

## Medium Risk Findings

- M-01 | Predictable / insecure randomness — `get_random_slice` derives the airdrop amount from `timestamp::now_microseconds() % 401`, a fully predictable and proposer-influenceable value, and does not use the secure `aptos_framework::randomness` API; the publicly-callable `#[randomness]` entry is also exposed to test-and-abort biasing, letting a caller manipulate/maximize the amount. (Dominant submission cluster: "Predictable Randomness from Timestamp", "Unsafe Public Randomness: Selective Abort Attack", etc.)
