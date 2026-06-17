---
name: feedback-immunefi-v22-severity
description: Immunefi Vulnerability Severity Classification System v2.2 — use these exact standards when triaging and judging all findings, not internal severity definitions
metadata:
  type: feedback
---

Always apply Immunefi v2.2 when scoring severity of smart contract findings. The user explicitly requested this.

**Why:** Immunefi is the bug bounty platform being targeted. Using a different scale produces wrong payout estimates and incorrect submission decisions.

**How to apply:** Replace any internal severity rubric with the table below at triage, calibration, and judge-simulation steps.

---

## Smart Contracts (primary scope)

| Level | Impact |
|-------|--------|
| **Critical** | Any governance voting result manipulation |
| | Direct theft of any user funds, whether at-rest or in-motion, **other than unclaimed yield** |
| | Direct theft of any user NFTs, whether at-rest or in-motion, other than unclaimed royalties |
| | Permanent freezing of funds |
| | Permanent freezing of NFTs |
| | **Miner-extractable value (MEV)** |
| | Unauthorized minting of NFTs |
| | Predictable or manipulable RNG that results in abuse of the principal or NFT |
| | Unintended alteration of what the NFT represents |
| | **Protocol insolvency** |
| **High** | Theft of unclaimed yield |
| | Theft of unclaimed royalties |
| | Permanent freezing of unclaimed yield |
| | Permanent freezing of unclaimed royalties |
| | **Temporary freezing of funds** |
| | Temporary freezing of NFTs |
| **Medium** | Smart contract unable to operate due to lack of token funds |
| | Block stuffing for profit |
| | Griefing (no profit motive for attacker, but damage to users or protocol) |
| | Theft of gas |
| | Unbounded gas consumption |
| **Low** | Contract fails to deliver promised returns, but doesn't lose value |
| **None** | Best practices |

## Blockchain/DLT

| Level | Impact |
|-------|--------|
| **Critical** | Network not being able to confirm new transactions |
| | Unintended permanent chain split requiring hard fork |
| | Direct loss of funds |
| | Permanent freezing of funds (fix requires hardfork) |
| | RPC API crash |
| **High** | Unintended chain split |
| | Transient consensus failures |
| **Medium** | High compute consumption by validator/mining nodes |
| | Attacks against thin clients |
| | DoS of >30% of validator/miner nodes (not shutting down network) |
| **Low** | DoS of >10% but <30% of validator/miner nodes |
| | Underpricing transaction fees relative to computation time |

## Websites and Apps

| Level | Impact |
|-------|--------|
| **Critical** | Execute arbitrary system commands |
| | Retrieve sensitive data/files from running server (shadow, db passwords, blockchain keys) |
| | Taking down the application/website |
| | State-modifying authenticated actions on behalf of other users without their interaction |
| | Direct theft of user funds or NFTs |
| | Malicious interactions with already-connected wallet |
| **High** | Injecting/modifying static content without JS (Persistent) |
| | Changing sensitive details of other users with ≤1 click |
| | Improperly disclosing confidential user information |
| | Subdomain takeover without already-connected wallet |
| **Medium** | Changing non-sensitive user details with ≤1 click |
| | Reflected HTML injection / open redirect |
| **Low** | Changing details with significant user interaction |
| | Taking over broken/expired outgoing links |
| | Temporarily disabling user access |
| **None** | SPF/DMARC misconfigured records |
| | Missing HTTP headers without demonstrated impact |
| | Automated scanner reports without demonstrated impact |

## Key downgrade rule (all categories)

> "If the exploit requires elevated privileges or uncommon user interaction, the level of the bug **may be downgraded** to reflect that or **rejected**."

Elevated privileges = admin/governor/strategist MUST be the attacker (not just a bystander performing routine actions). Routine protocol operations (strategist calling rebalance, vault calling withdrawAll on redemption) are NOT elevated privileges from the attacker's perspective.

## MEV clarification

MEV is explicitly **Critical** for smart contracts. This covers:
- Sandwich attacks on protocol transactions that extract real user funds
- Front-running that causes the protocol to mint unbacked tokens (→ protocol insolvency = Critical)
- Flash loan attacks that manipulate oracles and drain funds

## Yield vs principal theft

- Theft of **principal** (user deposits, locked collateral, vault WETH) = **Critical**
- Theft of **unclaimed yield** (not yet distributed rewards, pending interest) = **High**
