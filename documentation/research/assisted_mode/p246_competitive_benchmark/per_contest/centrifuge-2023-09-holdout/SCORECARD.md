# centrifuge-2023-09-holdout — SCORECARD

Freeze hash: 471c30ca54605916dedc406bf565584c11eacb1ac71f6777fedcbead2a4928fd (before reveal).
Sealed-key hash: 81cb03b04d084cbc. Awarded: 0 High + 8 Medium = 8.

## Awarded-finding scoring
| Awarded | Sev | My candidate | Class | Credit |
|---|---|---|---|---|
| M-01 onlyCentrifugeChainOrigin can't require msg.sender==axelarGateway | Medium | — (Axelar Router not read) | MISSED | 0 |
| M-02 requestRedeemWithPermit front-runnable via different pool | Medium | — (read LP permit fns, missed frontrun) | MISSED | 0 |
| M-03 cached DOMAIN_SEPARATOR wrong for tranche tokens | Medium | — (token/ERC20 not read) | MISSED | 0 |
| M-04 deposit tiny amount for other users → DoS | Medium | C-L1/C-H1 (process-for-others + price drift area) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-05 deposit() draws shared escrow → others can't claim maxDeposit/maxMint | Medium | C-H1 (orderbook/decreaseLimits accounting) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-06 DelayedAdmin cannot PauseAdmin.removePauser | Medium | — (admins not read) | MISSED | 0 |
| M-07 trancheTokenAmount must round UP on withdraw | Medium | C-H1 (rounding direction area) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-08 RestrictionManager incomplete ERC1404 → restricted accounts have access | Medium | — (RestrictionManager not read) | MISSED | 0 |

## System-finding scoring (precision)
C-M1 (isAllowedAsPoolCurrency return ignored)→PLAUSIBLE (real, not awarded H/M — likely QA); C-M2 (auth-gated
convertTo*)→PLAUSIBLE; C-M3 (withApproval no allowance)→PLAUSIBLE (async-4626 intentional divergence);
C-H1→AWARDED_EQUIVALENT-partial (M-04/05/07 area); C-L1→PLAUSIBLE; C-L2→BENIGN. Hard FP: 0.

## Metrics
- High recall: n/a (0 Highs). Medium recall: strict 0/8 = 0%; credited 0.75/8 = 9%.
- Weighted recall (denom 8): numerator 0.75 → **9.4%**.
- Coverage completeness: **~45%** (142/329 critical read — core IM+LP only). **Gate would BLOCK** (coverage
  incomplete) — correctly flagging that triage should not proceed here.
- Advisory lens contribution: 0. Proof: BLOCKED_BY_BUILD.

## Miss attribution
- M-01 → **Coverage** (Axelar Router unread)
- M-02 → **Permit/signature** (read LiquidityPool permit fns; missed cross-pool front-run)
- M-03 → **Coverage** (token/ERC20 DOMAIN_SEPARATOR unread)
- M-06 → **Coverage** (admins/DelayedAdmin/PauseAdmin unread)
- M-08 → **Coverage** (RestrictionManager unread)
- M-04/M-05/M-07 → partially credited; residual **Reasoning depth** (deposit-accounting / rounding-direction)

## Note
This is the realistic large-cross-chain datapoint: 4 of 8 misses sit in layers not fully read → the P245
gate would correctly BLOCK (coverage incomplete) rather than let a partial-coverage triage proceed. Recall
here is coverage-bound, consistent with P241/P243. Training-data confound applies to the public findings.
