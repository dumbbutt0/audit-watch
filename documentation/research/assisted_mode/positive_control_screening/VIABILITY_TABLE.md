# PCS — viability table

From firewall screening subagents (tallies only; orchestrator did not receive verbatim High titles/loci — see the
contamination note in `integrity_checks.md`). "Qualifying High" = contract-level AND source-reachable AND
(permissionless OR attacker-controlled) AND impact ∈ {theft, insolvency, permanent-loss, priv-transition}.

| corpus | High | Medium | likely contract-level Highs | source-reachable? | qualifying Highs | enough Mediums for over-HIGH demotion? | accept/reject + reason | unseal boundary |
|---|---|---|---|---|---|---|---|---|
| **decent-2024-01** | 4 | 5 | **4/4** | yes (all 4) | **4** (1 theft + 3 permanent-loss; 3 permissionless, 1 attacker-controlled) | **yes** (5) | **ACCEPT** — most qualifying contract-Highs of the three; bridge value-flow, all source-reachable | High titles+summaries+actor/impact (H-01..H-04); Medium count only |
| vultisig-2024-06 | 3 | 3 | 3/3 | yes (all 3) | 2 (2 permanent-loss permissionless; 1 classified "other"/access-bypass → non-qualifying) | borderline (3) | accept (2nd choice) — 2 qualifying but only 3 Mediums (thin demotion power) | High titles+summaries+brief body; Medium header count (3) |
| munchables-2024-05 | 2 | 4 | 2/2 | yes (both) | 2 (1 theft + 1 permanent-loss, both permissionless) | yes (4) | accept (3rd choice) — only 2 Highs total (thin preservation power); config/manager-heavy | High titles+summaries; Medium header count (4) |

## Read
- **All three** have contract-level, source-reachable, permissionless Highs — none is off-chain-dominated like
  zetachain. The campaign's positive-control problem is solvable.
- **decent** dominates: **4 qualifying** contract-Highs (incl. ≥1 clean permissionless theft) + 5 Mediums →
  strongest power for *both* High-preservation AND continued over-HIGH demotion.
- vultisig (2 qualifying / 3 Med) and munchables (2 qualifying / 2 High total) are viable fallbacks but thinner.
