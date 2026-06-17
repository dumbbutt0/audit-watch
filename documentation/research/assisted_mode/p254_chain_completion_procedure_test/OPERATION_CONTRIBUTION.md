# P254 — Operation contribution

Which of the five operations flipped a base bare-candidate into a completed chain, and how that maps to the
awarded truth. Credited only for **pre-reveal** completions (no hindsight).

## Per-locus operation labels (from frozen PROCEDURE_OUTPUTS.md)
| locus | STS | AAS | TSE | IDC | CCIT | chain status | award result |
|---|---|---|---|---|---|---|---|
| L1 AuraVault.claim | PASS | **STRENGTHENED** | PASS | **STRENGTHENED** | NO_EFFECT | PARTIAL | SAME_AREA_WRONG_MECH |
| L2 CDPVault.liquidatePosition | PASS | PASS | PASS | **STRENGTHENED** | NO_EFFECT | PARTIAL | **AWARDED_EQUIVALENT (High)** |
| L3 SwapAction/PositionAction | NO_EFFECT | UNCLEAR | PASS | NO_EFFECT | PASS(refute) | REFUTED | SAME_AREA_WRONG_MECH |
| L4 StakingLPEth cooldown | **STRENGTHENED** | NO_EFFECT(refute↓) | PASS | NO_EFFECT | NO_EFFECT | PARTIAL | SAME_AREA_WRONG_MECH |

## Which operation contributed the one awarded recovery (L2)
- **INVARIANT_DELTA_COMPUTATION (IDC)** is the decisive operation: it computed `collateral-out − debt-down > 0`
  → liquidator profit → the awarded #399 root cause (penalty not incorporated into collateral). This is the
  exact "who-gains/who-loses, is it amplifiable" question the base candidate had left open.
- **STATE_TRANSITION_SIMULATION (STS)** supplied the supporting path (repeat / self-liquidation, worsening
  health), reinforcing impact.
- Consistent with P253's finding that **IDC and STS carry accounting/state completion** — here IDC is the one
  that closed an awarded chain blind.

## Where operations correctly exercised restraint (no false positives)
- **CCIT at L3** correctly *refuted* a cross-principal theft hypothesis (per-proxy delegatecall isolation) — the
  routine did not hallucinate a theft chain. (It also, however, missed the awarded *stranded-funds* mechanism.)
- **AAS at L4** correctly bounded the cooldown-reset to self-inflicted (no on-behalf parameter) → avoided
  over-claiming a High. Honest down-rating.

## Where the operation set under-performed (the key limitation)
- The operations reliably **engage** the right loci but do **not reliably select the awarded mechanism**. At
  L1/L3/L4 the routine completed/refuted a *non-awarded* mechanism while the awarded one (L1 unclaimed-rewards
  mispricing, L3 stranded leftover funds #87, L4 MIN_SHARES donation #228/#382) went unselected — even when
  visible in the same function bodies. Mechanism-**selection**, not operation-execution, is the residual gap.
- No single operation, applied blind, told the operator *which* of several plausible mechanisms is the awarded
  one. The routine is a completion aid, not a mechanism-discovery oracle.

## Net
1 awarded High completed (L2, via IDC+STS), 0 severe FP, but a 1/4 awarded-mechanism selection rate on n=1.
The dominant P253 operations (STS+AAS) appeared, but **IDC** was the one that closed the awarded chain here.
