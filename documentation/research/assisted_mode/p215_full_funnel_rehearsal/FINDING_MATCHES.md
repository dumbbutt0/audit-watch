# P215 — FINDING MATCHES (detail)

## ZETA-04 ↔ H-13 — HIT (mechanism exact) · SEVERITY_UNDER
- **Official H-13** (High): "`onRevert` is gated with `whenNotPaused` while `onReceive` is not … a revert in `onReceive`
  kicks off the refund → calls `onRevert` on the originating chain, but that always reverts if paused → user funds lost
  in favor of the protocol." Files: `ZetaConnector.eth.sol#L85`, `ZetaConnector.non-eth.sol#L95`.
- **P215 ZETA-04**: "onReceive is onlyTssAddress but NOT whenNotPaused, while onRevert IS whenNotPaused. Pause cannot
  stop inbound delivery." Same files, same exact asymmetry.
- **Verdict:** the root cause is identical. P215 framed the impact as availability/Medium; the judges escalated to High
  because it causes **user fund loss during a paused CCTX**. → SEVERITY_UNDER by one level. Also: P215 left it
  `NEEDS_HARNESS` (no executed PoC), so the funnel never surfaced it as a submit-ready High.

## ZETA-11 ↔ H-10 — PARTIAL / WRONG_MECHANISM · SEVERITY_UNDER
- **Official H-10** (High): `ZetaTokenConsumerTrident.getZetaFromToken` calls the **wrong `exactInputSingle` router
  method** → always reverts (the contract can't deposit into BentoBox) → Trident swaps permanently broken.
- **P215 ZETA-11**: flagged the **same contract+function** and even quoted the exact lines
  (`poolFactory.getPools(token0,token1,0,1)`, `pool: pairPools[0]`), but identified a **different** defect (unvalidated
  pool array → DoS/empty-revert). Same location, same impact class (Trident swap reverts = DoS), different precise root
  cause. → PARTIAL with WRONG_MECHANISM; rated Medium vs official High → SEVERITY_UNDER.

## ZETA-03 ↔ QA[09] — HIT · SEVERITY_MATCH
- **Official QA[09]**: `updateTssAndConnectorAddresses` lets TSS & Updater be set to the same address.
- **P215 ZETA-03** folded this (renounce collapses two-party control / self-rotation) and **triaged it down to Low**
  (privileged/centralization). Official rated it QA. → correct calibration of a centralization item (**no over-rating**).

## ZETA-02 ↔ QA[05] — PARTIAL
- Official QA[05] "ERC20Custody divergence regarding fees" ≈ P215 ZETA-02 (zetaFee transfer not balance-checked).
  Both Low/QA.

## M-09 ↔ ZETA-10/ZETA-12 — ADJACENT
- M-09 (Medium): direct WETH swap incompatibility on `ZetaTokenConsumerUniV3`/`PancakeV3`. P215 examined the same
  contracts (reentrancy ZETA-10; deadline ZETA-12) but a different mechanism. Same surface, no mechanism match.

## True negatives (correctly not promoted)
- **ZETA-09** (anyone can deploy a connector) — rejected by-design in triage; **not in the answer key** → TRUE_NEGATIVE.
- **ZETA-R1** (deposit reentrancy), **ZETA-R3** (ZRC20 CEI), **ZETA-R4** (WZETA uint(-1)) — refuted at discovery;
  none in the key → TRUE_NEGATIVE.
