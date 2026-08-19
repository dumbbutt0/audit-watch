# Exactly — Immunefi bug bounty — audit conclusion

**Target:** Exactly (Immunefi, $25K max, Optimism, KYC + runnable PoC, live since Dec-2022, scope last updated Mar-19-2026).
**Scope:** 23 deployed Optimism contracts (12 named); verified source fetched via Etherscan V2 (chainid 10), proxies resolved to implementations. Repo `github.com/exactly/protocol` (HEAD 5c1d934) + plugin repo `github.com/exactly/mobile` used for context/dedup.
**Key reconciliation:** the deployed in-scope `InterestRateModelUSDC`, `DebtManager`, `IssuerChecker`, `Refunder` **differ from repo HEAD** (different addresses / not in repo) → audited the actual deployed bytecode-source, not HEAD.
**Focus (per "best odds"):** the freshest / least-audited surface — the **card/installments payment system** (`IssuerChecker`, `Refunder` are deployed-only, not in the public repo) + the deployed-vs-repo `InterestRateModelUSDC` and `DebtManager` delta.
**Prior audits (dedup):** ABDK ×9 (incl. IRM v2, InstallmentsRouter Apr-2024), Coinspect ×8, Chainsafe ×4, Quantstamp ×3 (Exa App **plugin** Jul-2024/Mar-2025/Oct-2025), Hashlock ×2, OZ, Sherlock.

## Verdict: no novel submittable finding

### Candidates assessed
| Candidate | Disposition |
|---|---|
| **CARD-001 — `IssuerChecker` signature is operation-agnostic**: signs only `(account, amount, timestamp)`, not which collect op (collectCredit/Debit/Installments/Collateral) nor params (maturity/route/slippage). One issuer sig could be substituted across collect variants. | **Not submittable.** Resolved via the plugin source (`exactly/mobile` `ExaPlugin.sol`): all four `collect*` are gated `keeperRuntimeValidationFunction` (manifest L388-402) → **only the trusted KEEPER** can call them. So substitution needs a malicious keeper (trusted role / centralization = OOS), the ExaPlugin is **out of the in-scope address set**, and it's **Quantstamp-audited ×3**. Defense-in-depth note at best. |
| **`IssuerChecker.check()` front-run griefing**: `check()` is permissionless and burns the replay hash, so seeing an issuer sig in the mempool lets an attacker pre-burn it → legitimate collect/refund reverts `Replay`. | **OOS** — griefing (explicitly out-of-scope for Exactly), re-issuable with a new timestamp, no fund loss/freeze ≥4h. |
| **EIP-712 typehash `uint40 timestamp` vs uint256 encode** | Cosmetic; self-consistent (32-byte word), chainid in domain. No replay. |
| **`DebtManager` flash-loan callback** | **Safe.** `receiveFlashLoan` asserts `msg.sender==balancerVault` + non-zero self-set `callHash==keccak(userData)` (zeroed in callback). Canonical missing-initiator class closed. |
| **`DebtManager` cross-user / drain** | **Safe.** Every op `msg.sender`-scoped behind Exactly `spendAllowance` / ERC4626 allowance; attacker holds no victim allowance. `permit` overloads only create a harmless dangling allowance (no primitive consumes another's allowance). |
| **Deployed `InterestRateModelUSDC`** | Legacy (already-audited) fixed/floating curve, not sigmoid v2; donation-immune (reads internal floatingDebt/Assets), reverts on utilization>1e18, no overflow/div-by-zero; flash-loan utilization swings extract no value. |
| **`InstallmentsRouter`** | borrower hard-bound to `msg.sender`, aggregate `maxRepay` slippage, permit self-only. Audited ABDK+Hashlock Apr-2024 (dup). |
| **`Refunder`** | keeper + issuer-signed, account-bound, replay-protected, deposits own USDC; no unprivileged drain (`withdraw` admin-only). |

## Submission
**Nothing submitted.** No novel, in-scope, permissionless fund-loss/freezing bug. The freshest surface (card system) is fully keeper+issuer trusted-gated; the changed IRM/DebtManager deployments re-derive clean; the core markets are exhaustively audited. Same well-built-negative outcome as the grunt and Ethena hunts.
