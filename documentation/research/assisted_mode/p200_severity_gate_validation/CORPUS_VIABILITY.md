# P200 — corpus viability

## Pre-registered targets both NON-VIABLE
| corpus | High | Medium | viable for High-vs-Medium calibration? |
|---|---|---|---|
| badger-2024-06-holdout (primary) | **0** | 2 | ❌ 0 High → cannot test genuine-High preservation; too thin |
| kleidi-2024-10-holdout (fallback) | **0** | 3 | ❌ 0 High → same defect |

The phase's core property — *does the gate avoid demoting genuine Highs* — is untestable on a 0-High corpus. The
approved plan's named target **and** its named fallback both fail the severity bar. This forced a documented
substitution (a deviation surfaced to the user, not a silent swap).

## Substitute: predy-2024-05-holdout (user-selected)
- **4 High / 8 Medium** — both severity tiers present; fresh (never used in P186/P189/P198).
- Predy V6 perps/gamma derivatives, 32 core `.sol` / 7402 LOC — CDP/liquidation/oracle/accounting/settlement
  surfaces, severity-rich. Best balance + sample-representativeness among the fresh candidates
  (vs zetachain 14H/34M = richer but sprawling/under-sampled; vultisig 3H/3M = thin).

## Viability verdict: VIABLE (with a recorded caveat)
predy supports the High-vs-Medium test. **Caveat surfaced by scoring:** of the 16 blind surfaces, only **5** carried
a blind mechanism that *matches* an awarded finding (exact/secondary), and only **1** awarded-High (H-02) was found
by mechanism. So the *severity-scoring* subset is small (n=5 matched Mediums, 1 matched High) — the result is an
out-of-sample **signal**, not a high-powered measurement. This is a recall limitation of a bounded 16-surface blind
sample, not a defect of predy itself.
