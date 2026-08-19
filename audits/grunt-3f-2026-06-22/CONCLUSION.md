# 3F "Grunt" — Cantina bug bounty — audit conclusion

**Target:** `github.com/3FLabs/grunt` @ `89cbfa01e5d14c34354ef715757bc84289cc2d04` (main HEAD)
**Scope:** `src/` (facility · request · manager · funds · borrow · guard · libs) — ~13.9k LOC, Solidity 0.8.34, Foundry, upgradeable (UCS/ERC-7201 namespaced storage), ERC-6909 intents, Morpho-Blue leverage, RWA fund wrappers (Centrifuge / Superstate USCC / Pareto-Idle).
**Prior audits (in-repo `audits/`):** ChainSecurity Grunt (Apr-2026) · ChainSecurity GruntFunds (Apr-2026) · Cantina Grunt (May-2026) · Cantina Fee Review (May-2026). This was a **post-audit residual hunt**.
**Method:** api-free deep pipeline — Step-0 deep analysis (24 invariants / 13 promising threads / 28 dead-ends) + 4 module deep-reads + 7 specialist agents (logic, economic_attack, erc4626, oracle, access_control, reentrancy, dos), then manual dedup against all 4 prior reports (extracted to text).

## Verdict: HONEST NEGATIVE — 0 novel submittable findings

The protocol is genuinely tight and exhaustively audited. **Every candidate the fleet surfaced maps 1:1 to an existing ChainSecurity/Cantina finding (mostly Low/Informational, several Acknowledged-won't-fix or already Fixed) or to the explicitly-accepted semi-trusted-operator threat model.** No permissionless profitable extraction path exists; no fund-moving/accounting function is reachable by a non-privileged user without proper authorization.

## Candidate → prior-finding dedup map

| Candidate (our fleet) | Prior finding | Status |
|---|---|---|
| **USCCFund `_state` raw-`balanceOf` donation → premature unlock / stranded proceeds** (our headline; logic LG-001 + dos DO-001) | **Cantina 3.3.1** "Raw USCCFund balances credited to wrong order, wrong intent, and wrong LP group" (**Low**) | **DUP — 3F Acknowledged / won't-fix** ("USCCFund is a rolling adapter… late/residual balances are intentionally carried forward"). Same root cause; donation is just a way to inject the residual. Not novel, not submittable. |
| convertToShares/convertToAssets asymmetry (zero-asset 1:1) | **Cantina 3.2.x** zero-asset `convertToAssets`/`previewWithdraw` (**Low/Info**) | **DUP — Fixed in PR185** (partial; residual is documented Low). erc4626 specialist independently found it accounting-only, no value leak. |
| USCC Chainlink missing heartbeat / max-age | Oracle area covered by **Cantina 3.4.10** (accountingPause), **3.3.13** (oracle-revert PM DoS), 3.2.x staleness | **Borderline Low, not filed by 2 audits** — defense-in-depth deviation rail, DEPOSITOR-gated, slow-NAV asset. Not a clean submittable. |
| resolve()/`order.output=0` state-transition bypass | **CS-GRUNT-004** "Facilitator Can Set Return Amount to 0" (Medium) | **DUP — Code Corrected** (+ facilitator is semi-trusted). |
| PM share inflation via direct Morpho collateral donation; virtualShareOffset==1 | **ChainSecurity** "Share Inflation via Direct Morpho Collateral Donation" | **DUP** — and deposit is MINTER-gated (only Facility), so unreachable by an EOA. |
| onRequestConsumed callback reentrancy | **Cantina 3.2.5** | **DUP** (current code clears under re-read). |
| swap() no value-equivalence / stale-rate cross-intent value transfer | **Cantina §1048-1058** (stale approval / intent value transfer) | **DUP** — and requires FACILITATOR + guardian quorum. |
| quorum==0 disables guardian second-factor; stuck funds stolen by malicious facilitator | **ChainSecurity §4.1.1 #4** threat model | **OOS — accepted** (Facilitator semi-trusted). |
| rebalance full-balance sweep to receiver / maxRebalanceLoss bleed | **ChainSecurity §4.1.2** threat model | **OOS — accepted** (Rebalancer semi-trusted). |
| removeBorrowModule no empty-position guard | ChainSecurity §4.1 (owner/semi-trusted; stuck-funds acknowledged) | **OOS — rogue-admin.** |

## Verified-safe (high-value surfaces re-derived clean)
- **No permissionless profitable extraction** (economic_attack): only permissionless fn is `preLiquidate`; bonus bounded to intended 1−LTV, rounding conservative-to-protocol in both modes.
- **Flash-loan callbacks** (Morpho FLR + rebalancer): `msg.sender==MORPHO` + `rawDebt!=0` reentry-block; only EXECUTOR/REBALANCER initiate.
- **PT/YT backing conservation** holds (PT 1:1; YT a yield claim); ERC4626 rounding favors the vault; direct deposits disabled (no inflation surface).
- **Donation immunity** confirmed for Centrifuge/Pareto (balance-delta accounting) and PM NAV (Morpho-ledger collateral, not token balance).
- **Access control**: every fund-moving path role/owner-gated or self-scoped; factories init atomically (no front-run); _disableInitializers present.

## Submission
**Nothing submitted.** No novel, in-scope, reachable, first-to-report vulnerability. Consistent with a 4×-audited target. If a human auditor wants to escalate the oracle-heartbeat Low or the USCCFund residual, both would first need to clear the prior-audit-overlap + acknowledged-design bars in a KYC'd Cantina account — neither is recommended as a payable submission.
