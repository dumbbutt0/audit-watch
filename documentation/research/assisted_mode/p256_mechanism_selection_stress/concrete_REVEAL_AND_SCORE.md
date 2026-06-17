# concrete — Phase 5: Reveal & score — **REVEAL UNAVAILABLE**

## Freeze integrity (recorded AFTER the three concrete freezes, BEFORE any reveal attempt)
- `concrete_BASE_FREEZE.md`       sha256 `41625ef5c312ee3d…`
- `concrete_MECHANISM_GATE.md`    sha256 `731f2de10fa87296…`
- `concrete_PROCEDURE_OUTPUTS.md` sha256 `e99520861a9f02ed…`

## Reveal outcome: NOT RETRIEVABLE
`audits/concrete-2024-11-fresh/reports/` is empty (no local key). The public reveal sources used for P254/P255
were not retrievable for this contest:
- `code4rena.com/reports/2024-11-concrete` → **HTTP 404** (report slug not published/!indexed at that path).
- `github.com/code-423n4/2024-11-concrete-findings/issues?...` → **HTTP 404** (findings repo not public-accessible).
- Solodit / WebSearch returned no specific concrete-2024-11 finding details.
- `gh` CLI not installed in this environment.

**Consequence:** concrete's awarded mechanisms cannot be obtained without contaminating the freeze (there is no
key to open). Per the no-hindsight rule, concrete's gate outputs remain **frozen and hashed but UN-SCORED**. They
are recorded for provenance; concrete contributes **0 scored loci** to the P256 diagnosis.

## Frozen (un-scored) concrete gate selections — for the record only
| locus | SELECTED | RUNNER_UP | (cannot classify — no key) |
|---|---|---|---|
| C-L1 WithdrawalQueue.prepareWithdrawal | M1 finalize-direction inversion | M2 strict-availability off-by-one | UNSCORED |
| C-L2 Vault.takeFees/protocol fee | M1 protocol-fee dilution on totalAssets | M2 HWM pre-mint timing | UNSCORED |
| C-L3 _withdrawStrategyFunds | M1 diff-vs-amount_ basis mismatch | M2 Ceil dust | UNSCORED |

**Impact on P256:** the diagnosis rests on **plaza only** (1 fully-revealed contest, 3 scored loci). This is the
key limitation of P256 and is carried into the verdict — a confirmation run on another fully-revealed subtle
contest is required before treating the diagnosis as settled.
