# sentiment — Phase 7: Full(er) per-issue reveal & score — CONTAMINATED-DISCLOSED
## Freeze integrity (AFTER the six sentiment freezes, BEFORE key opened)
BASE_FREEZE `b6494e085ac6de0b…` · SELECTED_LOCI `f1b13eb5ed609dcd…` · MECHANISM_DISCOVERY `909f931d6df2dad5…` ·
DISCOVERY_COVERAGE `5d3adefe6d4968bf…` · RANKING_ABLATION `b3bccb5ef3ec9758…` · PROCEDURE_OUTPUTS `ccdc0ea70306fc7b…`.

## Reveal source / depth
`sherlock-audit/2024-08-sentiment-v2-judging` (post-freeze; search-level-plus). **#541 was pre-excluded** (leaked
P257) — held. Asterisk: contaminated target.

## Awarded findings (retrieved) vs my loci
| issue | locus | mechanism | award-class | vs my selection |
|---|---|---|---|---|
| #613 | bad debt (S-L2 area) | user's bad-debt monitoring → severe losses for others; bad-debt liquidations **inflate SuperPool shares** | subtle_accounting_state (share-price) | S-L2 selected; my winners T7/T6; share-inflation = my T8 family but placed at S-L1 not S-L2 → **ENUMERATED_OUTSIDE_TOP5** (right family, wrong locus/rank) |
| #361/#206 | repay/PositionManager paused | repay blocked when paused, interest accrues | access_control/pause | OUTSIDE_SELECTED_LOCUS (pause class, not selected) |
| #277 | SuperPool | not strictly EIP4626 | token_compatibility/compliance | S-L3 area but compliance class (not my queue-strand) |
| #510/#440 | SuperPool fee | fee set over spec / update lockout | access_control/config | OUTSIDE (config class) |
| #541 | Pool.accrue | (EXCLUDED — leaked P257) | — | hard-excluded, held |

## Scoring
- **S-L2 bad-debt (#613 share-inflation):** my Pass-2 **T8 share-price family was discovered** but placed at S-L1,
  and S-L2 winners were T7/T6 → the awarded share-inflation is **ENUMERATED_OUTSIDE_TOP5 / RANKED_TOO_LOW** (right
  family, wrong locus/rank) — again a **locus/placement** issue more than a discovery-of-shape issue.
- **S-L1 liquidation:** no clean 2024-08 liquidation award confirmed at this depth for my T7 over-seize → UNVERIFIED.
- **S-L3 queues:** awarded SuperPool bugs are EIP4626/fee-config (compliance/access-control class) — NOT my T2
  queue-strand → my S-L3 did not match (partial target-fit: SuperPool awards skew compliance/config).
- Per-profile awarded-selected (confirmed): A 0 / B 0 / C 0. Severe FP: 0. **Asterisk: contaminated + partial reveal.**
