# Ventuals (vHYPE liquid staking, HyperEVM) — audit findings (Cantina bounty)

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Repo: `ventuals/ventuals-contracts` @ `3621e4d` (Solidity, Foundry, solc 0.8.28, HyperEVM). Cantina bounty (the
$1M Ventuals program). Note: the Solidity scope is **not the pre-IPO perps engine** — it's the **vHYPE liquid-
staking** system on HyperEVM (deposit HYPE → vHYPE; batched withdrawals; staking to a Hyperliquid-L1 validator via
CoreWriter/L1Read precompiles). ~2.2k SLOC. Foundry build OK. Picked as a "less-audited" Cantina target.

## VERDICT: HONEST NEGATIVE — no permissionless High/Critical found. (Target turned out twice-audited.)
`docs/audits/` contains **Nethermind (2025-10-08)** + **Zenith (2025-10-14)** reports — so this is NOT un-audited.
The codebase is carefully built (explicit one-block-delay guards around HyperEVM↔L1 reads; conservative rounding).

## Reviewed
- **Exchange rate / first-depositor inflation** (`StakingVaultManager.exchangeRate` = raw `totalBalance·1e18/
  totalSupply`, no virtual-shares/dead-shares offset; deploy script does NOT seed): structurally the classic
  first-depositor inflation exists, and `totalBalance()` counts external donations (L1 spot-send to the vault /
  force-fed `evmBalance`). **However:** (a) the protocol is twice-audited and `ARCHITECTURE.md` explicitly discusses
  exchange-rate/donation/same-block manipulation (it's a considered area; donation-via-burn is an *intended*
  mechanic), and (b) `require(amountToMint > 0)` turns the round-to-zero case into a revert (griefing, not theft),
  and (c) **exploitability requires an empty vault (`totalSupply==0`)** — on a live, seeded deployment the first
  deposit already happened, so it's not currently exploitable. Honest rating: **Informational/Low, contingent on
  live state** (per the infiniFi rule: verify `vHYPE.totalSupply()` on HyperEVM before any higher claim; a seeded
  live vault ⇒ not exploitable). Not submitted as a finding.
- **Decimals (8↔18)** (`Converters`): HYPE is 8-dec on L1, 18-dec on EVM. `to8Decimals` truncates; deposit strips
  sub-1e10 dust; `claimWithdraw` sends `to8Decimals()` while `totalHypeClaimed` counts the full 18-dec → dust stays
  with the protocol (favors existing holders). Conservative; no value creation/extraction.
- **Withdrawal queue** (`StructuredLinkedList`): the battle-tested vittominacori/EigenLayer library; `remove`/
  `insert`/cursor used correctly. `cancelWithdraw` only removes UNprocessed nodes (`batchIndex==max`); `processBatch`
  advances an O(1) cursor (`lastProcessedWithdrawId`) and doesn't remove processed nodes (minor storage growth, not
  a security issue). No double-process / cursor-corruption found.
- **Batch processing / claim** (`processBatch`/`finalizeBatch`/`claimWithdraw`): withdrawals settle at the batch
  `snapshotExchangeRate` (or `slashedExchangeRate`); escrowed vHYPE burned on finalize; claim gated by `finalizedAt
  + 7 days + claimWindowBuffer`; capacity bounded by `totalBalance − minimumStakeBalance − hypeProcessed`. Rounding
  (`Math.mulDiv` floor) favors the protocol. `totalBalance` underflow guarded
  (`AccountBalanceLessThanReservedHypeForWithdraws`).
- **HyperEVM↔L1 timing** (`StakingVault`): careful one-block-delay guards on `spotBalance`/`delegation` reads after
  state-changing actions (`lastSpotBalanceChangeBlockNumber`, `lastDelegationChangeBlockNumber`) — the L1Read
  staleness pitfall is explicitly handled. `spotSend`/`transferHypeToCore` check core-account existence (avoid
  silent HYPE loss). Validators whitelisted; `unstake` respects the 5-pending-withdrawal L1 limit.
- **Access control**: `onlyManager`/`onlyOwner`/`onlyOperator` via `RoleRegistry`; slash/emergency/reset are
  owner-only (privileged → OOS for permissionless bugs). `applySlash` adjusts `totalHypeProcessed` consistently.

## Bottom line
The vHYPE liquid-staking system is carefully built and twice-audited; conversions/queue/batch/L1-timing all hold,
rounding favors the protocol, and the only structural note (no virtual shares) is a known, live-state-contingent
Informational. No permissionless High/Critical → **honest negative, not submitted.** (The "less-audited" thesis
didn't hold — Ventuals' staking is twice-audited.)
