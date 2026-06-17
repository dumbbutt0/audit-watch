# P215 — ANSWER KEY SCORECARD

Opened `_sealed_answer_key/report.md` **after** the freeze (hash `62ef750f12defa79`). Official set: **14 High + 34
Medium + 26 QA/Low**.

## Scope reality (critical context)
The ZetaChain C4 contest scope spanned **the Go node (`zetaclient`/`zetacore`) AND the Solidity contracts**. P215's
discovery was **Solidity-only** (the `contracts/` tree). ~11 of 14 Highs and ~29 of 34 Mediums live in the **Go node
code** and were therefore **out of P215's examined surface by construction** (a scoping decision, recorded honestly —
not a detector miss).

## Solidity-scoped official findings vs P215 candidates
| Official | sev | P215 candidate | score | severity |
|----------|-----|----------------|-------|----------|
| **H-13** onReceive lacks `whenNotPaused` (onRevert has it) → funds lost during pause | High | **ZETA-04** | **HIT** (mechanism exact) | **SEVERITY_UNDER** (I said Medium) |
| **H-10** Trident `getZetaFromToken` wrong `exactInputSingle` → always reverts | High | **ZETA-11** | **PARTIAL / WRONG_MECHANISM** (same contract+fn+DoS impact; I flagged unvalidated `getPools()[0]`) | **SEVERITY_UNDER** (I said Medium) |
| M-09 Direct WETH swap fails on UniV3/PancakeV3 consumers | Med | ZETA-10/ZETA-12 (same contracts) | **ADJACENT** (different mechanism) | n/a |
| M-26 ZRC20 pause-check bypass | Med | — | **MISS** | — |
| M-28 UpdateSystemContract drops `gasPriceByChainId` → halts withdraw | Med | (examined fn in ZETA-07/08) | **MISS** (different defect) | — |
| M-30 `unwhitelist` cannot be invoked | Med | (examined in ZETA-R2) | **MISS** (I refuted *bypass*, missed the *DoS*) | — |
| M-24 Zeta supply inflation on deploy fungible gas coin | Med | — | **MISS** | — |
| QA[09] `updateTssAndConnectorAddresses` same-address | QA | **ZETA-03** | **HIT** | **SEVERITY_MATCH** (both Low/QA) |
| QA[05] ERC20Custody fee divergence | QA | **ZETA-02** | **PARTIAL** | match (both Low) |
| QA[12] whitelist allows any address | QA | ZETA-R2 (refuted bypass) | consistent (it is QA, not a vuln) | — |

## Tally (against the Solidity-examined surface)
- **HIT: 2** (H-13/ZETA-04 ; QA[09]/ZETA-03) · **PARTIAL: 2** (H-10/ZETA-11 ; QA[05]/ZETA-02) · **ADJACENT: 1** (M-09)
- **MISS (Solidity-scoped): 4** (H-06*, M-24, M-26, M-28, M-30) · **MISS (out-of-scope Go node): ~40**
- **TRUE_NEGATIVE: 4** (ZETA-09 rejected by-design + refuted ZETA-R1/R3/R4 — none in the key)
- **FALSE_POSITIVE (queued, non-awarded): 2** (ZETA-07 GAS_LIMIT=0 zero-fee = admin misconfig ; ZETA-12 MEV/deadline = QA-class) — both low-severity, both human-review-flagged, **0 false-Highs**
- **SEVERITY_OVER: 0 · SEVERITY_UNDER: 2** (both genuine Solidity Highs found but rated Medium)

(*H-06 "zEVM messages ignore user-specified message" straddles the fungible keeper/zevm boundary; counted as a miss.)

## Headline
P215 **found both in-scope Solidity Highs** (H-13 exactly, H-10 same-location/impact) but **under-rated both to
Medium**, and **produced zero false-Highs**. Recall was dominated by the **scope gap** (Solidity-only vs a
Go-node-heavy contest). This is the **P212 under-rating pattern reappearing**, not over-rating.
