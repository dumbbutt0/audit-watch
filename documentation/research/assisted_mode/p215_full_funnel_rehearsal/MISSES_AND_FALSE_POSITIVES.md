# P215 — MISSES AND FALSE POSITIVES

## Misses — out of scope (by construction, not detector failure)
~11 of 14 Highs and ~29 of 34 Mediums are in the **Go node** (`zetaclient`/`zetacore`): observer/voting/cctx/UTXO/TSS
logic (H-01..H-09, H-11, H-12, H-14; most Mediums). P215 discovery was **Solidity-only**, so these were never examined.
**Lesson:** for a real ZetaChain-style hunt the funnel must scope the off-chain node code, which is where most
fund-loss Highs lived.

## Misses — Solidity-scoped (genuine recall gaps within the examined surface)
- **M-30** `unwhitelist` cannot be invoked (ERC20Custody DoS): P215 examined whitelist/unwhitelist but only checked for
  an access-control *bypass* (refuted as ZETA-R2). It did not test the *liveness* of `unwhitelist` → missed the DoS.
- **M-28** `UpdateSystemContract` drops `gasPriceByChainId` → halts `withdraw`: P215 examined both
  `updateSystemContractAddress` (ZETA-08) and `withdrawGasFee` (ZETA-07) but flagged different defects (mint-authority;
  GAS_LIMIT=0) and missed the state-migration DoS.
- **M-26** ZRC20 pause-check bypass; **M-24** Zeta supply inflation on deploy-fungible-gas-coin: not surfaced.
- **H-06** zEVM message-ignored: straddles fungible keeper / zevm boundary; not surfaced.

## False positives (entered dry-run queue, non-awarded) — both low, both human-flagged, 0 false-Highs
- **ZETA-07** GAS_LIMIT=0 → zero gas fee: real on-chain behavior (executed harness), but it requires a **privileged
  misconfig** and is **not an awarded finding** → treat as QA/admin-hardening, not a vuln.
- **ZETA-12** deadline=`block.timestamp+200` / weak MEV slippage: a recognized QA-class observation, **not awarded** in
  this contest.
Neither is a dangerous false-High; both were queued as Low/Medium with `human_review_required=true`.

## Wrong-refutation check
P215 refuted ZETA-R2 (whitelist *bypass*) — consistent with official QA[12] (whitelisting any address is QA, not a
vuln). No official finding was wrongly refuted. The M-30 *unwhitelist DoS* is a **separate** mechanism P215 simply did
not look for — a miss, not a wrong refutation.
