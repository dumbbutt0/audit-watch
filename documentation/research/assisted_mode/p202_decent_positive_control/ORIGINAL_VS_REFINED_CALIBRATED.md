# P202 — original threat-ceiling vs refined calibration (decent-2024-01)

Scored separately. Calibration by **fresh firewall subagent** (`90cf2a4f`), frozen before the key was opened.
Awarded: 4 High / 5 Medium.

## Headline
| metric | original (ceiling) | refined (gate) |
|---|---|---|
| surfaces ≥ HIGH | **13 / 14 (92.9%)** | **6 / 14 HIGH_CONFIRMED** |
| per-mechanism labels (33) | — | 8 HIGH_CONFIRMED · 12 Medium · 13 Harness |
| genuine awarded-High confirmed (mechanism-matched) | n/a | **H-01 (decent-09) ✅** |
| genuine Highs demoted to Medium/None | — | **0** |
| over-HIGH on matched awarded-Mediums | **5/5** | **3/5** (M-03 receiveFromBridge still High) |
| false HIGH_CONFIRMED | — | M-03×3 (over-HIGH) + decent-06 (+ decent-12 double-withdrawal) |
| HIGH-bucket precision (clean awarded-High / all HIGH_CONFIRMED surfaces) | — | **1/6** clean (decent-09); ~2/6 if loose H-04 counted |

## Two-sided reading
- **Positive (new, decisive):** the refined gate's **High-confirmation path works out-of-sample** — it confirmed a
  genuine permissionless-theft High (H-01 DcntEth setRouter) and demoted/held the rest, with **0 genuine Highs
  demoted to Medium**. P200/P201 never reached this; P201 produced 0 HIGH_CONFIRMED. The fresh-firewall-subagent
  design makes this a valid out-of-sample result (not CONTAMINATED_UPPER_BOUND).
- **Negative:** **HIGH-bucket precision is poor (~1/6).** The gate over-confirmed the awarded-Medium M-03
  (receiveFromBridge) as HIGH on 3 surfaces, plus 1–2 unawarded mechanisms (decent-06 public-swap; decent-12
  double-withdrawal). The Medium-demotion that P201 had validated **regressed** wherever the blind layer over-claimed
  theft.
- **Root cause:** the gate trusts the blind output's asserted magnitude/exploitability. When blind **recall**
  over-claims (theft impact that ignores a real precondition), the gate over-confirms. The gate lacks an independent
  precondition/magnitude check.

## Contrast across the three out-of-sample runs
| run | corpus | Medium-demotion | High-confirmation |
|---|---|---|---|
| P200 | predy | partial (1/4 over-HIGH fixed) | 1 matched High under-graded |
| P201 | zetachain | strong (6/7→0/7) | **untestable** (0 matched contract-Highs) |
| **P202** | **decent** | **regresses** (over-confirms over-claimed Medium) | ✅ **works** (H-01 confirmed; 0 false demotions) |

The campaign now has evidence on **both** axes — but never simultaneously clean. P201 showed clean demotion / no
confirmation; P202 shows confirmation / regressed demotion. The unifying lever: **gate severity must not inherit the
blind layer's magnitude assertion** — it needs an independent magnitude/precondition gate.
